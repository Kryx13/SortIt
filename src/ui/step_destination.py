"""Step 2: Select destination folders for photos and videos, and transfer mode."""

from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk


class StepDestination(ctk.CTkFrame):
    def __init__(self, parent, state):
        super().__init__(parent, fg_color="transparent")
        self.state = state

        # Title
        ctk.CTkLabel(
            self,
            text="Destinations & mode de transfert",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(pady=(20, 10))

        ctk.CTkLabel(
            self,
            text="Définissez les dossiers de destination et le mode de transfert.",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        ).pack(pady=(0, 20))

        # Photo destination
        photo_frame = ctk.CTkFrame(self)
        photo_frame.pack(fill="x", padx=30, pady=(0, 10))

        ctk.CTkLabel(
            photo_frame,
            text="Destination des photos (.nef, .raw, .jpg, .cr2, …) :",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=15, pady=(10, 5))

        row_photo = ctk.CTkFrame(photo_frame, fg_color="transparent")
        row_photo.pack(fill="x", padx=15, pady=(0, 10))

        self.photo_var = ctk.StringVar()
        ctk.CTkEntry(row_photo, textvariable=self.photo_var, width=450).pack(
            side="left", fill="x", expand=True, padx=(0, 10)
        )
        ctk.CTkButton(
            row_photo, text="Parcourir…", command=self._browse_photo, width=120
        ).pack(side="right")

        # Video destination
        video_frame = ctk.CTkFrame(self)
        video_frame.pack(fill="x", padx=30, pady=(0, 10))

        ctk.CTkLabel(
            video_frame,
            text="Destination des vidéos (.mov, .mp4, .avi, …) :",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=15, pady=(10, 5))

        row_video = ctk.CTkFrame(video_frame, fg_color="transparent")
        row_video.pack(fill="x", padx=15, pady=(0, 10))

        self.video_var = ctk.StringVar()
        ctk.CTkEntry(row_video, textvariable=self.video_var, width=450).pack(
            side="left", fill="x", expand=True, padx=(0, 10)
        )
        ctk.CTkButton(
            row_video, text="Parcourir…", command=self._browse_video, width=120
        ).pack(side="right")

        # Transfer mode toggle
        mode_frame = ctk.CTkFrame(self)
        mode_frame.pack(fill="x", padx=30, pady=15)

        ctk.CTkLabel(
            mode_frame,
            text="Mode de transfert :",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=15, pady=(10, 5))

        self.mode_var = ctk.StringVar(value="copy")
        radio_row = ctk.CTkFrame(mode_frame, fg_color="transparent")
        radio_row.pack(padx=15, pady=(0, 10), anchor="w")

        ctk.CTkRadioButton(
            radio_row, text="Copier (les originaux restent sur la source)",
            variable=self.mode_var, value="copy",
        ).pack(side="left", padx=(0, 30))

        ctk.CTkRadioButton(
            radio_row, text="Déplacer (les originaux sont supprimés)",
            variable=self.mode_var, value="move",
        ).pack(side="left")

        # Validation feedback
        self.info_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=13), text_color="red"
        )
        self.info_label.pack(pady=5)

    def on_enter(self):
        if self.state.photo_dest:
            self.photo_var.set(self.state.photo_dest)
        if self.state.video_dest:
            self.video_var.set(self.state.video_dest)
        self.mode_var.set(self.state.transfer_mode)

    def _browse_photo(self):
        folder = filedialog.askdirectory(title="Destination des photos")
        if folder:
            self.photo_var.set(folder)

    def _browse_video(self):
        folder = filedialog.askdirectory(title="Destination des vidéos")
        if folder:
            self.video_var.set(folder)

    def validate(self) -> bool:
        photo = self.photo_var.get().strip()
        video = self.video_var.get().strip()

        if not photo or not Path(photo).is_dir():
            self.info_label.configure(
                text="⚠ Veuillez sélectionner un dossier de destination valide pour les photos."
            )
            return False
        if not video or not Path(video).is_dir():
            self.info_label.configure(
                text="⚠ Veuillez sélectionner un dossier de destination valide pour les vidéos."
            )
            return False

        self.info_label.configure(text="")
        self.state.photo_dest = photo
        self.state.video_dest = video
        self.state.transfer_mode = self.mode_var.get()
        return True
