import os
import socket
import threading
import csv
import time

CSV_PATH = "csvlog/"
CSV_NAME = "data"
SERVER_IP = '192.168.0.100'
SERVER_PORT = 42069

START_MSG = "meta"
END_MSG = "end"

def handle_client(client_socket, client_address):
    print(f"Connection from {client_address}")

    # check for start message from the client
    if client_socket.recv(1024).decode('utf-8') != START_MSG:
        client_socket.close()
        print("Wrong start message")
        return
    
    # let the client know that the server is ready
    input_message = input("Allow client to start: y\n")
    if input_message != 'y':
        client_socket.close()
        print("Server not allowed to start")
        return
    
    client_socket.sendall(START_MSG.encode('utf-8'))
    
    # open the log file
    csv_name = os.path.join(CSV_PATH, f"{CSV_NAME}_Marker.csv")
    with open(csv_name, 'a', newline='') as csvfile:
        log_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        # log the start
        log_writer.writerow([time.time(),'start'])
        
        while True:
            data = client_socket.recv(1024)
            unixtime = int(time.time())
            message = data.decode('utf-8')

            # log the data
            log_entry = [unixtime, message]
            log_writer.writerow(log_entry)
            print("Logged:",log_entry)

            # keep receive messages until it sends an end message
            if message == END_MSG: break

    print(f"Closing connection {client_address}")
    client_socket.close()


def create_csv_file():
    # create dir
    csv_name = os.path.join(CSV_PATH, f"{CSV_NAME}_Marker.csv")
    if not os.path.exists(CSV_PATH):
        os.makedirs(CSV_PATH)

    # create file
    if not os.path.isfile(csv_name):
        with open(csv_name, 'w', newline='') as csvfile:
            log_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            log_writer.writerow(["TimeStamp", "Code"])
            print(f"Created file: {csv_name}")


def main():
    # create if it doesnt exist
    create_csv_file()

    # create the server 
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_IP, SERVER_PORT))
    server.listen(5)

    print(f"Listening on {SERVER_IP}:{SERVER_PORT}")

    try:
        # listen for connections
        while True:
            client_socket, client_address = server.accept()
            client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_handler.start()
    except KeyboardInterrupt:
        print("\nStopping server...")
    
    server.close()

if __name__ == '__main__':
    main()
