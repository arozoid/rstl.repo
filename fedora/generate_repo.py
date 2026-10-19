#!/usr/bin/env python3
"""
generate_repo.py — Generate Fedora/DNF repository metadata (repodata).

Reads RPM files from Packages directories and produces:
  repomd.xml      — repository metadata with checksums
  primary.xml     — package name, version, release, arch, summary, deps
  filelists.xml   — files provided by each package
  other.xml       — changelog, etc.

Usage:
  python3 generate_repo.py [repodir]

Where repodir defaults to fedora/x86_64. Scans repodir/Packages/ for .rpm files
and writes repodata into repodir/repodata/.
"""

import hashlib
import os
import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime, timezone

try:
    import rpmfile
except ImportError:
    print("ERROR: rpmfile module required. Install with: pip install rpmfile", file=sys.stderr)
    sys.exit(1)


PACKAGES_DIR_NAME = "Packages"
REPODATA_DIR_NAME = "repodata"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha1_file(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def md5_file(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def file_size(path):
    return os.path.getsize(path)


def escape_xml(text):
    if text is None:
        return ""
    return (text.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;")
             .replace("'", "&apos;"))


def pretty_xml(elem):
    """Return a pretty-printed XML string for an element."""
    rough = ET.tostring(elem, encoding="unicode")
    reparsed = minidom.parseString(rough)
    return reparsed.toprettyxml(indent="  ")


def collect_packages(packages_dir):
    """Scan packages_dir for .rpm files and extract metadata using rpmfile."""
    packages = []
    if not os.path.isdir(packages_dir):
        return packages

    for fname in sorted(os.listdir(packages_dir)):
        if not fname.endswith(".rpm"):
            continue
        fpath = os.path.join(packages_dir, fname)
        try:
            with rpmfile.open(fpath) as rpm:
                pkg = {
                    "filename": fname,
                    "path": fpath,
                    "name": rpm.get("Name", ""),
                    "version": rpm.get("Version", ""),
                    "release": rpm.get("Release", ""),
                    "arch": rpm.get("Arch", "noarch"),
                    "epoch": rpm.get("Epoch", 0),
                    "summary": rpm.get("Summary", ""),
                    "description": rpm.get("Description", ""),
                    "license": rpm.get("License", ""),
                    "vendor": rpm.get("Vendor", ""),
                    "packager": rpm.get("Packager", ""),
                    "buildhost": rpm.get("BuildHost", ""),
                    "buildtime": rpm.get("BuildTime", 0),
                    "size": rpm.get("Size", 0),
                    "installsize": rpm.get("InstallSize", 0),
                    "source_rpm": rpm.get("SourceRpm", ""),
                    "provides": rpm.get("Provides", []),
                    "requires": rpm.get("Requires", []),
                    "obsoletes": rpm.get("Obsoletes", []),
                    "conflicts": rpm.get("Conflicts", []),
                    "files": rpm.get("FileNames", []),
                }
                packages.append(pkg)
        except Exception as e:
            print(f"WARNING: could not read {fname}: {e}", file=sys.stderr)
    return packages


def generate_primary(packages):
    """Generate primary.xml content."""
    root = ET.Element("packages")
    root.set("count", str(len(packages)))

    for pkg in packages:
        pkg_elem = ET.SubElement(root, "package")
        pkg_elem.set("pkgid", sha256_file(pkg["path"]))
        pkg_elem.set("name", pkg["name"])
        pkg_elem.set("arch", pkg["arch"])

        version = ET.SubElement(pkg_elem, "version")
        version.set("epoch", str(pkg["epoch"]))
        version.set("ver", pkg["version"])
        version.set("rel", pkg["release"])

        ET.SubElement(pkg_elem, "title").text = escape_xml(pkg["summary"])
        ET.SubElement(pkg_elem, "issued").set("date", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))

        summary = ET.SubElement(pkg_elem, "summary")
        summary.set("xml:lang", "en_US")
        summary.text = escape_xml(pkg["summary"])

        desc = ET.SubElement(pkg_elem, "description")
        desc.set("xml:lang", "en_US")
        desc.text = escape_xml(pkg["description"])

        if pkg["packager"]:
            ET.SubElement(pkg_elem, "packager").text = escape_xml(pkg["packager"])

        url = ET.SubElement(pkg_elem, "url")
        url.text = escape_xml(pkg.get("url", ""))

        etag = ET.SubElement(pkg_elem, "time")
        etag.set("event", "build")
        etag.set("value", str(int(pkg["buildtime"]) if pkg["buildtime"] else 0))

        size = ET.SubElement(pkg_elem, "size")
        size.set("package", str(file_size(pkg["path"])))
        size.set("installed", str(pkg["installsize"]))
        size.set("archive", str(file_size(pkg["path"])))

        location = ET.SubElement(pkg_elem, "location")
        location.set("href", pkg["filename"])

        fmt = ET.SubElement(pkg_elem, "format")
        fmt.set("rpm", "version")

        for req in pkg["requires"]:
            req_elem = ET.SubElement(pkg_elem, "requires")
            req_elem.set("type", "rpm")
            req_elem.set("name", escape_xml(req.get("name", "")))
            if req.get("flags"):
                req_elem.set("flags", escape_xml(req["flags"]))
            if req.get("version"):
                req_elem.set("ver", escape_xml(req["version"]))

        for prov in pkg["provides"]:
            prov_elem = ET.SubElement(pkg_elem, "provides")
            prov_elem.set("type", "rpm")
            prov_elem.set("name", escape_xml(prov.get("name", "")))
            if prov.get("version"):
                prov_elem.set("ver", escape_xml(prov["version"]))

        for obs in pkg["obsoletes"]:
            obs_elem = ET.SubElement(pkg_elem, "obsoletes")
            obs_elem.set("type", "rpm")
            obs_elem.set("name", escape_xml(obs.get("name", "")))
            if obs.get("version"):
                obs_elem.set("ver", escape_xml(obs["version"]))

        for conf in pkg["conflicts"]:
            conf_elem = ET.SubElement(pkg_elem, "conflicts")
            conf_elem.set("type", "rpm")
            conf_elem.set("name", escape_xml(conf.get("name", "")))
            if conf.get("version"):
                conf_elem.set("ver", escape_xml(conf["version"]))

    return pretty_xml(root)


def generate_filelists(packages):
    """Generate filelists.xml content."""
    root = ET.Element("filelists")
    root.set("count", str(len(packages)))

    for pkg in packages:
        pkg_elem = ET.SubElement(root, "package")
        pkg_elem.set("pkgid", sha256_file(pkg["path"]))
        pkg_elem.set("name", pkg["name"])
        pkg_elem.set("arch", pkg["arch"])

        version = ET.SubElement(pkg_elem, "version")
        version.set("epoch", str(pkg["epoch"]))
        version.set("ver", pkg["version"])
        version.set("rel", pkg["release"])

        for fpath in pkg["files"]:
            file_elem = ET.SubElement(pkg_elem, "file")
            file_elem.set("path", escape_xml(fpath))

    return pretty_xml(root)


def generate_other(packages):
    """Generate other.xml content."""
    root = ET.Element("other")
    root.set("count", str(len(packages)))

    for pkg in packages:
        pkg_elem = ET.SubElement(root, "package")
        pkg_elem.set("pkgid", sha256_file(pkg["path"]))
        pkg_elem.set("name", pkg["name"])
        pkg_elem.set("arch", pkg["arch"])

        version = ET.SubElement(pkg_elem, "version")
        version.set("epoch", str(pkg["epoch"]))
        version.set("ver", pkg["version"])
        version.set("rel", pkg["release"])

        changelog = rpmfile.get_changelog(pkg["path"]) if hasattr(rpmfile, 'get_changelog') else []
        if changelog:
            cl_elem = ET.SubElement(pkg_elem, "changelog")
            for entry in changelog:
                cel = ET.SubElement(cl_elem, "entry")
                cel.set("date", str(entry.get("time", 0)))
                cel.set("name", escape_xml(entry.get("name", "")))
                cel.text = escape_xml(entry.get("text", ""))

    return pretty_xml(root)


def generate_repomd(packages, repodata_dir):
    """Generate repomd.xml."""
    repomd = ET.Element("repomd")
    repomd.set("xmlns", "http://linux.duke.edu/metadata/repo")
    repomd.set("xmlns:rpm", "http://linux.duke.edu/metadata/rpm")

    revision = ET.SubElement(repomd, "revision")
    revision.text = str(int(datetime.now(timezone.utc).timestamp()))

    data_types = [
        ("primary", "primary.xml"),
        ("filelists", "filelists.xml"),
        ("other", "other.xml"),
    ]

    for dtype, fname in data_types:
        fpath = os.path.join(repodata_dir, fname)
        if not os.path.exists(fpath):
            continue
        m = {
            "sha256": sha256_file(fpath),
            "sha1": sha1_file(fpath),
            "md5": md5_file(fpath),
            "size": file_size(fpath),
        }

        data = ET.SubElement(repomd, "data")
        data.set("type", dtype)

        location = ET.SubElement(data, "location")
        location.set("href", fname)

        for checksum_type in ["sha256", "sha1", "md5"]:
            cs = ET.SubElement(data, "checksum")
            cs.set("type", checksum_type)
            cs.text = m[checksum_type]

        timestamp = ET.SubElement(data, "timestamp")
        timestamp.text = str(int(datetime.now(timezone.utc).timestamp()))

        size_el = ET.SubElement(data, "size")
        size_el.text = str(m["size"])

        open_size = ET.SubElement(data, "open-size")
        open_size.text = "0"

    rough = ET.tostring(repomd, encoding="unicode")
    reparsed = minidom.parseString(rough)
    return reparsed.toprettyxml(indent="  ")


def generate_repo(packages_dir):
    """Main: scan packages, generate all repodata files."""
    packages_dir = os.path.abspath(packages_dir)
    pkg_dir = os.path.join(packages_dir, PACKAGES_DIR_NAME)
    repodata_dir = os.path.join(packages_dir, REPODATA_DIR_NAME)

    os.makedirs(repodata_dir, exist_ok=True)

    packages = collect_packages(pkg_dir)
    print(f"Found {len(packages)} RPM packages")

    primary_xml = generate_primary(packages)
    with open(os.path.join(repodata_dir, "primary.xml"), "w") as f:
        f.write(primary_xml)
    print("Wrote primary.xml")

    filelists_xml = generate_filelists(packages)
    with open(os.path.join(repodata_dir, "filelists.xml"), "w") as f:
        f.write(filelists_xml)
    print("Wrote filelists.xml")

    other_xml = generate_other(packages)
    with open(os.path.join(repodata_dir, "other.xml"), "w") as f:
        f.write(other_xml)
    print("Wrote other.xml")

    repomd_xml = generate_repomd(packages, repodata_dir)
    with open(os.path.join(repodata_dir, "repomd.xml"), "w") as f:
        f.write(repomd_xml)
    print("Wrote repomd.xml")

    print(f"\nRepository metadata generated in {repodata_dir}/")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "fedora"
    generate_repo(target)
