import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load timing data
df = pd.read_csv("timing_data.csv")

# Sort by vector size for cleaner plots
df = df.sort_values("VectorSize")

# Compute averages per vector size
grouped = df.groupby("VectorSize").mean().reset_index()

# Print average times
print("\nAverage Times per Vector Size:")
print(grouped[["VectorSize", "PlaintextComputeTime", "FHEComputeTime", "CompileTime"]])

# -------- Plot 1: Compute Time (Plaintext vs. FHE) --------
plt.figure(figsize=(10, 6))
plt.scatter(df["VectorSize"], df["PlaintextComputeTime"], marker='o', label="Plaintext Compute Time")
plt.scatter(df["VectorSize"], df["FHEComputeTime"], marker='o', label="FHE Compute Time")

fhe_fit = np.polyfit(df["VectorSize"], df["FHEComputeTime"], 1)
plain_fit = np.polyfit(df["VectorSize"], df["PlaintextComputeTime"], 1)
plt.plot(df["VectorSize"], np.polyval(fhe_fit, df["VectorSize"]), color="orange", linestyle="--", label="FHE Trend")
plt.plot(df["VectorSize"], np.polyval(plain_fit, df["VectorSize"]), color="blue", linestyle="--", label="Plaintext Trend")


plt.title("Computation Time vs. Vector Size")
plt.xlabel("Vector Size")
plt.ylabel("Time (seconds)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("compute_time_plot.png")
plt.show()

fhe_slope, fhe_intercept = fhe_fit
plain_slope, plain_intercept = plain_fit

print(f"FHE Line of Best Fit: y = {fhe_slope:.6f}x + {fhe_intercept:.6f}")
print(f"Plaintext Line of Best Fit: y = {plain_slope:.6f}x + {plain_intercept:.6f}")


# -------- Plot 2: Compile Time Only --------
plt.figure(figsize=(10, 6))
plt.scatter(df["VectorSize"], df["CompileTime"], color="purple", label="FHE Compile Time")
# compile_fit = np.polyfit(df["VectorSize"], df["CompileTime"], 1)
#plt.plot(df["VectorSize"], np.polyval(compile_fit, df["VectorSize"]), '--', color='purple', label="Compile Trend")

# Fit a 2nd-degree polynomial (quadratic)
compile_fit = np.polyfit(df["VectorSize"], df["CompileTime"], 2)
plt.plot(df["VectorSize"], np.polyval(compile_fit, df["VectorSize"]),
         '--', color='purple', label="Compile Trend (Quadratic)")


plt.title("FHE Compile Time vs. Vector Size")
plt.xlabel("Vector Size")
plt.ylabel("Compile Time (seconds)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("compile_time_plot.png")
plt.show()

