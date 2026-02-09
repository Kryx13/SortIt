"""Transfer (copy/move) files to organized destination folders."""

import os
import shutil
from pathlib import Path
from typing import Callable

from src.scanner import FileInfo, Group


def _unique_path(dest: Path) -> Path:
    """Return a unique path by appending _1, _2, etc. if dest already exists."""
    if not dest.exists():
        return dest
    stem = dest.stem
    suffix = dest.suffix
    parent = dest.parent
    counter = 1
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        candidate = parent / new_name
        if not candidate.exists():
            return candidate
        counter += 1


def _build_dest_path(base_dir: Path, group: Group, filename: str) -> Path:
    """Build destination path: base/YYYY/MM/DD_GroupName/filename."""
    first = group.first_date
    year = f"{first.year:04d}"
    month = f"{first.month:02d}"
    day_folder = f"{first.day:02d}_{group.name}"
    return base_dir / year / month / day_folder / filename


def execute_transfer(
    groups: list[Group],
    photo_dest: str | Path,
    video_dest: str | Path,
    mode: str,
    callback: Callable[[int, int, str], None] | None = None,
) -> dict:
    """Transfer files from groups to destination directories.

    Args:
        groups: List of Group objects containing files to transfer.
        photo_dest: Base directory for photos.
        video_dest: Base directory for videos.
        mode: "copy" or "move".
        callback: Called with (current_file_index, total_files, filename)
            after each file is processed.

    Returns:
        Dict with keys: "transferred", "errors" (list of (filename, error_msg)).
    """
    photo_dest = Path(photo_dest)
    video_dest = Path(video_dest)
    transfer_fn = shutil.copy2 if mode == "copy" else shutil.move

    all_files: list[tuple[Group, FileInfo]] = []
    for group in groups:
        for file_info in group.files:
            all_files.append((group, file_info))

    total = len(all_files)
    transferred = 0
    errors: list[tuple[str, str]] = []

    for idx, (group, file_info) in enumerate(all_files):
        base = photo_dest if file_info.file_type == "photo" else video_dest
        dest_path = _build_dest_path(base, group, file_info.filename)
        dest_path = _unique_path(dest_path)

        try:
            os.makedirs(dest_path.parent, exist_ok=True)
            transfer_fn(str(file_info.path), str(dest_path))
            transferred += 1
        except Exception as e:
            errors.append((file_info.filename, str(e)))

        if callback:
            callback(idx + 1, total, file_info.filename)

    return {"transferred": transferred, "errors": errors}
