import socket
import pickle
import time
from concrete import fhe
from check_result import should_continue
import struct
import os
import csv

csv_path = "client_data.csv"
write_header = not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0

START_VALUE = 1
print("START_VALUE =", START_VALUE)
print("SV_SIZE (bits) =", START_VALUE.bit_length())

with open(csv_path, "a", newline="") as csvfile:
    writer = csv.writer(csvfile)
    if write_header:
        writer.writerow(["Iteration", "InitialValue", "DecryptedResult"])

# Helper to send/receive messages with length prefix
def send_msg(sock, msg: bytes):
    msg_len = struct.pack('>I', len(msg))
    sock.sendall(msg_len + msg)

def recv_msg(sock):
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    return recvall(sock, msglen)

def recvall(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

# Configuration
HOST = "127.0.0.1"
PORT = 65432

max_iters = 100

# Connect to server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
print("Connected to server.")

# Load circuit specs
serialized_specs = pickle.loads(recv_msg(sock))
client_specs = fhe.ClientSpecs.deserialize(serialized_specs)
client = fhe.Client(client_specs)
client.keys.generate()

# Encrypt initial value
value = START_VALUE
iteration = 0

while iteration < max_iters:
    enc_x = client.encrypt(value)    
    # Send encrypted data and eval keys
    to_send = {
        "eval_keys": client.evaluation_keys.serialize(),
        "enc_val": enc_x.serialize(),
    }
    send_msg(sock, pickle.dumps(to_send))
    print("Sent encrypted vector and evaluation keys.")

    # Receive result
    response = recv_msg(sock)
    if response is None:
        print("No result received. Exiting.")
        break

    result = pickle.loads(response)
    enc_result = fhe.Value.deserialize(result["result"])
    dec_result = client.decrypt(enc_result)

    with open("client_data.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([iteration, START_VALUE, dec_result])
 

    # Call the checker to see if result is still accurate
    if not should_continue():
        print("Stopping due to mismatch (likely noise).")
        break

    # Prepare for next iteration
    value = dec_result
    iteration += 1

sock.close()
print("Client finished.")

