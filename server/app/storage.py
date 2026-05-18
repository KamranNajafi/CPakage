import hashlib
import os
import shutil

STORAGE_DIR = os.getenv("STORAGE_DIR", "storage")


def save_package_file(name: str, version: str, data: bytes) -> tuple[str, int, str]:
    pkg_dir = os.path.join(STORAGE_DIR, name)
    os.makedirs(pkg_dir, exist_ok=True)

    filename = f"{name}-{version}.tar.gz"
    file_path = os.path.join(pkg_dir, filename)

    with open(file_path, "wb") as f:
        f.write(data)

    checksum = hashlib.sha256(data).hexdigest()
    return file_path, len(data), checksum


def get_package_path(name: str, version: str) -> str:
    return os.path.join(STORAGE_DIR, name, f"{name}-{version}.tar.gz")


def delete_package_file(name: str, version: str) -> None:
    path = get_package_path(name, version)
    if os.path.exists(path):
        os.remove(path)
    pkg_dir = os.path.join(STORAGE_DIR, name)
    if os.path.exists(pkg_dir) and not os.listdir(pkg_dir):
        shutil.rmtree(pkg_dir)
