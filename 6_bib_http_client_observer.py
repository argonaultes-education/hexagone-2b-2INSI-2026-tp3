import json
import requests
#import threading

#TODO: trigger 2 threads
# thread to listen to client input
# thread to listen to server connection => mini http server

HOST, PORT = "localhost", 8000

# Create a socket (SOCK_STREAM means a TCP socket)
def send_message(msg_json, verb):
    response = requests.request(method=verb, url=f'http://{HOST}:8000', json=msg_json)
    

    print("Sent:    ", msg_json)
    print("Received:", response.json())


class ConsoleInput:
    
    def __init__(self):
        self.should_continue = True
    
    def create_new_gameboard(self):
        title = input('Title: ')
        author = input('Author: ')
        price = float(input('Price: '))
        return {
            'title': title,
            'author': author,
            'price': price
        }, 'POST'

    def delete_gameboard(self):
        id_to_delete = int(input('Id to delete: '))
        return {
            'id_to_delete': id_to_delete
        }, 'DELETE'

    def list_gameboards(self):
        return {
        }, 'GET'
        
    def should_exit(self):
        self.should_continue = False
        return None, None

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
        msg_json, verb = actions[input_action]()
        if msg_json is not None:
            result_str = send_message(msg_json, verb)
            result_json = None
            try:
                result_json = json.loads(result_str)
            except:
                ...
            print(result_json)