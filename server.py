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

    def broadcast_message(self, text_message: str):
        if not self.is_leader:
            return

        print(f"\n[LIDER {self.server_id}] Chce wysłać: '{text_message}'")

        # Dane wejściowe (symulacja)
        data_packet = [1, 3, 7]
        print(f"[LIDER {self.server_id}] Dane do zakodowania (k=3): {data_packet}")

        # Kodowanie
        encoded_packet = self.rs.encode(data_packet)
        print(f"[LIDER {self.server_id}] Wiadomość zakodowana (n=7): {encoded_packet}")

        # Wysyłanie do sąsiadów
        for neighbor in self.neighbors:
            print(f"  -> Wysyłanie pakietu do Serwera {neighbor.server_id}...")
            time.sleep(0.5)

            # Tworzymy kopię wiadomości do wysłania
            packet_to_send = list(encoded_packet)

            # --- SYMULACJA BŁĘDU ---
            # Celowo psujemy wiadomość tylko dla Serwera nr 1 (żeby pokazać różnicę)
            if neighbor.server_id == 1:
                print(f"     [!!!] Wstrzykiwanie błędu transmisji do Serwera {neighbor.server_id}!")
                # Zmieniamy pierwszą wartość z '1' na '5' (błąd!)
                packet_to_send[0] = 5
                print(f"     [!!!] Wysłano uszkodzony pakiet: {packet_to_send}")

            neighbor.receive_packet(packet_to_send, sender_id=self.server_id)

    def receive_packet(self, encoded_data: list, sender_id: int):
        print(f"    [Serwer {self.server_id}] Odebrano surowe dane: {encoded_data}")

        # 4. DEKODOWANIE I KOREKCJA
        decoded_data = self.rs.decode(encoded_data)

        print(f"    [Serwer {self.server_id}] Po dekodowaniu RS: {decoded_data}")
        self.process_data(decoded_data)

    def process_data(self, data):
        # Sprawdzenie czy to to, co wysłaliśmy ([1, 3, 7])
        if data == [1, 3, 7]:
            print(f"    [Serwer {self.server_id}] Sukces! Wiadomość poprawna.")
        else:
            print(f"    [Serwer {self.server_id}] Porażka! Dane uszkodzone.")