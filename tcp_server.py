import os
import socket
import csv
import time


CSV_PATH = 'logdata/'
CSV_NAME = 'Experiment2'
SERVER_IP = '192.168.0.100'
START_MSG = 'meta'
END_MSG = 'end'

SERVER_PORT = 42069

def main():
    # create the csv file if it doesnt exist
    create_csv_file()
    # create the server 
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_IP, SERVER_PORT))
    server.listen(5)

    print(f"Listening on {SERVER_IP}:{SERVER_PORT}")

    while True:
        try:
            # listen for connections
            client_socket, client_address = server.accept()
            handle_client(client_socket, client_address)
        except KeyboardInterrupt:
            print("\nStopping server...")
            break
    
    server.close()
    
def handle_client(client_socket, client_address):
    print(f"Connection from {client_address}")

    # check for start message from the client
    received_message = client_socket.recv(1024).decode('utf-8');
    if received_message != START_MSG:
        client_socket.close()
        print("Wrong start message:",received_message)
        return
    
    print("Right start message:",received_message)

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
            unixtime = time.time()
            message = client_socket.recv(1024).decode('utf-8')

            # log the data
            log_entry = [unixtime, message]
            log_writer.writerow([message])
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

if __name__ == '__main__':
    main()
