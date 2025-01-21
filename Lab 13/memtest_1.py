import psutil
import math
import random
import sys

def measure_memory():
    process = psutil.Process()
    return process.memory_info().rss / (1024 * 1024)

class Ułamek:
    def __init__(self, licznik, mianownik):
        assert mianownik != 0, "Mianownik nie może być równy 0"

        if mianownik < 0:
            licznik = -licznik
            mianownik = -mianownik

        gcd = math.gcd(licznik, mianownik)
        self.licznik = licznik // gcd
        self.mianownik = mianownik // gcd

    def __add__(self, other):
        licznik = self.licznik * other.mianownik + self.mianownik * other.licznik
        mianownik = self.mianownik * other.mianownik
        return Ułamek(licznik, mianownik)

def main():
    n = int(sys.argv[1])
    k = int(sys.argv[2])

    memory_before = measure_memory()

    ulamek_list = [Ułamek(random.randint(1, 100), random.randint(1, 100)) for _ in range(n)]

    for i in range(k):
        idx = i % n
        ulamek_list[idx] = ulamek_list[idx] + ulamek_list[(idx + 1) % n]

    memory_after = measure_memory()

    print(f"Memory used: {memory_after - memory_before:.2f} MB")

if __name__ == "__main__":
    main()