import tkinter as tk
from tkinter import messagebox, simpledialog
import random

# --- MONOPOLY BOARD SETUP ---
BOARD_SPACES = [
    "Go", "Mediterranean Avenue", "Community Chest", "Baltic Avenue", "Income Tax",
    "Reading Railroad", "Oriental Avenue", "Chance", "Vermont Avenue", "Connecticut Avenue",
    "Jail / Just Visiting", "St. Charles Place", "Electric Company", "States Avenue", "Virginia Avenue",
    "Pennsylvania Railroad", "St. James Place", "Community Chest", "Tennessee Avenue", "New York Avenue",
    "Free Parking", "Kentucky Avenue", "Chance", "Indiana Avenue", "Illinois Avenue",
    "B&O Railroad", "Atlantic Avenue", "Ventnor Avenue", "Water Works", "Marvin Gardens",
    "Go To Jail", "Pacific Avenue", "North Carolina Avenue", "Community Chest", "Pennsylvania Avenue",
    "Short Line Railroad", "Chance", "Park Place", "Luxury Tax", "Boardwalk"
]

COLORS = {
    "brown": [1, 3],
    "lightblue": [6, 8, 9],
    "pink": [11, 13, 14],
    "orange": [16, 18, 19],
    "red": [21, 23, 24],
    "yellow": [26, 27, 29],
    "green": [31, 32, 34],
    "cyan": [37, 39]
}

PROPERTY_PRICES = {i: random.randint(100, 400) for i in range(len(BOARD_SPACES))}
RENT_FACTOR = 0.2
OWNERSHIP = {i: None for i in range(len(BOARD_SPACES))}
HOUSES = {i: 0 for i in range(len(BOARD_SPACES))}

CHANCE_CARDS = [
    ("Advance to Go", lambda p, app: app.move_to(p, 0)),
    ("Go to Jail", lambda p, app: app.move_to(p, 10, jailed=True)),
    ("Collect $200", lambda p, app: setattr(p, 'money', p.money + 200)),
    ("Pay $100", lambda p, app: setattr(p, 'money', p.money - 100)),
]

CHEST_CARDS = [
    ("Bank error in your favor: Collect $200", lambda p, app: setattr(p, 'money', p.money + 200)),
    ("Doctor's fee: Pay $50", lambda p, app: setattr(p, 'money', p.money - 50)),
    ("Get Out of Jail Free", lambda p, app: setattr(p, 'has_card', True)),
    ("Go to Jail", lambda p, app: app.move_to(p, 10, jailed=True)),
]

class Player:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.money = 1500
        self.position = 0
        self.properties = []
        self.has_card = False

class MonopolyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎩 Monopoly - Houses & Hotels Edition 🎲")
        self.tiles = []
        self.players = []
        self.current_player = 0
        self.jailed = set()

        self.create_board()
        self.create_dashboard()
        self.setup_players()
        
    def create_board(self):
        board = tk.Frame(self.root, bg="black")
        board.grid(row=0, column=0, rowspan=2)

        index = 0
        for r in range(11):
            for c in range(11):
                if r in [0, 10] or c in [0, 10]:
                    if index < len(BOARD_SPACES):
                        name = BOARD_SPACES[index]
                        bg_color = self.get_space_color(index)
                        label = tk.Label(board, text=f"{index}\n{name}", bg=bg_color, fg="black", width=9, height=4, relief="ridge", wraplength=80)
                        label.grid(row=r, column=c, padx=1, pady=1)
                        self.tiles.append(label)
                        index += 1
                else:
                    tk.Label(board, text="", bg="beige", width=9, height=4).grid(row=r, column=c)

    def get_space_color(self, index):
        for color, spaces in COLORS.items():
            if index in spaces:
                return color
        return "white"

    def create_dashboard(self):
        dash = tk.Frame(self.root)
        dash.grid(row=0, column=1, sticky="n")

        self.info_label = tk.Label(dash, text="Welcome to Monopoly!", font=("Arial", 14))
        self.info_label.pack(pady=10)

        self.dice_label = tk.Label(dash, text="🎲 Roll: -", font=("Arial", 12))
        self.dice_label.pack(pady=5)

        self.roll_btn = tk.Button(dash, text="Roll Dice", command=self.roll_dice)
        self.roll_btn.pack(pady=5)

        self.buy_btn = tk.Button(dash, text="Buy Property", command=self.buy_property, state="disabled")
        self.buy_btn.pack(pady=5)



        self.end_btn = tk.Button(dash, text="End Turn", command=self.next_turn, state="disabled")
        self.end_btn.pack(pady=5)

        self.player_stats = tk.Label(dash, text="", justify="left")
        self.player_stats.pack(pady=10)

    def setup_players(self):
        num = simpledialog.askinteger("Players", "Enter number of players (2-4):", minvalue=2, maxvalue=4)
        colors = ["red", "blue", "green", "orange"]
        for i in range(num):
            name = simpledialog.askstring("Player Name", f"Enter name for Player {i+1}:")
            self.players.append(Player(name, colors[i]))
        self.update_stats()

    def roll_dice(self):
        roll = random.randint(1, 6)
        player = self.players[self.current_player]
        self.dice_label.config(text=f"🎲 Roll: {roll}")
        if self.current_player in self.jailed:
            self.jailed.remove(self.current_player)
            messagebox.showinfo("Jail", f"{player.name} is released from Jail!")
        else:
            self.move_player(player, roll)

    def move_player(self, player, steps):
        player.position = (player.position + steps) % len(BOARD_SPACES)
        self.update_board()
        self.check_tile(player)

    def move_to(self, player, pos, jailed=False):
        player.position = pos
        if jailed:
            self.jailed.add(self.current_player)
            messagebox.showinfo("Jail", f"{player.name} has been sent to Jail!")
        self.update_board()

    def update_board(self):
        for i, tile in enumerate(self.tiles):
            owner = OWNERSHIP.get(i)
            if owner is not None:
                tile.config(relief="sunken", highlightbackground=self.players[owner].color)
                tile.config(text=f"{i}\n{BOARD_SPACES[i]}\nH:{HOUSES[i]}")
            else:
                tile.config(relief="ridge", text=f"{i}\n{BOARD_SPACES[i]}")

        for player in self.players:
            if player.position < len(self.tiles):
                tile = self.tiles[player.position]
                tile.config(text=f"{tile.cget('text')}\n👤 {player.name}")

    def check_tile(self, player):
        pos = player.position
        space = BOARD_SPACES[pos]

        if space == "Chance":
            card = random.choice(CHANCE_CARDS)
            messagebox.showinfo("Chance!", card[0])
            card[1](player, self)

        elif space == "Community Chest":
            card = random.choice(CHEST_CARDS)
            messagebox.showinfo("Community Chest!", card[0])
            card[1](player, self)

        elif pos in PROPERTY_PRICES:
            owner = OWNERSHIP[pos]
            if owner is None:
                price = PROPERTY_PRICES[pos]
                messagebox.showinfo("Unowned Property", f"{space} is unowned. Price: ${price}")
                self.buy_btn.config(state="normal")
            elif owner == self.current_player:
                self.build_btn.config(state="normal")
            else:
                rent = int(PROPERTY_PRICES[pos] * (RENT_FACTOR + HOUSES[pos]*0.1))
                player.money -= rent
                self.players[owner].money += rent
                messagebox.showinfo("Rent Paid", f"{player.name} paid ${rent} rent to {self.players[owner].name}!")
        else:
            messagebox.showinfo("Special Tile", f"{space} — no action.")
        self.end_btn.config(state="normal")
        self.update_stats()

    def buy_property(self):
        pos = self.players[self.current_player].position
        price = PROPERTY_PRICES[pos]
        player = self.players[self.current_player]
        if player.money >= price and OWNERSHIP[pos] is None:
            player.money -= price
            player.properties.append(pos)
            OWNERSHIP[pos] = self.current_player
            messagebox.showinfo("Purchase Successful", f"{player.name} bought {BOARD_SPACES[pos]} for ${price}!")
        else:
            messagebox.showwarning("Cannot Buy", f"You cannot buy this property!")
        self.buy_btn.config(state="disabled")
        self.update_stats()

    def next_turn(self):
        self.current_player = (self.current_player + 1) % len(self.players)
        player = self.players[self.current_player]

        self.buy_btn.config(state="disabled")
        self.end_btn.config(state="disabled")


        if player.properties:
            self.build_btn.config(state="normal")
        else:
            self.build_btn.config(state="disabled")

        self.info_label.config(text=f"{player.name}'s turn!")
        self.update_stats()

    def update_stats(self):
        stats = "\n".join([f"{p.name} - ${p.money} ({len(p.properties)} props)" for p in self.players])
        self.player_stats.config(text=stats)

if __name__ == "__main__":
    root = tk.Tk()
    app = MonopolyGUI(root)
    root.mainloop()