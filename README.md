# dotfiles (chezmoi)

Personal dotfiles managed with [chezmoi](https://www.chezmoi.io/).
Source repo: `github.com/mickmcq/dotfiles` → applied to `$HOME`.

## What's here

| Source file | Target | Notes |
| --- | --- | --- |
| `private_dot_bashrc` | `~/.bashrc` | `private_` = mode 600 on apply |
| `dot_bash_profile` | `~/.bash_profile` | sources `~/.profile` and `~/.secrets` |
| `private_dot_profile` | `~/.profile` | sets `LANG=en_US.UTF-8` when that locale exists |
| `encrypted_private_dot_secrets.age` | `~/.secrets` | age-encrypted secrets and personal identifiers — the single source of truth (renamed from `.api_keys` 2026-08-02; not everything in it is an API key) |
| `private_dot_dircolors/private_LS_COLORS` | `~/.dircolors/LS_COLORS` | [trapd00r/LS_COLORS](https://github.com/trapd00r/LS_COLORS) palette, dir mode 700; loaded by `~/.bashrc` via GNU `dircolors` (needs `coreutils`) |
| `dot_config/nvim-private/encrypted_private_personal.lua.age` | `~/.config/nvim-private/personal.lua` | age-encrypted, machine-local nvim settings |
| `dot_config/private_kitty/` | `~/.config/kitty/` | kitty terminal config, dir mode 700; runtime state/backups excluded via `.chezmoiignore` |
| `dot_homebrew/Brewfile` | `~/.homebrew/Brewfile` | Homebrew manifest (taps/brews/casks); install with `brew bundle --global` |
| `private_dot_gitconfig` | `~/.gitconfig` | git config (user, filters, gh credential helper) |
| `dot_config/git/ignore` | `~/.config/git/ignore` | global git ignore (`.claude/settings.local.json`) |
| `private_dot_gitignore_global` | `~/.gitignore_global` | legacy global ignore (`.DS_Store`, `*~`) referenced by `core.excludesfile` |
| `private_dot_inputrc` | `~/.inputrc` | readline vi mode and `vi-command` binds |
| `private_dot_blerc` | `~/.blerc` | [ble.sh](https://github.com/akinomyoga/ble.sh) binds; ble.sh itself is installed separately (see step 3) |
| `private_dot_editrc` | `~/.editrc` | libedit vi mode |
| `private_dot_Rprofile` | `~/.Rprofile` | R startup: **loads `~/.secrets`** (see below), quit-without-saving, history hook |
| `private_dot_Renviron` | `~/.Renviron` | non-secret R startup vars only; `R_LIBS_USER` must live here because R reads it before `.Rprofile` runs |
| `encrypted_private_dot_gcalclirc.age` | `~/.gcalclirc` | age-encrypted; Google OAuth client id + secret |
| `dot_config/todoist/encrypted_private_config.json.age` | `~/.config/todoist/config.json` | age-encrypted; Todoist API token |
| `private_dot_dictdrc` | `~/.dictdrc` | dictd client; hardcodes `/Users/mm223266` paths |
| `dot_hammerspoon/private_init.lua` | `~/.hammerspoon/init.lua` | Hammerspoon config |
| `private_dot_ssh/private_config` | `~/.ssh/config` | agent/keychain settings only — key material is excluded via `.chezmoiignore` |
| `dot_config/mpv/` | `~/.config/mpv/` | `mpv.conf` + `input.conf` (rubberband pitch binds) |
| `dot_config/private_cmus/private_rc` | `~/.config/cmus/rc` | cmus settings; cache/history/playlists excluded via `.chezmoiignore` |
| `dot_config/yazi/` | `~/.config/yazi/` | `yazi.toml` + `package.toml`; plugins are git clones, restored with `ya pkg install` |
| `.chezmoiexternal.toml` | — | recipe: clone `mickmcq/kickstart.nvim` into `~/.config/nvim` |

> **Not managed:** `~/.git-credentials` holds plaintext tokens (`credential.helper = store`)
> and is excluded via `.chezmoiignore` — never commit it. Same for `~/.ssh/id_*`.
> `~/.config/gh/hosts.yml` is also left alone: `gh auth login` regenerates it (step 0).

## Secrets

`~/.secrets` is the **single source of truth** for every credential and personal
identifier. It is age-encrypted in this repo and reaches programs two ways:

- **Shells** — `~/.bash_profile` sources it, so exports land in every login shell.
- **R** — `~/.Rprofile` parses it and calls `Sys.setenv()`. This is deliberate and
  not redundant: RStudio.app and R.app are GUI apps, so they launch *without* the
  login shell's environment. Anything already set in the environment wins, so a
  shell export still overrides the file.

Two files are encrypted separately rather than folded into `~/.secrets`, because
each program insists on reading its own config file: `~/.gcalclirc` and
`~/.config/todoist/config.json`.

> **History:** until 2026-08-02 the R keys were a second, hand-maintained copy
> inside `~/.Renviron`. The copies had drifted — a different `ANTHROPIC_API_KEY`
> and two extra HuggingFace tokens under the spellings `HF_Token` and
> `HF_NEW_TOKEN`. If some R script still references those two names, update it to
> `HF_TOKEN`; the old tokens were live at the time of the merge and are worth
> revoking at huggingface.co/settings/tokens.

Neovim config is **not stored here**; it's pulled in as an *external* (its own
repo, `mickmcq/kickstart.nvim`). See that repo's README for its editing workflow.

Encryption uses **age**. The private key lives at `~/.config/chezmoi/key.txt`
(never committed). Config is in `~/.config/chezmoi/chezmoi.toml`.

## Bootstrapping a new machine

> ⚠️ **Order matters: restore the age key _before_ `chezmoi apply`.** Without it,
> chezmoi cannot decrypt `.secrets` / `personal.lua` and apply fails.

### 0. Prerequisites

The following process assumes that `bash` is your shell. If you use this on a new macOS machine, you may find that `zsh` is your shell. I installed `bash` from brew in a later step, detailed below. The changes to your configuration won't take effect until after that step.

The first command below comes from [https://brew.sh](https://brew.sh), and may change over time. It may be better to view that URL to copy the latest command. Then run the second and third commands.

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install chezmoi age gh
gh auth login          # enables HTTPS git pulls (no SSH key needed)
```

### 1. Restore the age private key  🔑

The key is backed up two ways (see **Key backup** below). Preferred — the
passphrase-encrypted blob synced via iCloud Drive:

```bash
age -d "$HOME/Library/Mobile Documents/com~apple~CloudDocs/chezmoi-age-key.age" \
  > ~/.config/chezmoi/key.txt          # prompts for your passphrase
chmod 600 ~/.config/chezmoi/key.txt
```

(Same-Mac alternative — restore from the local Keychain copy:)

```bash
security find-generic-password -s chezmoi-age-key -w | xxd -r -p \
  > ~/.config/chezmoi/key.txt
chmod 600 ~/.config/chezmoi/key.txt
```

### 2. Initialize and apply

```bash
chezmoi init --apply mickmcq
```

This clones this repo, applies the bash files, **decrypts** `.secrets` and
`personal.lua` using `key.txt`, and **clones** the nvim external into
`~/.config/nvim`. It also lays down `~/.homebrew/Brewfile`.

### 3. Install all packages

`chezmoi apply` (step 2) put the Brewfile in place; now install everything from it:

```bash
brew bundle --global          # installs all taps, brews, casks (incl. powerline-go)
```

The most important package is `bash`. After installing it, you need to say

```bash
chsh -s /opt/homebrew/bin/bash
```

Even this may not be enough. I have sometimes had to also manually add `/opt/homebrew/bin/bash` to `/etc/shells`. On the other hand, in one case it was automatically added without my knowing intervention.

One package that is not added in the above process is `ble.sh`. That package must be installed separately, using the instructions at [https://github.com/akinomyoga/ble.sh](https://github.com/akinomyoga/ble.sh).

Yazi's plugins are also not covered by `brew bundle` — they're git clones listed
in the managed `~/.config/yazi/package.toml`. Restore them with:

```bash
ya pkg install
```

### 4. Verify

```bash
chezmoi verify && echo "state matches"
test -f ~/.secrets && test -d ~/.config/nvim && echo "files in place"
```

## Daily workflow

Edit a normal managed file (bash configs, etc.):

```bash
chezmoi edit ~/.bashrc          # edits the source
chezmoi apply                   # writes changes to $HOME
chezmoi cd && git add -A && git commit -m "..." && git push && exit
```

Edit an encrypted file (decrypts, re-encrypts on save):

```bash
chezmoi edit ~/.secrets
chezmoi edit ~/.config/nvim-private/personal.lua
chezmoi cd && git add -A && git commit -m "..." && git push && exit
```

Edit the **neovim config itself** (`init.lua`, plugins, colors …): that's the
*external* repo — edit those files directly and commit to `mickmcq/kickstart.nvim`,
**not** via chezmoi. (`chezmoi edit ~/.config/nvim/init.lua` → "not managed".)

## Key backup

`~/.config/chezmoi/key.txt` is the only thing that can decrypt anything here.
Two backups exist:

1. **Local macOS Keychain** — service `chezmoi-age-key` (this Mac only).
2. **Passphrase-encrypted blob in iCloud Drive** — the off-machine backup;
   restore with `age -d` (see Step 1). The passphrase is memorized, stored nowhere.

If `key.txt` **and** both backups are lost, the encrypted files are
unrecoverable. Keep the passphrase safe.
