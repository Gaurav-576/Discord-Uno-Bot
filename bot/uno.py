import random

class UNOCard:
    def __init__(self, color, value):
        self.color = color
        self.value = value
    def __str__(self):
        return f"{self.color} {self.value}"

class UNODeck:
    colors = ['red', 'green', 'blue', 'yellow']
    values = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 's', 'r', '+2']
    wild_cards = ['wild', 'draw+4']

    def __init__(self):
        self.cards = []
        self.build_deck()

    def build_deck(self):
        for color in self.colors:
            for value in self.values:
                self.cards.append(UNOCard(color, value))
                if value != '0':
                    self.cards.append(UNOCard(color, value))
        for _ in range(4):
            self.cards.append(UNOCard(None, 'wild'))
            self.cards.append(UNOCard(None, 'draw+4'))
            
    def shuffle_deck(self):
        random.shuffle(self.cards)
        
    def draw_card(self):
        return self.cards.pop() if self.cards else None

    def draw_cards(self, number):
        return [self.draw_card() for _ in range(number)]

    def reset_deck(self):
        self.cards = []
        self.build_deck()
        self.shuffle_deck()