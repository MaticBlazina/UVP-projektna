import re
import csv
import requests
import os
import html
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
}

pot = os.path.dirname(os.path.abspath(__file__))

def poisci_rekorde_iz_kategorije(niz):
    seznam_rekordov = []
    
    vzorci_novi = [
        r'href="(/world-records/[^"]+)"[^>]*data-qa="record-title"',
        r'<a[^>]*href="(/world-records/[^"]+)"[^>]*data-testid="record-link"',
        r'<h3[^>]*>\s*<a[^>]*href="(/world-records/[^"]+)"',
        r'<div[^>]*class="[^"]*record-card[^"]*"[^>]*>.*?<a[^>]*href="(/world-records/[^"]+)"',
    ]
    
    vzorec_stari = r'<a class="record-grid-item" href="(/world-records/[^"]+\.html)">'
    
    for vzorec in vzorci_novi:
        ujemanja = re.findall(vzorec, niz, re.DOTALL)
        for ujemanje in ujemanja:
            url_rekorda = "https://www.guinnessworldrecords.com" + ujemanje
            if url_rekorda not in seznam_rekordov:
                seznam_rekordov.append(url_rekorda)
    
    if len(seznam_rekordov) == 0:
        ujemanja = re.findall(vzorec_stari, niz)
        for ujemanje in ujemanja:
            url_rekorda = "https://www.guinnessworldrecords.com" + ujemanje
            if url_rekorda not in seznam_rekordov:
                seznam_rekordov.append(url_rekorda)
    
    return seznam_rekordov

def poisci_podatke_zapisa(niz):
    najdeni_podatki = {
        'naslov': "",
        'opis': "", 
        'kategorija': "",
        'leto': "",
        'lokacija': "",
        'tip': ""
    }
    
    if not niz or len(niz.strip()) == 0:
        return najdeni_podatki
    
    # 1. NASLOV - vedno deluje iz title tag-a
    vzorec_naslov = r'<title>(.*?)</title>'
    ujemanje = re.search(vzorec_naslov, niz)
    if ujemanje:
        naslov = ujemanje.group(1)
        naslov = re.sub(r'\s*\|\s*Guinness World Records', '', naslov)
        najdeni_podatki['naslov'] = html.unescape(naslov.strip())

    # 2. OPIS
    vzorec_meta = r'<meta[^>]*name="description"[^>]*content="([^"]*)"'
    ujemanje_meta = re.search(vzorec_meta, niz)
    if ujemanje_meta:
        meta_opis = ujemanje_meta.group(1).strip()
        meta_opis = re.sub(r' - Guinness World Records$', '', meta_opis)
        if len(meta_opis) > 30:
            najdeni_podatki['opis'] = html.unescape(meta_opis)
    
    if not najdeni_podatki['opis']:
        vzorec_besedilo = r'<p>(.*?)</p>'
        besedila = re.findall(vzorec_besedilo, niz, re.DOTALL)
        for p in besedila:
            ocisceno_besedilo = re.sub(r'<[^>]*>', '', p).strip()
            if len(ocisceno_besedilo) > 50:
                najdeni_podatki['opis'] = html.unescape(ocisceno_besedilo)
                break

    # 3. LETO
    vzorec_leto = r'\b(19|20)\d{2}\b'
    ujemanje_leto = re.search(vzorec_leto, niz)
    if ujemanje_leto:
        najdeni_podatki['leto'] = ujemanje_leto.group(0)
    else:
        najdeni_podatki['leto'] = "Neznano"

    # 4. LOKACIJA
    znane_lokacije = [
        'USA', 'United States', 'UK', 'United Kingdom', 'England', 'Australia', 
        'Canada', 'India', 'China', 'Japan', 'Germany', 'France', 'Italy', 'Spain',
        'Brazil', 'Russia', 'Mexico', 'South Africa', 'Egypt', 'Kenya', 'Pakistan',
        'Hawaii', 'Alaska', 'California', 'Texas', 'Florida', 'New York', 'Nevada',
        'Europe', 'Asia', 'Africa', 'North America', 'South America', 'Antarctica',
        'Venezuela', 'Chile', 'Argentina', 'Peru', 'Colombia', 'Vietnam', 'Thailand',
        'Indonesia', 'Malaysia', 'Philippines', 'South Korea', 'North Korea'
    ]
    
    lokacija_najdena = False
    html_lower = niz.lower()
    
    for lokacija in znane_lokacije:
        if lokacija.lower() in html_lower:
            vzorec = r'\b' + re.escape(lokacija.lower()) + r'\b'
            if re.search(vzorec, html_lower):
                najdeni_podatki['lokacija'] = lokacija
                lokacija_najdena = True
                break
    
    if not lokacija_najdena:
        najdeni_podatki['lokacija'] = "Neznano"

    zamenjave_lokacij = {
        "United States": "USA",
        "U.S.A.": "USA",
        "US": "USA",
        "UK": "United Kingdom",
        "England": "United Kingdom"
    }

    lokacija2 = najdeni_podatki.get('lokacija', '')
    if lokacija2 in zamenjave_lokacij:
        najdeni_podatki['lokacija'] = zamenjave_lokacij[lokacija2]

    # 5. TIP REKORDA
    tipi_rekordov = [
        'longest', 'largest', 'highest', 'tallest', 'most', 'greatest',
        'smallest', 'shortest', 'lowest', 'fastest', 'slowest', 'oldest',
        'youngest', 'deepest', 'heaviest', 'lightest', 'strongest', 'weakest',
        'stretchiest', 'farthest', 'widest', 'brightest', 'darkest'
    ]
    
    for tip in tipi_rekordov:
        if tip in najdeni_podatki['naslov'].lower():
            najdeni_podatki['tip'] = tip
            break
    else:
        najdeni_podatki['tip'] = "other"

    return najdeni_podatki

def obdelaj_kategorijo(kategorija_url, kategorija_ime):
    print(f"Obdelujem kategorijo: {kategorija_ime}")
    print(f"  URL: {kategorija_url}")
    
    try:
        r = requests.get(kategorija_url, headers=headers)
        r.raise_for_status()
        vsebina = r.text
    except requests.RequestException as e:
        print(f"  Napaka pri pridobivanju kategorije: {e}")
        return {}

    # Poišči povezave do rekordov
    povezave = poisci_rekorde_iz_kategorije(vsebina)
    print(f"  Najdenih rekordov: {len(povezave)}")
    
    if len(povezave) == 0:
        print(f"  PRESKOČENA - HTML struktura ni prepoznana")
        return {}
    
    rekordi_kategorije = {}
    
    # Obdelaj vse rekorde
    for i, povezava in enumerate(povezave, 1):
        print(f"  {i}. {povezava}")
        
        try:
            r_rekord = requests.get(povezava, headers=headers)
            r_rekord.raise_for_status()
            vsebina_rekorda = r_rekord.text
        except requests.RequestException as e:
            print(f"    Napaka pri rekord {i}: {e}")
            continue

        # Izlušči podatke
        podatki_rekorda = poisci_podatke_zapisa(vsebina_rekorda)
        if podatki_rekorda is None:
            continue
        
        # Nastavi kategorijo
        podatki_rekorda['kategorija'] = kategorija_ime
        podatki_rekorda['url'] = povezava
                
        if podatki_rekorda['naslov']:
            rekordi_kategorije[podatki_rekorda['naslov']] = podatki_rekorda
        
        time.sleep(0.3)
    
    print(f"  Uspešno obdelanih rekordov: {len(rekordi_kategorije)}")
    return rekordi_kategorije

def podatki():
    # VSE KATEGORIJE - poskusimo vse
    kategorije = {
        'nature': 'https://www.guinnessworldrecords.com/records/showcase/nature',
        'human_body': 'https://www.guinnessworldrecords.com/records/showcase/human-body',
        'science': 'https://www.guinnessworldrecords.com/records/showcase/science-technology',
        'sports': 'https://www.guinnessworldrecords.com/records/showcase/sports', 
        'entertainment': 'https://www.guinnessworldrecords.com/records/showcase/entertainment',
        'arts_media': 'https://www.guinnessworldrecords.com/records/showcase/arts-media',
        'weird': 'https://www.guinnessworldrecords.com/records/showcase/weird',
        'gaming': 'https://www.guinnessworldrecords.com/records/showcase/gaming',
        'transport': 'https://www.guinnessworldrecords.com/records/showcase/transport'
    }
    
    vsi_rekordi = {}
    
    for kategorija_ime, kategorija_url in kategorije.items():
        rekordi_kategorije = obdelaj_kategorijo(kategorija_url, kategorija_ime)
        vsi_rekordi.update(rekordi_kategorije)
        print(f"Skupaj zbranih rekordov: {len(vsi_rekordi)}")
        

    print(f"SKUPAJ uspešno pridobljenih rekordov: {len(vsi_rekordi)}")

    # Shrani v CSV
    pot_csv = os.path.join(pot, "..", "podatki", "guinness_rekordi.csv")
    with open(pot_csv, "w", newline='', encoding='utf-8') as dat:
        pisatelj = csv.writer(dat)
        pisatelj.writerow([
            "naslov",
            "opis", 
            "kategorija",
            "leto",
            "lokacija", 
            "tip",
            "url"
        ])
        for naslov, info in vsi_rekordi.items():
            pisatelj.writerow([
                naslov,
                info["opis"],
                info["kategorija"],
                info["leto"],
                info["lokacija"],
                info["tip"],
                info["url"]
            ])
    
    print(f"Vsi podatki shranjeni v: {pot_csv}")
    
    # ANALIZA
    
    print("ANALIZA ZBRANIH PODATKOV:")
    
    
    kategorije_count = {}
    for record in vsi_rekordi.values():
        kategorija = record['kategorija']
        kategorije_count[kategorija] = kategorije_count.get(kategorija, 0) + 1
    
    print(f"Kategorije: {kategorije_count}")
    print(f"Skupaj kategorij: {len(kategorije_count)}")
    
    return vsi_rekordi

if __name__ == "__main__":
    podatki()