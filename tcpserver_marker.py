import os
import socket
import threading
import csv
import time
import os

from psychopy import core, event, visual, monitors

import markers 

CSV_PATH = 'logdata/'
CSV_NAME = 'Experiment2'
SERVER_IP = '192.168.0.100'
START_MSG = 'meta'
END_MSG = 'end'

SERVER_PORT = 42069

def main():
    
    monitor = monitors.Monitor('viewpixx')
    win_size = (1920, 1080)
    win_color = 'black'
    win = visual.Window(
        size=monitor.getSizePix(), fullscr=False, screen=1, allowGUI=True, allowStencil=False,
        units='pix', monitor=monitor, colorSpace=u'rgb', color=win_color
        )
    win.recordFrameIntervals = True

    with markers.get_marker('viewpixx', win) as m:

        # create the csv file if it doesnt exist
        create_csv_file()

        # create the server 
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((SERVER_IP, SERVER_PORT))
        server.listen(5)
        server.settimeout(None)
        print(f"Listening on {SERVER_IP}:{SERVER_PORT}")
       
        while True:
            try:
                # listen for connections
                client_socket, client_address = server.accept()
                handle_client(client_socket, client_address, m, win)

            except KeyboardInterrupt:
                print("\nStopping server...")
            
        server.close()
    win.close()
    core.quit()   

    
def handle_client(client_socket, client_address, m, win):
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
    
        # timer = core.CountdownTimer()

        # win.callOnFlip(timer.reset)  
        
    while True:
        # def check_abort(win):
        #     if event.getKeys(keyList=["escape"]):
        #         win.close()
        #         core.quit()

        message = client_socket.recv(1024).decode('utf-8')
        print("Logged:",message)

        # keep receive messages until it sends an end message

        
        m.send(i)
        win.flip()
        
        # timer.add(1)
        # while timer.getTime() > 0:
        #     check_abort(win)

        win.flip()

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


message_dict = {
    "start": 0,
    "resume": 1,
    "pause": 2,        
}

def parse_message(message):
    parts = message.split('_')
    if len(parts) == 2 and parts[0] in message_dict:
        try:
            num = int(parts[1])
            return int(message_dict[parts[0]] + str(num))
        except ValueError:
            pass
    return None


if __name__ == '__main__':
    main()