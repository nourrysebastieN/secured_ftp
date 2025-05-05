import socket

HOST = '127.0.0.1'
PORT = 2121

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print(s.recv(1024).decode(), end='')

        while True:
            cmd = input("ftp> ")
            if not cmd:
                continue

            s.sendall((cmd + "\r\n").encode())

            response = b''
            while True:
                part = s.recv(4096)
                response += part
                if len(part) < 4096:
                    break

            print(response.decode(errors="replace"), end='')

            if cmd.strip().upper() == "QUIT":
                break

if __name__ == "__main__":
    main()

