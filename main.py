# Nazwa pliku: main.py
from server import Server  # <-- Importujemy klasę Server z pliku server.py


def main():
    print("=== SYMULACJA SYSTEMU ROZPROSZONEGO (4 SERWERY) ===\n")

    # 1. Tworzenie 4 serwerów
    servers = [Server(i) for i in range(4)]

    # 2. Budowanie topologii grafu
    s0, s1, s2, s3 = servers

    # Lider (s0) połączony z resztą
    s0.connect_neighbor(s1)
    s0.connect_neighbor(s2)
    s0.connect_neighbor(s3)

    # Dodatkowe połączenie między s1 i s2
    s1.connect_neighbor(s2)

    # 3. Wybór lidera
    leader = s0
    leader.set_as_leader()

    # 4. Symulacja transmisji
    original_message = "Hello World"
    leader.broadcast_message(original_message)

    print("\n=== KONIEC SYMULACJI ===")


if __name__ == "__main__":
    main()