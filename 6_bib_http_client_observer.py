import json
import requests
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler, HTTPStatus
import sys

#TODO: trigger 2 threads
# thread to listen to client input
# thread to listen to server connection => mini http server

HOST, PORT = "localhost", 8000

# Create a socket (SOCK_STREAM means a TCP socket)
def send_message(msg_json, verb, resource):
    response = requests.request(method=verb, url=f'http://{HOST}:8000{resource}', json=msg_json)
    

    print("Sent:    ", msg_json)
    print("Received:", response.json())


class ConsoleInput:
    
    def __init__(self, notification_address, notification_port):
        self.should_continue = True
        self.__notification_address = notification_address
        self.__notification_port = notification_port
    
    def create_new_gameboard(self):
        title = input('Title: ')
        author = input('Author: ')
        price = float(input('Price: '))
        return {
            'title': title,
            'author': author,
            'price': price
        }, 'POST', ''

    def delete_gameboard(self):
        id_to_delete = int(input('Id to delete: '))
        return {
            'id_to_delete': id_to_delete
        }, 'DELETE', ''

    def list_gameboards(self):
        return {
        }, 'GET', ''
        
    def subscribe(self):
        return {
            'address': self.__notification_address,
            'port': self.__notification_port
        }, 'POST', '/subscribe'
        
    def should_exit(self):
        self.should_continue = False
        return None, None, None

def console_input(notification_address, notification_port):
    ci = ConsoleInput(notification_address, notification_port)
    actions = {
        'h': lambda : print('Help'),
        'c': ci.create_new_gameboard,
        'd': ci.delete_gameboard,
        'l': ci.list_gameboards,
        's': ci.subscribe,
        'q': ci.should_exit
    }
    while ci.should_continue:
        input_action = input('Action: ')
        msg_json, verb, resource = actions[input_action]()
        if msg_json is not None:
            result_str = send_message(msg_json, verb, resource)
            result_json = None
            try:
                result_json = json.loads(result_str)
            except:
                ...
            print(result_json)

class BibNotificationHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_header(self, result):
        result_json = json.dumps(result)
        enc = 'UTF-8'
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/json; charset=%s" % enc)
        self.send_header("Content-Length", str(len(result_json)))
        self.end_headers()
        return result_json        

    def do_POST(self):
        length = self.headers.get('Content-Length')
        msg = self.rfile.read(int(length))
        msg_obj = json.loads(msg)
        print('\n', f'Got event {msg_obj["event"]} !!!!!')
        result_json = self.set_header({'status': 'OK'})
        self.wfile.write(result_json.encode('utf-8'))

def server_notification(notification_address, notification_port):
    server_address = (notification_address, notification_port)
    httpd = HTTPServer(server_address, BibNotificationHandler)
    httpd.serve_forever()

if __name__ == '__main__':

    threads = []
    notification_address = sys.argv[1]
    notification_port = int(sys.argv[2])
    

    t = threading.Thread(target=console_input, args=(notification_address, notification_port))
    threads.append(t)
    t = threading.Thread(target=server_notification, args=(notification_address, notification_port))
    threads.append(t)

    # Start each thread
    for t in threads:
        t.start()
        
    # Wait for all threads to finish
    for t in threads:
        t.join()
    
