## --------------------
## server.py
## --------------------

import socket
import pickle
import struct
import random
import time
import csv
from concrete import fhe


# setup circuit:
VECTOR_SIZE = 100

# Generate randomized secret vector for production use
secret_vector = [random.randint(0, 10) for _ in range(VECTOR_SIZE)]
if len(secret_vector) <= 100: 
    print("Server secret vector (for reference/debug):", secret_vector)
    print(f"VECTOR_SIZE = {VECTOR_SIZE}")
else:
    print("Server secret vector size:", VECTOR_SIZE)

# Function factory
@fhe.compiler({"x": "encrypted"})
def dot_product(x):
    return sum([a * b for a, b in zip(x, secret_vector)])

# Compile with dummy inputset
inputset = [[random.randint(0, 10) for _ in range(VECTOR_SIZE)] for _ in range(10)]
print("⏳ Compiling FHE circuit...")
start_compile = time.time()
circuit = dot_product.compile(inputset)
end_compile = time.time()
compile_time = end_compile - start_compile
print(f"Circuit compiled in {compile_time:.4f} seconds.")

circuit.server.save("server.zip")

# Save the vector so the client can verify correctness
with open("server_secret_vector.txt", "w") as f:
    f.write(",".join(map(str, secret_vector)))

print("Production circuit compiled and saved.")

server = fhe.Server.load("server.zip")

# Network settings
HOST = "0.0.0.0"
PORT = 65432

# Helper functions
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

print("🌐 Server is ready and listening...")

# Start TCP server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
conn, addr = server_socket.accept()
print(f"Connected to {addr}")

# Send client specs
client_specs = server.client_specs
serialized_specs = pickle.dumps(client_specs.serialize())
send_msg(conn, serialized_specs)
print("Sent ClientSpecs to client.")

# Receive encrypted input and evaluation keys
received = pickle.loads(recv_msg(conn))
eval_keys = fhe.EvaluationKeys.deserialize(received["eval_keys"])
enc_x = fhe.Value.deserialize(received["enc_x"])
vector_size = received["vector_size"]

# Server-side computation benchmarking
start = time.time()
result = server.run(enc_x, evaluation_keys=eval_keys)
end = time.time()
compute_time = end - start
print(f"Computation complete in {compute_time:.4f} seconds.")

# Send result
serialized_result = result.serialize()
send_msg(conn, pickle.dumps({
    "serialized_result": serialized_result,
}))

print("Result sent and logged.")
conn.close()
server_socket.close()

# Save the server's secret vector, compile time, and compute time to server_data.txt
with open("server_data.txt", "w") as f:
    f.write(",".join(map(str, secret_vector)) + "\n")
    f.write(f"{compile_time:.6f}\n")
    f.write(f"{compute_time:.6f}\n")
