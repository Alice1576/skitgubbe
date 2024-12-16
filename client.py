import pickle
import socket
import Cards
import time




def handle_instructions(client_socket):
    
    while True:

        try:
            public_state = pickle.loads(client_socket.recv(4096))

            print(public_state)
            print(f"Players: {public_state['player count']}")
            print("---------")
            print(public_state["turn"])
            print("---------")
            print(f"Stack: {public_state['stack']}")
            print("---------")

            #private_state = pickle.loads(client_socket.recv(4096))
            #print(private_state)

            try:
                instruction = pickle.loads(client_socket.recv(4096))

                if instruction["action"] == "play_card":
            
                    print(f"Your hand: {instruction['hand']}")
            
                    card_index = int(input(f"Please input a card you would like to play: "))
                    response = {"action": "play_card", "index": card_index}
                    serialized_response = pickle.dumps(response)
                    client_socket.send(serialized_response)

                elif instruction["action"] == "take_stack":
            
                    input("You cannot play any card. Please press any button to take the entire stack")
                
                    response = {"action": "take_stack"}
                    serialized_response = pickle.dumps(response)
                    client_socket.send(serialized_response)

            except Exception as e:
                continue

        except Exception as e:
            print(f"Error {e}")

def main():
    host= "localhost"
    port = 5050

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((host, port))
        print("Connected!")
    
    except Exception as e:
        print(f"Failed connecting to {e}")

    handle_instructions(client_socket)


if __name__ == "__main__":
    main()