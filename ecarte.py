import datetime
import random
from typing import Dict
import inquirer


def logger(message):
    print(message)
    with open('../Stuff/log.txt', 'a') as f:
        f.write(message + " \n")


class Card:
    suit_color: Dict[str, str] = {"Diamonds": "R",
                                  "Hearts": "R", "Clubs": "B", "Spades": "B"}

    def __init__(self, rank, suit, value):
        self.rank = rank
        self.suit = suit
        self.value = value
        self.name = ""
        self.color = ""
        self.card_name()
        self.set_color()

    def card_name(self):
        self.name = f"{self.rank} of {self.suit}"

    def set_color(self):
        self.color = self.suit_color.get(self.suit)

    def __str__(self):
        return self.name


class EcarteDeck:
    ranks = [str(n) for n in range(7, 11)] + list("AJQK")
    values = [n for n in range(7, 15)]
    suits = "Spades Diamonds Clubs Hearts".split()

    def __init__(self) -> None:
        self._cards = [Card(self.ranks[i], suit, self.values[i])
                       for suit in self.suits for i in range(len(self.ranks))]
        self.deckSize = self.__len__()
        self.shuffle()
        logger("\tDeck Created and Shuffled!")

    def __len__(self) -> int:
        return len(self._cards)

    def __getitem__(self, pos: int):
        return self._cards[pos]

    def shuffle(self):
        random.shuffle(self._cards)

    def draw(self, n) -> list:
        cards = [self._cards.pop(0) for _ in range(n)]
        self.deckSize -= n
        return cards

    def new_deck(self):
        self.__init__()

    @property
    def cards(self):
        return self._cards


class Mechanics:
    def __init__(self):
        self._discard = False
        self.discarded = False
        self.isDealer = False
        self.turnPlayer = False
        self.firstReject = False
        self.reject = False
        self.skip = False
        self.discardAmt = 0
        self.tricks = 0
        self.points = 0
        self.playedCard = None

    def discard_check(self):
        pass

    def discard(self):
        pass

    def play_card(self, card: Card):
        pass

class Player(Mechanics):

    def __init__(self):
        self.hand = []
        self.name = "Player"
        super().__init__()

    def show_hand(self):
        logger(f"Player Hand: {', '.join([str(card) for card in self.hand])}")

    def discard_check(self, first: bool = False, turnPass: bool = False, **kwargs):
        self.discardAmt = 0
        deckSize = kwargs.get("deckSize", 21)
        oppDiscardAmt = kwargs.get("discardAmt", None)
        if not self.isDealer:
            q1 = [
                inquirer.Confirm(
                    "discard",
                    message=f"Would you like to discard cards? ({deckSize} cards left in the deck)",
                    default=True),
            ]
            a1 = inquirer.prompt(q1)
            self._discard = a1['discard']
            if self._discard:
                discardAmounts = list(range(1, min(6, deckSize))) if deckSize > 1 else [0]
                self.discarded = True
                q2 = [
                    inquirer.List("num",
                                  message="How many cards?",
                                  choices=discardAmounts,
                                  default=None,
                                  ),
                ]
                a2 = inquirer.prompt(q2)

                if not a2["num"]:
                    logger("Not enough cards remaining")
                    return False
                self.discardAmt = a2["num"]
                logger(f"\t{self.name} wishes to discard {self.discardAmt} cards")
                return False
            elif first and not self._discard:
                self.skip = True
                logger("\tSkipping Discard Phase...")
                return True
            else:
                self.reject = True
                logger("\tEnding Discard Phase...")
                return True
        else:
            q3 = [
                inquirer.Confirm(
                    "proposal",
                    message="Would you like to accept the discard proposal?"),
            ]
            a3 = inquirer.prompt(q3)
            if turnPass:
                return False
            elif not a3["proposal"] and first:
                self.firstReject = True
                logger(f"\t{self.name} rejects the trade proposal")
            elif not a3["proposal"]:
                self.reject = True
                logger(f"\t{self.name} rejects the trade proposal")
            else:
                self._discard = True
                logger(f"\t{self.name} accepts the trade proposal")
                discardAmounts = list(range(1, min(6, deckSize))) if deckSize > 1 else [0]
                deckRem = deckSize-oppDiscardAmt if deckSize-oppDiscardAmt > 0 else 0
                q4 = [
                    inquirer.List("num",
                                  message=f"Discard how many cards? ({deckRem} card(s) left in the deck)",
                                  choices=discardAmounts,
                                  default=None,
                                  ),
                ]
                a4 = inquirer.prompt(q4)

                if not a4["num"]:
                    logger("Not enough cards remaining")
                    return False
                self.discardAmt = a4["num"]
                logger(f"\t{self.name} will discard {self.discardAmt} card(s)")
                return True
        return False

    def discard(self, agree=True, **kwargs):
        if self._discard and agree:
            safe = False
            # How many cards to discard?
            q5 = [
                inquirer.Checkbox(
                    "amount",
                    message=f"Discard {self.discardAmt}. (Use left and right arrow keys to select then press 'Enter')",
                    choices=[
                        str(card) for card in self.hand]),
            ]
            a5 = inquirer.prompt(q5)
            if len(a5["amount"]) == 0:
                print("\tPlease select a valid number of cards...")
                self.discard()
            elif len(a5["amount"]) != self.discardAmt:
                print(f"\tYou specified {self.discardAmt} card(s) to discard.")
                self.discard()
            else:
                safe = True
            if safe:
                for c in a5["amount"]:
                    card_index = list(map(str, self.hand)).index(str(c))
                    self.hand.pop(card_index)

    def play_card(self, card: Card):
        q6 = [
            inquirer.List("play",
                          message="Play which card?",
                          choices=[str(card) for card in self.hand],
                          default=None,
                          ),
        ]
        a6 = inquirer.prompt(q6)
        toPlay = a6["play"]
        suitList = [c.suit for c in self.hand]
        cardIndex = list(map(str, self.hand)).index(str(toPlay))
        playedCard = self.hand[cardIndex]
        # print(f"Debug: \nHand: {self.hand}\nCard Index: {cardIndex}\nPlayed Card: {playedCard}\n Card Type: {type(playedCard)}")
        if not self.turnPlayer:
            if card.suit in suitList:
                if playedCard.suit != card.suit:
                    print(f"Invalid card selection. Please play a {card.suit}")
                    return self.play_card(card)
                else:
                    logger(f"{self.name} plays {toPlay}")
                    self.hand.pop(cardIndex)
                    return playedCard
            else:
                logger(f"{self.name} plays {toPlay}")
                self.hand.pop(cardIndex)
                return playedCard
        else:
            logger(f"{self.name} plays {toPlay}")
            self.hand.pop(cardIndex)
            return playedCard



# noinspection PyUnresolvedReferences
class AI(Mechanics):

    def __init__(self):
        self.hand = []
        self.name = "Computer"
        self.history = []
        self.discard_idx = []
        super().__init__()

    def show_hand(self):
        logger(f"Player Hand: {', '.join([str(card) for card in self.hand])}")

    def _score_hand(self, eleventh: Card, deckSize: int):
        # matching suit
        # if diamond then heart ; if club then spade
        # 36 < hand_value < 69
        if not self.history:
            list(map(self.history.append, self.hand))
        else:
            [self.history.append(card) for card in self.hand if card not in self.history]

        card_priority = []
        for card in self.hand:
            if card.suit == eleventh.suit:
                card_priority.append(3)
            elif card.color == eleventh.color:
                card_priority.append(2)
            elif card.value >= 10:
                card_priority.append(1)
            else:
                card_priority.append(0)

        hand_avg = sum(card_priority) / len(card_priority)
        counts = (card_priority.count(0), card_priority.count(1))
        if hand_avg >= 2.2 or counts in [(0, 0), (0, 1)]:
            return False

        if counts[0] >= 3 and len(self.history) + 1 <= deckSize:
            self.discard_idx = [
                i for i, v in enumerate(card_priority) if v == 0]
        elif counts[0] == 2 and len(self.history) + 1 <= deckSize:
            self.discard_idx = [
                i for i, v in enumerate(card_priority) if v == 0]
        elif counts[0] >= 1 and len(self.history) + 1 <= deckSize:
            self.discard_idx = [
                i for i, v in enumerate(card_priority) if v == 0]
        elif counts[1] >= 2 and len(self.history) + 1 <= deckSize:
            discard_idx = [
                i for i, v in enumerate(card_priority) if v == 1]
            self.discard_idx = random.sample(discard_idx, k=random.randint(1, len(discard_idx)))
        else:
            return False
        self.discardAmt = len(self.discard_idx)
        return True

    def discard(self, agree: bool = True, **kwargs):
        if self._discard and agree:
            logger(f"{self.name} discards {self.discardAmt} card(s)\n")
            cardsToDiscard = [str(self.hand[i]) for i in self.discard_idx]
            for c in cardsToDiscard:
                cardIndex = list(map(str, self.hand)).index(str(c))
                self.hand.pop(cardIndex)

    def discard_check(self, first: bool = False,turnPass: bool = False, **kwargs):
        self.discardAmt = 0
        cardEleven = kwargs.get('eleventh', None)
        # oppDiscardAmt = kwargs.get("discardAmt", None)
        deckSize = kwargs.get("deckSize", 21)
        if not self.isDealer and not turnPass:
            self._discard = self._score_hand(eleventh=cardEleven, deckSize=deckSize)
            if self._discard:
                logger(
                    f"\t{self.name} wishes to discard {self.discardAmt} card(s)...")
                return False
            elif first and not self._discard:
                self.skip = True
                logger(f"\t{self.name} is skipping the Discard Phase...")
                return True
            else:
                self.reject = True
                logger(f"\t{self.name} is ending the Discard Phase...")
                return True
        elif turnPass:
            return False
        else:
            accept = self._score_hand(eleventh=cardEleven, deckSize=deckSize)
            if first and not accept:
                self.firstReject = True
                logger(f"\t{self.name} rejects the trade proposal\n")
            elif not accept:
                self.reject = True
                logger(f"\t{self.name} rejects the trade proposal\n")
            else:
                self._discard = True
                logger(f"\t{self.name} accepts the trade proposal\n")
                return accept
        return False

    def play_card(self, oppCard: Card):
        oppSuit = oppCard.suit
        oppValue = oppCard.value
        sameSuitIndex = [idx for idx, c in enumerate(self.hand) if oppSuit==c.suit]
        bestPrelim = [idx for idx, c in enumerate(self.hand) if oppSuit==c.suit and oppValue>c.value]
        bestChoices = list(set(sameSuitIndex)|set(bestPrelim))
        if bestChoices:
            idx = random.choice(bestChoices)
            cc = self.hand.pop(idx)
            logger(f"{self.name} plays {str(cc)}")
            return cc

        if self.turnPlayer:
            playIdx = random.choice(range(len(self.hand)))
            cc = self.hand.pop(playIdx)
            logger(f"{self.name} plays {str(cc)}")
            return cc
        else:
            bestCard =  None
            for i, c in enumerate(self.hand):
                if not bestCard:
                    bestCard = (i, c)

                if c.value < oppValue and c.value <= bestCard[1].value:
                    bestCard = (i,c)
            cc = self.hand.pop(bestCard[0])
            logger(f"{self.name} plays {str(cc)}")
            return bestCard[1]

class Game(Player, AI):
    logger(f"\n##### {str(datetime.datetime.now())} ######")

    def __init__(self):
        self.stateDesc = "Game State - Deck Creation"
        logger(self.stateDesc)
        self.deck = EcarteDeck()
        self.gameState = True
        self.eleventhCard = None
        self.dealer = None
        self.player = None
        self.turnPlayer = None
        self.followPlayer = None
        self.prevWinner = None
        self.trickWinner = None
        self.trickLoser = None
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
            while p.points < 5 or ai.points < 5:
                print(f"\t----Round {game_round}----")
                if self.prevWinner:
                    self.update_state(f"Round {game_round} Start")
                    p.hand = []
                    ai.hand = []
                    self.set_roles(ai, p)
                    self.deck.new_deck()

                self.dealer.hand += self.deck.draw(3)
                self.player.hand += self.deck.draw(3)
                self.dealer.hand += self.deck.draw(2)
                self.player.hand += self.deck.draw(2)
                self.eleventhCard = self.deck.draw(1)[0]
                logger(f"The eleventh card is the {str(self.eleventhCard)}")
                self.dealer_point()
                self.king_point()
                # self.dealer._score_hand(self.eleventhCard)
                p.show_hand()
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

                    if len(self.deck) - self.player.discardAmt > 0:
                        confirm = self.dealer.discard_check(first, passTurn, eleventh=self.eleventhCard,
                                                            deckSize=len(self.deck), discardAmt=self.player.discardAmt)
                        self.player.discard(confirm)
                        if confirm:
                            self.player.hand += self.deck.draw(self.player.discardAmt)
                        self.dealer.discard(confirm)
                        if confirm:
                            self.dealer.hand += self.deck.draw(self.dealer.discardAmt)
                        p.show_hand()
                    else:
                        break

                    first = False
                self.update_state("End of Discard Phase")
                logger(self.stateDesc)
                self.update_state("Battle Phase")
                for turn in range(5):
                    self.play()
                    break
                # p.hand += deck.draw(p.discardAmt)
                game_round += 1
                break
            self.gameState = False

    def set_roles(self, a, b):
        self.dealer = self.followPlayer = self.trickLoser = a
        self.dealer.isDealer = True
        self.turnPlayer = self.trickWinner = self.player = b
        self.player.turnPlayer = True
        self.turnPlayer = self.trickWinner = self.player

    def play(self, flip = False):
        if flip:
            self.dealer.turnPlayer, self.player.turnPlayer = self.player.turnPlayer, self.dealer.turnPlayer
            self.turnPlayer = self.trickWinner
            self.trickLoser
        self.turnPlayer.playedCard = self.turnPlayer.play_card(self.eleventhCard)
        self.trickLoser.playedCard = self.trickLoser.play_card(self.turnPlayer.playedCard)
        # create function that determines winner

    def determine_winner(self):
        if (self.turnPlayer.playedCard.suit == self.eleventhCard.suit) and (self.trickLoser.playedCard.suit == self.eleventhCard.suit):
            if self.turnPlayer.playedCard.value > self.trickLoser.playedCard.value:
                return self.turnPlayer

    def dealer_point(self):
        if self.eleventhCard.rank == 'K':
            self.dealer.points += 1
            logger("\tEleventh Card is a King. Dealer gains a point.")

    def king_point(self):
        king = 'K of ' + self.eleventhCard.suit
        pv = [True for card in self.player.hand if king == str(card)]
        if pv:
            self.player.points += 1
            logger(f"\tKing of Trumps is in hand. {self.player.name} gains a point.")
        dv = [True for card in self.dealer.hand if king == str(card)]
        if dv:
            self.dealer.points += 1
            logger(f"\tKing of Trumps is in hand. {self.dealer.name} gains a point.")

    def trick_point(self):
        if self.dealer.tricks == 5:
            self.dealer.points += 2
            logger(f"{self.dealer.name} won all 5 tricks, they gain two points.")
            if self.player.skip:
                self.dealer.points += 1
                logger(
                    f"{self.dealer.name} gains one extra point because {self.player.name} did not make a proposal to discard.")

        elif self.dealer.tricks >= 3:
            self.dealer.points += 1
            logger(f"{self.dealer.name} gains one point.")
            if self.player.skip:
                self.dealer.points += 1
                logger(
                    f"{self.dealer.name} gains one extra point because {self.player.name} did not make a proposal to discard.")

        elif self.player.tricks == 5:
            self.player.points += 2
            logger(f"{self.player.name} won all 5 tricks, they gain two points.")
            if self.dealer.reject:
                self.player.points += 1
                logger(
                    f"{self.player.name} gains one extra point because {self.dealer.name} rejected the proposal to discard.")

        elif self.player.tricks >= 3:
            self.dealer.points += 1
            logger(f"{self.player.name} gains one point.")
            if self.dealer.reject:
                self.player.points += 1
                logger(
                    f"{self.player.name} gains one extra point because {self.dealer.name} rejected the proposal to discard.")


# beer_card = Card('7', "Diamonds", 7)
g = Game()
g.game()
