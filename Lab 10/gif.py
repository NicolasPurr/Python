import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Parameters
n_frames = 50       # adjust for longer animation
n_bins = 30
lambda_exp = 1

def generate_exponential_samples(n_samples):
    return np.random.exponential(1 / lambda_exp, n_samples)

# Histogram creation
fig, ax = plt.subplots(figsize=(6, 4))
ax.set_title("Centralne Twierdzenie Graniczne")
ax.set_xlabel("Wartość")
ax.set_ylabel("Prawdopodobieństwo")

def update_histogram(frame):
    ax.clear()

    n_samples = frame * 10
    samples = np.sum([generate_exponential_samples(10) for _ in range(n_samples)], axis=0)

    ax.hist(samples, bins=n_bins, density=True, alpha=0.6, color='g')

    # Dynamically adjust x-axis limits
    ax.set_xlim(max(min(samples) - max(samples) + min(samples), 0), max(samples) + max(samples) - min(samples))  # Extend x-limits slightly beyond data
    ax.set_ylim(0, 0.5)

    ax.set_title("Centralne Twierdzenie Graniczne")
    ax.set_xlabel("Wartość")
    ax.set_ylabel("Prawdopodobieństwo")
    
ani = FuncAnimation(fig, update_histogram, frames=range(1, n_frames + 1), repeat=False)
ani.save('clt.gif', writer='imagemagick', fps=10)

plt.show()
