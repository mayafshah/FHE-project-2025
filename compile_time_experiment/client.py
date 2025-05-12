## --------------------
## client.py
## --------------------
import socket
import pickle
import struct
import time
import random
import subprocess
from concrete import fhe
VECTOR_SIZE = 100


# Settings
HOST = "127.0.0.1"
PORT = 65432


# Generate a random vector x
x = [random.randint(0, 10) for _ in range(VECTOR_SIZE)]
print(f"Generated input vector: {x}")

# Helpers
def send_msg(sock, msg: bytes):
    msg_length = struct.pack(">I", len(msg))
    sock.sendall(msg_length + msg)

def recv_msg(sock):
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack(">I", raw_msglen)[0]
    return recvall(sock, msglen)

def recvall(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

# Connect to server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
print("Connected to server.")

# Receive client specs
serialized_specs = pickle.loads(recv_msg(client_socket))
client_specs = fhe.ClientSpecs.deserialize(serialized_specs)

# Create client
client = fhe.Client(client_specs)

# Keygen timing
start_keygen = time.time()
client.keys.generate()
end_keygen = time.time()
keygen_time = end_keygen - start_keygen

# Encrypt timing
start_encrypt = time.time()
enc_x = client.encrypt(x)
end_encrypt = time.time()
encrypt_time = end_encrypt - start_encrypt

# Send encrypted data and eval keys
to_send = {
    "eval_keys": client.evaluation_keys.serialize(),
    "enc_x": enc_x.serialize(),
    "vector_size": VECTOR_SIZE
}
send_msg(client_socket, pickle.dumps(to_send))
print("Sent encrypted vector and evaluation keys.")

# Receive result
response = pickle.loads(recv_msg(client_socket))
result = fhe.Value.deserialize(response["serialized_result"])

# Decrypt timing
start_decrypt = time.time()
decrypted = client.decrypt(result)
end_decrypt = time.time()
decrypt_time = end_decrypt - start_decrypt

print("Result decrypted and saved.")
print(f"Decrypted result: {decrypted}")

with open("client_data.txt", "w") as f:
    f.write(f"ClientVector: {x}\n")
    f.write(f"DecryptedResult: {decrypted}\n")

client_socket.close()

# Run the result checker script
print("Running accuracy checker...")
subprocess.run(["python3", "check_result.py"])
