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

    def broadcast_message(self, message_data: List[int]):
        """
        Lider koduje podaną wiadomość i rozsyła do sąsiadów.
        message_data: lista liczb z zakresu 0-7 (dla RS 7,3)
        """
        if not self.is_leader:
            print(f"[Błąd] Serwer {self.server_id} nie jest liderem.")
            return

        print(f"\n[LIDER {self.server_id}] Otrzymał zlecenie wysłania: {message_data}")

        # 1. Kodowanie wiadomości (używamy naszej klasy RS)
        # Wynik to np. [1, 3, 7, x, y, z, q]
        encoded_packet = self.rs.encode(message_data)
        print(f"[LIDER {self.server_id}] Zakodowano (dodano nadmiarowość): {encoded_packet}")

        # 2. Rozsyłanie do sąsiadów
        for neighbor in self.neighbors:
            print(f"  -> Transmisja do Serwera {neighbor.server_id}...")
            time.sleep(0.5)

            # Kopia pakietu do wysłania
            packet_to_send = list(encoded_packet)

            # --- SYMULACJA USZKODZEŃ ---
            # Tutaj nadal trzymamy nasz mechanizm psucia dla testów
            if neighbor.server_id == 1:
                print(f"     [!!!] AWARIA ŁĄCZA! Pakiet ulega uszkodzeniu w locie.")
                # Zmieniamy pierwszy bajt na losową inną wartość (np. 0)
                old_val = packet_to_send[0]
                packet_to_send[0] = (old_val + 1) % 8
                print(f"     [!!!] Zmieniono wartość {old_val} -> {packet_to_send[0]}")

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