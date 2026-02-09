"""Step 4: Execute the transfer with progress feedback."""

import threading

import customtkinter as ctk

from src.transfer import execute_transfer


class StepTransfer(ctk.CTkFrame):
    def __init__(self, parent, state):
        super().__init__(parent, fg_color="transparent")
        self.state = state
        self._running = False

        # Title
        ctk.CTkLabel(
            self, text="Transfert", font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 10))

        # Summary before transfer
        self.summary_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=14), wraplength=600
        )
        self.summary_label.pack(pady=(0, 15))

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self, width=500)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)

        # Progress text
        self.progress_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=13), text_color="gray"
        )
        self.progress_label.pack(pady=5)

        # Current file
        self.file_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=12), text_color="gray"
        )
        self.file_label.pack(pady=2)

        # Start button
        self.btn_start = ctk.CTkButton(
            self, text="Lancer le transfert", command=self._start_transfer, width=200,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.btn_start.pack(pady=20)

        # Result area
        self.result_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=14), wraplength=600
        )
        self.result_label.pack(pady=10)

    def on_enter(self):
        """Build summary when entering this step."""
        total_files = sum(len(g.files) for g in self.state.groups)
        n_groups = len(self.state.groups)
        mode_text = "Copie" if self.state.transfer_mode == "copy" else "Déplacement"

        self.summary_label.configure(
            text=(
                f"{n_groups} groupe(s), {total_files} fichier(s) à transférer.\n"
                f"Mode : {mode_text}\n"
                f"Photos → {self.state.photo_dest}\n"
                f"Vidéos → {self.state.video_dest}"
            )
        )
        self.progress_bar.set(0)
        self.progress_label.configure(text="")
        self.file_label.configure(text="")
        self.result_label.configure(text="")
        self.btn_start.configure(state="normal")
        self._running = False

    def _start_transfer(self):
        if self._running:
            return
        self._running = True
        self.btn_start.configure(state="disabled")
        self.result_label.configure(text="")
        threading.Thread(target=self._run_transfer, daemon=True).start()

    def _run_transfer(self):
        def callback(current: int, total: int, filename: str):
            progress = current / total if total > 0 else 1.0
            self.after(0, lambda: self._update_progress(current, total, filename, progress))

        result = execute_transfer(
            groups=self.state.groups,
            photo_dest=self.state.photo_dest,
            video_dest=self.state.video_dest,
            mode=self.state.transfer_mode,
            callback=callback,
        )

        self.after(0, lambda: self._on_complete(result))

    def _update_progress(self, current: int, total: int, filename: str, progress: float):
        self.progress_bar.set(progress)
        self.progress_label.configure(text=f"{current} / {total} fichier(s)")
        self.file_label.configure(text=filename)

    def _on_complete(self, result: dict):
        self._running = False
        transferred = result["transferred"]
        errors = result["errors"]

        if errors:
            error_lines = "\n".join(f"  • {name}: {err}" for name, err in errors[:10])
            extra = f"\n  … et {len(errors) - 10} autres." if len(errors) > 10 else ""
            self.result_label.configure(
                text=(
                    f"Transfert terminé : {transferred} fichier(s) transféré(s), "
                    f"{len(errors)} erreur(s).\n\nErreurs :\n{error_lines}{extra}"
                ),
                text_color="orange",
            )
        else:
            self.result_label.configure(
                text=f"✔ Transfert terminé avec succès ! {transferred} fichier(s) transféré(s).",
                text_color="#2FA572",
            )

        self.progress_bar.set(1.0)
        self.progress_label.configure(text="Terminé")
        self.file_label.configure(text="")
