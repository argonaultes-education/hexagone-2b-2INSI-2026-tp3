import socket
import json


HOST, PORT = "localhost", 9999

# Create a socket (SOCK_STREAM means a TCP socket)
def send_message(msg_json):
    data = json.dumps(msg_json)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connect to server and send data
        sock.connect((HOST, PORT))
        sock.sendall(bytes(data, "utf-8"))
        sock.sendall(b"\n")

        # Receive data from the server and shut down
        received = str(sock.recv(1024), "utf-8")

    print("Sent:    ", data)
    print("Received:", received)


class ConsoleInput:
    
    def __init__(self):
        self.should_continue = True
    
    def create_new_gameboard(self) -> dict:
        title = input('Title: ')
        author = input('Author: ')
        price = float(input('Price: '))
        return {
            'action': 'c',
            'title': title,
            'author': author,
            'price': price
        }

    def delete_gameboard(self) -> dict:
        id_to_delete = int(input('Id to delete: '))
        return {
            'action': 'd',
            'id_to_delete': id_to_delete
        }

    def list_gameboards(self) -> dict:
        return {
            'action': 'l'
        }
        
    def should_exit(self) -> None:
        self.should_continue = False

if __name__ == '__main__':
    
    ci = ConsoleInput()
    actions = {
        'h': lambda : print('Help'),
        'c': ci.create_new_gameboard,
        'd': ci.delete_gameboard,
        'l': ci.list_gameboards,
        'q': ci.should_exit
    }
    while ci.should_continue:
        input_action = input('Action: ')
        msg_json = actions[input_action]()
        if msg_json is not None:
            result_str = send_message(msg_json)
            result_json = None
            try:
                result_json = json.loads(result_str)
            except:
                ...
            print(result_json)