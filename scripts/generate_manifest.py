"""Compute SHA-256 checksums and build reproducibility manifest."""

import hashlib
import json
import os
from pathlib import Path
import platform
import time

ROOT_DIR = Path(__file__).resolve().parent.parent


def get_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def main():
    manifest_records = []
    checksum_lines = []

    tracked_extensions = {".py", ".yaml", ".yml", ".md", ".txt", ".toml", ".cff", ".parquet", ".csv", ".xlsx", ".png", ".pdf"}

    for root, dirs, files in os.walk(ROOT_DIR):
        # Skip __pycache__ and pytest caches
        if "__pycache__" in root or ".pytest_cache" in root or ".git" in root:
            continue

        for f in files:
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

    manifest = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "total_files": len(manifest_records),
        "files": manifest_records,
    }

    manifest_path = ROOT_DIR / "reproducibility_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    checksum_path = ROOT_DIR / "checksums.sha256"
    with open(checksum_path, "w", encoding="utf-8") as f:
        f.writelines(checksum_lines)

    print(f"Generated manifest with {len(manifest_records)} tracked files:")
    print(f"  {manifest_path}")
    print(f"  {checksum_path}")


if __name__ == "__main__":
    main()
