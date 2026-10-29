
"""AirOS - Visual Control Panel"""

import subprocess
import sys
import tkinter as tk
from tkinter import messagebox


class AirOSControlPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("AirOS Control Center")
        self.root.geometry("620x520")
        self.root.configure(bg="#101827")
        self.root.resizable(False, False)

        self.process = None

        tk.Label(
            root, text="AirOS", font=("Segoe UI", 30, "bold"),
            bg="#101827", fg="#55E6C1"
        ).pack(pady=(24, 0))

        tk.Label(
            root, text="AI Gesture-Controlled Desktop",
            font=("Segoe UI", 12), bg="#101827", fg="#B8C4D9"
        ).pack(pady=(0, 18))

        self.status_label = tk.Label(
            root, text="● STOPPED", font=("Segoe UI", 15, "bold"),
            bg="#101827", fg="#FF7777"
        )
        self.status_label.pack(pady=8)

        buttons = tk.Frame(root, bg="#101827")
        buttons.pack(pady=18)

        self.start_button = tk.Button(
            buttons, text="▶  START AirOS", width=18,
            font=("Segoe UI", 12, "bold"),
            bg="#55E6C1", fg="#101827",
            activebackground="#38CBA8",
            command=self.start_airos, relief="flat", pady=10
        )
        self.start_button.grid(row=0, column=0, padx=8)

        self.stop_button = tk.Button(
            buttons, text="■  STOP AirOS", width=18,
            font=("Segoe UI", 12, "bold"),
            bg="#FF7777", fg="#101827",
            activebackground="#E65C5C",
            command=self.stop_airos, relief="flat", pady=10,
            state="disabled"
        )
        self.stop_button.grid(row=0, column=1, padx=8)

        tk.Label(
            root, text="GESTURE CONTROLS",
            font=("Segoe UI", 13, "bold"),
            bg="#101827", fg="#55E6C1"
        ).pack(pady=(18, 8))

        instructions = (
            "INDEX FINGER     Move the mouse pointer\n"
            "LITTLE FINGER    Left-click once when raised\n"
            "LOWER FINGER     Re-arm the next click\n"
            "P KEY            Pause / resume mouse control\n"
            "Q KEY            Close the webcam window"
        )

        tk.Label(
            root, text=instructions, justify="left",
            font=("Consolas", 11), bg="#1B2638",
            fg="#E3EAF5", padx=22, pady=18
        ).pack(padx=28, fill="x")

        tk.Label(
            root,
            text="Safety: Mouse control starts PAUSED.\n"
                 "Test gestures carefully and keep Q available to quit.",
            font=("Segoe UI", 9), bg="#101827",
            fg="#B8C4D9", justify="center"
        ).pack(pady=18)

        self.root.protocol("WM_DELETE_WINDOW", self.close_panel)
        self.root.after(500, self.check_process)

    def start_airos(self):
        if self.process is not None and self.process.poll() is None:
            return

        try:
            self.process = subprocess.Popen(
                [sys.executable, "-m", "airos"]
            )
            self.status_label.config(
                text="● STARTING", fg="#FFD166"
            )
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
        except Exception as error:
            messagebox.showerror(
                "Could not start AirOS", str(error)
            )

    def stop_airos(self):
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()

        self.process = None
        self.status_label.config(text="● STOPPED", fg="#FF7777")
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")

    def check_process(self):
        if self.process is not None:
            if self.process.poll() is None:
                self.status_label.config(
                    text="● RUNNING", fg="#55E6C1"
                )
            else:
                self.process = None
                self.status_label.config(
                    text="● STOPPED", fg="#FF7777"
                )
                self.start_button.config(state="normal")
                self.stop_button.config(state="disabled")

        self.root.after(500, self.check_process)

    def close_panel(self):
        if self.process is not None and self.process.poll() is None:
            if not messagebox.askyesno(
                "Exit AirOS", "Stop AirOS and close the control panel?"
            ):
                return
            self.stop_airos()

        self.root.destroy()


if __name__ == "__main__":
    window = tk.Tk()
    app = AirOSControlPanel(window)
    window.mainloop()
