import math

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

    def __sub__(self, other):
        licznik = self.licznik * other.mianownik - self.mianownik * other.licznik
        mianownik = self.mianownik * other.mianownik
        return Ułamek(licznik, mianownik)

    def __mul__(self, other):
        licznik = self.licznik * other.licznik
        mianownik = self.mianownik * other.mianownik
        return Ułamek(licznik, mianownik)

    def __truediv__(self, other):
        assert other.licznik != 0, "Dzielnik nie może być równy 0"
        licznik = self.licznik * other.mianownik
        mianownik = self.mianownik * other.licznik
        return Ułamek(licznik, mianownik)

    def __lt__(self, other):
        return self.licznik * other.mianownik < self.mianownik * other.licznik

    def __le__(self, other):
        return self.licznik * other.mianownik <= self.mianownik * other.licznik

    def __eq__(self, other):
        return self.licznik == other.licznik and self.mianownik == other.mianownik

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        return self.licznik * other.mianownik > self.mianownik * other.licznik

    def __ge__(self, other):
        return self.licznik * other.mianownik >= self.mianownik * other.licznik

    def __str__(self):
        return f"{self.licznik}/{self.mianownik}"

    def __repr__(self):
        return f"Ułamek({self.licznik}, {self.mianownik})"

