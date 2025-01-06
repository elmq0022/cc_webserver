import os
import pathlib
import socket
import sys
import threading

BASE_DIR = pathlib.Path(__file__).parent.absolute()
WWW_DIR = os.environ.get("WWW_DIR", BASE_DIR / "www")


class HttpServer(object):
    def __init__(self, host="0.0.0.0", port=8888):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)

    def run(self):
        while True:
            try:
                client_connection, client_address = self.server_socket.accept()
                t = threading.Thread(target=handler, args=(client_connection,))
                t.start()
            except KeyboardInterrupt:
                print("got keyboard interrupt - shutdown server")
                self.server_socket.close()
                sys.exit(0)


def handler(client_connection):
    data = client_connection.recv(1024)
    lines = data.split(b"\r\n")
    verb, path, http_version = lines[0].split(b" ")
    str_path = path.decode("utf-8")
    str_path = str_path[1:] if str_path.startswith("/") else str_path
    str_path = str_path[:-1] if str_path.endswith("/") else str_path
    str_path = WWW_DIR / str_path

    html_path = None
    if str_path.exists():
        if str_path.is_file():
            html_path = str_path
        elif str_path.is_dir():
            str_path = str_path / "index.html"
            if str_path.exists() and str_path.is_file():
                html_path = str_path

    if html_path:
        with open(html_path, "rb") as f:
            html = f.read()
        resp = b"HTTP/1.1 200 OK\r\n\r\n" + html + b"\r\n"
    else:
        resp = b"HTTP/1.1 400 Not Found\r\n\r\nCould not find path: " + path + b"\r\n"

    client_connection.sendall(resp)
    client_connection.close()


if __name__ == "__main__":
    server = HttpServer()
    server.run()
