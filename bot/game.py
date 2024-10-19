from uno import UNODeck, UNOCard

class UNOGame:
    def __init__(self):
        self.deck = UNODeck()
        self.players = {}
        self.current_player = None
        self.direction = 1
        self.current_color = None
        self.current_card = None
        self.game_over = False
        self.game_started = False
        self.game_created = False
        self.game_creator = None

    def add_player(self, player_id):
        if player_id not in self.players:
            self.players[player_id] = []
            return True
        return False

    def create_game(self,creator_id):
        if not self.game_created:
            self.game_created = True
            self.game_creator = creator_id
            return True
        return False
    
    def get_players(self):
        return self.players
    
    def start_game(self):
        self.deck.shuffle_deck()
        for player in self.players:
            self.players[player] = self.deck.draw_cards(7)
        self.current_card = self.deck.draw_card()
        self.current_color = self.current_card.color if self.current_card.color else self.current_card.value

    def get_current_card(self):
        if self.current_card:
            return f"{self.current_card.color} {self.current_card.value}"
        return "No card"
    
    def reset_game(self):
        self.deck = UNODeck()
        self.players = {}
        self.current_player = None
        self.direction = 1
        self.current_color = None
        self.current_card = None
        self.game_over = False
        self.game_created = False
        self.game_creator = None
        
    def get_player_cards(self, player_id):
        return self.players[player_id]
    
    # def play_card(self, player_id, card):
    #     if card in self.players[player_id]:
    #         if self.is_valid_play(card):
    #             self.players[player_id].remove(card)
    #             self.current_card = card
    #             self.current_color = card.color if card.color else self.current_card.value
    #             self.check_win_condition(player_id)
    #             return True
    #     return False

    # def is_valid_play(self, card):
    #     return card.color == self.current_color or card.value == self.current_card.value or card.color is None

    # def check_win_condition(self, player_id):
    #     if not self.players[player_id]:
    #         self.game_over = True
    #         return f"Player {player_id} has won the game!"

    # def next_player(self):
    #     player_ids = list(self.players.keys())
    #     current_index = player_ids.index(self.current_player)
    #     next_index = (current_index + self.direction) % len(player_ids)
    #     self.current_player = player_ids[next_index]
