import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("noise_summary.csv")

plt.figure(figsize=(8, 6))
for name, group in df.groupby("FunctionName"):
    plt.plot(group["InputBits"], group["CorrectIters"], marker='o', label=name)

plt.xlabel("Input Size (bits)")
plt.ylabel("Correct Iterations")
plt.title("Noise Tolerance vs Input Size")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("iter_plot.png")
plt.show()

