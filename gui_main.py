# Nazwa pliku: gui_main.py
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from server import Server

class RSSimulationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Projekt: Korekcja błędów Reeda-Solomona")
        self.root.geometry("800x500")

        # --- SEKCJA GÓRNA: STEROWANIE ---
        control_frame = ttk.LabelFrame(root, text="Panel Sterowania")
        control_frame.pack(fill="x", padx=10, pady=5)

        # 1. Wybór wiadomości (Rząd 0)
        ttk.Label(control_frame, text="Wiadomość (3 liczby 0-7):").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.msg_entry = ttk.Entry(control_frame)
        self.msg_entry.insert(0, "1 2 3")
        self.msg_entry.grid(row=0, column=1, padx=5, pady=5)

        # 2. Wybór ofiary ataku (Rząd 0)
        ttk.Label(control_frame, text="Cel ataku (błąd):").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.target_var = tk.StringVar(value="Brak")
        target_options = ["Brak", "Serwer 1", "Serwer 2", "Serwer 3"]
        self.target_menu = ttk.OptionMenu(control_frame, self.target_var, "Brak", *target_options)
        self.target_menu.grid(row=0, column=3, padx=5, pady=5)

        # 3. Wybór typu błędu
        ttk.Label(control_frame, text="Rodzaj błędu:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.error_type_var = tk.StringVar(value="1. Symbol Flip (1 błąd)")
        # Opcje wymagane przez projekt:
        error_type_options = [
            "1. Symbol Flip (1 błąd)",
            "2. Burst (2 błędy, test limitu)",
            "3. Deletion (Usunięcie symbolu)"
        ]
        self.error_type_menu = ttk.OptionMenu(control_frame, self.error_type_var, error_type_options[0], *error_type_options)
        self.error_type_menu.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky='ew')

        # Przycisk start (Rząd 1, po prawej)
        self.start_btn = ttk.Button(control_frame, text="URUCHOM SYMULACJĘ", command=self.start_simulation_thread)
        self.start_btn.grid(row=1, column=3, columnspan=2, padx=20, pady=5, sticky='ew')

        # --- SEKCJA ŚRODKOWA: WIZUALIZACJA ---
        viz_frame = ttk.LabelFrame(root, text="Status Sieci")
        viz_frame.pack(fill="x", padx=10, pady=5)

        # Prosta wizualizacja 4 serwerów jako etykiety
        self.server_labels = {}
        colors = ["#FFD700", "#ADD8E6", "#ADD8E6", "#ADD8E6"]
        names = ["LIDER (S0)", "Serwer 1", "Serwer 2", "Serwer 3"]

        for i in range(4):
            lbl = tk.Label(viz_frame, text=names[i], bg=colors[i], width=20, height=3, relief="raised")
            lbl.pack(side="left", expand=True, padx=5, pady=10)
            self.server_labels[i] = lbl

        # --- SEKCJA DOLNA: LOGI ---
        log_frame = ttk.LabelFrame(root, text="Logi Transmisji")
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.log_area = scrolledtext.ScrolledText(log_frame, state='disabled', height=15)
        self.log_area.pack(fill="both", expand=True, padx=5, pady=5)

        # Konfiguracja kolorów w logach
        self.log_area.tag_config("INFO", foreground="blue")
        self.log_area.tag_config("ERROR", foreground="red")
        self.log_area.tag_config("SUCCESS", foreground="green")
        self.log_area.tag_config("WARN", foreground="orange")

    def log_message(self, text):
        """Metoda dodająca tekst do okna logów (bezpieczna dla wątków)."""
        self.log_area.config(state='normal')

        # Kolorowanie składni na podstawie treści
        tag = "black"
        if "LIDER" in text: tag = "INFO"
        if "KOREKCJA" in text: tag = "WARN"
        if "PAKIET_OK" in text: tag = "SUCCESS"
        if "BLAD_KRYTYCZNY" in text or "ATAK" in text: tag = "ERROR"

        self.log_area.insert(tk.END, text + "\n", tag)
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def start_simulation_thread(self):
        self.start_btn.config(state="disabled")
        threading.Thread(target=self.run_simulation, daemon=True).start()

    def run_simulation(self):
        try:
            # 1. Pobranie danych z GUI
            msg_str = self.msg_entry.get()
            try:
                message = [int(x) for x in msg_str.split()]
                if len(message) != 3: raise ValueError
            except:
                self.log_message("Błąd: Wiadomość musi składać się z 3 liczb oddzielonych spacją (np. 1 2 3)")
                self.root.after(0, lambda: self.start_btn.config(state="normal"))
                return

            target_str = self.target_var.get()
            error_target = -1
            if target_str == "Serwer 1": error_target = 1
            if target_str == "Serwer 2": error_target = 2
            if target_str == "Serwer 3": error_target = 3

            # Pobranie typu błędu z menu
            error_type = self.error_type_var.get()

            # 2. Inicjalizacja sieci
            self.log_message("-" * 40)
            self.log_message(f"Start symulacji... Wiadomość: {message}")
            self.log_message(f"Konfiguracja: Cel={target_str}, Typ={error_type}")

            servers = [Server(i, log_callback=self.log_message) for i in range(4)]
            s0, s1, s2, s3 = servers
            s0.connect_neighbor(s1)
            s0.connect_neighbor(s2)
            s0.connect_neighbor(s3)

            leader = s0
            leader.set_as_leader()

            # 3. Transmisja - przekazujemy teraz error_type!
            leader.broadcast_message(
                message,
                simulation_error_target=error_target,
                error_type=error_type
            )

            self.log_message("Symulacja zakończona.")

        except Exception as e:
            self.log_message(f"Wystąpił niespodziewany błąd: {e}")
        finally:
            self.root.after(0, lambda: self.start_btn.config(state="normal"))

if __name__ == "__main__":
    root = tk.Tk()
    app = RSSimulationApp(root)
    root.mainloop()