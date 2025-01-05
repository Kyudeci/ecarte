from typing import Dict
import random
from utils import logger
from terminal_playing_cards import Deck, View, Card

class EcarteDeck(Deck):
    suit_color: Dict[str, str] = {"diamonds": "R",
                                  "hearts": "R", "clubs": "B", "spades": "B"}
    ecarte_specs = {'7': {'spades': 7, 'diamonds': 7, 'clubs': 7, 'hearts': 7}, '8': {'spades': 8, 'diamonds': 8, 'clubs': 8, 'hearts': 8}, '9': {'spades': 9, 'diamonds': 9, 'clubs': 9, 'hearts': 9}, '10': {'spades': 10 , 'diamonds': 10, 'clubs': 10, 'hearts': 10}, 'A': {'spades': 11, 'diamonds': 11, 'clubs': 11, 'hearts': 11}, 'J': {'spades': 12, 'diamonds': 12, 'clubs': 12, 'hearts': 12}, 'Q': {'spades': 13, 'diamonds': 13, 'clubs': 13, 'hearts': 13}, 'K': {'spades': 14, 'diamonds': 14, 'clubs': 14, 'hearts': 14}}
    
    def __init__(self) -> None:
        self._cards = Deck(specifications=self.ecarte_specs, picture=False)
        # [Card(self.ranks[i], suit, self.values[i])
                    #    for suit in self.suits for i in range(len(self.ranks))]
        self.deckSize = self.__len__()
        self._add_color()
        self.shuffle()
        logger("\tDeck Created and Shuffled!")

    def __len__(self) -> int:
        return len(self._cards)

    def __getitem__(self, pos: int):
        return self._cards[pos]

    def shuffle(self):
        self._cards.shuffle()

    def draw(self, n):
        if n > self.deckSize:
            raise Exception("Unable to draw cards")
        drawn = View(cards = [self._cards.pop() for _ in range(n)], spacing=-5)
        self.deckSize -= n
        return drawn

    def _add_color(self):
        for c in self._cards:
            c.color = self.suit_color[c.suit]

    def new_deck(self):
        self.__init__()

    @property
    def cards(self):
        return self._cards
