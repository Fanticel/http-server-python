import socket
import threading
import os
import sys

server_socket = socket.create_server(("localhost", 4221))


#
def generateAnswerText(content):
    ans = (f"HTTP/1.1 200 OK\r\n"
           f"Content-Type: text/plain\r\n"
           f"Content-Length: {len(content)}\r\n\r\n"
           f"{content}")
    return ans.encode()


def generateAnswerOctet(content):
    ans = (f"HTTP/1.1 200 OK\r\n"
           f"Content-Type: application/octet-stream\r\n"
           f"Content-Length: {len(content)}\r\n\r\n"
           f"{content}")
    return ans.encode()


class singleThreadSocket(threading.Thread):
    def run(self):
        print(f"Log:\n\n")
        conn, address = server_socket.accept()
        with conn:
            print(f"Connection with {address} established\n\t\t\tCreating another listening device; ")
            newSocket = singleThreadSocket()
            newSocket.start()
            directory = sys.argv[-1]
            data = conn.recv(2048).decode()
            data_split = data.split("\r\n")
            HTTPMethod, path, HTTPVersion = data_split[0].split(" ")
            if path == "/":
                conn.send(b"HTTP/1.1 200 OK\r\n\r\n")
            else:
                path_split = path.split("/")
                if path_split[1] == "echo":#checks if the given command is echo and if so returns what's after echo in path
                    conn.send(generateAnswerText(path.replace("/echo/", "")))
                elif path_split[1] == "user-agent":#checks if the given command is user agent, if so goes through data_split looking for the user agent, and returns it
                    for i in data_split:
                        if "User-Agent: " in i:
                            conn.send(generateAnswerText(i.replace("User-Agent: ", "")))
                elif path_split[1] == "files":#checks if the given command is related to files
                    file_name = directory + path.replace("/files/", "")#checks if the user wants to get a file
                    if HTTPMethod == "GET":
                        if os.path.isfile(file_name):
                            with open(file_name) as file:
                                conn.send(generateAnswerOctet(file.read()))
                        else:
                            conn.send(b"HTTP/1.1 404 Not Found\r\n\r\n")
                    elif HTTPMethod == "POST":#or post a file
                        with open(file_name, "w") as file:
                            file.write(data_split[-1])
                            conn.send(b"HTTP/1.1 201 Content Saved\r\n\r\n")
                else:
                    conn.send(b"HTTP/1.1 404 Not Found\r\n\r\n")


def main():
    newSocket = singleThreadSocket()
    newSocket.start()


if __name__ == "__main__":
    main()
