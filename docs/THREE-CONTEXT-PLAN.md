# Personal, freelance, and Kavak configuration

1. Remove the machine-wide GitHub restriction. Machine profiles select software
   defaults; directory contexts select Git identities and providers.
2. Add personal credential reuse to work contexts. Freelance supports GitHub
   and GitLab; Kavak keeps dedicated credentials and GitLab only.
3. Generate path-scoped URL rewrites for both providers, avoiding competing
   global rewrites. Route CLI authentication independently of the default host.
4. Test actual Git URL resolution (including clone destinations), SSH selection,
   signing, CLI routing, and Kavak validation in an isolated home.
5. Render and apply only the relevant live Git/SSH/CLI configuration, preserving
   other local settings. Verify Kavak access after application.

GitLab migration is separate: creating a remote requires its destination
namespace. A mirror copies committed history, not uncommitted changes.

Implemented and applied on 2026-11-09. The 43-test regression suite and the
additional SSH/linked-worktree test passed. Live personal GitHub and Kavak
GitLab repository reads succeeded; the Kavak GitHub CLI route rejects calls.

Remaining account setup: GitLab rejects the personal public key offered by
1Password, so register/enable that key in the personal GitLab account. Personal
GitHub CLI, personal GitLab CLI, and Kavak GitLab CLI have no saved login in
their selected config directories. These API logins are separate from SSH.
