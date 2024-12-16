from Cards import Card, Deck, Player, Pile, Stack, CardSuites, CardValues
import socket
import pickle
import time

class GameServer:
    def __init__(self, host="localhost", port=5050):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()
        print(f"Server started on {host}:{port}")

        self.clients = [] 
        self.players = []  
        self.pile = None
        self.stack = None
        self.turn = 0

    def broadcast(self, data):
        
        for client_socket in self.clients:
            
            try:
                serialized_data = pickle.dumps(data)
                client_socket.send(serialized_data)
            
            except socket.error as e:
                print(f"Error sending data to client {e}")


    def get_game_state(self):
        public_state = {"type": "public_state",
                        "stack": self.stack.cards,
                        "turn": f"Player {self.turn+1}'s turn",
                        "player count": len(self.players),
                       }

        return public_state

    def update_game_state(self):
        public_state = self.get_game_state()
        self.broadcast(public_state)
        print("Broadcasted game state!")

        for i, client_socket in enumerate(self.clients):
            
            private_state = {"type": "private_state",
                             "hand": self.players[i].hand,
                             "lower hand": self.players[i].lower_hand
                            }
            
            private_state_serialized = pickle.dumps(private_state)
            #client_socket.send(private_state_serialized)



    def start(self):

        while len(self.clients) < 2:
            
            client_socket, addr = self.server.accept()
            self.clients.append(client_socket)
            player_id = len(self.players)
            print(f"Player {player_id+1} connected from {addr}.")

            new_player = Player(name=f"{player_id + 1}", lower_hand=[], hand=[])
            self.players.append(new_player)

        print("All players connected, starting game...")

        self.initialize_game()
        self.game_loop()


    def initialize_game(self):

        self.pile = Pile(cards=Deck().shuffle())
        self.stack = Stack(cards = [])

        for player in self.players:
            
            player.hand = [self.pile.cards.pop() for _ in range(3)]
            player.lower_hand = [self.pile.cards.pop() for _ in range(6)]

    def draw_card(self, player: Player, deck: list[Card]):

        while len(player.hand) < 3 and deck:
            player.hand.append(deck.pop())

        if len(player.hand) < 3 and not deck:
            
            if len(player.hand) == 0:
                
                try:
                    card_index = int(input(f"Which card would you like to play? Your lower hand is: {player.lower_hand}")) - 1 #take card from lower hand to 
                    player.hand.append(player.lower_hand[card_index]) #client side

                except IndexError as e:
                    print("This card does not exist!")

                except ValueError as e:
                    print("Please enter an integer corresponding to your card!")
            
            else:
                return player

        return player

    def special_cards(self, card: Card):

        if card.get_card_value() == 10:
            self.stack.add_card(self.players[self.turn].hand.pop(self.players[self.turn].hand.index(card)))
            self.stack.cards = []
            return True

        elif card.get_card_value() == 2:
            self.stack.add_card(self.players[self.turn].hand.pop(self.players[self.turn].hand.index(card)))
            return True

        return False

    def play_card(self, card_index: int): #the card index being sent here from the game_loop already has been decreased by 1
        
        try:
            played_card = self.players[self.turn].hand[card_index]

        except IndexError as e:
            return False 

        if self.special_cards(played_card):
            return False

        if self.stack.cards:
            if played_card.get_card_value() >= self.stack.cards[-1].get_card_value():
                played_card = self.players[self.turn].hand.pop(card_index)
                
                self.stack.add_card(played_card)
                
                for card in self.players[self.turn].hand:
                    if card.get_card_value() == played_card.get_card_value():
                        return False

            else:
                return False

        else:
            played_card = self.players[self.turn].hand.pop(card_index)
            self.stack.add_card(played_card)
            for card in self.players[self.turn].hand:
                if card.get_card_value() == played_card.get_card_value():
                    return False

        return True

    def special_cards_checker(self, card):
        
        if card.get_card_value() == 10:
            return True
        
        if card.get_card_value() == 2:
            return True

        return False


    def lowest_card(self, curr_hand: list[Card]):

        lowest_regular_card = None
        lowest_special_card = None

        for card in curr_hand:
            if not self.special_cards_checker(card):
                if lowest_regular_card is None or card.get_card_value() < lowest_regular_card.get_card_value():
                    lowest_regular_card = card

            else:
                if lowest_special_card is None or card.get_card_value() < lowest_special_card.get_card_value():
                    lowest_special_card = card

        if lowest_regular_card:
            return lowest_regular_card

        else:
            return lowest_special_card

    def stack_first_card(self) -> Card:
        k = None  # index of the player with the lowest non-special card
        lowest_card = None
        x = 15  # arbitrary high value to find the lowest card

        # first pass: try to find the lowest non-special card
        for i in range(len(self.players)):
            candidate_card = self.lowest_card(self.players[i].hand)  # 2
            if candidate_card.get_card_value() < x and not self.special_cards_checker(candidate_card):  # will fail
                # found a non-special card
                lowest_card = candidate_card
                x = candidate_card.get_card_value()
                k = i

        # if no non-special card was found, fallback to special cards
        if k is None:
            for i in range(len(self.players)):
                candidate_card = self.lowest_card(self.players[i].hand)
                if candidate_card.get_card_value() < x:  # Now allow special cards too
                    lowest_card = candidate_card
                    x = candidate_card.get_card_value()
                    k = i

        self.turn = k
        return self.players[k].hand.pop(self.players[k].hand.index(lowest_card))



    def game_loop(self):
        self.stack.add_card(self.stack_first_card())

        if self.stack.cards[-1].get_card_value() == 10:
            self.stack.cards = []

        self.draw_card(player=self.players[self.turn], deck=self.pile.cards)

        self.turn = (self.turn + 1) % len(self.players)

        while True:
            turn_finished = False
            while not turn_finished:
                
                self.update_game_state()
                current_player = self.players[self.turn]
                client_socket = self.clients[self.turn]
            
                if self.stack.cards:
                
                    valid_cards = []
                
                    for card in current_player.hand:
                        if card.get_card_value() >= self.stack.cards[-1].get_card_value():
                            valid_cards.append(card)
                else:
                    valid_cards = current_player.hand

                try:
                    if valid_cards:
                       action = {"type": "private_state",
                                 "action": "play_card", 
                                 "turn": self.turn, 
                                 "hand": self.players[self.turn].hand
                                }
                    
                    else:
                        action = {"type": "private_state",
                                  "action": "take_stack",
                                  "turn": self.turn,
                                  "hand": self.players[self.turn].hand
                                 }

                    instruction = pickle.dumps(action)
                    print(f"Sending private instruction to Player {self.turn + 1}: {instruction}...")
                    client_socket.send(instruction)

                except Exception as e:
                    print(f"Error sending data to client {e}")

                try:

                    action_response = pickle.loads(client_socket.recv(4096))
                    print(f"Repsponse received {action_response}")

                except Exception as e:
                    
                    print(f"Error receiving action from Player {self.turn + 1}: {e}")
                
                if action_response["action"] == "play_card":
                    card_index = action_response["index"] - 1
                    turn_finished = self.play_card(card_index)

                elif action_response["action"] == "take_stack":
                    current_player.hand.extend(self.stack.cards)
                    self.stack.cards = []
                    turn_finished = True

            self.draw_card(player=current_player, deck=self.pile.cards)
            self.turn = (self.turn + 1) % len(self.players)

if __name__ == "__main__":
    server = GameServer()
    server.start()

