# Server game

A simple local multiplayer turn based game.

## How to run this project

To test the game locally, you have to open three seperate terminals and follow the instructions

### Step 1: Run Server Lobby (Terminal 1)

This procesmust have been runing in the background
```bash
python server_lobby.py
```

### Step 2: Join a game as Player 1(Terminal 2)
```bash
python client.py
```
*Write name of a hero and value of attack that has to be between 1-100 and wait for the second player*

### Step 3: Join a game as Player 2 (Terminal 3)
```bash
python client.py
```
*If you write player 2 name and health you will be instantly connected to the arena.*

---
