# FHE Project 2025 – Homomorphic Encryption Timing and Noise Experiments

Exploring Fully Homomorphic Encryption (FHE) using the [Concrete](https://github.com/zama-ai/concrete) library. 
This repository contains two major components: **noise growth experiments** and **timing benchmarks**, each split into server and client scripts simulating a delegated secure computation setting.
---

## Project Structure
FHE-project-2025/
**noise_growth_experiment/**
 -  noisy_client.py # Client-side loop to test decryption accuracy
 -  noisy_server.py # Server-side circuit performing repeated scalar operations
 -  client_data.csv # Log of decrypted results per iteration
 -  server_data.txt # Log of server's secret function
 -  check_result.py # Validation script to detect when noise breaks correctness
 -  plot_noise_data.py # doesn't work since I couldn't collect enough valid data to plot
 -  noise_summary.csv # supposed to be the log of all the noise experiment results

**compile_time_experiment/**
 -  client.py # Sends encrypted vectors and times execution
 -  server.py # Compiles and runs dot product circuits
 -  timing_data.csv # Output of computation & compilation times
 -  plot_timing_data.py # Script to visualize timing data
 -  check_result.py # Validation script to do plaintext calculation + check if decrypted result matches plaintext
 -  client_data.txt # Stores decrypted vector result and client's initial vector
 -  server.zip # Stores compiled circuit needed to create server  
 -  server_data.txt # Stores server secret vector + compile/compute times (seconds)

---

## How to Run

1. **Install Dependencies**
   This project uses [Concrete](https://github.com/zama-ai/concrete) and requires Python 3.10+. Install the required packages:
   ```bash
   pip install concrete matplotlib numpy

2. **Run Server and Client**  
   Open two terminal windows for each experiment:

   - For **Noise Growth**:

     ```bash
     # Terminal 1
     python noise_growth_experiment/noisy_server.py

     # Terminal 2
     python noise_growth_experiment/noisy_client.py
     ```

   - For **Timing Experiment**:

     ```bash
     # Terminal 1
     python timing_experiment/server.py

     # Terminal 2
     python timing_experiment/client.py
     ```

## Timing Analysis

The **timing experiment** evaluates how both compilation time and encrypted compute time scale with input vector size. The vector sizes tested include:
[10, 25, 50, 100, 200, 500, 1000, 2000, 2500, 5000, 10000]


Each test runs a homomorphic dot product operation between a client-sent encrypted vector and a fixed server-side plaintext vector. Results are logged to `timing_data.csv` and visualized using `plot_timing_data.py`.
The server never sees the plaintext input vector, and the client never sees the server secret vector.

## Noise Growth Experiment

The **noise experiment** attempts to measure how repeated homomorphic operations increase ciphertext noise until decryption fails. The setup involves:

- Repeated application of the function `x = x * 3 + 7` on an encrypted scalar.
- The client decrypts after each operation and re-encrypts for the next iteration.
- Logging is done to track when decryption fails due to excessive noise.


### Limitations and Observations

Unfortunately, this experiment hit several roadblocks due to Concrete’s input range and circuit size limitations:

- **Input Overflow**: Even small inputs like `x = 1` grow too quickly under functions of degree ≥ 1. The compiler’s support for bit ranges is limited, and compiled circuits with large ranges (up to 1 million) take significant time without yielding visible noise failure.

- **Noise Not Visible**: The experiment couldn’t effectively observe noise breakdown because the ciphertexts remained within decryptable range even after many operations. This makes Concrete less suitable for raw noise-tracking at this time.

Despite this, the **timing benchmarks provide valuable insight** into the performance scaling behavior of homomorphic operations in Concrete.

