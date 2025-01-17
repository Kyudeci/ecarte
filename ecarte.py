import datetime
import inquirer
import sys
from mechanics import Player, AI
from utils import logger
from deck import EcarteDeck
from terminal_playing_cards import View, Card

class Game(Player, AI):
    logger(f"\n##### {str(datetime.datetime.now())} ######")
    
    def __init__(self):
        self.stateDesc = "Game State - Deck Creation"
        logger(self.stateDesc)
        self.deck = EcarteDeck()
        self.gameState = True
        self.eleventhCard = None
        self.dummy_card = Card(face="JK", suit="none", value= 0, picture=False, hidden=True)
        self.dealer = None
        self.player = None
        self.turnPlayer = None
        self.followPlayer = None
        self.prevWinner = None
        self.prevLoser = None
        self.trickWinner = None
        self.trickLoser = None
        self.menu_items = {"Start Game": self.game, "Quit":sys.exit}
        super().__init__()

    def update_state(self, state: str):
        self.stateDesc = "Game State - " + state

    def game(self):
        p = Player()
        ai = AI()
        while self.gameState:
            game_round = 1
            self.update_state(f"Round {game_round} Start")
            logger(self.stateDesc)
            self.set_roles(ai, p)
            while not (p.points >= 5 or ai.points >= 5) or (p.points==ai.points) and ((p.points + ai.points != 0) and game_round == 1):
                print(f"\t----Round {game_round}----")
                logger(f"Score:\nPlayer: {p.points}\nOpponent:{ai.points}", out=True)
                if self.prevWinner:
                    self.update_state(f"Round {game_round} Start")
                    p.hand = View(cards=[], spacing=-5)
                    ai.hand = View(cards=[], spacing=-5)
                    self.set_roles(self.prevWinner, self.prevLoser)
                    self.deck.new_deck()

                self.dealer.hand += self.deck.draw(3)
                self.player.hand += self.deck.draw(3)
                self.dealer.hand += self.deck.draw(2)
                self.player.hand += self.deck.draw(2)
                self.eleventhCard = self.deck.draw(1)[0]

                print(f"The eleventh card is the {View(cards=[self.eleventhCard,self.dummy_card],spacing=-2)}")
                logger(f"The eleventh card is the {repr(self.eleventhCard)}")
                self.dealer_point()
                self.king_point()
                # self.dealer._score_hand(self.eleventhCard)
                first = True
                self.update_state("Entering Discard Phase")
                logger(self.stateDesc)
                while not (self.dealer.skip or self.dealer.reject or self.dealer.firstReject or
                           self.player.skip or self.player.reject or self.player.firstReject):
                    if len(self.deck) == 0:
                        logger("\tDeck Is Empty..")
                        logger("\tBeginning The Bout")
                        break
                    passTurn = self.player.discard_check(first, False, eleventh=self.eleventhCard, deckSize=len(self.deck))

                    if passTurn and first:
                        break
                    if len(self.deck) - self.player.discardAmt > 0:
                        confirm = self.dealer.discard_check(first, passTurn, eleventh=self.eleventhCard,
                                                            deckSize=len(self.deck), discardAmt=self.player.discardAmt)
                        self.player.discard(confirm)
                        if confirm:
                            self.player.hand += self.deck.draw(self.player.discardAmt)
                        self.dealer.discard(confirm)
                        if confirm:
                            self.dealer.hand += self.deck.draw(self.dealer.discardAmt)
                    else:
                        logger("Not enough cards in Deck for discard request")
                        break

                    first = False
                self.update_state("End of Discard Phase")
                logger(self.stateDesc)
                self.update_state("Battle Phase")
                switch = False
                for turn in range(5):
                    logger(f"Trick {turn+1}")
                    switch = self.play(flip=switch)
                self.trick_point()
                game_round += 1
            logger(f"Final Score:\nPlayer: {p.points}\nOpponent:{ai.points}", out=True)
            self.gameState = False

    def set_roles(self, a, b):
        a.reset_state()
        b.reset_state()
        self.dealer = self.followPlayer = self.trickLoser = a
        self.dealer.isDealer = True
        self.dealer.turnPlayer = False
        self.player = self.turnPlayer = self.trickWinner = b
        self.player.turnPlayer = True
        self.player.isDealer = False

    def play(self, flip = False):
        logger(f"Game State - Pre Flip\nTrick Loser - {self.trickLoser.name}\nTrick Winner - {self.trickWinner.name}")
        if flip:
            # self.dealer.turnPlayer, self.player.turnPlayer = self.player.turnPlayer, self.dealer.turnPlayer
            self.trickLoser, self.trickWinner = self.trickWinner, self.trickLoser
            logger(f"Game State - Post Flip\nTrick Loser - {self.trickLoser.name}\nTrick Winner - {self.trickWinner.name}")

        self.trickWinner.playedCard = self.trickWinner.play_card(self.eleventhCard)
        print(f"\n{self.trickWinner.name} played:", View(cards=[self.trickWinner.playedCard, self.dummy_card], spacing=-2))
        self.trickLoser.playedCard = self.trickLoser.play_card(self.trickWinner.playedCard)
        print(f"{self.trickLoser.name} played:", View(cards=[self.trickLoser.playedCard, self.dummy_card], spacing=-2))
        # create function that determines winner
        self.determine_winner()
        if self.trickWinner != self.prevWinner: return True
        else: return False

    def determine_winner(self):
        logger("Game State - Determining Winner")
        if (self.trickWinner.playedCard.suit == self.eleventhCard.suit) and (self.trickLoser.playedCard.suit == self.eleventhCard.suit):
            if self.trickWinner.playedCard.value > self.trickLoser.playedCard.value:
                logger(f"{self.trickWinner.name} wins the trick.", out=True)
                self.trickWinner.tricks += 1
                self.prevWinner, self.prevLoser = self.trickWinner, self.trickLoser
            else:
                logger(f"{self.trickLoser.name} wins the trick.", out=True)
                self.trickLoser.tricks += 1
                self.prevWinner, self.prevLoser = self.trickLoser, self.trickWinner
        elif (self.trickWinner.playedCard.suit == self.eleventhCard.suit) and (self.trickLoser.playedCard.suit != self.eleventhCard.suit):
                logger(f"{self.trickWinner.name} wins the trick.", out=True)
                self.trickWinner.tricks += 1
                self.prevWinner, self.prevLoser = self.trickWinner, self.trickLoser
        elif (self.trickWinner.playedCard.suit != self.eleventhCard.suit) and (self.trickLoser.playedCard.suit == self.eleventhCard.suit):
            logger(f"{self.trickLoser.name} wins the trick.", out=True)
            self.trickLoser.tricks += 1
            self.prevWinner, self.prevLoser = self.trickLoser, self.trickWinner
        elif (self.trickWinner.playedCard.suit != self.eleventhCard.suit) and (self.trickLoser.playedCard.suit != self.eleventhCard.suit):
            if (self.trickWinner.playedCard.suit == self.trickLoser.playedCard.suit):
                if self.trickWinner.playedCard.value > self.trickLoser.playedCard.value:
                    logger(f"{self.trickWinner.name} wins the trick.", out=True)
                    self.trickWinner.tricks += 1
                    self.prevWinner, self.prevLoser = self.trickWinner, self.trickLoser
                else:
                    logger(f"{self.trickLoser.name} wins the trick.", out=True)
                    self.trickLoser.tricks += 1
                    self.prevWinner, self.prevLoser = self.trickLoser, self.trickWinner
            else:
                logger(f"{self.trickWinner.name} wins the trick.", out=True)
                self.trickWinner.tricks += 1
                self.prevWinner, self.prevLoser = self.trickWinner, self.trickLoser
       
        

    def dealer_point(self):
        if self.eleventhCard.face == 'K':
            self.dealer.points += 1
            logger(f"\tEleventh Card is a King. Dealer({self.dealer.name}) gains a point. [{self.dealer.points}]", out=True)

    def king_point(self):
        king = 'K of ' + self.eleventhCard.suit
        pv = [True for card in self.player.hand if king == f'{card.face} of {card.suit}']
        if pv:
            self.player.points += 1
            logger(f"\tKing of Trumps is in hand. {self.player.name} gains a point. [{self.player.points}]" , out=True)
        dv = [True for card in self.dealer.hand if king == f'{card.face} of {card.suit}']
        if dv:
            self.dealer.points += 1
            logger(f"\tKing of Trumps is in hand. {self.dealer.name} gains a point. [{self.dealer.points}]", out=True)

    def trick_point(self):
        if self.dealer.tricks == 5:
            self.dealer.points += 2
            logger(f"{self.dealer.name} won all 5 tricks, they gain two points. [{self.dealer.points}]", out=True)
            if self.player.skip:
                self.dealer.points += 1
                logger(
                    f"{self.dealer.name} gains one extra point because {self.player.name} did not make a proposal to discard. [{self.dealer.points}]", out=True)

        elif self.dealer.tricks >= 3:
            self.dealer.points += 1
            logger(f"{self.dealer.name} gains one point. [{self.dealer.points}]", out=True)
            if self.player.skip:
                self.dealer.points += 1
                logger(
                    f"{self.dealer.name} gains one extra point because {self.player.name} did not make a proposal to discard. [{self.dealer.points}]", out=True)

        elif self.player.tricks == 5:
            self.player.points += 2
            logger(f"{self.player.name} won all 5 tricks, they gain two points. [{self.player.points}]", out=True)
            if self.dealer.reject:
                self.player.points += 1
                logger(
                    f"{self.player.name} gains one extra point because {self.player.name} rejected the proposal to discard. [{self.player.points}]", out=True)

        elif self.player.tricks >= 3:
            self.player.points += 1
            logger(f"{self.player.name} gains one point. [{self.player.points}]", out=True)
            if self.dealer.reject:
                self.player.points += 1
                logger(
                    f"{self.player.name} gains one extra point because {self.dealer.name} rejected the proposal to discard. [{self.player.points}]", out=True)

    def play_again(self):
        pass

    def menu(self):
        options = [
                    inquirer.List("select",
                                  message="MENU",
                                  choices=list(self.menu_items.keys()),
                                  default=None,
                                  ),
                ]
        a2 = inquirer.prompt(options)
        self.menu_items[a2["select"]]()
g = Game()
g.game()
