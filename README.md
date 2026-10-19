# rstl.repo

Umbrella repository for the [rstl.sway](https://github.com/arozoid/rstl.sway/) rice —
custom package repositories for both Arch Linux (`pacman`) and Fedora (`dnf`).

## repository layout

| Endpoint | Format | Path |
|----------|--------|------|
| **Arch (backward compat)** | PKGBUILD | `pkgbuilds/<pkg>/PKGBUILD` |
| **Arch (future primary)** | PKGBUILD | `arch/pkgbuilds/<pkg>/PKGBUILD` |
| **Fedora** | PKGBUILD + .spec | `fedora/pkgs/<pkg>/PKGBUILD` + `fedora/specs/<pkg>/<pkg>.spec` |

The root of this repository remains the Arch Linux `pacman` repository for backwards
compatibility. The `arch/` directory is a parallel Arch repository that will become
the primary Arch endpoint in the future. The `fedora/` directory is a new Fedora
`dnf` repository with both PKGBUILDs (reference/build metadata) and `.spec` files
(RPM specs) for every package.


## packages

- `rstlpk`: Minimal polkit authentication agent (no gtk)
- `dssd`: Dead simple freedesktop SecretService implementation
- `xdg-desktop-portal-termfilechooser`: Terminal file chooser portal backend
- `yambar`: Modular status panel (built without -Werror)
- `ttf-jetbrains-mono-nerd-min`: JetBrains Mono Nerd Font — regular weight only (replaces `ttf-jetbrains-mono-nerd`)
- `papirus-icon-theme-dark-only`: Papirus-Dark icon theme only (replaces `papirus-icon-theme`)
- `adwaita-icon-theme-dark`: GNOME standard Adwaita icons (dark-capable) without the `adwaita-cursors` dependency
- `xcursor-pro-dark`: Modern Professional Dark cursor theme only (replaces `xcursor-pro-cursor-theme`)
- `notwaita-cursors-grey`: Grey Notwaita cursor theme — Adwaita-inspired, HiDPI (grey only)
- `python-clickgen`: X11 & Windows cursor building API (build dep of `xcursor-pro-dark`)
- `python-yewtube-search-python`: Search for YouTube videos/channels/playlists without the Data API (runtime dep of `yewtube`)

- `bluetuith`: TUI-based bluetooth connection manager
- `clipse`: Configurable TUI clipboard manager for Unix
- `latuicon`: TUI icon picker (emojis / kaomojis / unicode / nerd fonts)
- `rstl-pick`: Compact fuzzy search TUI picker for terminal apps (nmtui / wiremix / clipse / bluetuith / latuicon)
- `xeo`: The `.xeo` scripting language interpreter (edition 2024)
- `xeon`: The 'modern' package manager for `.xeo` packages
- `calawk`: Small interactive expression calculator wrapper around awk
- `oxicord`: Vim-native Discord TUI client
- `concord`: Feature-rich TUI client for Discord (built from source; voice calls & screen share included)
- `rovr`: Post-modern terminal file explorer (Nuitka binary)
- `yewtube`: Terminal-based YouTube player and downloader
- `myx`: Lean, beautiful terminal Spotify player
- `chroncal`: Terminal-first calendar, todo and journal manager
- `fzf-tab`: Replace zsh's default completion selection menu with fzf
- `zsh-auto-notify`: Automatic notification when a long-running command finishes
- `vectorcraft`: Vector illustration; an open-source, clean-room reimplementation of Adobe Illustrator, rebuilt in pure Rust
- `filmcraft`: Video editing, color and sound; an open-source, clean-room reimplementation of Adobe Premiere Pro, rebuilt in pure Rust
- `photocraft`: Image editing; an open-source, clean-room reimplementation of Adobe Photoshop, rebuilt in pure Rust
- `pdfcraft`: The PDF workbench; an open-source, clean-room reimplementation of Adobe Acrobat, rebuilt in pure Rust
- `lightcraft`: Photo library and raw development; an open-source, clean-room reimplementation of Adobe Lightroom, rebuilt in pure Rust
- `designcraft`: Page layout and publishing; an open-source, clean-room reimplementation of Adobe InDesign, rebuilt in pure Rust
- `effectcraft`: Motion graphics and visual effects; an open-source, clean-room reimplementation of Adobe After Effects, rebuilt in pure Rust
- `wordcraft`: Writing and document design; an open-source, clean-room reimplementation of Microsoft Word, rebuilt in pure Rust
- `gridcraft`: Spreadsheets and data; an open-source, clean-room reimplementation of Microsoft Excel, rebuilt in pure Rust
- `deckcraft`: Presentations and slide shows; an open-source, clean-room reimplementation of Microsoft PowerPoint, rebuilt in pure Rust
- `figcraft`: Interface design; an open-source, clean-room reimplementation of Figma, rebuilt in pure Rust
- `soundcraft`: Recording, editing and mixing audio; an open-source, clean-room reimplementation of Avid Pro Tools, rebuilt in pure Rust
- `cadcraft`: Computer-aided design and drafting; an open-source, clean-room reimplementation of Autodesk AutoCAD, rebuilt in pure Rust

Packages auto-track their upstream: repos with releases use the latest release tag as the version (e.g. `3.5.1`); repos without releases use `YYYYMMDD`. `resolve.sh` + `inject.sh` patch the PKGBUILD at build time, so a scheduled build picks up new upstream versions automatically — no manual bumps needed. A few packages are pinned instead (no `# auto:` marker) because an auto-track version cannot resolve correctly, e.g. `calawk` and `python-yewtube-search-python`.

## usage — Arch (pacman)

add to `/etc/pacman.conf`:

```
[rstl-repo]
Server = https://arozoid.github.io/rstl.repo
```

then:

```bash
sudo pacman -Syu
```

## usage — Fedora (dnf)

Build RPMs from the spec files:

```bash
cd fedora
./build.sh
```

Or build a specific package:

```bash
./build.sh vectorcraft
```

Requires `rpmbuild` (from `rpm-build` package).

## adding a new package

1. create a directory in `pkgbuilds/<pkgname>/` (Arch root) and `arch/pkgbuilds/<pkgname>/` (Arch future)
2. create `fedora/pkgs/<pkgname>/PKGBUILD` and `fedora/specs/<pkgname>/<pkgname>.spec` (Fedora)
3. add an `# auto:` marker to the PKGBUILDs:
   - `# auto: release` — package version = upstream's latest release tag (leading `v` stripped)
   - `# auto: date` — package version = `YYYYMMDD`
4. push to `main` — the workflow will build it automatically

## building locally — Arch

```bash
chmod +x build.sh
./build.sh
```

## building locally — Fedora

```bash
chmod +x fedora/build.sh
./build.sh
```

---

the main goal of this was mostly to experiment with pacman repos, and also make rstl.sway installation easier and faster
