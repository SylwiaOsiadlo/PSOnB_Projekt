from server import Server
import time


def main():
    print("=== SYMULACJA: KOREKCJA BŁĘDÓW REEDA-SOLOMONA (RS 7,3) ===\n")

    # 1. Konfiguracja sieci
    servers = [Server(i) for i in range(4)]
    s0, s1, s2, s3 = servers

    s0.connect_neighbor(s1)
    s0.connect_neighbor(s2)
    s0.connect_neighbor(s3)
    s1.connect_neighbor(s2)  # Dodatkowa krawędź

    leader = s0
    leader.set_as_leader()

    # --- SCENARIUSZ 1: Transmisja bez błędów ---
    print("\n--- TEST 1: Transmisja idealna ---")
    msg_clean = [1, 2, 3]
    leader.broadcast_message(msg_clean)
    # Nie podajemy simulation_error_target, więc domyślnie jest brak błędu

    time.sleep(1)

    # --- SCENARIUSZ 2: Wprowadzenie błędu (Wymaganie projektowe) ---
    print("\n--- TEST 2: Symulacja uszkodzenia symbolu ---")
    msg_danger = [7, 0, 7]

    # Tutaj decydujemy: "Uszkodź wiadomość dla Serwera nr 3"
    target_victim = 3
    print(f"(Celujemy w Serwer {target_victim})")

    leader.broadcast_message(msg_danger, simulation_error_target=target_victim)

    print("\n=== KONIEC SYMULACJI ===")


if __name__ == "__main__":
    main()