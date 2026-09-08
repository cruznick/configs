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
ASDF_HOOK = ".chezmoiscripts/run_onchange_20-setup-asdf.sh.tmpl"


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
        for directory in (".chezmoitemplates", ".chezmoiscripts", "profiles", "homebrew", "bin"):
            shutil.copytree(REPO / directory, self.source / directory)
        for name in ("dot_tool-versions", "dot_zshrc.tmpl", "dot_gitconfig.tmpl", ".chezmoiignore"):
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
        for name in ("DOTFILES_PROFILE", "DOTFILES_PROVIDER"):
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
                self.assertTrue(outside["optional_integrations"]["homebrew_work"])
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


if __name__ == "__main__":
    unittest.main()
