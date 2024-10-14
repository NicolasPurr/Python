# Funkcja generująca tekst powitania w zależności od wybranego języka
def tekstPowitania(jezyk):
    powitania = {
        'pl': 'Cześć!',
        'ru': 'привет!',
        'es': '¡Hola!',
        'fr': 'Bonjour!',
    }

    if jezyk in powitania:
        return powitania[jezyk]
    else:
        return "Brak jezyka w bazie"

def powitanie():
    print(tekstPowitania(input("Podaj język:")))

powitanie()
