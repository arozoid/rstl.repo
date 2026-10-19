# rstl.repo — Fedora Repository

Fedora RPM repository for the [rstl.sway](https://github.com/arozoid/rstl.sway/) rice,
built alongside the Arch Linux `pacman` repository.

## Repository layout

```
fedora/
├── pkgs/<pkgname>/PKGBUILD   # Arch-style PKGBUILD (reference/build metadata)
├── specs/<pkgname>/<pkgname>.spec   # Fedora RPM spec file
├── build.sh                  # Build RPMs from spec files
└── README.md                 # This file
```

## packages

- `adwaita-icon-theme-dark`: GNOME standard icons (dark-capable Adwaita), bundled without the `adwaita-cursors` dependency
- `bluetuith`: TUI-based bluetooth connection manager
- `cadcraft`: Computer-aided design and drafting; an open-source, clean-room reimplementation of Autodesk AutoCAD, rebuilt in pure Rust
- `calawk`: Small interactive (and non-interactive) expression calculator wrapper around awk
- `chroncal`: Terminal-first calendar, todo and journal manager
- `clipse`: Configurable TUI clipboard manager for Unix
- `concord`: Feature-rich TUI client for Discord (built from source; voice calls & screen share included)
- `deckcraft`: Presentations and slide shows; an open-source, clean-room reimplementation of Microsoft PowerPoint, rebuilt in pure Rust
- `designcraft`: Page layout and publishing; an open-source, clean-room reimplementation of Adobe InDesign, rebuilt in pure Rust
- `dssd`: Dead simple freedesktop SecretService implementation
- `effectcraft`: Motion graphics and visual effects; an open-source, clean-room reimplementation of Adobe After Effects, rebuilt in pure Rust
- `figcraft`: Interface design; an open-source, clean-room reimplementation of Figma, rebuilt in pure Rust
- `filmcraft`: Video editing, color and sound; an open-source, clean-room reimplementation of Adobe Premiere Pro, rebuilt in pure Rust
- `fzf-tab`: Replace zsh's default completion selection menu with fzf
- `googledot-black`: Cursor theme inspired on Google — GoogleDot-Black only
- `gridcraft`: Spreadsheets and data; an open-source, clean-room reimplementation of Microsoft Excel, rebuilt in pure Rust
- `latuicon`: TUI icon picker (emojis / kaomojis / unicode / nerd fonts)
- `lightcraft`: Photo library and raw development; an open-source, clean-room reimplementation of Adobe Lightroom, rebuilt in pure Rust
- `myx`: Lean, beautiful terminal Spotify player
- `notwaita-cursors-grey`: Grey Notwaita cursor theme — Adwaita-inspired, HiDPI (grey only, trimmed to 24/32/48px)
- `oxicord`: Vim-native Discord TUI for terminal enthusiasts
- `papirus-icon-theme-dark-only`: Papirus icon theme — Papirus-Dark only
- `pdfcraft`: The PDF workbench; an open-source, clean-room reimplementation of Adobe Acrobat, rebuilt in pure Rust
- `photocraft`: Image editing; an open-source, clean-room reimplementation of Adobe Photoshop, rebuilt in pure Rust
- `python-clickgen`: X11 & Windows cursor building API
- `python-yewtube-search-python`: Search for YouTube videos, channels and playlists without the Data API (yewtube's fork)
- `rovr`: A post-modern terminal file explorer
- `rstl-pick`: Compact fuzzy-search TUI app picker for the rstl.sway desktop
- `rstlpk`: Minimal polkit authentication agent for the rstl.sway rice (no gtk)
- `soundcraft`: Recording, editing and mixing audio; an open-source, clean-room reimplementation of Avid Pro Tools, rebuilt in pure Rust
- `ttf-jetbrains-mono-nerd-min`: JetBrains Mono Nerd Font — minimal (regular weight only)
- `vectorcraft`: Vector illustration; an open-source, clean-room reimplementation of Adobe Illustrator, rebuilt in pure Rust
- `wordcraft`: Writing and document design; an open-source, clean-room reimplementation of Microsoft Word, rebuilt in pure Rust
- `xcursor-pro-dark`: Modern X11 Cursor Theme — dark only (trimmed from xcursor-pro-cursor-theme)
- `xdg-desktop-portal-termfilechooser`: xdg-desktop-portal backend for your favorite terminal file chooser
- `xeo`: The `.xeo` scripting language interpreter (edition 2024)
- `xeon`: The 'modern' package manager for `.xeo` packages
- `yambar`: Modular status panel for X11 and Wayland, inspired by polybar
- `yewtube`: Terminal-based YouTube player and downloader
- `zsh-auto-notify`: zsh plugin that automatically posts a notification when a long-running command finishes

## building

Each package has both a `PKGBUILD` (Arch reference) and a `.spec` file (Fedora RPM).
Build RPMs with:

```bash
cd fedora
./build.sh
```

Or build a specific package:

```bash
./build.sh vectorcraft
```

Requires `rpmbuild` (from `rpm-build` package) and source files accessible at the
URLs referenced in each spec file.

## umbrella repository

This repository is an umbrella for both package formats:

| Endpoint | Format | Path |
|----------|--------|------|
| Arch (backward compat) | PKGBUILD | `pkgbuilds/<pkg>/PKGBUILD` |
| Arch (future primary) | PKGBUILD | `arch/pkgbuilds/<pkg>/PKGBUILD` |
| Fedora | PKGBUILD + .spec | `fedora/pkgs/<pkg>/PKGBUILD` + `fedora/specs/<pkg>/<pkg>.spec` |
