from __future__ import annotations

import shutil
import subprocess
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path


DATASET = "nathanlauga/nba-games"
PUBLIC_DOWNLOAD_URL = "https://www.kaggle.com/api/v1/datasets/download/nathanlauga/nba-games"
ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "data" / "raw"
REQUIRED_FILES = {
    "games.csv",
    "games_details.csv",
    "players.csv",
    "ranking.csv",
    "teams.csv",
}


def find_kaggle_executable() -> str | None:
    venv_kaggle = Path(sys.executable).with_name("kaggle")
    if venv_kaggle.exists():
        return str(venv_kaggle)
    return shutil.which("kaggle")


def missing_files() -> list[str]:
    return sorted(name for name in REQUIRED_FILES if not (RAW_DIR / name).exists())


def download_with_kaggle_cli(kaggle: str) -> bool:
    command = [
        kaggle,
        "datasets",
        "download",
        "-d",
        DATASET,
        "-p",
        str(RAW_DIR),
        "--unzip",
    ]
    print("Downloading Kaggle dataset with Kaggle CLI:", DATASET)
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip().splitlines()
        if stderr:
            print("Kaggle CLI error:", stderr[-1])
        return False
    return True


def download_with_public_url() -> bool:
    zip_path = RAW_DIR / "nba-games.zip"
    print("Downloading Kaggle dataset with public API URL.")
    try:
        urllib.request.urlretrieve(PUBLIC_DOWNLOAD_URL, zip_path)
    except (urllib.error.URLError, OSError) as exc:
        print(f"Public download failed: {exc}")
        return False

    try:
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(RAW_DIR)
    finally:
        zip_path.unlink(missing_ok=True)
    return True


def main() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    missing = missing_files()
    if not missing:
        print("All raw CSV files already exist in data/raw.")
        return 0

    kaggle = find_kaggle_executable()
    print("Output directory:", RAW_DIR)
    downloaded = False
    if kaggle:
        downloaded = download_with_kaggle_cli(kaggle)
        if not downloaded:
            print("Kaggle CLI download failed; trying public API URL.")
    else:
        print("Kaggle CLI was not found; trying public API URL.")

    if not downloaded:
        downloaded = download_with_public_url()

    if not downloaded:
        print("\nDataset download failed.")
        print("If using Kaggle CLI, confirm ~/.kaggle/kaggle.json exists and has permission 600.")
        print("You can also manually download the dataset and unzip it into data/raw.")
        print("Required files:", ", ".join(sorted(REQUIRED_FILES)))
        return 1

    missing = missing_files()
    if missing:
        print("Download finished, but these required files are still missing:")
        for name in missing:
            print("-", name)
        return 1

    print("Dataset is ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
