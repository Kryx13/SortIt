"""Main application window with step-based navigation."""

from datetime import date
from pathlib import Path

import customtkinter as ctk

from src.scanner import FileInfo, Group
from src.ui.step_source import StepSource
from src.ui.step_destination import StepDestination
from src.ui.step_grouping import StepGrouping
from src.ui.step_transfer import StepTransfer


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AppState:
    """Shared state across all steps."""

    def __init__(self):
        self.source_path: str = ""
        self.photo_dest: str = ""
        self.video_dest: str = ""
        self.transfer_mode: str = "copy"  # "copy" or "move"
        self.files_by_date: dict[date, list[FileInfo]] = {}
        self.groups: list[Group] = []


class SortItApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SortIt — Tri de photos & vidéos")
        self.geometry("850x620")
        self.minsize(750, 550)

        self.app_state = AppState()
        self.current_step = 0

        # --- Header with step indicators ---
        self.header_frame = ctk.CTkFrame(self, height=50, corner_radius=0)
        self.header_frame.pack(fill="x", padx=0, pady=0)

        self.step_labels: list[ctk.CTkLabel] = []
        step_names = ["1. Source", "2. Destinations", "3. Regroupement", "4. Transfert"]
        for i, name in enumerate(step_names):
            label = ctk.CTkLabel(
                self.header_frame,
                text=name,
                font=ctk.CTkFont(size=14, weight="bold" if i == 0 else "normal"),
                text_color="#3B8ED0" if i == 0 else "gray",
            )
            label.pack(side="left", expand=True, pady=10)
            self.step_labels.append(label)

        # --- Content area ---
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill="both", expand=True, padx=15, pady=(10, 5))

        # --- Bottom navigation ---
        self.nav_frame = ctk.CTkFrame(self, height=50, fg_color="transparent")
        self.nav_frame.pack(fill="x", padx=15, pady=(5, 15))

        self.btn_prev = ctk.CTkButton(
            self.nav_frame, text="← Précédent", command=self._go_prev, width=140
        )
        self.btn_prev.pack(side="left")

        self.btn_next = ctk.CTkButton(
            self.nav_frame, text="Suivant →", command=self._go_next, width=140
        )
        self.btn_next.pack(side="right")

        # --- Build steps ---
        self.steps: list[ctk.CTkFrame] = []
        self._build_steps()
        self._show_step(0)

    def _build_steps(self):
        self.steps = [
            StepSource(self.content_frame, self.app_state),
            StepDestination(self.content_frame, self.app_state),
            StepGrouping(self.content_frame, self.app_state),
            StepTransfer(self.content_frame, self.app_state),
        ]

    def _show_step(self, index: int):
        for step in self.steps:
            step.pack_forget()

        self.current_step = index
        step = self.steps[index]
        step.pack(fill="both", expand=True)

        if hasattr(step, "on_enter"):
            step.on_enter()

        # Update header highlighting
        for i, label in enumerate(self.step_labels):
            if i == index:
                label.configure(
                    font=ctk.CTkFont(size=14, weight="bold"), text_color="#3B8ED0"
                )
            elif i < index:
                label.configure(
                    font=ctk.CTkFont(size=14, weight="normal"), text_color="#2FA572"
                )
            else:
                label.configure(
                    font=ctk.CTkFont(size=14, weight="normal"), text_color="gray"
                )

        # Update nav buttons
        self.btn_prev.configure(state="normal" if index > 0 else "disabled")
        if index == len(self.steps) - 1:
            self.btn_next.configure(state="disabled")
        else:
            self.btn_next.configure(state="normal")

    def _go_prev(self):
        if self.current_step > 0:
            self._show_step(self.current_step - 1)

    def _go_next(self):
        step = self.steps[self.current_step]
        if hasattr(step, "validate") and not step.validate():
            return
        if self.current_step < len(self.steps) - 1:
            self._show_step(self.current_step + 1)
