# Funkcja generująca tekst powitania w zależności od wybranego języka
def tekstPowitania(język):
    powitania = {
        'pl': 'Cześć!',
        'ru': 'привет!',
        'es': '¡Hola!',
        'fr': 'Bonjour!',
    }

    if język in powitania:
        return powitania[język]
    else:
        return "Nie znam języka: " + język

def powitanie():
    print(tekstPowitania(input("Podaj język: ")))

powitanie()
