import os
import socket
import csv
import time
from xml.sax import parseString
import explorepy
import argparse

SERVER_IP = '192.168.0.103'
START_MSG = 'meta'
END_MSG = 'end_meta'
SERVER_PORT = 42069



def parse_message (message):
    message_dict = {
        "start": 0,
        "resume": 1,
        "pause": 2
    }
    parts = message.split('_')
    if len(parts) == 2 and parts[0] in message_dict:
        try:
            num = int(parts[1])
            try: 
                return int(str(message_dict[parts[0]]) + parts[1])
            except: 
                return None
        except:
            return None
    return None

def main():
    
    parser = argparse.ArgumentParser(description="Example code for marker generation")
    parser.add_argument("-n", "--name", dest="name", type=str, help="Name of the device.")
    args = parser.parse_args()


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
    explore.record_data(file_name='2404_Participant1', file_type='csv', do_overwrite=True, block=False)
    # let the client know that the server is ready
    input_message = input("Allow client to start: y\n")
    if input_message != 'y':
        client_socket.close()
        explore.stop_recording()
        explore.disconnect()
        print("Server not allowed to start")
        return
    
    client_socket.sendall(START_MSG.encode('utf-8'))
    
    while True:
        unixtime = time.time()
        message = client_socket.recv(1024).decode('utf-8')
        marker = parse_message(message)
        if marker is not None:
            explore.set_marker(code=marker)
            print("Logged:",message, "marker: ",marker)
        else:
            print("Logged:",message)
        
        # if the message without new spaces is the end message, break
        if message == END_MSG: break
        
    explore.stop_recording()
    explore.disconnect()
    print(f"Closing connection {client_address}")
    client_socket.close()

if __name__ == '__main__':
    main()
