"""Scan a directory for photos/videos and extract dates."""

import os
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

import exifread

PHOTO_EXTENSIONS = {".nef", ".raw", ".jpg", ".jpeg", ".cr2", ".arw", ".dng"}
VIDEO_EXTENSIONS = {".mov", ".mp4", ".avi", ".mkv", ".mts"}
ALL_EXTENSIONS = PHOTO_EXTENSIONS | VIDEO_EXTENSIONS


@dataclass
class FileInfo:
    path: Path
    filename: str
    date: date
    file_type: str  # "photo" or "video"
    size: int


@dataclass
class Group:
    name: str
    dates: list[date] = field(default_factory=list)
    files: list[FileInfo] = field(default_factory=list)

    @property
    def first_date(self) -> date:
        return min(self.dates)


def classify_file(ext: str) -> str | None:
    """Return 'photo', 'video', or None based on extension."""
    ext_lower = ext.lower()
    if ext_lower in PHOTO_EXTENSIONS:
        return "photo"
    if ext_lower in VIDEO_EXTENSIONS:
        return "video"
    return None


def extract_exif_date(filepath: Path) -> date | None:
    """Extract DateTimeOriginal from EXIF data using exifread."""
    try:
        with open(filepath, "rb") as f:
            tags = exifread.process_file(f, stop_tag="DateTimeOriginal", details=False)
        tag = tags.get("EXIF DateTimeOriginal")
        if tag:
            dt = datetime.strptime(str(tag), "%Y:%m:%d %H:%M:%S")
            return dt.date()
    except Exception:
        pass
    return None


def extract_date(filepath: Path) -> date:
    """Extract date from EXIF or fall back to file modification time."""
    exif_date = extract_exif_date(filepath)
    if exif_date:
        return exif_date
    mtime = os.path.getmtime(filepath)
    return datetime.fromtimestamp(mtime).date()


def scan_directory(path: str | Path) -> dict[date, list[FileInfo]]:
    """Recursively scan a directory and return files grouped by date.

    Args:
        path: Root directory to scan.

    Returns:
        Dictionary mapping dates to lists of FileInfo objects.
    """
    path = Path(path)
    result: dict[date, list[FileInfo]] = {}

    for root, _dirs, files in os.walk(path):
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            file_type = classify_file(ext)
            if file_type is None:
                continue

            filepath = Path(root) / filename
            try:
                file_date = extract_date(filepath)
                size = filepath.stat().st_size
            except OSError:
                continue

            info = FileInfo(
                path=filepath,
                filename=filename,
                date=file_date,
                file_type=file_type,
                size=size,
            )

            result.setdefault(file_date, []).append(info)

    return result


def count_files(files_by_date: dict[date, list[FileInfo]]) -> tuple[int, int]:
    """Count total photos and videos across all dates."""
    photos = 0
    videos = 0
    for files in files_by_date.values():
        for f in files:
            if f.file_type == "photo":
                photos += 1
            else:
                videos += 1
    return photos, videos


def count_for_date(files: list[FileInfo]) -> tuple[int, int]:
    """Count photos and videos for a single date's file list."""
    photos = sum(1 for f in files if f.file_type == "photo")
    videos = sum(1 for f in files if f.file_type == "video")
    return photos, videos
