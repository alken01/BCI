import os
import socket
import csv
import time
import explorepy
import argparse


CSV_PATH = 'log/'
CSV_NAME = 'log_experiment'
SERVER_IP = '192.168.0.102'
START_MSG = 'meta'
END_MSG = 'end'

SERVER_PORT = 42069

def main():
    
    parser = argparse.ArgumentParser(description="Example code for marker generation")
    parser.add_argument("-n", "--name", dest="name", type=str, help="Name of the device.")
    args = parser.parse_args()

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
            handle_client(client_socket, client_address,args)
        except KeyboardInterrupt:
            print("\nStopping server...")
            break
    
    server.close()
    # from the csv remove all "'"
    with open(os.path.join(CSV_PATH, f"{CSV_NAME}_Marker.csv"), 'r') as f:
        lines = f.readlines()
    with open(os.path.join(CSV_PATH, f"{CSV_NAME}_Marker.csv"), 'w') as f:
        for line in lines:
            f.write(line.replace('"', ''))
    
    
def handle_client(client_socket, client_address,args):
    print(f"Connection from {client_address}")

    # check for start message from the client
    received_message = client_socket.recv(1024).decode('utf-8');
    # if the message contains the start message, continue
    if START_MSG not in received_message:
        client_socket.close()
        print("Wrong start message:",received_message)
        return
    
    print("Right start message:",received_message)
     # Create an Explore object
    explore = explorepy.Explore()
    explore.connect(device_name=args.name)
    explore.record_data(file_name='test_event_gen', file_type='csv', do_overwrite=True, block=False)
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
            print(message)
            explore.set_marker(code=101)
            # log the data
            log_entry = [unixtime, message]
            log_writer.writerow([message])
            print("Logged:",log_entry)

            # if the message without new spaces is the end message, break
            if message.replace(" ", "") == END_MSG:
                break
    explore.stop_recording()
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
            print(f"Created file: {csv_name}\n")
    # if it exists, overwrite
    else:
        with open(csv_name, 'w', newline='') as csvfile:
            log_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            log_writer.writerow(["TimeStamp", "Code"])
            print(f"Overwrote file: {csv_name}\n")

if __name__ == '__main__':
    main()
