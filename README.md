# dotfiles (chezmoi)

Personal dotfiles managed with [chezmoi](https://www.chezmoi.io/).
Source repo: `github.com/mickmcq/dotfiles` → applied to `$HOME`.

## What's here

| Source file | Target | Notes |
| --- | --- | --- |
| `private_dot_bashrc` | `~/.bashrc` | `private_` = mode 600 on apply |
| `dot_bash_profile` | `~/.bash_profile` | sources `~/.api_keys` |
| `encrypted_private_dot_api_keys.age` | `~/.api_keys` | age-encrypted secrets |
| `dot_config/nvim-private/encrypted_private_personal.lua.age` | `~/.config/nvim-private/personal.lua` | age-encrypted, machine-local nvim settings |
| `dot_config/private_kitty/` | `~/.config/kitty/` | kitty terminal config, dir mode 700; runtime state/backups excluded via `.chezmoiignore` |
| `dot_homebrew/Brewfile` | `~/.homebrew/Brewfile` | Homebrew manifest (taps/brews/casks); install with `brew bundle --global` |
| `.chezmoiexternal.toml` | — | recipe: clone `mickmcq/kickstart.nvim` into `~/.config/nvim` |

Neovim config is **not stored here**; it's pulled in as an *external* (its own
repo, `mickmcq/kickstart.nvim`). See that repo's README for its editing workflow.

Encryption uses **age**. The private key lives at `~/.config/chezmoi/key.txt`
(never committed). Config is in `~/.config/chezmoi/chezmoi.toml`.

## Bootstrapping a new machine

> ⚠️ **Order matters: restore the age key _before_ `chezmoi apply`.** Without it,
> chezmoi cannot decrypt `.api_keys` / `personal.lua` and apply fails.

### 0. Prerequisites

```bash
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

This clones this repo, applies the bash files, **decrypts** `.api_keys` and
`personal.lua` using `key.txt`, and **clones** the nvim external into
`~/.config/nvim`. It also lays down `~/.homebrew/Brewfile`.

### 3. Install all packages

`chezmoi apply` (step 2) put the Brewfile in place; now install everything from it:

```bash
brew bundle --global          # installs all taps, brews, casks (incl. powerline-go)
```

### 4. Verify

```bash
chezmoi verify && echo "state matches"
test -f ~/.api_keys && test -d ~/.config/nvim && echo "files in place"
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
chezmoi edit ~/.api_keys
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
