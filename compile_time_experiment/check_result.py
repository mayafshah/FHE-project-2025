## ---------------------
## check_result.py
## ---------------------

import ast
import time
import os
import pandas as pd

CSV_FILENAME = "timing_data.csv"

# Read server vector, compile time, and FHE compute time
with open("server_data.txt", "r") as f:
    lines = f.readlines()
    server_vector = list(map(int, lines[0].strip().split(",")))
    compile_time = float(lines[1].strip())
    fhe_compute_time = float(lines[2].strip())

# Load client vector and decrypted result
with open("client_data.txt", "r") as f:
    lines = f.readlines()
    client_vector = ast.literal_eval(lines[0].split(":", 1)[1].strip())
    decrypted_result = int(lines[1].split(":", 1)[1].strip())

vector_size = len(client_vector)

# Compute expected dot product
start = time.time()
expected_result = sum(a * b for a, b in zip(client_vector, server_vector))
end = time.time()
plain_compute_time = end - start

# Display
print("Checking Dot Product Result")
if len(client_vector) <= 100:
    print("Server secret vector:", server_vector)
    print("Client input vector: ", client_vector)

    print(f"VECTOR_SIZE = {len(server_vector)}")
else:
    print(f"VECTOR_SIZE = {len(server_vector)}")

print(f"Expected Result   : {expected_result}")
print(f"Decrypted Result  : {decrypted_result}")
#print(f"Plaintext Time   : {plain_compute_time:.8f} seconds")
#print(f"FHE Time         : {fhe_compute_time:.8f} seconds")

# Check correctness
if decrypted_result == expected_result:
    print("Match! Homomorphic computation correct.")
else:
    print("Mismatch! Encrypted result is incorrect.")

# Save to dataframe
new_entry = {
    "VectorSize": vector_size,
    "CompileTime": compile_time,
    "PlaintextComputeTime": plain_compute_time,
    "FHEComputeTime": fhe_compute_time
}

if os.path.exists(CSV_FILENAME):
    df = pd.read_csv(CSV_FILENAME)
    df = df._append(new_entry, ignore_index=True)
else:
    df = pd.DataFrame([new_entry])

df.to_csv(CSV_FILENAME, index=False)
print(f"Appended result to {CSV_FILENAME}.")

