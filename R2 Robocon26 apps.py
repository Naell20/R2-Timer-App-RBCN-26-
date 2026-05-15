import tkinter as tk
from tkinter import messagebox
import pygame
import os

class RoboconTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Timer & Scoring Latihan Robocon 2026")
        self.root.geometry("950x850")
        self.root.configure(bg="#2c3e50")

        # Inisialisasi Audio
        pygame.mixer.init()

        self.sound_file = "warning.wav"

        if os.path.exists(self.sound_file):
            self.warning_sound = pygame.mixer.Sound(self.sound_file)
        else:
            self.warning_sound = None
            print(f"Peringatan: File {self.sound_file} tidak ditemukan.")

        # State Variable
        self.setup_time = 60
        self.match_time = 180

        self.current_time = self.setup_time

        self.is_running = False
        self.phase = "Persiapan"

        self.score = 0

        # Penyimpanan tombol blok MF
        self.block_buttons = []

        # Status blok (1 klik hijau, 2x klik merah brti kfs gagal di ambil/ sudah diambil tapi jatuh)
        self.block_states = {}

        # Setup UI
        self.setup_ui()

    # AUDIO ALERT
    def play_alert(self):

        if self.warning_sound:
            self.warning_sound.play()
        else:
            self.root.bell()

    # UI
    def setup_ui(self):

        # HEADER
        self.phase_label = tk.Label(
            self.root,
            text="Fase: Persiapan",
            font=("Helvetica", 20, "bold"),
            bg="#2c3e50",
            fg="#f1c40f"
        )

        self.phase_label.pack(pady=15)

        # TIMER DISPLAY
        self.timer_label = tk.Label(
            self.root,
            text=self.format_time(self.current_time),
            font=("Helvetica", 60, "bold"),
            bg="#2c3e50",
            fg="white"
        )

        self.timer_label.pack(pady=10)

        # CONTROL BUTTON
        control_frame = tk.Frame(self.root, bg="#2c3e50")
        control_frame.pack(pady=10)

        self.start_btn = tk.Button(
            control_frame,
            text="Mulai / Lanjut",
            font=("Helvetica", 11),
            command=self.start_timer,
            width=12,
            bg="#27ae60",
            fg="white"
        )

        self.start_btn.grid(row=0, column=0, padx=5)

        self.pause_btn = tk.Button(
            control_frame,
            text="Jeda",
            font=("Helvetica", 11),
            command=self.pause_timer,
            width=12,
            bg="#e67e22",
            fg="white"
        )

        self.pause_btn.grid(row=0, column=1, padx=5)

        self.next_btn = tk.Button(
            control_frame,
            text="Masuk Pertandingan",
            font=("Helvetica", 11, "bold"),
            command=self.to_match_phase,
            width=18,
            bg="#3498db",
            fg="white"
        )

        self.next_btn.grid(row=0, column=2, padx=5)

        self.reset_btn = tk.Button(
            control_frame,
            text="Reset Waktu",
            font=("Helvetica", 11),
            command=self.reset_timer,
            width=12,
            bg="#c0392b",
            fg="white"
        )

        self.reset_btn.grid(row=0, column=3, padx=5)

        # SCORE DISPLAY
        self.score_label = tk.Label(
            self.root,
            text=f"Skor: {self.score}",
            font=("Helvetica", 40, "bold"),
            bg="#2c3e50",
            fg="#3498db"
        )

        self.score_label.pack(pady=15)

        # MAIN CONTENT FRAME
        main_frame = tk.Frame(self.root, bg="#2c3e50")
        main_frame.pack(pady=10)

        # FRAME KIRI = SCORING
        score_frame = tk.Frame(main_frame, bg="#2c3e50")
        score_frame.pack(side=tk.LEFT, padx=20, anchor="n")

        buttons = [
            ("Pickup Senjata", 0),
            ("Weapon Assembly", 10),
            ("KFS Masuk Arena", 10),
            ("Tic-Tac-Toe Tengah", 40),
            ("Tic-Tac-Toe Atas", 80)
        ]

        for i, (action_name, points) in enumerate(buttons):

            if points > 0:
                btn_text = f"{action_name} (+{points})"
            else:
                btn_text = action_name

            btn = tk.Button(
                score_frame,
                text=btn_text,
                font=("Helvetica", 11),
                width=24,
                command=lambda p=points, act=action_name:
                self.add_score(p, act)
            )

            btn.grid(row=i, column=0, pady=5)

        # FRAME KANAN = ARENA BLOK MF
        arena_frame = tk.Frame(main_frame, bg="#2c3e50")
        arena_frame.pack(side=tk.LEFT, padx=20, anchor="n")

        block_title = tk.Label(
            arena_frame,
            text="Arena Blok",
            font=("Helvetica", 13, "bold"),
            bg="#2c3e50",
            fg="white"
        )

        block_title.pack(pady=5)

        self.block_frame = tk.Frame(arena_frame, bg="#2c3e50")
        self.block_frame.pack()

        # BLOK MF
        for row in range(4): # pnjang ke blkng
            for col in range(3): # lebr ke smping

                block_number = row * 3 + col + 1

                btn = tk.Button(
                    self.block_frame,
                    text=f"{block_number}",
                    width=6,
                    height=3,
                    bg="#27ae60",
                    fg="white",
                    font=("Helvetica", 9, "bold"),
                    command=lambda b=block_number:
                    self.toggle_block(b)
                )

                btn.grid(
                    row=row,
                    column=col,
                    padx=3,
                    pady=3
                )

                self.block_buttons.append(btn)

        # KUNG FU MASTER BUTTON
        kf_master_btn = tk.Button(
            self.root,
            text="KUNG FU MASTER (Menang!)",
            font=("Helvetica", 12, "bold"),
            bg="#9b59b6",
            fg="white",
            command=self.kung_fu_master
        )

        kf_master_btn.pack(pady=10)

        # LOG HISTORY
        log_label = tk.Label(
            self.root,
            text="Log Poin & Waktu:",
            font=("Helvetica", 12),
            bg="#2c3e50",
            fg="white"
        )

        log_label.pack(anchor="w", padx=30)

        log_frame = tk.Frame(self.root)
        log_frame.pack(
            pady=5,
            padx=30,
            fill=tk.BOTH,
            expand=True
        )

        self.scrollbar = tk.Scrollbar(log_frame)

        self.scrollbar.pack(
            side=tk.RIGHT,
            fill=tk.Y
        )

        self.log_list = tk.Listbox(
            log_frame,
            yscrollcommand=self.scrollbar.set,
            font=("Consolas", 11),
            bg="#ecf0f1",
            fg="#2c3e50",
            height=8
        )

        self.log_list.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True
        )

        self.scrollbar.config(command=self.log_list.yview)

        # RESET SCORE BUTTON
        reset_score_btn = tk.Button(
            self.root,
            text="Reset Skor & Log",
            font=("Helvetica", 10),
            command=self.reset_score,
            bg="#7f8c8d",
            fg="white"
        )

        reset_score_btn.pack(pady=10)

    # FORMAT TIME
    def format_time(self, seconds):

        mins = seconds // 60
        secs = seconds % 60

        return f"{mins:02d}:{secs:02d}"

    # UPDATE TIMER
    def update_timer(self):

        if self.is_running and self.current_time > 0:

            self.current_time -= 1

            self.timer_label.config(
                text=self.format_time(self.current_time)
            )

            # Warning 10 detik terakhir
            if self.current_time <= 10 and self.current_time > 0:

                self.timer_label.config(fg="#e74c3c")
                self.play_alert()

            else:
                self.timer_label.config(fg="white")

            self.root.after(1000, self.update_timer)

        elif self.is_running and self.current_time == 0:

            self.is_running = False

            self.timer_label.config(fg="white")

            self.play_alert()

            if self.phase == "Persiapan":

                messagebox.showinfo(
                    "Persiapan Selesai",
                    "Waktu persiapan habis.\nTekan 'Masuk Pertandingan'."
                )

                self.log_list.insert(
                    tk.END,
                    "--- WAKTU PERSIAPAN HABIS ---"
                )

            else:

                messagebox.showinfo(
                    "Waktu Habis",
                    f"Pertandingan selesai!\nSkor Akhir: {self.score}"
                )

                self.log_list.insert(
                    tk.END,
                    f"--- PERTANDINGAN SELESAI | Skor: {self.score} ---"
                )

            self.log_list.yview(tk.END)

    # START TIMER
    def start_timer(self):

        if not self.is_running and self.current_time > 0:

            self.is_running = True
            self.update_timer()

    # PAUSE TIMER
    def pause_timer(self):

        self.is_running = False

    # MATCH PHASE
    def to_match_phase(self):

        self.is_running = False

        self.phase = "Pertandingan"

        self.phase_label.config(
            text="Fase: Pertandingan",
            fg="#e74c3c"
        )

        self.current_time = self.match_time

        self.timer_label.config(
            text=self.format_time(self.current_time),
            fg="white"
        )

        self.log_list.insert(
            tk.END,
            "--- FASE PERTANDINGAN DISIAPKAN ---"
        )

        self.log_list.yview(tk.END)

    # RESET TIMER
    def reset_timer(self):

        self.is_running = False

        self.phase = "Persiapan"

        self.phase_label.config(
            text="Fase: Persiapan",
            fg="#f1c40f"
        )

        self.current_time = self.setup_time

        self.timer_label.config(
            text=self.format_time(self.current_time),
            fg="white"
        )

    # ADD SCORE
    def add_score(self, points, action_name):

        self.score += points

        self.score_label.config(
            text=f"Skor: {self.score}"
        )

        if self.phase == "Persiapan":
            elapsed_secs = self.setup_time - self.current_time
        else:
            elapsed_secs = self.match_time - self.current_time

        elapsed_str = self.format_time(elapsed_secs)

        point_text = f" (+{points})" if points > 0 else ""

        log_text = (
            f"[{self.phase} - {elapsed_str}] "
            f"{action_name}{point_text}"
        )

        self.log_list.insert(tk.END, log_text)
        self.log_list.yview(tk.END)

    # TOGGLE BLOCK
    def toggle_block(self, block_number):

        btn = self.block_buttons[block_number - 1]

        current_state = self.block_states.get(block_number, 0)

        if self.phase == "Persiapan":
            elapsed_secs = self.setup_time - self.current_time
        else:
            elapsed_secs = self.match_time - self.current_time

        elapsed_str = self.format_time(elapsed_secs)

        # Klik pertama -> BIRU
        if current_state == 0:

            btn.config(
                bg="#2980b9",
                fg="white",
                text=f"{block_number}\n{elapsed_str}"
            )

            self.block_states[block_number] = 1

            log_text = (
                f"[{self.phase} - {elapsed_str}] "
                f"Blok MF {block_number} KFS diambil"
            )

        # Klik kedua -> MERAH
        elif current_state == 1:

            btn.config(
                bg="#e74c3c",
                fg="white",
                text=f"{block_number}\n{elapsed_str}"
            )

            self.block_states[block_number] = 2

            log_text = (
                f"[{self.phase} - {elapsed_str}] "
                f"Blok MF {block_number} KFS gagal diambil / jatuh"
            )

        # # Klik berikutnya 
        # else:

        #     btn.config(
        #         text=f"{block_number}\n{elapsed_str}"
        #     )

        #     log_text = (
        #         f"[{self.phase} - {elapsed_str}] "
        #         f"Blok MF {block_number} ditekan lagi"
        #     )

        self.log_list.insert(tk.END, log_text)
        self.log_list.yview(tk.END)

    # RESET SCORE
    def reset_score(self):

        self.score = 0

        self.score_label.config(
            text=f"Skor: {self.score}"
        )

        self.log_list.delete(0, tk.END)

        # Reset status blok
        self.block_states.clear()

        # Reset blok
        for i, btn in enumerate(self.block_buttons):

            btn.config(
                bg="#27ae60",
                fg="white",
                text=f"{i+1}"
            )

    # KUNG FU MASTER
    def kung_fu_master(self):

        self.is_running = False

        self.timer_label.config(fg="white")

        elapsed_secs = self.match_time - self.current_time

        elapsed_str = self.format_time(elapsed_secs)

        self.log_list.insert(
            tk.END,
            f"[{self.phase} - {elapsed_str}] "
            f"*** KUNG FU MASTER ***"
        )

        self.log_list.yview(tk.END)

        messagebox.showinfo(
            "KUNG FU MASTER!",
            f"Robot berhasil mencapai "
            f"Kung Fu Master pada {elapsed_str}!"
        )

# MAIN
if __name__ == "__main__":

    root = tk.Tk()

    app = RoboconTimerApp(root)

    root.mainloop()