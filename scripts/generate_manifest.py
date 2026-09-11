"""Compute SHA-256 checksums and build reproducibility manifest."""

import hashlib
import json
import os
from pathlib import Path
import platform
import time

ROOT_DIR = Path(__file__).resolve().parent.parent

# These generated integrity records describe the release; they must not hash
# themselves because that would create a self-referential checksum problem.
INTEGRITY_FILES = {"reproducibility_manifest.json", "checksums.sha256"}


def get_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def main():
    manifest_records = []
    checksum_lines = []

    tracked_extensions = {
        ".py", ".yaml", ".yml", ".md", ".txt", ".toml", ".cff",
        ".parquet", ".csv", ".xlsx", ".png", ".pdf"
    }
    excluded_dirs = {
        ".git", "__pycache__", ".pytest_cache", "venv", "env", "ENV",
        ".venv", "build", "dist"
    }

    for root, dirs, files in os.walk(ROOT_DIR):
        # Prune non-release directories before descending into them. In
        # particular, never hash local virtual environments.
        dirs[:] = [
            d for d in dirs
            if d not in excluded_dirs and not d.startswith(".venv")
        ]

        for f in files:
            if f in INTEGRITY_FILES:
                continue
            p = Path(root) / f
            if p.suffix in tracked_extensions:
                rel_path = p.relative_to(ROOT_DIR).as_posix()
                file_hash = get_sha256(p)
                file_size = p.stat().st_size
                manifest_records.append({
                    "path": rel_path,
                    "sha256": file_hash,
                    "size_bytes": file_size,
                })
                checksum_lines.append(f"{file_hash}  {rel_path}\n")

    manifest_records.sort(key=lambda r: r["path"])
    checksum_lines.sort(key=lambda line: line.split("  ", 1)[1])

    manifest = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "total_files": len(manifest_records),
        "files": manifest_records,
    }

    manifest_path = ROOT_DIR / "reproducibility_manifest.json"
    with open(manifest_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")

    checksum_path = ROOT_DIR / "checksums.sha256"
    with open(checksum_path, "w", encoding="utf-8", newline="\n") as f:
        f.writelines(checksum_lines)

    print(f"Generated manifest with {len(manifest_records)} repository files:")
    print(f"  {manifest_path}")
    print(f"  {checksum_path}")


if __name__ == "__main__":
    main()
