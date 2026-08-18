# rstl-repo

Custom pacman repository for the rstl.sway rice.

## Packages

| Package | Description |
|---------|-------------|
| `rstlpk` | Minimal polkit authentication agent (no gtk) |
| `dssd` | Dead simple freedesktop SecretService implementation |
| `xdg-desktop-portal-termfilechooser` | Terminal file chooser portal backend |
| `yambar` | Modular status panel (built without -Werror) |

## Usage

Add to `/etc/pacman.conf`:

```
[rstl-repo]
Server = https://arozoid.github.io/rstl-repo
```

Then:

```bash
sudo pacman -Sy rstl-repo-keyring
sudo pacman -Syu
```

## Adding a new package

1. Create a directory in `pkgbuilds/<pkgname>/`
2. Add a `PKGBUILD` file
3. Push to `main` — the weekly workflow will build it automatically

## Building locally

```bash
chmod +x build.sh
./build.sh
```
