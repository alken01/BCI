import socket

def main():
    server_ip = "192.168.0.100"
    server_port = 42069
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        
        server.connect((server_ip, server_port))
        print('Connected to', server_ip, server_port)
        message = "meta"
        server.sendall(message.encode('utf-8'))

        data = server.recv(1024).decode('utf-8')
        print('Server response:', data)
        
        if data != "meta":
            return
        print('Connected to', server_ip, server_port)
        
        try:
            while True:
                message = input()
                
                if message == "end":
                    server.sendall(message.encode('utf-8'))
                    break
                elif message:
                    server.sendall(message.encode('utf-8'))
                    print('Sent message:', message)
                    
        except KeyboardInterrupt:
            server.sendall("end".encode('utf-8'))
        
        server.close()

if __name__ == '__main__':
    main()
