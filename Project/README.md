# Projekt zaliczeniowy - analiza okrojonej bazy DrugBank

## Wstęp
Baza danych DrugBank to ogólnodostępna i bezpłatna baza informacji o lekach
(substancjach leczniczych). Została utworzona w 2006 roku przez zespół Craiga Knoxa i
Davida Wisharta z Wydziału Informatyki i Nauk Biologicznych Uniwersytetu Alberty w
Kanadzie. Łączy dane z dziedziny chemii, biochemii, genetyki, farmakologii i
farmakokinetyki.

Plik *drugbank_partial.xml* zawiera dane dla 100 leków.  Projekt zaliczeniowy polega na przeanalizowaniu zawartości 
okrojonej wersji bazy i utworzeniu różnego rodzaju tabel i wykresów podsumowujących zawartość bazy leków.

## Zadania

### 1 Podstawowe dane

> Utworzyć ramkę danych, która dla każdego leku zawiera następujące informacje: unikalny
identyfikator leku w bazie DrugBank, nazwę leku, jego typ, opis, postać w jakiej dany lek
występuje, wskazania, mechanizm działania oraz informacje z jakimi pokarmami dany lek
wchodzi w interakcje. (4 pkt)

Nigdzie nie znalazłem tagu odnoszącego się do "typu". Kolumna ta pozostanie wypełniona wartością None.

#### Funkcje

- drugbank/parsers.py
  - parse_drugs

### 2 Synonimy

> Utworzyć ramkę danych pozwalającą na wyszukiwanie po DrugBank ID informacji o
wszystkich synonimach pod jakimi dany lek występuje. Napisać funkcję, która dla podanego
DrugBank ID utworzy i wyrysuje graf synonimów za pomocą biblioteki NetworkX. Należy
zadbać o czytelność generowanego rysunku. (4 pkt)

#### Funkcje

- drugbank/parsers.py
  - parse_synonyms
- drugbank/visualisation.py
  - draw_synonym_graph

### 3 Produkty

> Utworzyć ramkę danych o produktach farmaceutycznych zawierających dany lek
(substancję leczniczą). Ramka powinna zawierać informacje o ID leku, nazwie produktu,
producencie, kod w narodowym rejestrze USA (ang. *National Drug Code*), postać w jakiej
produkt występuje, sposób aplikacji, informacje o dawce, kraju i agencji rejestrującej
produkt. (4 pkt)

#### Funkcje

- drugbank/parsers.py
  - parse_products

### 4 Szlaki 

> Utworzyć ramkę danych zawierającą informacje o wszystkich szlakach wszystkich
rodzajów, tj. sygnałowych, metabolicznych, itd., z jakimi jakikolwiek lek wchodzi w interakcje.
Podać całkowitą liczbę tych szlaków. (4 pkt)


**całkowita liczba szlaków dla *drugbank_partial.xml*:** 28

#### Funkcje

- drugbank/parsers.py
  - parse_pathways

### 5 Graf lek $\longleftrightarrow$ szlak

> Dla każdego szlaku sygnałowego/metabolicznego w bazie danych podać leki, które
wchodzą z nim w interakcje. Wyniki należy przedstawić w postaci ramki danych jak i w
opracowanej przez siebie formie graficznej. Przykładem takiej grafiki może być graf
dwudzielny, gdzie dwa rodzaje wierzchołków to szlaki sygnałowe i leki, a poszczególne
krawędzie reprezentują interakcję danego leku z danym szlakiem sygnałowym. Należy
zadbać o czytelność i atrakcyjność prezentacji graficznej. (4 pkt)

#### Funkcje

- drugbank/visualisers.py:
  - visualise_drug_pathways

### 6 Histogram: liczba szlaków dla leku

> Dla każdego leku w bazie danych podać liczbę szlaków, z którymi dany lek wchodzi w
interakcje. Przedstawić wyniki w postaci histogramu z odpowiednio opisanymi osiami.
(4 pkt)

#### Funkcje

- drugbank/visualisers.py:
  - drug_pathways_histogram

### 7 Targety

> Utworzyć ramkę danych zawierającą informacje o białkach, z którymi poszczególne leki
wchodzą w interakcje. Białka te to tzw. targety. Ramka danych powinna zawierać
przynajmniej DrugBank ID targetu, informację o zewnętrznej bazie danych (ang. *source*,
np. Swiss-Prot), identyfikator w zewnętrznej bazie danych, nazwę polipeptydu, nazwę genu
kodującego polipeptyd, identyfikator genu GenAtlas ID, numer chromosomu, umiejscowienie
w komórce. (4 pkt)

#### Funkcje

- drugbank/parsers.py:
  - parse_targets

### 8 Procentowe występowanie targetów

> Utworzyć wykres kołowy prezentujący procentowe występowanie targetów w różnych częściach komórki. (4 pkt)

#### Funkcje

- drugbank/visualisers.py:
  - visualise_cellular_locations

### 9 Status zatwierdzenia leku

> Utworzyć ramkę danych, pokazującą ile leków zostało zatwierdzonych, wycofanych, ile jest w fazie eksperymentalnej 
(ang. *experimental* lub *investigational*) i dopuszczonych w leczeniu zwierząt. Przedstawić te dane na wykresie
kołowym. Podać liczbę zatwierdzonych leków, które nie zostały wycofane. (4 pkt)

#### Funkcje

- drugbank/parsers.py:
  - parse_approval_status
- drugbank/visualisers.py:
  - visualise_statuses

### 10 Potencjalne interakcje

> Utworzyć ramkę danych zawierającą informacje dotyczące potencjalnych interakcji danego leku z innymi lekami. (4 pkt)

#### Funkcje

- drugbank/parsers.py:
  - parse_drug_interactions

### 11 Gene $\longrightarrow$ interacting-drug $\longrightarrow$ product
> Opracować według własnego pomysłu graficzną prezentację zawierającą informacje o
konkretnym genie lub genach, substancjach leczniczych, które z tym genem/genami
wchodzą w interakcje, oraz produktach farmaceutycznych, które zawierają daną substancję
leczniczą. Wybór dotyczący tego, czy prezentacja graficzna jest realizowana dla
konkretnego genu, czy wszystkich genów jednocześnie pozostawiamy Państwa decyzji.
Przy dokonywaniu wyboru należy kierować się czytelnością i atrakcyjnością prezentacji
graficznej. (7 pkt)

To zadanie zajęło mi bardzo dużo czasu, ale jestem z niego bardzo dumny. Konieczne
może być otworzenie wyeksportowanego obrazka.

#### Funkcje

- drugbank/parsers.py:
  - parse_genes
- drugbank/visualisers.py:
  - visualise_genes

### 12 Własna analiza i prezentacja danych
> Zaproponować własną analizę i prezentację danych dotyczących leków. Można w tym
celu pozyskiwać dodatkowe informacje z innych biomedycznych i bioinformatycznych baz
danych dostępnych online. Należy jednak upewnić się, czy dana baza danych pozwala na
zautomatyzowane pobieranie danych przez program. Na przykład baza danych GeneCards
wprost tego zabrania, co zostało na czerwono podkreślone na tej stronie. Przykładowe bazy
danych to: [UniProt](https://www.uniprot.org/), [Small Molecule Pathway Database](https://smpdb.ca/), [The Human Protein Atlas](https://www.proteinatlas.org/). (7 pkt)

Zdecydowałem się skorzystać z bazy danych [UniProt](https://www.uniprot.org/), wykorzystując *Selenium* oraz
*BeautifulSoup* do zbierania i parsowania danych. Mój program dla danego id leku, wykorzystując ramkę danych wygenerowaną
przy pomocy funkcji **parse_targets** z [zadania 7](README.md#7-targety), wyszukuje nazwę danego targetu w bazie danych
i pobiera stronę w html w celu sparsowania i otrzymania liczby aminokwasów. Następnie przygotowuje graf podobny do tego z 
[zadania 11](README.md#11-gene-longrightarrow-interacting-drug-longrightarrow-product), pokazując zależność drug 
$\longrightarrow$ target $\longrightarrow$ aa_count.

Zapewne dałoby się to zarequestować, stosując *external identifier* odpowiadający UniProt dla danego *drugbank-id*, 
ale lubię Selenium.

#### Funkcje

- drugbank/parsers.py:
  - get_amino_acid_count_for_target
  - get_target_amino_acid_count_for_drug
  - get_amino_acid_count_from_html
  - get_uniprot_cards_page
- drugbank/visualisers.py:
  - visualise_genes
  - visualise_drug_target_amino

### 13 Generowanie 20000 fałszywych leków

> Stworzyć symulator, który generuje testową bazę 20000 leków. Wartości generowanych
19900 leków w kolumnie “DrugBank Id” powinny mieć kolejne numery, a w pozostałych
kolumnach wartości wylosowane spośród wartości istniejących 100 leków. Zapisz wyniki w
pliku drugbank_partial_and_generated.xml. Przeprowadź analizę według punktów 1-12
testowej bazy. (7 pkt)

Niestety analiza punktów 4, 5, 6, 11 i 12 nie udała mi się :/

#### Pliki

- drugbank/simulator.py
- drugbank/iter_parsers.py
- scripts/run_drugbank_partial_generated.py

### 14 Testy jednostkowe

> Przygotować testy jednostkowe z pomocą biblioteki pytest. (7 pkt)

Wszystkie testy znajdują się w folderze [tests](https://github.com/NicolasPurr/Python/tree/master/Project/tests).

#### Pliki

- tests/test_api.py
- tests/test_parsers.py
- tests/test_simulation.py
- tests/test_visualisation.py

### 15 Serwer API

> Zrealizować punkt 6 tak, aby możliwe było wysłanie id leku na Twój serwer, który zwróci wynik w odpowiedzi (skorzystaj z fastapi i uvicorn; wystarczy zademonstrowanie przesłania
danych metodą POST, przez Execute w dokumentacji) (4 pkt)

#### Pliki

- drugbank/api.py
- scripts/run_api.py

## Opis folderów i plików

### /data/

#### drugbank_partial.xml
Dostarczona nam okrojona wersja bazy danych **DrugBank**

---

#### Pliki wygenerowane

Pliki wygenerowane przez skrypty.

---

#### gene_tree.png

Grafika przedstawiająca odpowiedź na zadanie nr **10**, czyli graf genu, interakcji tego genu z lekami i produkty zawierajace dany lek.

---

### /drugbank/

#### __init__.py

Sprawia, że folder staje się paczką.

---

#### api.py

Zawiera kod obsługujący serwer do wysyłania requestów o liczbę szlaków dla ID danego leku.

---

#### iter_parsers.py

Zawiera inne podejście do parsowania pliku w sposób iteracyjny, co polepsza modularność
i umożliwia parsowanie większych plików. Niestety z powodu późnego wymyślenia
tego podejścia, nie udało mi się zaimplementować wszystkich parserów.

---

#### parsers.py

Zawiera funkcje stworzone do przetwarzania pliku wejściowego po sparsowaniu z pliku *.xml* do **etree**.

---

#### simulator.py

Zawiera funkcje stworzone do generowania fałszywcyh leków.

---

#### visualisers.py

Zawiera funkcje stworzone do wizualizacji przetworzonych danych.

---

### /scripts/

#### run_api.py

Uruchamia serwer.

---

#### run_drugbank_partial.py 

[Zadania 1 - 12](README.md#zadania)

Wykonuje analizę i prezentację danych zawartych w pliku *drugbank_partial.xml*.

---

#### run_drugbank_partial_generated.py

[Zadanie 13](README.md#13-generowanie-20000-fałszywych-leków)

Wykonuje analizę i prezentację danych zawartych w pliku *drugbank_partial_generated.xml*.

---

#### run_simulation.py

[Zadanie 13](README.md#13-generowanie-20000-fałszywych-leków)

Uruchamia generowanie 20000 fałszywych leków.

---

### /tests/

[Zadanie 14](README.md#14-testy-jednostkowe)


#### __init__.py

Sprawia, że folder jest paczką.

---

#### test_api.py

[Zadanie 15](README.md#15-serwer-api)

Testuje funkcjonalność serwera.

---

#### test_parsers.py

Testuje funkcjonalność funkcji parsujących dane.


---

#### test_simulator.py

Testuje funkcjonalność generatora plików.

---

#### test_visualisers.py

Testuje funkcjonalność funkcji prezentujących dane.

---

## Proponowany sposób testowania projektu

Będąc w głównym folderze projektu, proponuję wywołać następujące instrukcje:

### Zadania 1-12 i 14
```angular2html
pytest tests/test_parsers.py
pytest tests/test_visualisers.py
python scripts/run_drugbank_partial.py
```

### Zadanie 13 i 14
```angular2html
pytest tests/test_simulator.py
python scripts/run_simulation.py
python scripts/run_drugbank_partial_generated.py
```

### Zadanie 14 i 15
```angular2html
pytest tests/test_api.py
python scripts/run_api.py
```