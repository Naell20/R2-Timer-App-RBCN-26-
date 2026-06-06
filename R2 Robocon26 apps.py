import tkinter as tk
from tkinter import messagebox
import pygame
import os


class RoboconTimerApp:

    def __init__(self, root):

        self.root = root
        self.root.title("R2 Timer & Scoring Latihan Robocon 2026")
        self.root.geometry("1100x850") # Diperlebar agar 2 Meihua Forest muat
        self.root.configure(bg="#2c3e50")

        # TRY MODE
        self.try_mode = False

        # DATA ASSEMBLY
        self.assembly_time = []
        self.last_assembly_time = 0

        # AUDIO
        pygame.mixer.init()

        self.sound_file = "warning.wav"

        if os.path.exists(self.sound_file):
            self.warning_sound = pygame.mixer.Sound(self.sound_file)
        else:
            self.warning_sound = None
            print(f"Peringatan: File {self.sound_file} tidak ditemukan.")

        # STATE
        self.setup_time = 60
        self.match_time = 180

        self.current_time = self.setup_time

        self.is_running = False
        self.phase = "Persiapan"

        self.score = 0

        # BLOK R2 dan R1
        self.block_buttons_r2 = {}
        self.block_states_r2 = {}
        
        self.block_buttons_r1 = {}
        self.block_states_r1 = {}

        # UI
        self.setup_ui()

        # Pickup Staff
        self.staff_pikup_time = None

    # AUDIO ALERT
    def play_alert(self):

        if self.warning_sound:
            self.warning_sound.play()
        else:
            self.root.bell()

    # FORMAT TIME
    def format_time(self, seconds):

        mins = seconds // 60
        secs = seconds % 60

        return f"{mins:02d}:{secs:02d}"

    # ADD LOG
    def add_log(self, text):

        self.log_list.insert(tk.END, text)
        self.log_list.yview(tk.END)

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

        # TIMER
        self.timer_label = tk.Label(
            self.root,
            text=self.format_time(self.current_time),
            font=("Helvetica", 60, "bold"),
            bg="#2c3e50",
            fg="white"
        )

        self.timer_label.pack(pady=10)

        # CONTROL FRAME
        control_frame = tk.Frame(self.root, bg="#2c3e50")
        control_frame.pack(pady=10)

        # START
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

        # PAUSE
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

        # MATCH
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

        # RESET TIMER
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

        # TRY MODE
        self.try_btn = tk.Button(
            control_frame,
            text="Mode Try",
            font=("Helvetica", 11, "bold"),
            command=self.start_try_mode,
            width=12,
            bg="#8e44ad",
            fg="white"
        )

        self.try_btn.grid(row=0, column=4, padx=5)

        # SCORE
        self.score_label = tk.Label(
            self.root,
            text=f"Skor: {self.score}",
            font=("Helvetica", 40, "bold"),
            bg="#2c3e50",
            fg="#3498db"
        )

        self.score_label.pack(pady=15)

        # MAIN FRAME
        main_frame = tk.Frame(self.root, bg="#2c3e50")
        main_frame.pack(pady=10)

        # SCORE FRAME
        score_frame = tk.Frame(main_frame, bg="#2c3e50")
        score_frame.pack(side=tk.LEFT, padx=20, anchor="n")

        buttons = [
            ("Pickup Staff", 0),
            ("Pickup Weapon", 0),
            ("Weapon Assembly", 10),
            ("KFS Masuk Arena", 10),
            ("Tic-Tac-Toe Bawah", 30),
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

        # ARENA FRAME CONTAINER (Untuk membungkus R2 dan R1 bersebelahan)
        arena_container = tk.Frame(main_frame, bg="#2c3e50")
        arena_container.pack(side=tk.LEFT, padx=20, anchor="n")

        # ================= MEIHUA FOREST R2 =================
        arena_frame_r2 = tk.Frame(arena_container, bg="#2c3e50")
        arena_frame_r2.pack(side=tk.LEFT, padx=15, anchor="n")

        block_title_r2 = tk.Label(
            arena_frame_r2,
            text="Meihua Forest R2",
            font=("Helvetica", 13, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        block_title_r2.pack(pady=5)

        reset_MF_btn_r2 = tk.Button(
            arena_frame_r2,
            text="Reset Blok R2",
            font=("Helvetica", 10, "bold"),
            bg="#7f8c8d",
            fg="white",
            command=lambda: self.reset_blocks("R2")
        )
        reset_MF_btn_r2.pack(pady=8)

        self.block_frame_r2 = tk.Frame(arena_frame_r2, bg="#2c3e50")
        self.block_frame_r2.pack()

        for row in range(4):
            for col in range(3):
                block_number = row * 3 + col + 1

                btn_r2 = tk.Button(
                    self.block_frame_r2,
                    text=f"{block_number}",
                    width=6,
                    height=3,
                    bg="#27ae60",
                    fg="white",
                    font=("Helvetica", 9, "bold"),
                    command=lambda b=block_number: self.toggle_block(b, "R2")
                )

                btn_r2.grid(row=row, column=col, padx=3, pady=3)
                self.block_buttons_r2[block_number] = btn_r2


        # ================= MEIHUA FOREST R1 =================
        arena_frame_r1 = tk.Frame(arena_container, bg="#2c3e50")
        arena_frame_r1.pack(side=tk.LEFT, padx=15, anchor="n")

        block_title_r1 = tk.Label(
            arena_frame_r1,
            text="Meihua Forest R1",
            font=("Helvetica", 13, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        block_title_r1.pack(pady=5)

        reset_MF_btn_r1 = tk.Button(
            arena_frame_r1,
            text="Reset Blok R1",
            font=("Helvetica", 10, "bold"),
            bg="#7f8c8d",
            fg="white",
            command=lambda: self.reset_blocks("R1")
        )
        reset_MF_btn_r1.pack(pady=8)

        self.block_frame_r1 = tk.Frame(arena_frame_r1, bg="#2c3e50")
        self.block_frame_r1.pack()

        for row in range(4):
            for col in range(3):
                block_number = row * 3 + col + 1
                
                # Melewatkan blok 5 dan 8 untuk R1
                if block_number in [5, 8]:
                    continue

                btn_r1 = tk.Button(
                    self.block_frame_r1,
                    text=f"{block_number}",
                    width=6,
                    height=3,
                    bg="#27ae60",
                    fg="white",
                    font=("Helvetica", 9, "bold"),
                    command=lambda b=block_number: self.toggle_block(b, "R1")
                )

                btn_r1.grid(row=row, column=col, padx=3, pady=3)
                self.block_buttons_r1[block_number] = btn_r1


        # Control Frame Log Reset Button
        final_frame = tk.Frame(self.root, bg="#2c3e50")
        final_frame.pack(pady=10)

        # KFM
        kf_master_btn = tk.Button(
            final_frame,
            text="KUNG FU MASTER (Menang!)",
            font=("Helvetica", 12, "bold"),
            bg="#9b59b6",
            fg="white",
            command=self.kung_fu_master,
            width=22
        )

        kf_master_btn.grid(row=0, column=0, padx=10)

        # LOG
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

        # SCROLLBAR VERTIKAL
        self.scrollbar_y = tk.Scrollbar(log_frame)

        self.scrollbar_y.pack(
            side=tk.RIGHT,
            fill=tk.Y
        )

        # LISTBOX LOG
        self.log_list = tk.Listbox(
            log_frame,
            yscrollcommand=self.scrollbar_y.set,
            font=("Consolas", 11),
            bg="#ecf0f1",
            fg="#2c3e50",
            height=20
        )

        self.log_list.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True
        )

        self.scrollbar_y.config(command=self.log_list.yview)

        # RESET SCORE & LOG
        reset_score_btn = tk.Button(
            final_frame,
            text="Reset Skor & Log",
            font=("Helvetica", 10),
            command=self.reset_score,
            bg="#7f8c8d",
            fg="white",
            width=18
        )
        reset_score_btn.grid(row=0, column=1, padx=10)


    # TIMER NORMAL
    def update_timer(self):

        if self.is_running and self.current_time > 0:

            self.current_time -= 1

            self.timer_label.config(
                text=self.format_time(self.current_time)
            )

            if self.current_time <= 10 and self.current_time > 0:

                self.timer_label.config(fg="#e74c3c")
                self.play_alert()

            else:

                self.timer_label.config(fg="white")

            self.root.after(1000, self.update_timer)

        elif self.is_running and self.current_time == 0:

            self.is_running = False

            self.play_alert()

            if self.phase == "Persiapan":

                messagebox.showinfo(
                    "Persiapan Selesai",
                    "Waktu persiapan habis."
                )

            else:

                # HITUNG RATA-RATA ASSEMBLY
                if len(self.assembly_time) > 0:

                    avg = (
                        sum(self.assembly_time)
                        / len(self.assembly_time)
                    )

                    avg_text = self.format_time(int(avg))

                    # TAMPILKAN SEMUA DATA
                    assembly_data = ", ".join(
                        [
                            self.format_time(t)
                            for t in self.assembly_time
                        ]
                    )

                else:

                    avg_text = "00:00"
                    assembly_data = "Tidak ada data"

                # LOG HASIL AKHIR
                self.add_log(
                    f"[PERTANDINGAN SELESAI] "
                    f"TOTAL POINT: {self.score}"
                )

                self.add_log(
                    f"[PERTANDINGAN SELESAI] "
                    f"DATA ASSEMBLY: {assembly_data}"
                )

                self.add_log(
                    f"[PERTANDINGAN SELESAI] "
                    f"RATA-RATA ASSEMBLY: {avg_text}"
                )

                # POPUP
                messagebox.showinfo(
                    "Waktu Habis",
                    f"Pertandingan selesai!"
                    f"\nSkor: {self.score}"
                    f"\n\nData Assembly:"
                    f"\n{assembly_data}"
                    f"\n\nRata-rata Assembly:"
                    f"\n{avg_text}"
                )


    # TRY TIMER
    def update_try_timer(self):

        if self.is_running and self.try_mode:

            self.current_time += 1

            self.timer_label.config(
                text=self.format_time(self.current_time)
            )

            self.root.after(1000, self.update_try_timer)

    # START
    def start_timer(self):

        if not self.is_running:

            self.is_running = True

            if self.try_mode:
                self.update_try_timer()
            else:
                self.update_timer()

    # PAUSE
    def pause_timer(self):

        self.is_running = False

    # TRY MODE
    def start_try_mode(self):

        self.is_running = False

        self.try_mode = True

        self.phase = "TRY MODE"

        self.current_time = 0

        self.phase_label.config(
            text="Fase: TRY MODE",
            fg="#9b59b6"
        )

        self.timer_label.config(
            text=self.format_time(self.current_time),
            fg="white"
        )

        self.add_log("--- TRY MODE DIMULAI ---")

    # FASE PERTANDINGAN
    def to_match_phase(self):

        self.is_running = False

        self.try_mode = False

        # RESET DATA ASSEMBLY
        self.assembly_time.clear()
        self.last_assembly_time = 0

        # RESET SKOR
        self.score = 0

        self.score_label.config(
            text=f"Skor: {self.score}"
        )

        # RESET BLOK R2
        self.block_states_r2.clear()
        for i, btn in self.block_buttons_r2.items():
            btn.config(bg="#27ae60", fg="white", text=f"{i}")

        # RESET BLOK R1
        self.block_states_r1.clear()
        for i, btn in self.block_buttons_r1.items():
            btn.config(bg="#27ae60", fg="white", text=f"{i}")

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

        self.add_log("--- PERTANDINGAN DIMULAI ---")

    # RESET TIMER
    def reset_timer(self):

        self.is_running = False

        self.try_mode = False

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

        # SIMPAN DATA ASSEMBLY
        if action_name == "Weapon Assembly" and self.phase == "Pertandingan":

            elapsed_match_time = (
                self.match_time - self.current_time
            )

            assembly_duration = (
                elapsed_match_time - self.last_assembly_time
            )

            self.assembly_time.append(
                assembly_duration
            )

            self.last_assembly_time = (
                elapsed_match_time
            )

        # ELAPSED TIME
        if self.try_mode:
            elapsed_secs = self.current_time

        elif self.phase == "Persiapan":
            elapsed_secs = self.setup_time - self.current_time

        else:
            elapsed_secs = self.match_time - self.current_time

        elapsed_str = self.format_time(elapsed_secs)

        if points == 0:
            point_text = " (time recorded only)"
        else:
            point_text = f" (+{points})"

        log_text = (
            f"[{self.phase} - {elapsed_str}] "
            f"{action_name}{point_text}"
        )

        self.add_log(log_text)

    # TOGGLE BLOCK (Dinamis untuk R2 maupun R1)
    def toggle_block(self, block_number, robot):

        if robot == "R2":
            btn = self.block_buttons_r2[block_number]
            current_state = self.block_states_r2.get(block_number, 0)
        else:
            btn = self.block_buttons_r1[block_number]
            current_state = self.block_states_r1.get(block_number, 0)

        elapsed_str = self.format_time(self.current_time)

        # BIRU
        if current_state == 0:

            btn.config(
                bg="#2980b9",
                fg="white",
                text=f"{block_number}\n{elapsed_str}"
            )

            if robot == "R2":
                self.block_states_r2[block_number] = 1
            else:
                self.block_states_r1[block_number] = 1

            log_text = (
                f"[{self.phase}] "
                f"Blok MF {robot} - {block_number} diambil"
            )

        # MERAH
        elif current_state == 1:

            btn.config(
                bg="#e74c3c",
                fg="white",
                text=f"{block_number}\n{elapsed_str}"
            )

            if robot == "R2":
                self.block_states_r2[block_number] = 2
            else:
                self.block_states_r1[block_number] = 2

            log_text = (
                f"[{self.phase}] "
                f"Blok MF {robot} - {block_number} gagal"
            )

        # BIRU LAGI
        else:

            btn.config(
                bg="#2980b9",
                fg="white",
                text=f"{block_number}\n{elapsed_str}"
            )

            if robot == "R2":
                self.block_states_r2[block_number] = 3
            else:
                self.block_states_r1[block_number] = 3

            log_text = (
                f"[{self.phase}] "
                f"Blok MF {robot} - {block_number} diambil lagi"
            )

        self.add_log(log_text)

    # RESET BLOK (Bisa reset R2 atau R1 secara terpisah)
    def reset_blocks(self, robot):

        if robot == "R2":
            self.block_states_r2.clear()
            for i, btn in self.block_buttons_r2.items():
                btn.config(bg="#27ae60", fg="white", text=f"{i}")
            self.add_log(f"[{self.phase}] Semua blok R2 di-reset")
            
        else:
            self.block_states_r1.clear()
            for i, btn in self.block_buttons_r1.items():
                btn.config(bg="#27ae60", fg="white", text=f"{i}")
            self.add_log(f"[{self.phase}] Semua blok R1 di-reset")

    # RESET SCORE (Secara keseluruhan)
    def reset_score(self):

        self.score = 0

        self.score_label.config(
            text=f"Skor: {self.score}"
        )

        self.log_list.delete(0, tk.END)

        self.assembly_time.clear()
        self.last_assembly_time = 0

        # Reset blok R2
        self.block_states_r2.clear()
        for i, btn in self.block_buttons_r2.items():
            btn.config(bg="#27ae60", fg="white", text=f"{i}")
            
        # Reset blok R1
        self.block_states_r1.clear()
        for i, btn in self.block_buttons_r1.items():
            btn.config(bg="#27ae60", fg="white", text=f"{i}")


    # KUNG FU MASTER
    def kung_fu_master(self):

        self.is_running = False

        elapsed_str = self.format_time(self.current_time)

        self.add_log(
            f"[{self.phase}] *** KUNG FU MASTER ***"
        )

        messagebox.showinfo(
            "KUNG FU MASTER!",
            f"Robot berhasil mencapai\n"
            f"Kung Fu Master pada {elapsed_str}"
        )


# MAIN
if __name__ == "__main__":

    root = tk.Tk()

    app = RoboconTimerApp(root)

    root.mainloop()