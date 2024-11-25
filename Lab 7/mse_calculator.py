import numpy as np

xA = np.array([1.0, 2.2, 2.0, 1.5, 3.2])
xB = np.array([1.3, 1.1, 2.4, 3.2, 1.2])
true_probabilities = np.array([0, 1, 1, 0, 1])

wA_values = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
wB_values = np.array([2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0])

mse_values = np.zeros((len(wA_values), len(wB_values)))

for i, wA in enumerate(wA_values):
    for j, wB in enumerate(wB_values):
        model_predictions = 1 / (1 + np.exp(-(wA * xA + wB * xB)))

        mse = np.mean((true_probabilities - model_predictions) ** 2)
        mse_values[i, j] = mse

print("2D array of MSE values:")
print(mse_values)
