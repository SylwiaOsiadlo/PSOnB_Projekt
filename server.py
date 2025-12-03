# Nazwa pliku: server.py
import time
from typing import List
from rs_codec import RSCoder  # <-- IMPORTUJEMY NASZ MODUŁ


class Server:
    def __init__(self, server_id: int):
        self.server_id = server_id
        self.neighbors: List['Server'] = []
        self.is_leader = False
        self.received_messages = []
        # Inicjalizacja kodeka Reeda-Solomona
        self.rs = RSCoder()

    def connect_neighbor(self, other_server: 'Server'):
        if other_server not in self.neighbors:
            self.neighbors.append(other_server)
            other_server.neighbors.append(self)

    def set_as_leader(self):
        self.is_leader = True
        print(f"--- [INFO] Serwer {self.server_id} został wybrany na LIDERA ---")

    def broadcast_message(self, message_data: List[int], simulation_error_target: int = -1):
        """
        message_data: lista danych do wysłania.
        simulation_error_target: ID serwera, który ma otrzymać uszkodzony pakiet (dla testów).
                                 Domyślnie -1 (brak błędów).
        """
        if not self.is_leader:
            return

        print(f"\n[LIDER {self.server_id}] Otrzymał zlecenie wysłania: {message_data}")

        # 1. Kodowanie
        encoded_packet = self.rs.encode(message_data)
        print(f"[LIDER {self.server_id}] Zakodowano: {encoded_packet}")

        # 2. Rozsyłanie
        for neighbor in self.neighbors:
            print(f"  -> Transmisja do Serwera {neighbor.server_id}...")
            time.sleep(0.5)

            packet_to_send = list(encoded_packet)

            # --- LOGIKA WPROWADZANIA BŁĘDU (DYNAMICZNA) ---
            # Sprawdzamy, czy ten sąsiad został wskazany jako cel ataku/błędu
            if neighbor.server_id == simulation_error_target:
                print(f"     [SYMULACJA] Celowe uszkodzenie symbolu dla Serwera {neighbor.server_id}!")

                # Typ błędu: Zmiana wartości jednego symbolu (Bit flip / Symbol corruption)
                # Zmieniamy pierwszy element na przeciwny w ciele GF(8) lub po prostu inny
                original = packet_to_send[0]
                packet_to_send[0] = (original + 1) % 8

                print(f"     [SYMULACJA] Zmieniono: {original} -> {packet_to_send[0]}")

            neighbor.receive_packet(packet_to_send, sender_id=self.server_id)

    def receive_packet(self, encoded_data: list, sender_id: int):
        print(f"    [Serwer {self.server_id}] Odebrano surowe dane: {encoded_data}")

        # 4. DEKODOWANIE I KOREKCJA
        decoded_data = self.rs.decode(encoded_data)

        print(f"    [Serwer {self.server_id}] Po dekodowaniu RS: {decoded_data}")
        self.process_data(decoded_data)

    def process_data(self, data):
        """Wyświetla ostateczny wynik po dekodowaniu."""
        # Nie porównujemy już ze "sztywnym" wzorcem, bo wiadomości są dynamiczne.
        print(f"    [Serwer {self.server_id}] ==> Odebrana wiadomość (finalna): {data}")