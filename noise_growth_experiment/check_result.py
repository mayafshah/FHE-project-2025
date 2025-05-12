# noisy_check_result.py

import os
import pandas as pd
import math

client_file = "client_data.csv"
server_file = "server_data.txt"
log_file = "noise_summary.csv"

def count_ops(func_str):
    ops = func_str.count('+') + func_str.count('-') + func_str.count('*') + func_str.count('/')
    return ops


def log_summary(iteration, func_str, initial_value):
    num_ops = count_ops(func_str)
    row = {
        "FunctionName": func_str,
        "FunctionOps": num_ops,
        "InputBits": initial_value.bit_length(),
        "CorrectIters": iteration 
    }
    if os.path.exists(log_file):
        df = pd.read_csv(log_file)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])
    df.to_csv(log_file, index=False)


def parse_client_data(filepath):
    df = pd.read_csv(filepath)
    last_row = df.iloc[-1]
    iteration = int(last_row["Iteration"])
    original = int(last_row["InitialValue"])
    decrypted = int(last_row["DecryptedResult"])
    return iteration, original, decrypted

def parse_server_function(filepath):
    with open(filepath, "r") as f:
        for line in f:
            if "repeat_scalar(x)" in line:
                rhs = line.split("=", 1)[1].strip()
                return f"lambda x: {rhs}"
    return None

def compute_expected(x, iterations, func_str):
    func = eval(func_str)  # Convert "lambda x: ..." string into a real function
    for _ in range(iterations + 1):
        x = func(x)
    return x

def should_continue():
    if not os.path.exists(client_file) or not os.path.exists(server_file):
        print("❌ Required data files not found.")
        return False

    iteration, original, decrypted = parse_client_data(client_file)
    func_str = parse_server_function(server_file)

    if not func_str:
        print("❌ Could not find server function definition.")
        return False

    expected = compute_expected(original, iteration, func_str)
#    print(f"f({original}) = {expected}")

    match = decrypted == expected

    if not match:
        print(f"❌ Iteration {iteration}:\n    expected={expected}\n    decrypted={decrypted}")
        log_summary(iteration, func_str, original)
    else:
        print(f"✅ Iteration {iteration}:\n    expected={expected}\n    decrypted={decrypted}")
    return match

if __name__ == "__main__":
    result = should_continue()
    exit(0 if result else 1)

