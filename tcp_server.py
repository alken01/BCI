import os
import socket
import threading
import csv
import time

path = "csvlog/"
csv_name = "data"
server_ip = '192.168.0.102'
server_port = 42069

csv_name = path + csv_name + "_Marker.csv"

def handle_client(client_socket, client_address):
    print("Connection from", client_address)

    input_message = input("Allow client to start:\n")
    client_socket.sendall(input_message.encode('utf-8'))

    with open(csv_name, 'a', newline='') as csvfile:
        log_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        while True:
            data = client_socket.recv(1024)
            message = data.decode('utf-8')
            unixtime = int(time.time())

            log_entry = [unixtime, message]
            log_writer.writerow(log_entry)
            print("Logged",unixtime,log_entry)

            if message == "end": break

        csvfile.close()
    
    print("Closing connection", client_address)
    client_socket.close()


def main():
    if not os.path.exists(path):
        os.makedirs(path)

    if not os.path.isfile(csv_name):
        with open(csv_name, 'w', newline='') as csvfile:
            log_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            log_writer.writerow(["TimeStamp", "Code"])
            print("Created file:", csv_name)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((server_ip, server_port))
    server.listen(5)

    print("Listening on",server_ip,server_port)

    try:
        while True:
            client_socket, client_address = server.accept()
            client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_handler.start()
    except KeyboardInterrupt:
        print("\nStopping server...")

    server.close()

if __name__ == '__main__':
    main()
