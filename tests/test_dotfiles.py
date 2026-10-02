"""Regression checks using real chezmoi rendering and isolated command doubles.

Run: python3 -m unittest discover -s tests -v
No real package installations, removals, or home-directory changes are made.
"""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
CHEZMOI = shutil.which("chezmoi")
BASH = shutil.which("bash")
ZSH = shutil.which("zsh")
ASDF_HOOK = ".chezmoiscripts/run_onchange_after_20-setup-asdf.sh.tmpl"


# All package-manager calls are intercepted. Unknown operations fail closed.
COMMAND_DOUBLE = r'''
import json
import os
from pathlib import Path
import subprocess
import sys

root = Path(os.environ["DOTFILES_TEST_ROOT"])
name = Path(sys.argv[0]).name
args = sys.argv[1:]
state = json.loads((root / "state.json").read_text())
with (root / "commands.jsonl").open("a") as log:
    record = {"command": name, "args": args, "cwd": os.getcwd()}
    if name == "asdf" and args == ["install"]:
        record["versions"] = Path(".tool-versions").read_text()
    log.write(json.dumps(record) + "\n")

if name == "chezmoi":
    if args[:1] == ["status"] and state.get("skip_chezmoi_status"):
        sys.exit(0)
    prefix = '{{ $fixture := deepCopy . }}{{ $_ := set $fixture.chezmoi "homeDir" ' + json.dumps(str(root / "home")) + ' }}{{ with $fixture }}'
    args = [prefix + arg + '{{ end }}' if arg.startswith('{{') else arg for arg in args]
    sys.exit(subprocess.call([os.environ["DOTFILES_TEST_CHEZMOI"], "--config", str(root / "config.toml"), "--persistent-state", str(root / "chezmoi.state"), *args]))
elif name == "brew":
    if state.get("brew_failure"):
        sys.exit(1)
    if args == ["list", "--formula", "--installed-on-request"]:
        print("\n".join(state["requested"]))
    elif args == ["list", "--formula"]:
        print("\n".join(state["formulae"]))
    elif args == ["list", "--cask"]:
        print("\n".join(state["casks"]))
    elif args[:2] in (["bundle", "install"], ["bundle", "check"]):
        sys.exit(state.get("bundle_failure", 0))
    elif args == ["update"]:
        pass
    elif args == ["--prefix"]:
        print(root / "brew-prefix")
    elif len(args) > 3 and args[:3] in (["uninstall", "--formula", "--"], ["uninstall", "--cask", "--"]):
        if os.environ.get("HOMEBREW_NO_AUTOREMOVE") != "1":
            raise SystemExit("Uninstall could remove packages outside the preview")
        sys.exit(state.get("uninstall_failure", 0))
    else:
        raise SystemExit("Unexpected brew operation: " + repr(args))
elif name == "asdf":
    if args == ["plugin", "list"]:
        print("python")
    elif args[:2] == ["plugin", "add"]:
        sys.exit(state.get("plugin_failure", 0))
    elif args == ["install"]:
        sys.exit(state.get("install_failure", 0))
    elif args != ["reshim"]:
        raise SystemExit("Unexpected asdf operation: " + repr(args))
elif name == "corepack" and args == ["enable"]:
    pass
else:
    raise SystemExit("Unexpected command: " + name)
'''


@unittest.skipUnless(CHEZMOI and BASH and shutil.which("jq"), "requires chezmoi, bash, and jq")
class DotfilesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dotfiles-tests-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.source = self.root / "source"
        self.source.mkdir()
        for directory in (".chezmoitemplates", ".chezmoiscripts", "profiles", "homebrew", "bin", "dot_ssh", "dot_config"):
            shutil.copytree(REPO / directory, self.source / directory)
        for name in ("dot_tool-versions", "dot_zshrc.tmpl", "dot_gitconfig.tmpl", ".chezmoiignore", "install.sh"):
            shutil.copy2(REPO / name, self.source / name)
        self.home = self.root / "home"
        self.home.mkdir()
        shutil.copyfile(self.source / "dot_tool-versions", self.home / ".tool-versions")
        self.contexts = self.home / ".config/dotfiles/work-contexts"
        self.contexts.mkdir(parents=True)
        self.outside = self.root / "unrelated-project"
        self.outside.mkdir()
        (self.outside / ".tool-versions").write_text("nodejs 0.0.1\n")
        (self.root / "config.toml").write_text("")
        (self.source / "profiles/personal.toml").write_text(
            '[identity]\ngit_name = "Fixture User"\ngit_email = "fixture@example.invalid"\n'
            '[optional_integrations]\nhomebrew_work = true\n'
        )
        self.state = {
            "requested": ["jq", "chezmoi", "terraform", "tcl-tk", "dual", "spare-cli"],
            "formulae": ["jq", "chezmoi", "terraform", "tcl-tk", "dual", "spare-cli", "dep-only"],
            "casks": ["core-app", "spare-app", "dual"],
        }
        self.save_state()
        mock_bin = self.root / "mock-bin"
        mock_bin.mkdir()
        for name in ("brew", "asdf", "corepack", "chezmoi"):
            command = mock_bin / name
            command.write_text(f"#!{sys.executable}\n" + COMMAND_DOUBLE)
            command.chmod(0o755)
        self.env = os.environ.copy()
        for name in ("DOTFILES_PROFILE", "DOTFILES_PROVIDER", "DOTFILES_MACHINE_PRESET"):
            self.env.pop(name, None)
        self.env.update(
            PATH=str(mock_bin) + os.pathsep + self.env["PATH"],
            ASDF_DATA_DIR=str(self.root / "asdf"),
            DOTFILES_TEST_ROOT=str(self.root),
            DOTFILES_TEST_CHEZMOI=CHEZMOI,
        )

    def save_state(self):
        (self.root / "state.json").write_text(json.dumps(self.state))

    def run_command(self, args, *, cwd=None, input="", check=True):
        result = subprocess.run(args, cwd=cwd or self.outside, env=self.env,
                                input=input, text=True, capture_output=True)
        if check:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def render(self, template, *, cwd=None):
        expression = (
            '{{ $fixture := deepCopy . }}'
            '{{ $_ := set $fixture.chezmoi "homeDir" ' + json.dumps(str(self.home)) + ' }}'
            '{{ $_ := set $fixture.chezmoi "os" "darwin" }}'
            '{{ includeTemplate ' + json.dumps(template) + ' $fixture }}'
        )
        return self.run_command(
            [CHEZMOI, "--config", str(self.root / "config.toml"),
             "--source", str(self.source), "execute-template", expression], cwd=cwd
        ).stdout

    def calls(self, name):
        log = self.root / "commands.jsonl"
        return [item for line in log.read_text().splitlines()
                if (item := json.loads(line))["command"] == name] if log.exists() else []

    def configure_brewfile(self):
        for group in ("core", "dev", "apps", "extras", "work"):
            (self.source / "homebrew" / f"Brewfile.{group}").write_text("")
        (self.source / "homebrew/Brewfile.core").write_text(
            'brew "jq"\nbrew "dual"\nbrew "dep-only"\ncask "core-app"\n'
        )

    def brew(self, *args, **kwargs):
        return self.run_command([BASH, str(self.source / "bin/executable_dots-brew"), *args], **kwargs)

    def test_profiles_render_identically_outside_source(self):
        for template in ("effective-config", "homebrew-config"):
            with self.subTest(template=template):
                name = f".chezmoitemplates/{template}.json.tmpl"
                inside = json.loads(self.render(name, cwd=self.source))
                outside = json.loads(self.render(name))
                self.assertEqual(inside, outside)
                # Machine capability presets override identity-profile flags.
                self.assertFalse(outside["optional_integrations"]["homebrew_work"])
                if template == "effective-config":
                    self.assertEqual(outside["identity"]["git_name"], "Fixture User")
        self.assertIn('name  = "Fixture User"', self.render("dot_gitconfig.tmpl"))

    def test_disabled_contexts_are_excluded_with_and_without_filter(self):
        for slug, setting in (("disabled", "enabled = false\n"),
                              ("enabled", "enabled = true\n"), ("implicit", "")):
            (self.contexts / f"{slug}.toml").write_text(f'[context]\nslug = "{slug}"\n{setting}')
        for requested in ([], ["disabled", "enabled", "implicit"], ["disabled"]):
            with self.subTest(requested=requested):
                (self.contexts.parent / "overrides.toml").write_text(
                    "work_contexts = " + json.dumps(requested) + "\n"
                )
                config = json.loads(self.render(".chezmoitemplates/effective-config.json.tmpl"))
                expected = [] if requested == ["disabled"] else ["enabled", "implicit"]
                self.assertEqual(config["selected_work_contexts"], expected)

    def test_cleanup_dry_run_uses_typed_audit_candidates(self):
        self.configure_brewfile()
        audit = json.loads(self.brew("audit", "--json").stdout)
        self.assertEqual(audit["missing"], [])
        self.assertEqual(audit["intentional_untracked"], ["chezmoi", "tcl-tk", "terraform"])
        self.assertEqual(audit["untracked_formulae"], ["spare-cli"])
        self.assertEqual(audit["untracked_casks"], ["dual", "spare-app"])
        result = self.brew("cleanup", "--dry-run", input="y\n")
        self.assertIn("formula: spare-cli", result.stdout)
        self.assertIn("cask: dual", result.stdout)
        self.assertTrue(all(call["args"][0] == "list" for call in self.calls("brew")))

    def test_cleanup_confirmation_and_force_remove_only_candidates(self):
        self.configure_brewfile()
        for options, reply in (([], "y\n"), (["--force"], "")):
            with self.subTest(options=options):
                (self.root / "commands.jsonl").write_text("")
                self.brew("cleanup", *options, input=reply)
                removals = [call["args"] for call in self.calls("brew") if call["args"][0] != "list"]
                self.assertEqual(removals, [["uninstall", "--cask", "--", "dual", "spare-app"],
                                            ["uninstall", "--formula", "--", "spare-cli"]])

    def test_cleanup_decline_and_eof_do_not_remove_packages(self):
        self.configure_brewfile()
        for reply in ("n\n", ""):
            self.assertIn("Cancelled", self.brew("cleanup", input=reply).stdout)
        self.assertTrue(all(call["args"][0] == "list" for call in self.calls("brew")))

    def test_cleanup_with_only_protected_packages_is_noop(self):
        self.configure_brewfile()
        self.state["requested"].remove("spare-cli")
        self.state["formulae"].remove("spare-cli")
        self.state["casks"] = ["core-app"]
        self.save_state()
        self.assertIn("No packages would be removed", self.brew("cleanup", "--force").stdout)
        self.assertTrue(all(call["args"][0] == "list" for call in self.calls("brew")))

    def test_cleanup_stops_when_audit_fails(self):
        self.state["brew_failure"] = True
        self.save_state()
        self.assertNotEqual(self.brew("cleanup", "--force", check=False).returncode, 0)
        self.assertTrue(all(call["args"][0] == "list" for call in self.calls("brew")))

    def test_cleanup_preserves_uninstall_failure(self):
        self.configure_brewfile()
        self.state["uninstall_failure"] = 7
        self.save_state()
        self.assertEqual(self.brew("cleanup", "--force", check=False).returncode, 7)

    def test_apply_installs_new_runtime_versions_after_deploying_file(self):
        source = self.root / "apply-source"
        scripts = source / ".chezmoiscripts"
        scripts.mkdir(parents=True)
        desired = (self.source / "dot_tool-versions").read_text()
        (source / "dot_tool-versions").write_text(desired)
        (self.home / ".tool-versions").write_text("nodejs lts\n")
        (scripts / Path(ASDF_HOOK).name[:-5]).write_text(self.render(ASDF_HOOK))
        self.run_command([
            CHEZMOI, "--config", str(self.root / "config.toml"),
            "--persistent-state", str(self.root / "apply.state"),
            "--source", str(source), "--destination", str(self.home),
            "apply", "--force",
        ])
        installs = [call for call in self.calls("asdf") if call["args"] == ["install"]]
        self.assertEqual(len(installs), 1)
        self.assertEqual(installs[0]["versions"], desired)

    def test_asdf_binary_installs_home_versions_and_skips_existing_plugins(self):
        result = self.run_command([BASH], input=self.render(ASDF_HOOK))
        calls = self.calls("asdf")
        installs = [call for call in calls if call["args"] == ["install"]]
        self.assertEqual(len(installs), 1)
        self.assertEqual(installs[0]["cwd"], str(self.home))
        self.assertEqual(installs[0]["versions"], (self.source / "dot_tool-versions").read_text())
        adds = [call["args"][2] for call in calls if call["args"][:2] == ["plugin", "add"]]
        self.assertEqual(adds, ["nodejs", "golang", "terraform", "kubectl", "helm"])
        self.assertEqual(calls[-1]["args"], ["reshim"])
        self.assertIn("asdf tool versions installed", result.stdout)

    def test_version_changes_change_onchange_script(self):
        before = self.render(ASDF_HOOK)
        versions = self.source / "dot_tool-versions"
        changed = "nodejs 24.0.0\n"
        versions.write_text(changed)
        after = self.render(ASDF_HOOK)
        self.assertNotEqual(before, after)
        (self.home / ".tool-versions").write_text(changed)
        self.run_command([BASH], input=after)
        install = next(call for call in self.calls("asdf") if call["args"] == ["install"])
        self.assertEqual(install["versions"], changed)

    def test_asdf_failures_warn_without_claiming_success(self):
        for failure in ("plugin_failure", "install_failure"):
            with self.subTest(failure=failure):
                self.state.pop("plugin_failure", None)
                self.state.pop("install_failure", None)
                self.state[failure] = 1
                self.save_state()
                result = self.run_command([BASH], input=self.render(ASDF_HOOK))
                self.assertIn("failed", result.stderr)
                self.assertNotIn("asdf tool versions installed", result.stdout)

    def test_asdf_can_be_disabled(self):
        (self.contexts.parent / "overrides.toml").write_text("[optional_integrations]\nasdf = false\n")
        result = self.run_command([BASH], input=self.render(ASDF_HOOK))
        self.assertIn("disabled", result.stdout)
        self.assertEqual(self.calls("asdf"), [])

    def test_disabled_zinit_skips_installation_and_shell_initialization(self):
        (self.contexts.parent / "overrides.toml").write_text("[optional_integrations]\nzinit = false\n")
        result = self.run_command([BASH], input=self.render(".chezmoiscripts/run_onchange_15-install-zinit.sh.tmpl"))
        self.assertIn("disabled", result.stdout)
        self.assertNotIn("source \"${ZINIT_HOME}/zinit.zsh\"", self.render("dot_zshrc.tmpl"))
        self.assertNotIn("zinit light", self.render("dot_zshrc.tmpl"))

    def test_disabled_integrations_do_not_activate_shell_or_export_keys(self):
        (self.contexts.parent / "overrides.toml").write_text(
            "[optional_integrations]\nasdf = false\nonepassword = false\n"
        )
        shell = self.render("dot_zshrc.tmpl")
        self.assertNotIn("export ASDF_DATA_DIR", shell)
        self.assertNotIn('installs/$_asdf_tool', shell)
        self.assertNotIn("export SSH_AUTH_SOCK", shell)
        self.assertNotIn("_auto_op_signin", shell)
        result = self.run_command([BASH], input=self.render(".chezmoiscripts/run_onchange_30-export-ssh-keys.sh.tmpl"))
        self.assertIn("disabled", result.stdout)

    @unittest.skipUnless(ZSH, "requires zsh")
    def test_asdf_local_binaries_follow_shims_and_existing_path(self):
        # Execute the rendered runtime block with isolated install directories.
        data = Path(self.env["ASDF_DATA_DIR"])
        go_bin = data / "installs/golang/1.2.3/bin"
        packages_bin = data / "installs/golang/1.2.3/packages/bin"
        for directory in (data / "shims", go_bin, packages_bin):
            directory.mkdir(parents=True)
        (self.home / ".tool-versions").write_text(
            "# a comment\n\ngolang 1.2.3\nnodejs missing\n"
        )
        shell = self.render("dot_zshrc.tmpl")
        block = shell[shell.index("# asdf install bin dirs"):shell.index("# UV —")]
        block = block.replace('$HOME/.tool-versions', str(self.home / ".tool-versions"))
        initial = f"{data}/shims:/usr/bin:/bin"
        script = (
            f"export PATH={json.dumps(initial)}\n"
            'path_append() { [[ ":$PATH:" != *":$1:"* ]] && export PATH="$PATH:$1"; }\n'
            + block + "\n" + block + '\nprint -r -- "$PATH"\n'
        )
        result = self.run_command([ZSH, "-f"], input=script)
        self.assertEqual(result.stdout.strip().split(":"),
                         initial.split(":") + [str(go_bin), str(packages_bin)])

    def test_brew_core_toggle_does_not_disable_other_groups(self):
        self.configure_brewfile()
        (self.contexts.parent / "overrides.toml").write_text(
            "[optional_integrations]\nhomebrew_core = false\nhomebrew_dev = true\n"
        )
        self.run_command([BASH], input=self.render(".chezmoiscripts/run_onchange_10-install-brew.sh.tmpl"))
        self.assertTrue(any(call["args"][:2] == ["bundle", "install"] for call in self.calls("brew")))

    def test_all_brew_groups_disabled_skips_package_commands(self):
        (self.contexts.parent / "overrides.toml").write_text(
            "[optional_integrations]\n" + "\n".join(
                f"homebrew_{group} = false" for group in ("core", "dev", "apps", "extras", "work")
            ) + "\n"
        )
        result = self.run_command([BASH], input=self.render(".chezmoiscripts/run_onchange_10-install-brew.sh.tmpl"))
        self.assertIn("all Homebrew groups are disabled", result.stdout)
        self.assertEqual(self.calls("brew"), [])

    def test_preset_and_identity_matrix(self):
        for preset in ("mac-dev", "mac-minimal"):
            for profile in ("personal", "work"):
                with self.subTest(preset=preset, profile=profile):
                    (self.contexts.parent / "overrides.toml").write_text(
                        f'machine_preset = "{preset}"\nprofile = "{profile}"\n'
                    )
                    config = json.loads(self.render(".chezmoitemplates/effective-config.json.tmpl"))
                    brew_config = json.loads(self.render(".chezmoitemplates/homebrew-config.json.tmpl"))
                    self.assertEqual(config["active_profile"], profile)
                    self.assertEqual(config["machine_preset"], preset)
                    self.assertEqual(config["optional_integrations"], brew_config["optional_integrations"])
                    options = config["optional_integrations"]
                    self.assertTrue(options["homebrew_core"])
                    self.assertFalse(options["homebrew_work"])
                    self.assertEqual(options["asdf"], preset == "mac-dev")
                    self.assertEqual(options["homebrew_apps"], preset == "mac-dev")
                    if preset == "mac-minimal":
                        self.assertNotIn('cask "', self.render(".chezmoitemplates/homebrew-active-brewfile.tmpl"))
                        gitconfig = self.render("dot_gitconfig.tmpl")
                        self.assertNotIn("external = difft", gitconfig)
                        self.assertNotIn("op-ssh-sign", gitconfig)

    def test_machine_local_overrides_and_environment_precedence(self):
        (self.contexts.parent / "overrides.toml").write_text(
            'machine_preset = "mac-minimal"\nprofile = "work"\nprovider = "gl"\n'
            '[optional_integrations]\nhomebrew_work = true\nzinit = false\n'
        )
        config = json.loads(self.render(".chezmoitemplates/effective-config.json.tmpl"))
        self.assertEqual(config["active_provider"], "gl")
        self.assertTrue(config["optional_integrations"]["homebrew_work"])
        self.assertFalse(config["optional_integrations"]["zinit"])
        self.env.update(DOTFILES_MACHINE_PRESET="mac-dev", DOTFILES_PROFILE="personal", DOTFILES_PROVIDER="gh")
        config = json.loads(self.render(".chezmoitemplates/effective-config.json.tmpl"))
        self.assertEqual(config["machine_preset"], "mac-dev")
        self.assertEqual(config["active_profile"], "personal")
        self.assertEqual(config["active_provider"], "gh")
        self.assertTrue(config["optional_integrations"]["asdf"])
        self.assertFalse(config["optional_integrations"]["zinit"])
        self.assertEqual(config["env_overrides"]["DOTFILES_MACHINE_PRESET"], "mac-dev")

    def test_old_overrides_default_to_dev_preset(self):
        (self.contexts.parent / "overrides.toml").write_text('profile = "personal"\n')
        config = json.loads(self.render(".chezmoitemplates/effective-config.json.tmpl"))
        self.assertEqual(config["machine_preset"], "mac-dev")
        self.assertTrue(config["optional_integrations"]["asdf"])

    def test_invalid_selection_fails_instead_of_silently_applying_defaults(self):
        for key in ("profile", "provider", "machine_preset"):
            with self.subTest(key=key):
                (self.contexts.parent / "overrides.toml").write_text(f'{key} = "invalid"\n')
                with self.assertRaises(AssertionError):
                    self.render(".chezmoitemplates/effective-config.json.tmpl")

    def test_homebrew_render_does_not_parse_private_work_contexts(self):
        (self.contexts / "broken.toml").write_text("not valid [ toml")
        self.assertIn('brew "git"', self.render(".chezmoitemplates/homebrew-active-brewfile.tmpl"))
        with self.assertRaises(AssertionError):
            self.render(".chezmoitemplates/effective-config.json.tmpl")

    def test_sync_and_plan_do_not_request_upgrades(self):
        self.brew("sync")
        result = self.brew("plan")
        self.assertIn("No missing packages", result.stdout)
        commands = [call["args"] for call in self.calls("brew")]
        self.assertEqual(len(commands), 2)
        self.assertEqual(commands[0][:3], ["bundle", "install", "--no-upgrade"])
        self.assertEqual(commands[1][:3], ["bundle", "check", "--no-upgrade"])

    def test_update_upgrades_only_the_active_brewfile(self):
        self.brew("update")
        commands = [call["args"] for call in self.calls("brew")]
        self.assertEqual(commands[0], ["update"])
        self.assertEqual(commands[1][:3], ["bundle", "install", "--upgrade"])
        self.assertEqual(len(commands), 2)

    def test_plan_does_not_claim_a_failed_check_requires_package_changes(self):
        self.state["bundle_failure"] = 1
        self.save_state()
        result = self.brew("plan")
        self.assertIn("Homebrew did not confirm", result.stdout)
        self.assertNotIn("Changes are needed", result.stdout)
        self.assertTrue(all(call["args"][:2] == ["bundle", "check"] for call in self.calls("brew")))

    def test_brew_apply_hook_installs_without_upgrade_or_update(self):
        self.run_command([BASH], input=self.render(".chezmoiscripts/run_onchange_10-install-brew.sh.tmpl"))
        commands = [call["args"] for call in self.calls("brew")]
        self.assertEqual(commands[0][:3], ["bundle", "install", "--no-upgrade"])
        self.assertNotIn(["update"], commands)
        self.assertNotIn(["upgrade"], commands)

    def test_disabled_onepassword_does_not_use_existing_key_selectors(self):
        selectors = self.home / ".ssh/signing-pubs"
        selectors.mkdir(parents=True)
        (selectors / "personal-gh.pub").write_text("fixture public key")
        (self.contexts.parent / "overrides.toml").write_text('[optional_integrations]\nonepassword = false\n')
        self.assertNotIn("signingkey =", self.render("dot_gitconfig.tmpl"))
        self.assertNotIn("IdentityFile", self.render("dot_ssh/config.tmpl"))
        self.assertIn(".config/1Password/**", self.render(".chezmoiignore"))
        (self.contexts / "fixture.toml").write_text(
            '[context]\nslug = "fixture"\n[git]\nsigning_key = "~/.ssh/signing-pubs/personal-gh.pub"\n'
        )
        work_hook = self.render(".chezmoiscripts/run_onchange_40-generate-work-gitconfigs.sh.tmpl")
        self.assertNotIn("signingkey =", work_hook)
        self.assertIn("gpgsign = false", work_hook)

    def test_health_skips_disabled_asdf_and_brew_groups(self):
        (self.contexts.parent / "overrides.toml").write_text(
            'machine_preset = "mac-minimal"\n[optional_integrations]\nhomebrew_core = false\n'
        )
        self.state["skip_chezmoi_status"] = True
        self.save_state()
        result = self.run_command([BASH, str(self.source / "bin/executable_dots-health")], check=False)
        self.assertIn("asdf is disabled; runtime and shim checks skipped", result.stdout)
        self.assertIn("all Homebrew groups are disabled; brew checks skipped", result.stdout)
        self.assertEqual(self.calls("asdf"), [])
        self.assertEqual(self.calls("brew"), [])

    def bootstrap(self, *args, check=True):
        # Source the actual bootstrap and mock only machine/network-facing commands.
        # HOME remains unchanged; helpers receive explicit fixture destinations.
        script = r'''
source "$1"
shift
OVERRIDES_DIR="$DOTFILES_TEST_ROOT/home/.config/dotfiles"
OVERRIDES_FILE="$OVERRIDES_DIR/overrides.toml"
record() { printf '%s\n' "$*" >> "$DOTFILES_TEST_ROOT/bootstrap.log"; }
ensure_curl() { :; }
install_homebrew_if_needed() { :; }
install_chezmoi() { :; }
find_local_source_candidate() { printf '%s\n' "$DOTFILES_TEST_ROOT/source"; }
chezmoi() {
  if [[ "$1" == execute-template ]]; then command chezmoi "$@"; return; fi
  [[ -f "$OVERRIDES_FILE" ]] || return 99
  record "chezmoi $*"
  case "$1" in
    source-path) [[ "${DOTFILES_TEST_EXISTING_SOURCE:-}" != 1 ]] || printf '%s\n' "$DOTFILES_TEST_ROOT/source" ;;
    init|apply) : ;;
    *) return 98 ;;
  esac
}
git() {
  record "git $*"
  [[ "$1" == -C ]] || return 98
  shift 2
  case "$1" in
    rev-parse) : ;;
    config) printf '%s\n' https://github.com/cruznick/configs.git ;;
    status) [[ "${DOTFILES_TEST_DIRTY:-}" != 1 ]] || printf '%s\n' ' M fixture' ;;
    pull) [[ "$2" == --ff-only && -f "$OVERRIDES_FILE" ]] ;;
    *) return 98 ;;
  esac
}
main "$@"
'''
        return self.run_command([BASH, "-c", script, "fixture", str(self.source / "install.sh"), *args], check=check)

    def test_bootstrap_seeds_preset_before_init_and_apply(self):
        self.bootstrap("--preset", "mac-minimal")
        overrides = (self.contexts.parent / "overrides.toml").read_text()
        self.assertIn('machine_preset = "mac-minimal"', overrides)
        commands = (self.root / "bootstrap.log").read_text().splitlines()
        self.assertTrue(any(command.startswith("chezmoi init") for command in commands))
        self.assertEqual(commands[-1], "chezmoi apply")
        config = json.loads(self.render(".chezmoitemplates/effective-config.json.tmpl"))
        self.assertFalse(config["optional_integrations"]["asdf"])

    def test_bootstrap_preserves_overrides_and_updates_source_without_implicit_apply(self):
        existing = 'machine_preset = "mac-minimal"\nprofile = "work"\n# Keep this comment.\n'
        (self.contexts.parent / "overrides.toml").write_text(existing)
        (self.source / ".git").mkdir()
        self.env["DOTFILES_TEST_EXISTING_SOURCE"] = "1"
        self.bootstrap()
        self.assertEqual((self.contexts.parent / "overrides.toml").read_text(), existing)
        commands = (self.root / "bootstrap.log").read_text().splitlines()
        self.assertTrue(any(command.endswith("pull --ff-only") for command in commands))
        self.assertEqual(commands.count("chezmoi apply"), 1)
        self.assertNotIn("chezmoi update", commands)

    def test_bootstrap_rejects_conflicting_preset_without_overwriting(self):
        existing = 'machine_preset = "mac-minimal"\n'
        (self.contexts.parent / "overrides.toml").write_text(existing)
        result = self.bootstrap("--preset", "mac-dev", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no overrides were replaced", result.stderr)
        self.assertEqual((self.contexts.parent / "overrides.toml").read_text(), existing)
        self.assertFalse((self.root / "bootstrap.log").exists())

    def test_bootstrap_rejects_invalid_preset_and_dirty_source(self):
        result = self.bootstrap("--preset", "unknown", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.contexts.parent / "overrides.toml").exists())
        (self.source / ".git").mkdir()
        self.env.update(DOTFILES_TEST_EXISTING_SOURCE="1", DOTFILES_TEST_DIRTY="1")
        result = self.bootstrap(check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Commit or stash", result.stderr)
        commands = (self.root / "bootstrap.log").read_text()
        self.assertNotIn("pull --ff-only", commands)
        self.assertNotIn("chezmoi apply", commands)

    def test_bootstrap_runs_downloaded_bash_c_and_file_entrypoints(self):
        # Keep the real execution guard; replace only main's side effects.
        script = (self.source / "install.sh").read_text()
        guard = script.rindex('\nif [[ -z "${BASH_SOURCE[0]:-}"')
        safe_script = script[:guard] + '\nmain() { printf "called:%s\\n" "$*"; }\n' + script[guard:]
        result = self.run_command(["/bin/bash", "-c", safe_script, "--", "--preset", "mac-minimal"])
        self.assertEqual(result.stdout, "called:--preset mac-minimal\n")
        fixture = self.root / "bootstrap-entrypoint.sh"
        fixture.write_text(safe_script)
        result = self.run_command(["/bin/bash", str(fixture), "--preset", "mac-dev"])
        self.assertEqual(result.stdout, "called:--preset mac-dev\n")

    def test_bootstrap_cli_preset_wins_over_environment(self):
        self.env["DOTFILES_MACHINE_PRESET"] = "mac-dev"
        self.bootstrap("--preset=mac-minimal")
        self.assertIn('machine_preset = "mac-minimal"', (self.contexts.parent / "overrides.toml").read_text())

    @unittest.skipUnless(ZSH, "requires zsh")
    def test_scripts_and_rendered_templates_have_valid_syntax(self):
        for script in [self.source / "install.sh", *self.source.glob("bin/executable_*")]:
            if script.suffix != ".tmpl":
                with self.subTest(script=script.name):
                    self.run_command([BASH, "-n", str(script)])
        templates = [*self.source.glob(".chezmoiscripts/*.tmpl"), *self.source.glob("bin/*.tmpl")]
        for preset in ("mac-dev", "mac-minimal"):
            self.env["DOTFILES_MACHINE_PRESET"] = preset
            for template in templates:
                with self.subTest(template=template.name, preset=preset):
                    self.run_command([BASH, "-n"], input=self.render(str(template.relative_to(self.source))))
            self.run_command([ZSH, "-n"], input=self.render("dot_zshrc.tmpl"))


if __name__ == "__main__":
    unittest.main()
