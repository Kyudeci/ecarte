from deck import Card
from utils import logger
from terminal_playing_cards import View
import inquirer
import random

class Mechanics:
    def __init__(self):
        self.hand = View(cards=[],spacing=-5)
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

    def reset_state(self):
        self.tricks = 0
        self.reject = False
        self.firstReject = False
        self.playedCard = None

class Player(Mechanics):

    def __init__(self):
        self.name = "Player"
        super().__init__()

    def show_hand(self):
        print(f"Player Hand: {self.hand}")
        logger(f"Player Hand: {', '.join([repr(card) for card in self.hand])}")

    def discard_check(self, first: bool = False, turnPass: bool = False, **kwargs):
        self.discardAmt = 0
        deckSize = kwargs.get("deckSize", 21)
        oppDiscardAmt = kwargs.get("discardAmt", None)
        self.show_hand()
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
            print(self.hand)
            # How many cards to discard?
            q5 = [
                inquirer.Checkbox(
                    "amount",
                    message=f"Discard {self.discardAmt}. (Use left and right arrow keys to select then press 'Enter')",
                    choices=range(1,len(self.hand)+1)),
            ]
            a5 = inquirer.prompt(q5)
            a5["amount"].sort(reverse=True)
            a5["amount"] = [a-1 for a in a5["amount"]]
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
                    self.hand.pop(c)

    def play_card(self, card: Card):
        print(self.hand)
        q6 = [
            inquirer.List("play",
                          message="Play which card?",
                          choices=range(1,len(self.hand)+1),
                          default=None,
                          ),
        ]
        a6 = inquirer.prompt(q6)
        toPlay = a6["play"]-1
        suitList = [c.suit for c in self.hand]
        cardIndex = toPlay
        playedCard = self.hand[cardIndex]
        # print(f"Debug: \nHand: {self.hand}\nCard Index: {cardIndex}\nPlayed Card: {playedCard}\n Card Type: {type(playedCard)}")
        if not self.turnPlayer:
            if card.suit in suitList:
                if playedCard.suit != card.suit:
                    print(f"Invalid card selection. Please play a {card.suit}")
                    return self.play_card(card)
                else:
                    logger(f"{self.name} plays {repr(playedCard)}")
                    self.hand.pop(cardIndex)
                    return playedCard
            else:
                logger(f"{self.name} plays {repr(playedCard)}")
                self.hand.pop(cardIndex)
                return playedCard
        else:
            logger(f"{self.name} plays {repr(playedCard)}")
            self.hand.pop(cardIndex)
            return playedCard


class AI(Mechanics):

    def __init__(self):
        self.name = "Computer"
        self.history = []
        self.discard_idx = []
        super().__init__()

    def show_hand(self):
        logger(f"Player Hand: {repr(self.hand)}")

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
            logger(f"{self.name} discards {self.discardAmt} card(s)\n", out=True)
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
                    f"\t{self.name} wishes to discard {self.discardAmt} card(s)...", out=True)
                return False
            elif first and not self._discard:
                self.skip = True
                logger(f"\t{self.name} is skipping the Discard Phase...", out=True)
                return True
            else:
                self.reject = True
                logger(f"\t{self.name} is ending the Discard Phase...", out=True)
                return True
        elif turnPass:
            return False
        else:
            accept = self._score_hand(eleventh=cardEleven, deckSize=deckSize)
            if first and not accept:
                self.firstReject = True
                logger(f"\t{self.name} rejects the trade proposal\n", out=True)
            elif not accept:
                self.reject = True
                logger(f"\t{self.name} rejects the trade proposal\n", out=True)
            else:
                self._discard = True
                logger(f"\t{self.name} accepts the trade proposal\n", out=True)
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
            logger(f"{self.name} plays {repr(cc)}")
            return cc

        if self.turnPlayer:
            playIdx = random.choice(range(len(self.hand)))
            cc = self.hand.pop(playIdx)
            logger(f"{self.name} plays {repr(cc)}")
            return cc
        else:
            bestCard =  None
            for i, c in enumerate(self.hand):
                if not bestCard:
                    bestCard = (i, c)

                if c.value < oppValue and c.value <= bestCard[1].value:
                    bestCard = (i,c)
            cc = self.hand.pop(bestCard[0])
            logger(f"{self.name} plays {repr(cc)}")
            return bestCard[1]
