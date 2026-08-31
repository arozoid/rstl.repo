# rstl.repo

custom pacman repository for the [rstl.sway](https://github.com/arozoid/rstl.sway/) rice

## packages

- `rstlpk`: Minimal polkit authentication agent (no gtk)
- `dssd`: Dead simple freedesktop SecretService implementation
- `xdg-desktop-portal-termfilechooser`: Terminal file chooser portal backend
- `yambar`: Modular status panel (built without -Werror)
- `ttf-jetbrains-mono-nerd-min`: JetBrains Mono Nerd Font — regular weight only (replaces `ttf-jetbrains-mono-nerd`)
- `papirus-icon-theme-dark-only`: Papirus-Dark icon theme only (replaces `papirus-icon-theme`)
- `googledot-black`: GoogleDot-Black cursor theme only (replaces `googledot-cursor-theme`)
- `python-clickgen`: X11 & Windows cursor building API (build dep of `googledot-black`)
- `fsh`: Interactive terminal script suite, installed at `/opt/fsh` with `fsh -> /opt/fsh/run.sh` symlink in `/usr/local/bin`
- `xeo`: The `.xeo` scripting language interpreter (edition 2024)
- `xeon`: The 'modern' package manager for `.xeo` packages
- `calawk`: Small interactive expression calculator wrapper around awk
- `oxicord`: Vim-native Discord TUI client

Packages auto-track their upstream: repos with releases use the latest release tag as the version (e.g. `3.5.1`); repos without releases use `YYYYMMDD`. `resolve.sh` + `inject.sh` patch the PKGBUILD at build time, so a scheduled build picks up new upstream versions automatically — no manual bumps needed.

## usage

add to `/etc/pacman.conf`:

```
[rstl-repo]
Server = https://arozoid.github.io/rstl.repo
```

then:

```bash
sudo pacman -Syu
```

## adding a new package

1. create a directory in `pkgbuilds/<pkgname>/`
2. add a `PKGBUILD` file
3. add an `# auto:` marker to tell the build how to version it:
   - `# auto: release` — package version = upstream's latest release tag (leading `v` stripped)
   - `# auto: date` — package version = `YYYYMMDD`; add `_commit=""` and set
     `source=(... ::$url/archive/$_commit.tar.gz)` with `build/package` cd'ing into
     `$srcdir/$pkgname-$_commit`
4. push to `main` — the workflow will build it automatically

## building locally

```bash
chmod +x build.sh
./build.sh
```

---

the main goal of this was mostly to experiment with pacman repos, and also make rstl.sway installation easier and faster
