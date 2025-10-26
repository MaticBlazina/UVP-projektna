# Analiza Guinnessovih svetovnih rekordov

## Uvod

Za Projektno nalogo pri predmetu Uvod v programiranje analiziramo Guinnessove svetovne rekorde. Cilj projekta je, da s spletnega mesta Guinness World Records zberemo podatke o rekordih in jih nato analiziramo.

## Opis podatkov

Podatki so bili pridobljeni z uradne spletne strani Guinness World Records. Zbrani so bili podatki iz naslednjih kategorij:
- Narava
- Človeško telo
- Igre

Za vsak rekord so na voljo naslednji podatki:
- Naslov rekorda
- Opis 
- Kategorija
- Leto 
- Lokacija
- Tip rekorda (največji, najhitrejši, itd.)
- URL naslov

## Potek 

Projekt je potekal v dveh glavnih korakih:

### Pridobivanje podatkov
Podatki so bili pridobljeni s spletne strani z uporabo knjižnic `requests` in `html`. Za vsako kategorijo so bili najprej pridobljeni vsi rekordi, nato pa so bili za vsak rekord posebej zbrani podatki.

### Analiza podatkov
Analizo smo izvedli v Jupyter notebooku z uporabo knjižnic `pandas`, `numpy`, `matplotlib` in `seaborn`. Analizirali smo:
- Porazdelitev rekordov po kategorijah
- Časovno porazdelitev rekordov
- Geografsko porazdelitev
- Povezavo med kategorijami in lokacijami
- Tipe rekordov

## Rezultati

Analiza je pokazala naslednje:
- Določene kategorije rekordov so precej bolj zastopane kot druge
- Rekordi so bili merjeni le v dveh državah
- Opaziti je mogoče časovne trende v ustanavljanju rekordov
- Obstajajo zanimive povezave med tipi rekordov in kategorijami

## Uporabili smo

- **Python 3**
- **Knjižnice**: 
  - `requests` in `html` za spletno strganje
  - `pandas` in `numpy` za analizo podatkov
  - `matplotlib` in `seaborn` za vizualizacijo
- **Jupyter Notebook** za interaktivno analizo
