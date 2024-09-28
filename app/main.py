from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from multiprocessing import Process
import mimetypes
import json
import urllib.parse
import pathlib
import socket
import logging

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb://mongodb:27017"

HTTPServer_Port = 3000
UDP_IP = '127.0.0.1'
UDP_PORT = 5000


class HttpGetHandler(BaseHTTPRequestHandler):
    # TODO Реалізувати логіку веб сервера для обробки статичних ресурсів, відправки вірних статус кодів та маршрутизації
    # Документація наслідуваних методів з BaseHTTPRequestHandler: https://docs.python.org/3/library/http.server.html
    def do_POST(self):
        pass

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


# def send_data_to_socket(data):
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     server = UDP_IP, UDP_PORT
#     # TODO Дописати відправку даних


# def save_data(data):
#     client = MongoClient(uri, server_api=ServerApi("1"))
#     db = client.DB_NAME
#
#     # Дописати логіку збереження даних в БД з відповідними вимогами до структурою документу
#     """
#     {
# 	    "date": "2024-04-28 20:21:11.812177",
#         "username": "Who",
# 	    "message": "What"
#     }
#     """
#     # Ключ "date" кожного повідомлення — це час отримання повідомлення: datetime.now()
#     data_parse = urllib.parse.unquote_plus(data.decode())
#
#
# def run_socket_server(ip, port):
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     server = ip, port
#     sock.bind(server)
#     # TODO Дописати логіку прийняття даних та їх збереження в БД


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(threadName)s %(message)s')

    # TODO Зробити два процеса для кожного з серверів
    http_server_process = Process(target=run_http_server)
    http_server_process.start()

    # socket_server_process = Process()
    # socket_server_process.start()

