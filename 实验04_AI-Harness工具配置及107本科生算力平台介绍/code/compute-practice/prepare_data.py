"""Verify and extract the original CIFAR-10 archive without PyTorch or network calls."""

import argparse
import hashlib
from pathlib import Path, PurePosixPath
import shutil
import tarfile


ARCHIVE_MD5 = "c58f30108f718f92721af3b95e74349a"
FOLDER = "cifar-10-batches-py"
# Checksums published by torchvision.datasets.CIFAR10 (v0.22.1).
FILES = {
    "data_batch_1": "c99cafc152244af753f735de768cd75f",
    "data_batch_2": "d4bba439e000b95fd0a9bffe97cbabec",
    "data_batch_3": "54ebc095f3ab1f0389bbae665268c751",
    "data_batch_4": "634d18415352ddfa80567beed471001a",
    "data_batch_5": "482c414d41f54cd18b22e5b47cb7c3cb",
    "test_batch": "40351d587109b95175f43aff81a1287e",
    "batches.meta": "5ff9c542aee3614f3951f8cda6e48888",
}


def digest(path):
    value = hashlib.md5()  # Matches the original dataset's transfer checksum.
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def verify(root):
    folder = root / FOLDER
    for name, expected in FILES.items():
        path = folder / name
        if not path.is_file() or digest(path) != expected:
            raise ValueError(f"CIFAR-10 missing or checksum mismatch: {path}")
    print(f"verified CIFAR-10: {folder}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, help="Original cifar-10-python.tar.gz")
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    root = args.data_dir.resolve()
    if args.check_only or (root / FOLDER).exists():
        verify(root)
        return
    if args.archive is None or not args.archive.is_file():
        parser.error("Provide --archive, or --check-only for an extracted dataset.")
    if digest(args.archive) != ARCHIVE_MD5:
        raise ValueError("Archive MD5 mismatch; download again before extracting.")
    # Extract only expected regular dataset files. Never follow archive links.
    with tarfile.open(args.archive, "r:gz") as archive:
        selected = {}
        for member in archive.getmembers():
            parts = PurePosixPath(member.name).parts
            if len(parts) == 2 and parts[0] == FOLDER and parts[1] in FILES:
                if not member.isfile() or parts[1] in selected:
                    raise ValueError(f"Unexpected dataset archive entry: {member.name}")
                selected[parts[1]] = member
        if set(selected) != set(FILES):
            raise ValueError("Archive does not contain the complete expected dataset.")
        destination = root / FOLDER
        destination.mkdir(parents=True, exist_ok=False)
        for name, member in selected.items():
            with archive.extractfile(member) as source, (destination / name).open("xb") as target:
                shutil.copyfileobj(source, target)
    verify(root)


if __name__ == "__main__":
    main()
