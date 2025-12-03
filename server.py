import time
from typing import List


class Server:
    def __init__(self, server_id: int):
        self.server_id = server_id
        self.neighbors: List['Server'] = []  # Lista sąsiadów
        self.is_leader = False
        self.received_messages = []

    def connect_neighbor(self, other_server: 'Server'):
        """Tworzy połączenie (krawędź grafu) z innym serwerem."""
        if other_server not in self.neighbors:
            self.neighbors.append(other_server)
            # Dla grafu nieskierowanego, połącz też w drugą stronę:
            other_server.neighbors.append(self)

    def set_as_leader(self):
        """Ustawia ten serwer jako Lidera."""
        self.is_leader = True
        print(f"--- [INFO] Serwer {self.server_id} został wybrany na LIDERA ---")

    def broadcast_message(self, message: str):
        """Metoda dla Lidera do wysłania wiadomości do sąsiadów."""
        if not self.is_leader:
            print(f"[Błąd] Serwer {self.server_id} próbuje wysłać, ale nie jest liderem.")
            return

        print(f"\n[LIDER {self.server_id}] Rozpoczyna nadawanie wiadomości: '{message}'")

        # Symulacja wysyłania do wszystkich podłączonych sąsiadów
        for neighbor in self.neighbors:
            print(f"  -> Wysyłanie pakietu do Serwera {neighbor.server_id}...")
            # Symulacja opóźnienia sieci
            time.sleep(0.5)
            neighbor.receive_packet(message, sender_id=self.server_id)

    def receive_packet(self, data: str, sender_id: int):
        """Odbiera wiadomość i loguje zdarzenie."""
        print(f"    [Serwer {self.server_id}] Odebrano dane od Serwera {sender_id}: '{data}'")
        self.received_messages.append(data)

        # Tutaj w przyszłości dodamy logikę dekodowania Reeda-Solomona
        self.process_data(data)

    def process_data(self, data: str):
        """Placeholder na logikę przetwarzania danych (dekodowanie)."""
        # Na razie tylko potwierdzenie odbioru
        print(f"    [Serwer {self.server_id}] Przetwarzanie zakończone sukcesem.")