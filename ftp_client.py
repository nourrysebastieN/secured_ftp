#!/usr/bin/python3
import socket
import argparse

def recv_until_prompt(sock, end_prompt=b"ftp> "):
    data = b''
    while True:
        chunk = sock.recv(1024)
        if not chunk:
            break
        data += chunk
        if end_prompt in data or b"Username:" in data or b"Password:" in data:
            break
    return data.decode(errors="replace")

def main():
    parser = argparse.ArgumentParser(description="Simple FTP Client")
    parser.add_argument('--host', default='127.0.0.1', help='FTP server host (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=2122, help='FTP server port (default: 2121)')
    args = parser.parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((args.host, args.port))
        print(recv_until_prompt(s), end='')

        while True:
            user_input = input()
            s.sendall((user_input + "\n").encode())
            response = recv_until_prompt(s)
            print(response, end='')

            if "Goodbye." in response or "Too many failed attempts" in response or "Access denied" in response:
                break

            if "ftp>" in response:
                while True:
                    cmd = input()
                    if not cmd:
                        continue
                    s.sendall((cmd + "\n").encode())
                    response = recv_until_prompt(s)
                    print(response, end='')
                    if cmd.strip().upper() == "QUIT":
                        return

if __name__ == "__main__":
    main()
