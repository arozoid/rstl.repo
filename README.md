# rstl.repo

custom pacman repository for the [rstl.sway](https://github.com/arozoid/rstl.sway/) rice

## packages

- `rstlpk:` Minimal polkit authentication agent (no gtk)
- `dssd:` Dead simple freedesktop SecretService implementation 
- `xdg-desktop-portal-termfilechooser:` Terminal file chooser portal backend 
- `yambar:` Modular status panel (built without -Werror) 

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
3. push to `main` — the weekly workflow will build it automatically

## building locally

```bash
chmod +x build.sh
./build.sh
```

---

the main goal of this was mostly to experiment with pacman repos, and also make rstl.sway installation easier and faster
