import socket 
import json
import secrets
import subprocess
import threading
from hero import Hero

HOST = '0.0.0.0'
PORT = 8080
CURRENT_MATCH_PORT = 25000
queue_lock = threading.Lock()
queue = []

def gamer_service(conn, addr):
    print(f"Someone went to lobby: {addr}")
    try:
        bajt_data = conn.recv(2048)
        text_json = bajt_data.decode()

        hero = Hero.from_json(text_json)

        if hero.attack > 100 or hero.attack <= 0:
            print(f"Attack should be  between 1 and 100 !!!")
            conn.close()
            return

        print(f"Registration went succesfull:\n Hero name: {hero.name}\n attack: {hero.attack}")

        with queue_lock:
            queue.append({"connection": conn, "hero": hero})
            print(f"Added to queue. Current queue length: {len(queue)}")

            if len(queue) >= 2:
                player1 = queue.pop(0)
                player2 = queue.pop(0)

                global CURRENT_MATCH_PORT
                match_port = CURRENT_MATCH_PORT
                CURRENT_MATCH_PORT += 1

                token1 = secrets.token_hex(8)
                token2 = secrets.token_hex(8)

                print(f"Pair found! Creating match on port {match_port}")

                hero1_json = player1["hero"].to_json()
                hero2_json = player2["hero"].to_json()

                subprocess.Popen([
                    "python", "server_battle.py",
                    str(match_port),
                    token1, token2,
                    hero1_json, hero2_json
                ])
                
                msg_p1 = json.dumps({"port": match_port, "token": token1})
                player1["connection"].send(msg_p1.encode())
                player1["connection"].close()

                msg_p2 = json.dumps({"port": match_port, "token": token2})
                player2["connection"].send(msg_p2.encode())
                player2["connection"].close()
                print(f"Rddirected both players to port {match_port} and closed lobby connections")

    except Exception as e:
        print(f"Error {addr}: {e}")
        conn.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print(f"Lobby is running on port {PORT}...")

while True:
    conn, addr = server.accept()
    thread = threading.Thread(target=gamer_service, args=(conn, addr))
    thread.start()
