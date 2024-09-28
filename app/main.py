from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from multiprocessing import Process
import mimetypes
import urllib.parse
import pathlib
import socket
import logging

from pymongo import MongoClient
from pymongo.server_api import ServerApi

HTTPServer_Port = 3000
UDP_IP = '127.0.0.1'
UDP_PORT = 5000
MONGO_URL = "mongodb://root:password@mongo/?retryWrites=true&w=majority"


class HttpGetHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        logging.info(f"Received data: {data}")
        send_data_to_socket(data)
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('public/index.html')
        elif pr_url.path == '/message':
            self.send_html_file('public/message.html')
        else:
            if pathlib.Path('public').joinpath(pr_url.path[1:]).exists():
                logging.info(f"Sending static file: {self.path}")
                self.send_static()
            else:
                self.send_html_file('public/error.html', 404)

    def send_html_file(self, filename, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        static_file = 'public' + self.path
        mt = mimetypes.guess_type(static_file)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'{static_file}', 'rb') as file:
            self.wfile.write(file.read())


def run_http_server(server_class=HTTPServer, handler_class=HttpGetHandler):
    server_address = ('', HTTPServer_Port)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        logging.info("Server is shutting down")
        http.server_close()
    except Exception as e:
        logging.error(e)


def send_data_to_socket(data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = UDP_IP, UDP_PORT
    sock.sendto(data, server)
    sock.close()


def save_data(data):
    connection = MongoClient(
        MONGO_URL,
        server_api=ServerApi("1"),
    )

    with connection as client:
        result = client.my_application.messages.insert_one(data)
        print(result)


def run_socket_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = UDP_IP, UDP_PORT
    sock.bind(server)
    try:
        while True:
            data, address = sock.recvfrom(1024)
            logging.info(f"Received data: {data.decode()} from: {address}")
            data_parse = urllib.parse.unquote_plus(data.decode())
            data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
            row = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                "username": data_dict.get("username"),
                "message": data_dict.get("message")
            }
            save_data(row)


    except KeyboardInterrupt:
        logging.info("Destroy server")
    finally:
        logging.info("Server is shutting down")
        sock.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')

    logging.info("Starting HTTP and Socket servers")
    http_server_process = Process(target=run_http_server)
    http_server_process.start()

    socket_server_process = Process(target=run_socket_server)
    socket_server_process.start()
