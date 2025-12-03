# Nazwa pliku: main.py
from server import Server


def main():
    print("=== SYMULACJA SIECI Z KOREKCJĄ BŁĘDÓW REEDA-SOLOMONA ===\n")

    # 1. Inicjalizacja serwerów
    servers = [Server(i) for i in range(4)]
    s0, s1, s2, s3 = servers

    # 2. Budowa topologii (Lider w centrum)
    s0.connect_neighbor(s1)
    s0.connect_neighbor(s2)
    s0.connect_neighbor(s3)
    # Opcjonalne połączenia między innymi
    s1.connect_neighbor(s2)

    # 3. Wybór lidera
    leader = s0
    leader.set_as_leader()

    # 4. PRZEBIEG TESTU
    # Definiujemy wiadomość. Pamiętaj: liczby 0-7 (bo RS 7,3 działa na 3 bitach)
    test_message = [5, 2, 7]

    print(f"\n--- Rozpoczęcie transmisji wiadomości: {test_message} ---")
    leader.broadcast_message(test_message)

    print("\n=== KONIEC SYMULACJI ===")


if __name__ == "__main__":
    main()