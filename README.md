# rstl.repo

an umbrella repository for [rstl.sway](https://github.com/arozoid/rstl.sway/), providing custom packages for arch linux (`pacman`), fedora (`dnf`) and void linux (`xbps`).

## repository layout

| endpoint | format | path |
|---|---|---|
| **arch (backwards compatibility)** | PKGBUILD | `pkgbuilds/<pkg>/PKGBUILD` |
| **arch (future primary)** | PKGBUILD | `arch/pkgbuilds/<pkg>/PKGBUILD` |
| **fedora** | PKGBUILD + .spec | `fedora/pkgs/<pkg>/PKGBUILD` + `fedora/specs/<pkg>/<pkg>.spec` |
| **void linux** | XBPS package | `void/` (converted from built arch packages) |

the root `pkgbuilds/` directory is still used for arch packages to keep existing workflows working. `arch/pkgbuilds/` currently mirrors it, with the intention of moving the primary arch package sources under `arch/` in the future.

the published `pacman` repository is served from `/arch/`, while the site root remains available as an alias for the old repository URL.

fedora packages have their own directory, containing both PKGBUILDs and RPM spec files. the PKGBUILDs hold the reference build metadata, while the `.spec` files are used to build the actual RPMs.

void works a little differently: rather than maintaining a separate package definition for every program, CI converts the finished arch packages into `.xbps` packages and indexes them using `xbps-rindex`. this happens alongside the RPM builds.

## release snapshots and github pages

CI builds the packages every sunday at 12:00 UTC, as well as whenever changes are pushed or a manual workflow dispatch is triggered.

each successful build is published as a GitHub release tagged `repo-YYYYMMDD-HHMMSS`. releases contain a complete snapshot of the packages built during that run, including every arch `.pkg.tar.*`, fedora `.rpm` and void `.xbps` package.

the Pages repository is rebuilt using the newest three releases. CI downloads the current and previous snapshots, merges their packages, regenerates the `pacman`, `dnf` and `xbps` metadata, and deploys the resulting site.

older releases are only pruned after a successful deployment, so a failed build or deployment won't leave the published repository without its previous packages. keeping three snapshots also means that up to three versions of each program remain available for rollback.

the number of releases to retain can be changed through `RELEASES_TO_KEEP` at the top of [`.github/workflows/build.yml`](.github/workflows/build.yml).

## packages

| package | description |
|---|---|
| `rstlpk` | minimal polkit authentication agent without gtk |
| `dssd` | dead simple freedesktop secretservice implementation |
| `xdg-desktop-portal-termfilechooser` | terminal file chooser portal backend |
| `yambar` | modular status panel, built without `-Werror` |
| `awww` | animated wallpaper daemon for wayland, with runtime controls |
| `ttf-jetbrains-mono-nerd-min` | jetbrains mono nerd font, regular weight only; replaces `ttf-jetbrains-mono-nerd` |
| `papirus-icon-theme-dark-only` | papirus dark icon theme without the other variants; replaces `papirus-icon-theme` |
| `adwaita-icon-theme-dark` | gnome's standard adwaita icons, with dark-theme support and without the `adwaita-cursors` dependency |
| `xcursor-pro-dark` | modern professional dark cursor theme; replaces `xcursor-pro-cursor-theme` |
| `notwaita-cursors-grey` | grey notwaita cursor theme, inspired by adwaita and designed for hidpi displays |
| `python-clickgen` | x11 and windows cursor building api; build dependency of `xcursor-pro-dark` |
| `python-yewtube-search-python` | searches youtube videos, channels and playlists without using the data api; runtime dependency of `yewtube` |
| `bluetuith` | tui-based bluetooth connection manager |
| `bluetui` | tui for managing bluetooth devices |
| `clipse` | configurable tui clipboard manager for unix |
| `disktui` | tui for disk management and partitioning |
| `latuicon` | tui icon picker for emojis, kaomojis, unicode and nerd fonts |
| `ratl` | json-driven terminal dialogs rendered with ratatui |
| `linux-cachyos-frugal` | builds and deploys frugal boot artifacts from the latest prebuilt cachyos kernel |
| `rstl-pick` | compact fuzzy-search picker for terminal applications, including nmtui, wiremix, clipse, bluetuith and latuicon |
| `xeo` | interpreter for the `.xeo` scripting language (edition 2024) |
| `xeon` | modern package manager for `.xeo` packages |
| `calawk` | small interactive expression calculator built around awk |
| `eva` | simple calculator repl, similar to `bc(1)` |
| `oxicord` | vim-native discord tui client |
| `concord` | feature-rich discord tui client, built from source with voice calls and screen sharing |
| `rovr` | post-modern terminal file explorer, distributed as a nuitka binary |
| `superfile` | terminal file manager; installs as `spf` |
| `yewtube` | terminal-based youtube player and downloader |
| `myx` | lean terminal spotify player |
| `chroncal` | terminal-first calendar, todo and journal manager |
| `fzf-tab` | replaces zsh's default completion selection menu with fzf |
| `zsh-completions` | additional completion definitions for zsh |
| `zsh-auto-notify` | sends a notification when a long-running command finishes |
| `vectorcraft` | vector illustration; clean-room reimplementation of adobe illustrator in pure rust |
| `filmcraft` | video editing, colour and sound; clean-room reimplementation of adobe premiere pro in pure rust |
| `photocraft` | image editing; clean-room reimplementation of adobe photoshop in pure rust |
| `pdfcraft` | pdf workbench; clean-room reimplementation of adobe acrobat in pure rust |
| `lightcraft` | photo library and raw development; clean-room reimplementation of adobe lightroom in pure rust |
| `designcraft` | page layout and publishing; clean-room reimplementation of adobe indesign in pure rust |
| `effectcraft` | motion graphics and visual effects; clean-room reimplementation of adobe after effects in pure rust |
| `wordcraft` | writing and document design; clean-room reimplementation of microsoft word in pure rust |
| `gridcraft` | spreadsheets and data; clean-room reimplementation of microsoft excel in pure rust |
| `deckcraft` | presentations and slide shows; clean-room reimplementation of microsoft powerpoint in pure rust |
| `figcraft` | interface design; clean-room reimplementation of figma in pure rust |
| `soundcraft` | audio recording, editing and mixing; clean-room reimplementation of avid pro tools in pure rust |
| `cadcraft` | computer-aided design and drafting; clean-room reimplementation of autodesk autocad in pure rust |

### automatic package versions

most packages track their upstream versions automatically. if an upstream repository publishes releases, the latest release tag is used as the package version, with a leading `v` stripped where necessary. repositories without releases use the current date in `YYYYMMDD` format.

`resolve.sh` and `inject.sh` handle the version changes at build time by patching the relevant PKGBUILD. this means scheduled builds can pick up new upstream versions without requiring manual version bumps.

a few packages are intentionally pinned because their versions cannot be resolved reliably through the automatic tracking system. these currently include `calawk`, `python-yewtube-search-python` and `linux-cachyos-frugal`. the latter also has a slightly different installation process, since its helper downloads and builds the kernel artifacts when installed.

### frugal cachyos kernel

`linux-cachyos-frugal` installs a small helper alongside a pacman hook. whenever the package is installed or `linux-cachyos` is upgraded, the helper downloads the latest prebuilt cachyos kernel package and builds the required frugal boot artifacts:

- `vmlinuz`
- `initrd.gz`
- `00modules.sfs`

the resulting files are placed in `<FRUGALS>/BOOT/<kernelver>/`.

the generated initrd can use `02modules.new` and `03firmware.new` in place of the original layer files, so updating the cachyos kernel doesn't require changing profile links or boot entries.

the helper discovers the active frugal profile through the running overlay, `w_bootfrom` and mounted `FRUGALS` directories. it doesn't rely on a hardcoded mount path.

more details are available in [`pkgbuilds/linux-cachyos-frugal/README.md`](pkgbuilds/linux-cachyos-frugal/README.md).

## usage - arch linux (pacman)

add the following to `/etc/pacman.conf`:

```ini
[rstl-repo]
SigLevel = Optional TrustAll
Server = https://arozoid.github.io/rstl.repo/arch/
```

the repository is also available from the site root (`https://arozoid.github.io/rstl.repo`) for backwards compatibility.

then sync your package databases:

```bash
sudo pacman -Syu
```

## usage - fedora (dnf)

add the repository as `/etc/yum.repos.d/rstl.repo`:

```ini
[rstl-repo]
name=rstl.repo
baseurl=https://arozoid.github.io/rstl.repo/fedora/
enabled=1
gpgcheck=0
```

refresh the repository metadata:

```bash
sudo dnf makecache
```

### building RPMs

to build the RPM packages from their spec files:

```bash
cd fedora
./build.sh
```

to build a particular package instead:

```bash
./build.sh vectorcraft
```

this requires `rpmbuild`, available through the `rpm-build` package.

## usage - void linux (xbps)

add the repository to `/etc/xbps.d/0-rstl.conf`:

```ini
repository=https://arozoid.github.io/rstl.repo/void
```

then sync the repository:

```bash
sudo xbps-install -S
```

you'll need to accept the repository signing key the first time you sync.

the `0-` filename prefix makes rstl.repo take precedence over packages with the same names in the official void repositories. the rstl.sway installers handle creating this file and importing the signing key automatically on void systems.

## adding a new package

1. create a package directory under `pkgbuilds/<pkgname>/` for the current arch layout, and `arch/pkgbuilds/<pkgname>/` for the future layout.
2. add the fedora build files:
   - `fedora/pkgs/<pkgname>/PKGBUILD`
   - `fedora/specs/<pkgname>/<pkgname>.spec`
3. add an `# auto:` marker to the PKGBUILDs if the package should track its upstream version:
   - `# auto: release` uses the latest upstream release tag, with a leading `v` stripped.
   - `# auto: date` uses the current date in `YYYYMMDD` format.
4. push the changes to `main`. CI will pick up the new package and build it automatically.

there's no need to add anything to the void directory. CI converts the finished arch packages into XBPS packages automatically.

## building locally (arch)

```bash
chmod +x build.sh
./build.sh
```

## building locally (fedora)

```bash
chmod +x fedora/build.sh
./fedora/build.sh
```

## building locally (void)

```bash
chmod +x void/build.sh
./void/build.sh
```

this requires the xbps tools:

```bash
sudo xbps-install -Sy xbps
```

if you're building from a non-void system, run the build inside the official void container. see [`void/README.md`](void/README.md) for details.

---

the main reason i started this repository was to experiment with custom pacman repositories and see how far i could take the same idea across different distributions. it also gives rstl.sway a place to host its own packages, making installations a little easier and faster.
