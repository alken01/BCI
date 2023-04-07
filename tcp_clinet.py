import socket
import sys

def main():

    server_ip = "192.168.0.102"
    server_port = 42069
    
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, server_port))
    print(f"[*] Connected to {server_ip}:{server_port}")
    
    message = "start"
    while True:
        client.sendall(message.encode('utf-8'))
        print(f"[*] Sent message: {message}")
    
        if message == "end":
            break
        message = input()
    
    client.close()

if __name__ == '__main__':
    main()