# SortIt

Desktop app to sort photos and videos from an SD card (Nikon, iPhone, etc.) into organized date-based folders.

## What it does

1. **Select source** — Pick an SD card, USB drive, or any folder. Removable devices are auto-detected.
2. **Set destinations** — Choose separate folders for photos and videos. Pick copy or move mode.
3. **Group by date** — Files are scanned and sorted by EXIF date. Check dates, name a group, and repeat until all dates are assigned.
4. **Transfer** — Files are copied/moved into a clean folder structure:

```
Destination/
└── 2025/
    └── 01/
        └── 15_Wedding/
            ├── DSC_0001.nef
            ├── DSC_0002.jpg
            └── ...
```

## Supported formats

| Photos | Videos |
|---|---|
| .nef .raw .jpg .jpeg .cr2 .arw .dng | .mov .mp4 .avi .mkv .mts |

## Install & run

```bash
pip install -r requirements.txt
python main.py
```

Or use the standalone executable in `dist/SortIt.exe` (no Python needed).

## Build the exe

```bash
pip install pyinstaller
pyinstaller SortIt.spec
```

## Tech

Python 3 · CustomTkinter · Pillow · exifread
