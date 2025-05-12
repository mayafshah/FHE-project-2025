## --------------------
## server_noise.py
## --------------------
import socket
import pickle
import struct
from concrete import fhe

def send_msg(sock, msg):
    msg_len = struct.pack('>I', len(msg))
    sock.sendall(msg_len + msg)

def recv_msg(sock):
    raw_len = recvall(sock, 4)
    if not raw_len:
        return None
    msg_len = struct.unpack('>I', raw_len)[0]
    return recvall(sock, msg_len)

def recvall(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

# Define repeat scalar function
@fhe.compiler({"x": "encrypted"})
def repeat_scalar_multi(x):
    return (x * 3 - 1) % 15
with open("server_data.txt", "w") as f:
    f.write("repeat_scalar(x) = (x * 3 - 1) % 15\n")

# Compile the circuit
print("Compiling circuit...")
circuit = repeat_scalar_multi.compile(range(100))
server = circuit.server
client_specs = server.client_specs

# Start socket server
HOST = '0.0.0.0'
PORT = 65432
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print("🌐 Server ready...")

conn, addr = server_socket.accept()
print(f"Connected to {addr}")

# Send client specs
send_msg(conn, pickle.dumps(client_specs.serialize()))

# Begin loop
MAX_ITER = 100
iteration = 0
while iteration < MAX_ITER:
    # Receive encrypted scalar
    data = recv_msg(conn)
    if data is None:
        print("No data received.")
        break

    payload = pickle.loads(data)
    enc_val = fhe.Value.deserialize(payload["enc_val"])
    evaluation_keys = fhe.EvaluationKeys.deserialize(payload["eval_keys"])

    # Run computation
    result_enc = server.run(enc_val, evaluation_keys=evaluation_keys)
    result_serialized = result_enc.serialize()

    # Send back result
    send_msg(conn, pickle.dumps({"result": result_serialized}))
    iteration += 1

conn.close()
server_socket.close()
print("Server closed.")

