"""Step 3: Scan source, display dates, let user create named groups."""

import io
import threading
from datetime import date

import customtkinter as ctk
from PIL import Image

from src.scanner import (
    FileInfo,
    Group,
    count_for_date,
    scan_directory,
)


THUMB_SIZE = (64, 64)


def _load_thumbnail(files: list[FileInfo]) -> ctk.CTkImage | None:
    """Try to generate a thumbnail from the first photo in the list."""
    for f in files:
        if f.file_type == "photo" and f.path.suffix.lower() in (".jpg", ".jpeg"):
            try:
                img = Image.open(f.path)
                img.thumbnail(THUMB_SIZE)
                return ctk.CTkImage(light_image=img, dark_image=img, size=THUMB_SIZE)
            except Exception:
                continue
    return None


class StepGrouping(ctk.CTkFrame):
    def __init__(self, parent, state):
        super().__init__(parent, fg_color="transparent")
        self.state = state
        self.check_vars: dict[date, ctk.BooleanVar] = {}
        self.date_rows: dict[date, ctk.CTkFrame] = {}

        # Title
        ctk.CTkLabel(
            self,
            text="Regroupement par date",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(pady=(10, 5))

        self.status_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=13), text_color="gray"
        )
        self.status_label.pack(pady=(0, 5))

        # Groups display area (top)
        self.groups_frame = ctk.CTkFrame(self)
        self.groups_frame.pack(fill="x", padx=15, pady=(0, 5))
        ctk.CTkLabel(
            self.groups_frame,
            text="Groupes créés :",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(anchor="w", padx=10, pady=(5, 2))
        self.groups_list_frame = ctk.CTkFrame(self.groups_frame, fg_color="transparent")
        self.groups_list_frame.pack(fill="x", padx=10, pady=(0, 5))

        # Action bar
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(fill="x", padx=15, pady=5)

        self.name_entry = ctk.CTkEntry(
            action_frame, placeholder_text="Nom du groupe (ex: Mariage_Julie)", width=300
        )
        self.name_entry.pack(side="left", padx=(0, 10))

        self.btn_create_group = ctk.CTkButton(
            action_frame, text="Créer un groupe", command=self._create_group, width=150
        )
        self.btn_create_group.pack(side="left")

        self.group_error_label = ctk.CTkLabel(
            action_frame, text="", font=ctk.CTkFont(size=12), text_color="red"
        )
        self.group_error_label.pack(side="left", padx=10)

        # Scrollable date list
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Dates détectées")
        self.scroll_frame.pack(fill="both", expand=True, padx=15, pady=(5, 5))

        # Info at bottom
        self.bottom_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=13), text_color="#2FA572"
        )
        self.bottom_label.pack(pady=(0, 5))

    def on_enter(self):
        """Called when this step becomes visible — trigger scan."""
        self.status_label.configure(text="Scan en cours…", text_color="gray")
        self.state.groups.clear()
        self._refresh_groups_display()
        # Run scan in background thread
        threading.Thread(target=self._scan, daemon=True).start()

    def _scan(self):
        files_by_date = scan_directory(self.state.source_path)
        self.state.files_by_date = files_by_date
        self.after(0, lambda: self._populate_dates(files_by_date))

    def _populate_dates(self, files_by_date: dict[date, list[FileInfo]]):
        # Clear previous
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.check_vars.clear()
        self.date_rows.clear()

        sorted_dates = sorted(files_by_date.keys())
        total_files = sum(len(v) for v in files_by_date.values())
        self.status_label.configure(
            text=f"{len(sorted_dates)} date(s), {total_files} fichier(s) détecté(s).",
            text_color="#2FA572",
        )

        for d in sorted_dates:
            files = files_by_date[d]
            photos, videos = count_for_date(files)
            var = ctk.BooleanVar(value=False)
            self.check_vars[d] = var

            row = ctk.CTkFrame(self.scroll_frame)
            row.pack(fill="x", pady=2)
            self.date_rows[d] = row

            ctk.CTkCheckBox(row, text="", variable=var, width=30).pack(
                side="left", padx=(5, 0)
            )

            # Thumbnail
            thumb = _load_thumbnail(files)
            if thumb:
                ctk.CTkLabel(row, image=thumb, text="").pack(side="left", padx=5)

            info_text = f"{d.strftime('%Y-%m-%d')}   —   {photos} photo(s), {videos} vidéo(s)"
            ctk.CTkLabel(row, text=info_text, font=ctk.CTkFont(size=13)).pack(
                side="left", padx=10
            )

        self._update_bottom_label()

    def _create_group(self):
        name = self.name_entry.get().strip()
        if not name:
            self.group_error_label.configure(text="Entrez un nom de groupe.")
            return

        selected_dates = [d for d, var in self.check_vars.items() if var.get()]
        if not selected_dates:
            self.group_error_label.configure(text="Cochez au moins une date.")
            return

        self.group_error_label.configure(text="")

        # Gather files for selected dates
        group_files: list[FileInfo] = []
        for d in selected_dates:
            group_files.extend(self.state.files_by_date[d])

        group = Group(name=name, dates=sorted(selected_dates), files=group_files)
        self.state.groups.append(group)

        # Remove selected dates from UI and tracking
        for d in selected_dates:
            row = self.date_rows.pop(d, None)
            if row:
                row.destroy()
            self.check_vars.pop(d, None)
            self.state.files_by_date.pop(d, None)

        self.name_entry.delete(0, "end")
        self._refresh_groups_display()
        self._update_bottom_label()

    def _refresh_groups_display(self):
        for widget in self.groups_list_frame.winfo_children():
            widget.destroy()

        if not self.state.groups:
            ctk.CTkLabel(
                self.groups_list_frame, text="Aucun groupe.", text_color="gray"
            ).pack(anchor="w")
            return

        for i, group in enumerate(self.state.groups):
            date_str = group.first_date.strftime("%Y/%m/%d")
            folder_name = f"{group.first_date.strftime('%d')}_{group.name}"
            n_files = len(group.files)
            dates_count = len(group.dates)

            row = ctk.CTkFrame(self.groups_list_frame, fg_color="transparent")
            row.pack(fill="x", pady=1)

            text = (
                f"📂  {date_str[0:4]}/{date_str[5:7]}/{folder_name}"
                f"   ({dates_count} date(s), {n_files} fichier(s))"
            )
            ctk.CTkLabel(row, text=text, font=ctk.CTkFont(size=13)).pack(
                side="left", padx=5
            )

            ctk.CTkButton(
                row,
                text="✕",
                width=30,
                fg_color="transparent",
                hover_color=("gray80", "gray30"),
                text_color="red",
                command=lambda idx=i: self._remove_group(idx),
            ).pack(side="right")

    def _remove_group(self, index: int):
        group = self.state.groups.pop(index)
        # Restore dates back to files_by_date and UI
        for d in group.dates:
            matching = [f for f in group.files if f.date == d]
            self.state.files_by_date[d] = matching
        # Re-populate the dates list
        self._populate_dates(self.state.files_by_date)
        self._refresh_groups_display()

    def _update_bottom_label(self):
        remaining = len(self.check_vars)
        if remaining == 0 and self.state.groups:
            self.bottom_label.configure(
                text="✔ Toutes les dates sont regroupées. Vous pouvez continuer.",
                text_color="#2FA572",
            )
        elif remaining > 0:
            self.bottom_label.configure(
                text=f"{remaining} date(s) restante(s) à regrouper.",
                text_color="gray",
            )
        else:
            self.bottom_label.configure(text="")

    def validate(self) -> bool:
        if self.check_vars:
            self.bottom_label.configure(
                text="⚠ Regroupez toutes les dates avant de continuer.", text_color="red"
            )
            return False
        if not self.state.groups:
            self.bottom_label.configure(
                text="⚠ Aucun groupe créé.", text_color="red"
            )
            return False
        return True
