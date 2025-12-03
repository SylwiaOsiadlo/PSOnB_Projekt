# Nazwa pliku: server.py
import time
from typing import List, Callable, Optional
from rs_codec import RSCoder


class Server:
    def __init__(self, server_id: int, log_callback: Optional[Callable] = None):
        self.server_id = server_id
        self.neighbors: List['Server'] = []
        self.is_leader = False
        self.rs = RSCoder()
        # Funkcja do wysyłania tekstu do GUI (jeśli brak, używa zwykłego print)
        self.log = log_callback if log_callback else print

    def connect_neighbor(self, other_server: 'Server'):
        if other_server not in self.neighbors:
            self.neighbors.append(other_server)
            other_server.neighbors.append(self)

    def set_as_leader(self):
        self.is_leader = True
        self.log(f"[INFO] Serwer {self.server_id} przejął rolę LIDERA.")

    def broadcast_message(self, message_data: List[int], simulation_error_target: int = -1):
        if not self.is_leader: return

        self.log(f"\n--- START TRANSMISJI ---")
        self.log(f"[LIDER {self.server_id}] Wysyła wiadomość: {message_data}")

        encoded_packet = self.rs.encode(message_data)
        self.log(f"[LIDER {self.server_id}] Zakodowano RS(7,3): {encoded_packet}")

        for neighbor in self.neighbors:
            time.sleep(0.5)  # Opóźnienie dla efektu wizualnego

            packet_to_send = list(encoded_packet)

            # Symulacja błędu
            if neighbor.server_id == simulation_error_target:
                self.log(f"   [ATAK] Uszkadzanie pakietu dla Serwera {neighbor.server_id}!")
                original_val = packet_to_send[0]
                packet_to_send[0] = (original_val + 1) % 8
                self.log(f"   [ATAK] Zmieniono: {original_val} -> {packet_to_send[0]}")

            self.log(f"   -> Wysłano do Serwera {neighbor.server_id}: {packet_to_send}")
            neighbor.receive_packet(packet_to_send, sender_id=self.server_id)

    def receive_packet(self, encoded_data: list, sender_id: int):
        self.log(f"       [Serwer {self.server_id}] Odebrano: {encoded_data}")

        decoded_data = self.rs.decode(encoded_data)

        # Weryfikacja czy nastąpiła naprawa
        re_encoded = self.rs.encode(decoded_data) if decoded_data else []

        if decoded_data is None:
            self.log(f"       [Serwer {self.server_id}] BLAD_KRYTYCZNY: Nie udało się naprawić.")
        elif re_encoded != encoded_data:
            self.log(f"       [Serwer {self.server_id}] KOREKCJA: Naprawiono błędy! Wynik: {decoded_data}")
        else:
            self.log(f"       [Serwer {self.server_id}] PAKIET_OK: Pakiet poprawny: {decoded_data}")