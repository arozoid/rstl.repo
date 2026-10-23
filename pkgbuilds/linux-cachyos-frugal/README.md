# linux-cachyos-frugal

Builds a FRUGAL kernel set from the latest **prebuilt** CachyOS
`linux-cachyos` package and installs it into an existing FRUGAL profile.

No kernel source tree is compiled.  The helper downloads the CachyOS binary
package, extracts it in a temporary directory, and produces:

- `vmlinuz`
- `initrd.gz` (FRUGAL skeleton plus storage/overlay modules)
- `00modules.sfs` (the complete module tree)
- `readme_kernel_version.txt`

The CachyOS package is verified against the SHA-256 from its repository
database before it is used.

## Finding the FRUGAL profile

There is no hard-coded path such as `/mnt/sda2/@/FRUGALS`.  The profile is
discovered from, in order:

1. `--frugal-dir` / `FRUGAL_DIR` (explicit override).
2. The overlay `upperdir` of the running root, when the profile is currently
   mounted.
3. `w_bootfrom=...` on the kernel command line.
4. Mounted filesystems containing a `FRUGALS` directory.
5. The last profile recorded in `/var/lib/linux-cachyos-frugal/profile`.

A directory is treated as a profile only when it contains `vmlinuz`,
`initrd.gz`, an overlay/rootfs layer, and either `00modules.sfs` or
`02modules.new`.  Versioned `BOOT` directories are therefore not confused
with profiles.  If the current boot is
a non-CachyOS fallback but a sibling CachyOS profile exists, the CachyOS
profile is preferred; `rstl.sway` is used as a tie-breaker between multiple
CachyOS profiles.

## Usage

```sh
# Detect the profile that would be used
linux-cachyos-frugal detect

# List all detected profiles
linux-cachyos-frugal list

# Show the source/version and target without downloading or writing
linux-cachyos-frugal --dry-run

# Build from the latest prebuilt CachyOS package and activate it
sudo linux-cachyos-frugal

# Rebuild from the already installed linux-cachyos package (no download)
sudo linux-cachyos-frugal --from-installed

# Use a specific profile
sudo linux-cachyos-frugal --frugal-dir /path/to/FRUGALS/rstl.sway

# Repoint 00modules.sfs directly instead of using 02modules.new
sudo linux-cachyos-frugal --legacy-links

# Build artifacts only, without touching FRUGAL
linux-cachyos-frugal build --build-dir /tmp/frugal-kernel --source installed
```

Artifacts are written to `<FRUGALS>/BOOT/<kernelver>/`.  By default the
profile's `vmlinuz`, `initrd.gz`, and `readme_kernel_version.txt` links are
repointed to that directory, while `00modules.sfs` and `01firmware.sfs` are
left alone.  Instead, the profile gets a `02modules.new` link to the new
module SFS; if a shared firmware SFS exists, it also gets a `03firmware.new`
link (an existing `03firmware.new` is never replaced).

The generated initrd understands those replacement names.  At boot it looks
for `NNmodules.new` and `NNfirmware.new` (two-digit prefix) and uses the
highest-numbered match as the `00modules`/`01firmware` layer.  This means a
profile can be updated without switching to another entry or editing the
original layer links.  If a replacement is missing or cannot be mounted, the
initrd falls back to the original `00modules`/`01firmware`.

Use `--legacy-links` to return to the old behaviour: repoint
`00modules.sfs` directly and remove package-managed `.new` links.  Existing
versioned directories and the fallback profile are left intact.  Each
installed version includes a generated `restore-previous.sh`.

## Automatic updates

A pacman hook runs after an install or upgrade of `linux-cachyos` and rebuilds
the artifacts from the installed package:

```
/usr/share/libalpm/hooks/90-linux-cachyos-frugal.hook
```

The hook is a no-op on systems without a discoverable FRUGAL profile.

## Package source

The binary CachyOS package is selected from the CachyOS `cachyos-v3` repository
on x86-64-v3 capable systems, or `cachyos` otherwise.  `--mirror`, `--arch`,
and `--repo` can override the detected values.  The package cache defaults to
`/var/cache/linux-cachyos-frugal` when run as root.

## Credits

`mkFRkernel` is a modified version of the FirstRib FRUGAL initrd builder.
See the header of that script for the original copyright and license notices.
