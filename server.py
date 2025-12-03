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
        self.log = log_callback if log_callback else print

    def connect_neighbor(self, other_server: 'Server'):
        if other_server not in self.neighbors:
            self.neighbors.append(other_server)
            other_server.neighbors.append(self)

    def set_as_leader(self):
        self.is_leader = True
        self.log(f"[INFO] Serwer {self.server_id} przejął rolę LIDERA.")

    def broadcast_message(self, message_data: List[int], simulation_error_target: int = -1, error_type: str = "Brak"):
        if not self.is_leader: return

        self.log(f"\n--- START TRANSMISJI ---")
        self.log(f"[LIDER {self.server_id}] Wysyła wiadomość: {message_data}")

        encoded_packet = self.rs.encode(message_data)
        self.log(f"[LIDER {self.server_id}] Zakodowano RS(7,3): {encoded_packet}")

        for neighbor in self.neighbors:
            time.sleep(0.5)

            packet_to_send = list(encoded_packet)

            # --- DYNAMICZNA LOGIKA BŁĘDÓW ---
            if neighbor.server_id == simulation_error_target and error_type != "Brak":
                self.log(f"   [ATAK] Aktywowano symulację błędu typu: {error_type} dla Serwera {neighbor.server_id}!")

                # Typ 1: Symbol Flip (1 błąd)
                if error_type == "1. Symbol Flip (1 błąd)":
                    original_val = packet_to_send[0]
                    packet_to_send[0] = (original_val + 1) % 8
                    self.log(
                        f"   [ATAK] 1. Zmieniono wartość symbolu na pozycji 0: {original_val} -> {packet_to_send[0]}")

                # Typ 2: Burst (Błąd Zgrupowany - Test limitu korekcji)
                elif error_type == "2. Burst (2 błędy, test limitu)":
                    # Wprowadzamy 2 błędy (nasz limit korekcji RS(7,3) to t=2)
                    for i in range(2):
                        if i < len(packet_to_send):
                            original_val = packet_to_send[i]
                            packet_to_send[i] = (original_val + 1 + i) % 8
                            self.log(
                                f"   [ATAK] 2. Zmieniono symbol na pozycji {i}: {original_val} -> {packet_to_send[i]}")
                    self.log("   [ATAK] Wprowadzono 2 błędy zgrupowane. RS powinien to naprawić.")

                # Typ 3: Deletion (Błąd synchronizacji / usunięcie)
                elif error_type == "3. Deletion (Usunięcie symbolu)":
                    if len(packet_to_send) > 0:
                        packet_to_send.pop(0)  # Usuwamy pierwszy symbol
                        self.log("   [ATAK] 3. Usunięto symbol z początku pakietu. RS ZAWYŻYŁ numerację symboli!")
                        self.log("   [ATAK] Ostrzeżenie: RS bez dodatkowych mechanizmów nie jest odporny na usunięcia.")

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