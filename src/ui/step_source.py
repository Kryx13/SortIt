"""Step 1: Select the source directory (SD card, USB drive, or folder)."""

import platform
import subprocess
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from src.scanner import ALL_EXTENSIONS


class StepSource(ctk.CTkFrame):
    def __init__(self, parent, state):
        super().__init__(parent, fg_color="transparent")
        self.state = state

        # Title
        ctk.CTkLabel(
            self, text="Sélection de la source", font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 10))

        ctk.CTkLabel(
            self,
            text="Choisissez le périphérique ou le dossier contenant vos photos et vidéos.",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        ).pack(pady=(0, 20))

        # Removable devices section
        devices_frame = ctk.CTkFrame(self)
        devices_frame.pack(fill="x", padx=30, pady=(0, 10))

        ctk.CTkLabel(
            devices_frame,
            text="Périphériques détectés :",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=15, pady=(10, 5))

        self.devices_list_frame = ctk.CTkFrame(devices_frame, fg_color="transparent")
        self.devices_list_frame.pack(fill="x", padx=15, pady=(0, 5))

        self.btn_refresh = ctk.CTkButton(
            devices_frame, text="Rafraîchir", command=self._detect_devices, width=120
        )
        self.btn_refresh.pack(pady=(0, 10))

        # Manual browse
        browse_frame = ctk.CTkFrame(self)
        browse_frame.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(
            browse_frame,
            text="Ou parcourir manuellement :",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=15, pady=(10, 5))

        row = ctk.CTkFrame(browse_frame, fg_color="transparent")
        row.pack(fill="x", padx=15, pady=(0, 10))

        self.path_var = ctk.StringVar()
        self.path_entry = ctk.CTkEntry(row, textvariable=self.path_var, width=450)
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(row, text="Parcourir…", command=self._browse, width=120).pack(
            side="right"
        )

        # Info label
        self.info_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=13), text_color="#2FA572"
        )
        self.info_label.pack(pady=15)

    def on_enter(self):
        self._detect_devices()
        if self.state.source_path:
            self.path_var.set(self.state.source_path)

    def _detect_devices(self):
        for widget in self.devices_list_frame.winfo_children():
            widget.destroy()

        devices = self._list_removable_drives()
        if not devices:
            ctk.CTkLabel(
                self.devices_list_frame,
                text="Aucun périphérique amovible détecté.",
                text_color="gray",
            ).pack(anchor="w")
        else:
            for dev_path, label in devices:
                btn = ctk.CTkButton(
                    self.devices_list_frame,
                    text=f"📁  {label}  ({dev_path})",
                    anchor="w",
                    command=lambda p=dev_path: self._select_path(p),
                    fg_color="transparent",
                    border_width=1,
                    text_color=("gray10", "gray90"),
                    hover_color=("gray80", "gray30"),
                )
                btn.pack(fill="x", pady=2)

    def _list_removable_drives(self) -> list[tuple[str, str]]:
        system = platform.system()
        drives = []
        if system == "Windows":
            try:
                result = subprocess.run(
                    ["wmic", "logicaldisk", "where", "DriveType=2", "get",
                     "DeviceID,VolumeName", "/format:csv"],
                    capture_output=True, text=True, timeout=5,
                )
                for line in result.stdout.strip().splitlines():
                    parts = line.split(",")
                    if len(parts) >= 3 and parts[1].endswith(":"):
                        dev_id = parts[1]
                        vol_name = parts[2] if parts[2] else "Amovible"
                        drives.append((dev_id + "\\", vol_name))
            except Exception:
                pass
        elif system == "Darwin":
            volumes = Path("/Volumes")
            if volumes.exists():
                for vol in volumes.iterdir():
                    if vol.name == "Macintosh HD":
                        continue
                    drives.append((str(vol), vol.name))
        return drives

    def _browse(self):
        folder = filedialog.askdirectory(title="Sélectionner le dossier source")
        if folder:
            self._select_path(folder)

    def _select_path(self, path: str):
        self.path_var.set(path)
        self.state.source_path = path
        self._count_files(path)

    def _count_files(self, path: str):
        root = Path(path)
        if not root.is_dir():
            self.info_label.configure(text="⚠ Dossier introuvable.", text_color="red")
            return

        count = 0
        for dirpath, _dirs, files in __import__("os").walk(root):
            for f in files:
                ext = __import__("os").path.splitext(f)[1].lower()
                if ext in ALL_EXTENSIONS:
                    count += 1

        self.info_label.configure(
            text=f"✔ {count} fichier(s) photo/vidéo détecté(s).", text_color="#2FA572"
        )

    def validate(self) -> bool:
        path = self.path_var.get().strip()
        if not path or not Path(path).is_dir():
            self.info_label.configure(
                text="⚠ Veuillez sélectionner un dossier source valide.", text_color="red"
            )
            return False
        self.state.source_path = path
        return True
