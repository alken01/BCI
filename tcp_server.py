import socket
import explorepy


SERVER_IP = '192.168.0.100'
SERVER_PORT = 42069
START_MSG = 'meta'
END_MSG = 'end_meta'

EXPLORE_DEVICE = 'Explore_8559'


def handle_client(client_socket, client_address):
    """
    Handle a client connection.
    """
    print(f"Connection from {client_address}")

    # Check for the start message from the client
    received_message = client_socket.recv(1024).decode('utf-8')

    # If the message doesn't contain the start message, close the connection
    if START_MSG not in received_message:
        client_socket.close()
        print("Wrong start message:", received_message)
        return

    print("Right start message:", received_message)

    # Ask the user whether to allow the client to start
    input_message = input("Allow client to start: y\n")

    if input_message != 'y':
        client_socket.close()
        print("Server not allowed to start")
        return

    # Let the client know that the server is ready
    client_socket.sendall(START_MSG.encode('utf-8'))

    while True:
        message = client_socket.recv(1024).decode('utf-8')

        code = parse_message(message)

        if code is not None:
            # Look for Explore_8559 connection with explorepy
            device = explorepy.find_device(EXPLORE_DEVICE)

            if device is not None:
                # Send the parsed message as a marker to the explorepy device
                device.send_marker(code)
                print("Logged:", message, "code:", code)
        else:
            print("Logged:", message)

        if message == END_MSG: 
            break

    print(f"Closing connection {client_address}")
    client_socket.close()


def parse_message(message):
    """
    Parse a message from the client and return a code, or None if the message is invalid.
    """
    message_dict = {
        "start": 0,
        "resume": 1,
        "pause": 2
    }

    parts = message.split('_')

    if len(parts) == 2 and parts[0] in message_dict:
        # Check if the second part is a number too
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
    # Create the server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_IP, SERVER_PORT))
    server.listen(5)

    print(f"Listening on {SERVER_IP}:{SERVER_PORT}")

    while True:
        try:
            # Listen for connections
            client_socket, client_address = server.accept()
            handle_client(client_socket, client_address)
        except KeyboardInterrupt:
            print("\nStopping server...")
            break

    server.close()


if __name__ == '__main__':
    main()
