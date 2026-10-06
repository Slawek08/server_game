import socket
import json
from hero import Hero

LOBBY_HOST = "127.0.0.1"
LOBBY_PORT = 8080

def run_client():
    print("=== WELCOME ===")
    name = input("Enter your Hero name: ")

    while True:
        try:
            attack = int(input("Enter attack value (1-100): "))
            if 1 <= attack <= 100:
                break
            print("Attack must be between 1 and 100!")
        except ValueError:
            print("Please enter a valid number.")
    
    my_hero = Hero(name=name, attack=attack)
    hero_json = my_hero.to_json()

    print(f"\nConnecting to Lobby on port {LOBBY_PORT}")
    lobby_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        lobby_sock.connect((LOBBY_HOST, LOBBY_PORT))
        lobby_sock.send(hero_json.encode())

        print("Character sent! Waiting for a opponent to join...")

        response_bytes = lobby_sock.recv(1024)
        if not response_bytes:
            print("Disconnected from lobby. Check if your stats were valid.")
            return

        match_data = json.loads(response_bytes.decode())
        match_port = match_data["port"]
        my_token = match_data["token"]

    except Exception as e:
        print(f"Lobby connection error: {e}")
        return
    finally:
        lobby_sock.close()

    print(f"\n[MATCHMAKER] Match found! Redirecting to port {match_port}...")

    battle_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        battle_sock.connect((LOBBY_HOST, match_port))
        battle_sock.send(my_token.encode())
    
        auth_status = battle_sock.recv(1024).decode()
        if auth_status != "AUTH_OK":
            print("[BATTLE] Authentication failed! Access denied.")
            battle_sock.close()
            return
        
        print("[BATTLE] Connected and verified! Waiting for the match to start...")

        while True:
            server_msg = battle_sock.recv(2048).decode()
            if not server_msg:
                print("\n[BATTLE] Server closed connection.")
                break

            if "CHOOSE_MOVE" in server_msg:
                while True:
                    move = input("Your move (attack / dodge): ").strip().lower()
                    if move in ["attack", "dodge"]:
                        break
                    print("Invalid move! Type 'attack' or 'dodge'.")

                battle_sock.send(move.encode())
                print("Move submitted. Waiting for opponent...")

            else:
                print(server_msg)

                if "=== GAME OVER ===" in server_msg:
                    print("Thank you for playing!")
                    break

    except Exception as e:
        print(f"Battle connection error: {e}")
    finally:
        battle_sock.close()

if __name__ == "__main__":
    run_client()
