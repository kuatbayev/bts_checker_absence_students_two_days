#!/usr/bin/env python3
"""Styled GUI for comparing BTS day files."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from compare_bts import build_outputs, load_records, write_lines


COLORS = {
    "bg": "#f4f7fb",
    "card": "#ffffff",
    "text": "#1e2a38",
    "muted": "#5b6b7f",
    "accent": "#0a7a6a",
    "accent_dark": "#075d51",
    "line": "#d9e3ee",
}

FONT_FAMILY = "Roboto"


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("BTS Нәтиже Салыстыру")
        self.geometry("920x430")
        self.minsize(820, 380)
        self.configure(bg=COLORS["bg"])

        self.day1_var = tk.StringVar(value="БТС1.txt")
        self.day2_var = tk.StringVar(value="БТС2.txt")
        self.status_var = tk.StringVar(value="Дайын")

        self._setup_styles()
        self._build_ui()

    def _setup_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("App.TFrame", background=COLORS["bg"])
        style.configure("Card.TFrame", background=COLORS["card"], relief="solid", borderwidth=1)
        style.configure(
            "Title.TLabel",
            background=COLORS["bg"],
            foreground=COLORS["text"],
            font=(FONT_FAMILY, 17, "bold"),
        )
        style.configure(
            "Body.TLabel",
            background=COLORS["card"],
            foreground=COLORS["text"],
            font=(FONT_FAMILY, 10),
        )
        style.configure(
            "Hint.TLabel",
            background=COLORS["card"],
            foreground=COLORS["muted"],
            font=(FONT_FAMILY, 9),
        )
        style.configure(
            "Status.TLabel",
            background=COLORS["card"],
            foreground="#0b5b17",
            font=(FONT_FAMILY, 10, "bold"),
        )
        style.configure(
            "Path.TEntry",
            fieldbackground="#fbfdff",
            foreground=COLORS["text"],
            bordercolor=COLORS["line"],
            lightcolor=COLORS["line"],
            darkcolor=COLORS["line"],
            padding=6,
        )
        style.configure(
            "Neutral.TButton",
            font=(FONT_FAMILY, 10),
            padding=(12, 7),
            background="#eef3f8",
            foreground=COLORS["text"],
        )
        style.map("Neutral.TButton", background=[("active", "#e3edf7")])

        style.configure(
            "Accent.TButton",
            font=(FONT_FAMILY, 10, "bold"),
            padding=(18, 9),
            background=COLORS["accent"],
            foreground="white",
            borderwidth=0,
        )
        style.map(
            "Accent.TButton",
            background=[("active", COLORS["accent_dark"]), ("pressed", COLORS["accent_dark"])],
        )

    def _build_ui(self) -> None:
        root = ttk.Frame(self, style="App.TFrame")
        root.pack(fill="both", expand=True, padx=20, pady=18)

        self._build_banner(root)
        self._build_card(root)

    def _build_banner(self, parent: ttk.Frame) -> None:
        banner = tk.Canvas(parent, height=90, bd=0, highlightthickness=0, bg=COLORS["bg"])
        banner.pack(fill="x")

        width = 900
        for i in range(width):
            ratio = i / width
            r = int(10 + ratio * 22)
            g = int(122 + ratio * 30)
            b = int(106 + ratio * 26)
            banner.create_line(i, 12, i, 88, fill=f"#{r:02x}{g:02x}{b:02x}")

        banner.create_text(
            24,
            36,
            text="BTS Нәтиже Салыстыру",
            fill="white",
            anchor="w",
            font=(FONT_FAMILY, 18, "bold"),
        )
        banner.create_text(
            24,
            63,
            text="Екі күндік TXT енгізіңіз, жүйе нәтижені автоматты шығарады",
            fill="#e8f6f3",
            anchor="w",
            font=(FONT_FAMILY, 10),
        )

    def _build_card(self, parent: ttk.Frame) -> None:
        card = ttk.Frame(parent, style="Card.TFrame", padding=18)
        card.pack(fill="both", expand=True, pady=(12, 0))

        ttk.Label(card, text="Файлдарды таңдаңыз", style="Title.TLabel").grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 10)
        )
        ttk.Label(
            card,
            text="Тек 2 TXT керек. Нәтиже файлдары 1-күн файлының папкасына сақталады.",
            style="Hint.TLabel",
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 14))

        self._add_file_row(card, row=2, label_text="1-күн TXT", var=self.day1_var)
        self._add_file_row(card, row=3, label_text="2-күн TXT", var=self.day2_var)

        actions = ttk.Frame(card, style="Card.TFrame")
        actions.grid(row=4, column=0, columnspan=3, sticky="w", pady=(14, 4))

        ttk.Button(actions, text="Салыстыруды бастау", style="Accent.TButton", command=self.run_compare).pack(
            side="left"
        )

        ttk.Label(card, textvariable=self.status_var, style="Status.TLabel").grid(
            row=5, column=0, columnspan=3, sticky="w", pady=(14, 4)
        )

        card.columnconfigure(1, weight=1)

    def _add_file_row(self, parent: ttk.Frame, row: int, label_text: str, var: tk.StringVar) -> None:
        ttk.Label(parent, text=label_text, style="Body.TLabel").grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=6
        )
        ttk.Entry(parent, textvariable=var, style="Path.TEntry").grid(
            row=row, column=1, sticky="ew", pady=6
        )
        ttk.Button(
            parent,
            text="Таңдау...",
            style="Neutral.TButton",
            command=lambda v=var: self.pick_input(v),
        ).grid(row=row, column=2, sticky="e", padx=(10, 0), pady=6)

    def pick_input(self, target_var: tk.StringVar) -> None:
        path = filedialog.askopenfilename(
            title="TXT файл таңдаңыз",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if path:
            target_var.set(path)

    def run_compare(self) -> None:
        day1_path = Path(self.day1_var.get().strip())
        day2_path = Path(self.day2_var.get().strip())
        out_dir = day1_path.parent if day1_path.parent.exists() else Path.cwd()
        both_out_path = out_dir / "eki_kunde_katyskandar.txt"
        one_day_out_path = out_dir / "bir_kun_katyskandar.txt"

        if not day1_path.exists() or not day2_path.exists():
            messagebox.showerror("Қате", "1-күн немесе 2-күн TXT файлы табылмады.")
            return

        try:
            day1_records, day1_skipped = load_records(day1_path)
            day2_records, day2_skipped = load_records(day2_path)

            both_lines, one_day_lines = build_outputs(day1_records, day2_records)
            write_lines(both_out_path, both_lines)
            write_lines(one_day_out_path, one_day_lines)

            both_count = len(set(day1_records) & set(day2_records))
            one_day_count = len(set(day1_records) ^ set(day2_records))
            skipped_count = len(day1_skipped) + len(day2_skipped)

            self.status_var.set(
                f"Дайын: екі күн={both_count}, бір күн={one_day_count}, өткізіліп кеткені={skipped_count}"
            )
            messagebox.showinfo(
                "Аяқталды",
                (
                    f"Екі күн қатысқан: {both_count}\n"
                    f"Бір күн ғана қатысқан: {one_day_count}\n"
                    f"Сақталды:\n{both_out_path}\n{one_day_out_path}"
                ),
            )
        except Exception as exc:
            messagebox.showerror("Қате", f"Өңдеу кезінде қате шықты:\n{exc}")


if __name__ == "__main__":
    App().mainloop()
