# rstl.repo — Void Linux Repository

Void Linux (`xbps`) repository for the [rstl.sway](https://github.com/arozoid/rstl.sway/)
rice, built alongside the Arch `pacman` and Fedora `dnf` repositories.

## How it is built

The Void endpoint uses the same process as the Fedora endpoint: CI first builds
every package as an Arch `.pkg.tar.*`, then a parallel `void` job converts those
finished packages into XBPS `.xbps` archives with
[`.github/scripts/pkg2xbps.sh`](../.github/scripts/pkg2xbps.sh) and registers
them with `xbps-rindex`.

Nothing needs to be duplicated per distribution: name, version, description,
license, dependencies and file list all come from the built package's
`.PKGINFO`, so the Void endpoint can never drift from the Arch one.

```
void/
├── keys/rstl-repo.pem   # persistent RSA repository-signing key
├── build.sh             # local conversion + xbps-rindex
└── README.md            # this file
```

## Using as an XBPS repository

Add the repository to `/etc/xbps.d/0-rstl.conf`:

```ini
repository=https://arozoid.github.io/rstl.repo/void
```

The `0-` prefix makes it the first repository in the list, so rstl.repo builds
(and custom packages such as `yambar` or `ttf-jetbrains-mono-nerd-min`) take
precedence over same-named packages in the official Void repositories.

Then sync:

```bash
sudo xbps-install -S
```

The first sync asks whether to import the repository's RSA public key. Accept
it; the fingerprint is shown in the prompt. The `rstl.sway` installers import
it automatically (`bin/install.sh`, `bin/install-min.sh`,
`bin/install-base.sh`).

Install packages exactly like from any other repository:

```bash
sudo xbps-install -S yambar clipse rstl-pick rovr
```

Using a local checkout instead of GitHub Pages:

```ini
repository=file:///home/youruser/rstl.repo/void/repo
```

Local repositories do not need to be signed.

## Building locally

On Void Linux with the `xbps` tools installed:

```bash
sudo xbps-install -Sy xbps
./void/build.sh
```

The script converts every `.pkg.tar.*` in `repo/` and `arch/repo/` into
`void/repo/`, creates `x86_64-repodata` with `xbps-rindex`, and signs the index
and packages with `void/keys/rstl-repo.pem`.

To convert specific packages:

```bash
./void/build.sh /path/to/*.pkg.tar.*
```

Or from a non-Void host, using the official Void container:

```bash
podman run --rm -v "$PWD:/work" -w /work \
  ghcr.io/void-linux/void-glibc-full:latest \
  ./void/build.sh
```

## Package name mapping

The converter maps Arch dependency names to Void package names. Notable
mappings include:

| Arch | Void |
|------|------|
| `gcc-libs` | `libgcc` + `libstdc++` |
| `libudev.so` | `eudev-libudev` |
| `libpulse` | `libpulseaudio` |
| `libinih` | `inih` |
| `libx11` / `libxcursor` / `libxi` | `libX11` / `libXcursor` / `libXi` |
| `networkmanager` | `NetworkManager` |
| `vulkan-icd-loader` | `vulkan-loader` |
| `python-*` | `python3-*` |
| `bluez-libs` | `libbluetooth` |

Packages built by this repository keep their name, so in-repo dependencies
(`xeo`, `python-yewtube-search-python`, ...) resolve inside the same repo.

## Signing key

`void/keys/rstl-repo.pem` is the persistent RSA key that signs the repository
index and every package (`.xbps.sig2`). It is committed on purpose so the
automated builds always produce packages that existing installations trust.
It provides integrity for the custom repository only and is not a secret used
for anything else.

To rotate the key, replace `void/keys/rstl-repo.pem`; clients will be asked to
trust the new fingerprint on their next sync. If you prefer to keep the key out
of the repository, store it in a `XBPS_PRIVKEY` GitHub Actions secret and write
it to `void/keys/rstl-repo.pem` in the workflow before the signing step.
