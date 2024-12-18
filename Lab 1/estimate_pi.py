import math
import random

iterations = int(input("Podaj liczbę iteracji: "))
step = int(input("Podaj krok: "))
hits = 0

for i in range(iterations):
    x = random.uniform(0, 1)
    y = random.uniform(0, 1)
    pytagoras = math.sqrt(x**2 + y**2)
    if pytagoras <= 1.0:
        hits += 1
    if i == step:
        print(4.0 * hits / i)
        step *= 2

pi_estimate = 4.0 * hits / iterations
print(pi_estimate)
print(math.pi - pi_estimate)