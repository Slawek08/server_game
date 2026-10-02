import socket
import sys
import json
import threading
import random
from hero import Hero

PORT = int(sys.argv[1])
TOKEN_1 = sys.argv[2]
TOKEN_2 = sys.argv[3]
HERO1_JSON = sys.argv[4]
HERO2_JSON = sys.argv[5]

HOST = "0.0.0.0"

hero1 = Hero.from_json(HERO1_JSON)
hero2 = Hero.from_json(HERO2_JSON)



print(f"[BATTLE] Instance started on port {PORT}")
print(f"[BATTLE] Except fighters: {hero1.name} vs {hero2.name}")

expected_players = {
    TOKEN_1: {"conn": None, "hero": hero1, "name": hero1.name},
    TOKEN_2: {"conn": None, "hero": hero2, "name": hero2.name}
}

current_round_moves = {
    TOKEN_1: None,
    TOKEN_2: None
}

battle_lock = threading.Lock()

battle_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
battle_server.bind((HOST, PORT))
battle_server.listen()

print(f"[BATTLE] Waiting for 2 players to authenticate...")

def execute_round_logic(t1, t2, move1, move2):
    p1 = expected_players[t1]
    p2 = expected_players[t2]

    h1 = p1["hero"]
    h2 = p2["hero"]

    report = f"\n--- ROUND RESULTS ---\n"
    report += f"{h1.name}: {move1.upper()} | {h2.name}: {move2.upper()}\n"

    if move1 == "attack" and move2 == "attack":
        
        if h1.attack > h2.attack:
            diff = h1.attack - h2.attack
            h2.health -= diff
            report += f"{h1.name} broke through! {h2.name} takes {diff} DMG. \n"
        
        elif h2.attack > h1.attack:
            diff = h2.attack - h1.attack
            h1.health -= diff
            report += f"{h2.name} broke through! {h1.name} takes {diff} DMG\n"
        else:
            report += "Draw! Both attacks clashed. 0 DMG taken.\n"

    elif move1 == "dodge" and move2 == "dodge":
        h1.health -= 5
        h2.health -= 5
        report += "Both players dodged! -5HP each due to fatigue.\n"

    elif move1 == "attack" and move2 == "dodge":
        if random.randint(1,100) <= h2.dodge:
            report += f"{h2.name} successfully dodged {h1.name}'s attack\n"
        else:
            h2.health -= h1.attack
            report += f"{h2.name} failed to dodge! Takes full {h1.attack} DMG from{h1.name}.\n"

    elif move1 == "dodge" and move2 == "attack":
        if random.randint(1, 100) <= h1.dodge:
            report += f"{h1.name} successfully dodge {h2.name}'s attack!\n"
        else:
            h1.health -= h2.attack
            report += f"{h1.name} failed to dodge! Takes full {h2.attack} DMG from {h2.name}.\n"

    report += f"STATUS: {h1.name} ({h1.health} HP) | {h2.name} ({h2.health} HP)\n"

    game_over = False
    if h1.health <= 0 or h2.health <= 0:
        game_over = True
        report += "\n=== GAME OVER ===\n"
        if h1.health <= 0 and h2.health <= 0:
            report += "It's a tie! Both fell in battle.\n"
        elif h1.health <= 0:
            report += f"Winner: {h2.name}!\n"
        else:
            report += f"Winner: {h1.name}!\n"             

    p1["conn"].send(report.encode())
    p2["conn"].send(report.encode())

    if game_over:
        print("[BATTLE] Battle finished. Shuting down instance.")
        p1["conn"].close()
        p2["conn"].close()
        sys.exit(0)

    current_round_moves[t1] = None
    current_round_moves[t2] = None
    print("[BATTLE] Round processed. Moves reset for next round.")

def handle_battle_client(player_token):
    player_data = expected_players[player_token]
    conn = player_data["conn"]
    name = player_data["name"]

    print(f"[BATTLE] Thread started for player: {name}")

    while True:
        try:
            conn.send("CHOOSE_MOVE".encode())

            data = conn.recv(1024)
            if not data:
                break

            move = data.decode().strip().lower()

            with battle_lock:
                current_round_moves[player_token] = move
                print(f"[BATTLE] Player {name} chose: {move} (Hidden from opponent)")

                tokens = list(current_round_moves.keys())
                move1 = current_round_moves[tokens[0]]
                move2 = current_round_moves[tokens[1]]

                if move1 is not None and move2 is not None:
                    print("[BATTLE] Both players made a move! Calculating results...")

                    execute_round_logic(tokens[0], tokens[1], move1, move2)

        except Exception as e:
            print(f"[BATTLE] Error handling player {name}: {e}")
            break

    print(f"[BATTLE] Player {name} disconnected from battle instance.")
    conn.close()

authenticated_count = 0

while authenticated_count < 2:
    conn, addr = battle_server.accept()

    try:
        token_data = conn.recv(1024)
        received_token = token_data.decode().strip()

        if received_token in expected_players and expected_players[received_token]["conn"] is None:
            expected_players[received_token]["conn"] = conn
            authenticated_count += 1

            player_name = expected_players[received_token]["name"]
            print(f"[BATTLE] Player '{player_name}' authenticated successfully from {addr}!!!")

            conn.send("AUTH_OK".encode())

        else:
            print(f"[BATTLE] Unauthorized connection attempt from {addr}. Disconnecting.")    
            conn.send("AUTH_FAILED".encode())
            conn.close()
    
    except Exception as e:
        print(f"[BATTLE] Connection error during authentication: {e}")
        conn.close()

for token in expected_players.keys():
    thread = threading.Thread(target=handle_battle_client, args=(token,))
    thread.start()

print("[BATTLE] Both players connected! Starting battle threads...")

