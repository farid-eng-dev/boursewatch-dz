#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Scraper de la Bourse d'Alger (SGBV)
Récupère les cours des actions (marché principal et croissance), les obligations OAT,
l'indice Dzair Index avec son historique de tendance, et les métriques de la séance.
"""

import os
import re
import json
import urllib.request
from html.parser import HTMLParser

SGBV_URL = "https://www.sgbv.dz/"

class SGBVParser(HTMLParser):
    """
    Parseur pour extraire les données du code HTML de sgbv.dz.
    """
    def __init__(self):
        super().__init__()
        self.in_orange_box = False
        self.in_session_title = False
        self.session_date = ""
        self.session_day = ""
        
        # Pour les statistiques du marché
        self.in_volume_table = False
        self.in_tr = False
        self.in_td = False
        self.current_td_index = -1
        self.current_table_type = "" # "principal", "croissance", "oat"
        
        # Pour extraire les tableaux de cotation (main-table)
        self.in_table = False
        self.in_tbody = False
        self.table_classes = []
        self.current_row = []
        self.current_data = ""
        self.current_table_index = 0 # 1: Principal, 2: Croissance, 3: Obligataire
        self.raw_tables = {1: [], 2: [], 3: []}
        
        # Pour extraire l'indice Dzair Index actuel
        self.in_indice_var = False
        self.indice_var_text = ""
        self.indice_val_text = ""
        self.in_span = False
        self.indice_spans = []
        
        # Stats de volumes
        self.stats = {
            "principal": {"volume": 0, "value": 0.0, "listings": 9, "bonds_encours": 0.0},
            "croissance": {"volume": 0, "value": 0.0, "listings": 4},
            "oat": {"volume": 0, "value": 0.0, "listings_bonds": 45, "oat_encours": 0.0}
        }
        self.temp_stat_row = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        # 1. Date de séance
        if tag == "div" and attrs_dict.get("id") == "orange":
            self.in_orange_box = True
        elif tag == "span" and self.in_orange_box:
            self.in_session_title = True
            
        # 2. Indice de marché actuel
        elif tag == "div" and attrs_dict.get("id") == "indice-var":
            self.in_indice_var = True
            self.indice_spans = []
        elif tag == "span" and self.in_indice_var:
            self.in_span = True
            
        # 3. Statistiques de volumes (tabs)
        elif tag == "div" and attrs_dict.get("id") in ["box-one", "box-two", "box-three"]:
            self.current_table_type = attrs_dict.get("id").replace("box-one", "principal").replace("box-two", "croissance").replace("box-three", "oat")
        elif tag == "div" and attrs_dict.get("id") == "volume" and self.current_table_type:
            self.in_volume_table = True
        elif tag == "tr" and self.in_volume_table:
            self.in_tr = True
            self.temp_stat_row = []
        elif tag == "td" and self.in_tr:
            self.in_td = True
            self.current_data = ""
            
        # 4. Tableaux des cours (Cote officielle)
        elif tag == "div" and attrs_dict.get("id") in ["table1", "table2", "table3"]:
            self.current_table_index = int(attrs_dict.get("id").replace("table", ""))
        elif tag == "table" and self.current_table_index:
            self.in_table = True
        elif tag == "tr" and self.in_table:
            self.in_tr = True
            self.current_row = []
        elif tag == "td" and self.in_tr:
            self.in_td = True
            self.current_data = ""

    def handle_data(self, data):
        data_clean = data.strip()
        if not data_clean:
            return
            
        if self.in_session_title:
            self.session_day = data_clean
        elif self.in_orange_box and not self.in_session_title:
            self.session_date += " " + data_clean
            
        elif self.in_indice_var:
            if self.in_span:
                self.indice_spans.append(data_clean)
                
        elif self.in_td:
            self.current_data += " " + data_clean

    def handle_endtag(self, tag):
        if tag == "span":
            self.in_session_title = False
            self.in_span = False
        elif tag == "div":
            if self.in_orange_box:
                self.in_orange_box = False
                self.session_date = self.session_date.strip()
            elif self.in_indice_var:
                self.in_indice_var = False
                if len(self.indice_spans) >= 2:
                    self.indice_var_text = self.indice_spans[0]
                    self.indice_val_text = self.indice_spans[1]
                elif len(self.indice_spans) == 1:
                    self.indice_var_text = self.indice_spans[0]
            elif self.in_volume_table:
                self.in_volume_table = False
                self.current_table_type = ""
        elif tag == "td":
            self.in_td = False
            if self.in_volume_table and self.in_tr:
                self.temp_stat_row.append(self.current_data.strip())
            elif self.in_table and self.in_tr:
                self.current_row.append(self.current_data.strip())
        elif tag == "tr":
            self.in_tr = False
            if self.in_volume_table and self.temp_stat_row:
                self.parse_market_stat(self.current_table_type, self.temp_stat_row)
            elif self.in_table and self.current_row:
                # Éviter la ligne d'en-tête
                if not any(header in self.current_row[0].upper() for header in ["CODE", "OUVERTURE", "CLÔTURE", "VALEUR"]):
                    self.raw_tables[self.current_table_index].append(self.current_row)
        elif tag == "table":
            self.in_table = False

    def parse_market_stat(self, table_type, row_data):
        if len(row_data) < 2:
            return
        label = row_data[0].lower()
        val_str = re.sub(r'[^\d,.]', '', row_data[1]).replace(',', '.')
        try:
            val = float(val_str) if val_str else 0.0
        except ValueError:
            val = 0.0
            
        if "volume" in label:
            self.stats[table_type]["volume"] = int(val)
        elif "valeur" in label:
            self.stats[table_type]["value"] = val
        elif "sociétés" in label or "nombre" in label:
            if table_type == "principal":
                self.stats[table_type]["listings"] = int(val)
            elif table_type == "croissance":
                self.stats[table_type]["listings"] = int(val)
            else:
                self.stats[table_type]["listings_bonds"] = int(val)
        elif "encours" in label:
            if table_type == "principal":
                self.stats[table_type]["bonds_encours"] = val
            elif table_type == "oat":
                self.stats[table_type]["oat_encours"] = val

class SGBVOrdresParser(HTMLParser):
    """
    Parseur pour extraire les ordres non exécutés depuis la page page=ordre.
    """
    def __init__(self):
        super().__init__()
        self.in_table = False
        self.in_tr = False
        self.in_td = False
        self.current_row = []
        self.current_data = ""
        self.orders = []

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.in_table = True
        elif tag == "tr" and self.in_table:
            self.in_tr = True
            self.current_row = []
        elif tag == "td" and self.in_tr:
            self.in_td = True
            self.current_data = ""

    def handle_data(self, data):
        if self.in_td:
            self.current_data += data

    def handle_endtag(self, tag):
        if tag == "td" and self.in_td:
            self.in_td = False
            self.current_row.append(self.current_data.strip())
        elif tag == "tr" and self.in_tr:
            self.in_tr = False
            if self.current_row:
                # Éviter la ligne d'en-tête
                if any(x in self.current_row[0].upper() for x in ["SOCIÉTÉ", "SOCIETE", "CODE"]):
                    pass
                else:
                    self.orders.append(self.current_row)
        elif tag == "table":
            self.in_table = False

class SGBVAvisParser(HTMLParser):
    """
    Parseur pour extraire les bulletins / avis officiels depuis la page page=avis.
    """
    def __init__(self):
        super().__init__()
        self.bulletins = []
        self.in_listing = False
        self.in_li = False
        self.in_title_p = False
        self.in_span = False
        self.current_bulletin = {}
        self.current_text = ""
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "ul" and attrs_dict.get("id") == "listing":
            self.in_listing = True
        elif tag == "li" and self.in_listing:
            self.in_li = True
            self.current_bulletin = {"id": "", "date": "", "file": "", "title": ""}
            self.current_text = ""
        elif tag == "p" and attrs_dict.get("class") == "listing_title" and self.in_li:
            self.in_title_p = True
        elif tag == "span" and self.in_title_p:
            self.in_span = True
        elif tag == "a" and self.in_li:
            href = attrs_dict.get("href", "")
            if "avis/" in href and href.endswith(".pdf"):
                self.current_bulletin["file"] = os.path.basename(href)

    def handle_data(self, data):
        if self.in_span:
            self.current_bulletin["date"] = data.strip()
        elif self.in_title_p:
            self.current_text += data

    def handle_endtag(self, tag):
        if tag == "ul" and self.in_listing:
            self.in_listing = False
        elif tag == "span" and self.in_span:
            self.in_span = False
        elif tag == "p" and self.in_title_p:
            self.in_title_p = False
        elif tag == "li" and self.in_li:
            self.in_li = False
            title_text = self.current_text.strip()
            if title_text.startswith(":"):
                title_text = title_text[1:].strip()
            
            match = re.search(r'(\d+-\d+)', title_text)
            self.current_bulletin["id"] = match.group(1) if match else ""
            self.current_bulletin["title"] = title_text
            
            if self.current_bulletin.get("file"):
                self.bulletins.append(self.current_bulletin)

class SGBVOatPageParser(HTMLParser):
    """
    Parseur pour extraire les Obligations du Trésor (OAT) depuis la page page=oat.
    """
    def __init__(self):
        super().__init__()
        self.oats = []
        self.in_table = False
        self.in_tr = False
        self.in_td = False
        self.current_row = []
        self.current_data = ""
        
    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.in_table = True
        elif tag == "tr" and self.in_table:
            self.in_tr = True
            self.current_row = []
        elif tag == "td" and self.in_tr:
            self.in_td = True
            self.current_data = ""
            
    def handle_data(self, data):
        if self.in_td:
            self.current_data += data
            
    def handle_endtag(self, tag):
        if tag == "td" and self.in_td:
            self.in_td = False
            self.current_row.append(self.current_data.strip())
        elif tag == "tr" and self.in_tr:
            self.in_tr = False
            if len(self.current_row) >= 8:
                ticker = self.current_row[1].strip()
                if "CODE" in ticker.upper() or "ISIN" in self.current_row[2].upper():
                    return
                self.oats.append(self.current_row)
        elif tag == "table" and self.in_table:
            self.in_table = False

def clean_num(val_str):
    if not val_str or val_str.upper() == "NC":
        return None
    val_str = re.sub(r'[^\d,.\-]', '', val_str).replace(' ', '').replace(',', '.')
    try:
        return float(val_str)
    except ValueError:
        return None

def clean_percent(val_str):
    if not val_str:
        return "0,00 %"
    val_str = val_str.strip().replace(' ', '').replace('.', ',')
    if not val_str.endswith('%'):
        val_str += " %"
    return val_str

def parse_highcharts_history(html_content):
    """
    Extrait l'historique complet du Dzair Index du code JavaScript Highcharts.
    """
    # Regex pour capturer le tableau de données du DzairIndex
    match = re.search(r"name\s*:\s*'Dzair Indice',\s*data\s*:\s*(\[\[.*?\]\])", html_content, re.DOTALL)
    if not match:
        # Essayer avec un autre nom d'indice ou un format plus simple
        match = re.search(r"data\s*:\s*(\[\[\d+,\d+\.?\d*\].*?\]\])", html_content, re.DOTALL)
        
    if match:
        data_str = match.group(1)
        try:
            # Rendre valide le JSON en s'assurant qu'il n'y a pas de formatages étranges
            # Par exemple, supprimer les sauts de ligne ou espaces doubles
            data_str = re.sub(r'\s+', '', data_str)
            history = json.loads(data_str)
            print(f"Historique de l'indice extrait avec succès : {len(history)} points de données.")
            return history
        except Exception as e:
            print(f"Erreur d'analyse JSON de l'historique : {e}")
            
    print("Impossible de récupérer l'historique via Highcharts dans l'HTML.")
    return []

def run_scraper():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # 1. Récupérer la page principale
    try:
        req = urllib.request.Request(SGBV_URL, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
    except Exception as e:
        print(f"Erreur de connexion à {SGBV_URL} : {e}")
        return
        
    # 2. Récupérer la page des ordres non exécutés
    orders_url = "https://www.sgbv.dz/?page=ordre&lang=fr"
    orders_html = ""
    try:
        req_orders = urllib.request.Request(orders_url, headers=headers)
        with urllib.request.urlopen(req_orders, timeout=15) as response:
            orders_html = response.read().decode('utf-8')
    except Exception as e:
        print(f"Erreur de connexion à {orders_url} : {e}")

    # 2.5 Récupérer la page des OAT
    oat_url = "https://www.sgbv.dz/?page=oat&lang=fr"
    oat_html = ""
    try:
        req_oat = urllib.request.Request(oat_url, headers=headers)
        with urllib.request.urlopen(req_oat, timeout=15) as response:
            oat_html = response.read().decode('utf-8')
    except Exception as e:
        print(f"Erreur de connexion à {oat_url} : {e}")
        
    # Analyser l'HTML principal
    parser = SGBVParser()
    parser.feed(html)
    
    # Analyser l'HTML des ordres
    scraped_orders = []
    if orders_html:
        try:
            orders_parser = SGBVOrdresParser()
            orders_parser.feed(orders_html)
            
            for row in orders_parser.orders:
                if len(row) >= 5:
                    company_name = row[0]
                    ticker = row[1].strip().upper()
                    price_val = clean_num(row[2])
                    vol_val = clean_num(row[3])
                    volume = int(vol_val) if vol_val is not None else 0
                    side = row[4].strip()
                    
                    scraped_orders.append({
                        "ticker": ticker,
                        "name": company_name,
                        "price": price_val if price_val is not None else 0.0,
                        "volume": volume,
                        "side": side
                    })
            print(f"Scrapé avec succès {len(scraped_orders)} ordres.")
        except Exception as e:
            print(f"Erreur lors du parsing des ordres : {e}")

    # Analyser l'HTML des OAT
    scraped_oat_bonds = []
    if oat_html:
        try:
            oat_parser = SGBVOatPageParser()
            oat_parser.feed(oat_html)
            for row in oat_parser.oats:
                cat = row[0].strip()
                ticker = row[1].strip().upper()
                isin = row[2].strip().upper()
                intro_price = clean_num(row[3])
                issue_date = row[4].strip()
                maturity_date = row[5].strip()
                encours = row[6].strip()
                coupon = row[7].strip()
                
                scraped_oat_bonds.append({
                    "ticker": ticker,
                    "name": cat,
                    "isin": isin,
                    "open": intro_price if intro_price is not None else 100.0,
                    "close": intro_price if intro_price is not None else 100.0,
                    "change": "0,00 %",
                    "coupon": coupon,
                    "issueDate": issue_date,
                    "maturityDate": maturity_date,
                    "encours": encours
                })
            print(f"Scrapé avec succès {len(scraped_oat_bonds)} Obligations du Trésor (OAT).")
        except Exception as e:
            print(f"Erreur lors du parsing de la page OAT : {e}")
    
    # 1. Traiter la séance
    session_date = parser.session_date.replace("\n", " ").strip()
    session_day = parser.session_day.replace("Séance du", "").replace(":", "").strip()
    formatted_date = f"{session_day} {session_date}".strip()
    
    # 2. Traiter l'indice Dzair Index
    index_val = clean_num(parser.indice_val_text)
    index_var = clean_percent(parser.indice_var_text)
    
    # 3. Traiter l'historique de l'indice
    raw_history = parse_highcharts_history(html)
    
    # 4. Traiter les entreprises cotées (Equities)
    # Tickers officiels
    ticker_mapping = {
        "ALL": "ALL",
        "AOM": "AOM",
        "AYRD": "AYRD",
        "BDL": "BDL",
        "BIO": "BIO",
        "CREX": "CREX",
        "CPA": "CPA",
        "AUR": "AUR",
        "MST": "MST",
        "SAI": "SAI"
    }
    
    scraped_quotes = {}
    
    # Parcourir la table 1 (Principal) et la table 2 (Croissance)
    for table_idx in [1, 2]:
        for row in parser.raw_tables[table_idx]:
            if len(row) >= 4:
                # Format: [Nom de l'entreprise, Ticker, Ouverture, Clôture, Variation %]
                name = row[0]
                ticker = row[1].strip().upper()
                open_p = clean_num(row[2])
                close_p = clean_num(row[3])
                change = clean_percent(row[4])
                
                if ticker in ticker_mapping:
                    scraped_quotes[ticker] = {
                        "name": name,
                        "open": open_p,
                        "close": close_p,
                        "change": change
                    }
                    
    # 5. Traiter les obligations (Table 3)
    scraped_bonds = []
    for row in parser.raw_tables[3]:
        if len(row) >= 4:
            # Format: [Nom de l'obligation, Ticker, Ouverture, Clôture, Variation %]
            name = row[0]
            ticker = row[1].strip().upper()
            if ticker in ["CODE", "CODE BOURSE", "TICKER"]:
                continue
            open_p = clean_num(row[2])
            close_p = clean_num(row[3])
            change = clean_percent(row[4])
            
            # Déduire le type de coupon / libellé
            coupon = "OAT"
            if ticker == "AL30":
                coupon = "OBLIG 6.5%"
            elif ticker == "ML30":
                coupon = "OBLIG 6.25%"
            elif ticker == "TS30":
                coupon = "OBLIG 5.75%"
            elif "OBLI" in name.upper() or "LEAS" in name.upper() or "TOSY" in name.upper():
                coupon = "OBLIG"
            
            scraped_bonds.append({
                "ticker": ticker,
                "name": name,
                "open": open_p,
                "close": close_p,
                "change": change,
                "coupon": coupon
            })
            
    # Ajouter les OAT publiques
    scraped_bonds.extend(scraped_oat_bonds)

    # Charger la base de données JSON existante
    db_file = "market_data.json"
    existing_data = {}
    if os.path.exists(db_file):
        try:
            with open(db_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except Exception:
            pass

    # Définir ou mettre à jour la séance
    existing_data["session"] = {
        "date": formatted_date,
        "index_name": "Dzair Index",
        "index_value": index_val if index_val else (existing_data.get("session", {}).get("index_value", 3843.95)),
        "index_change": index_var,
        "total_volume_equities": parser.stats["principal"]["volume"] + parser.stats["croissance"]["volume"],
        "total_value_equities": parser.stats["principal"]["value"] + parser.stats["croissance"]["value"],
        "total_volume_bonds": parser.stats["oat"]["volume"],
        "total_value_bonds": parser.stats["oat"]["value"],
        "market_cap": parser.stats["principal"]["bonds_encours"] # Souvent utilisé comme proxy cap globale actions sur l'entête
    }

    # Liste des profils statiques des entreprises à fusionner (si non présents dans le JSON existant)
    default_profiles = {
        "CPA": {
            "name": "Crédit Populaire d'Algérie",
            "sector": "Bancaire",
            "sectorKey": "Bancaire",
            "ipoYear": 2024,
            "ipoPrice": 2300,
            "description": "Le Crédit Populaire d'Algérie (CPA) est l'une des plus importantes institutions bancaires publiques en Algérie. Son introduction en bourse en 2024 a constitué la plus grande opération historique de la place d'Alger.",
            "div2023": 125, "div2024": 125, "div2025": 175.00, "yield": 7.61, "yieldTarget": False,
            "history": {
                2023: {"price": None, "div": 125},
                2024: {"price": 2300, "div": 125},
                2025: {"price": 2300, "div": 175},
                2026: {"price": 2300.00, "div": None}
            }
        },
        "BIO": {
            "name": "Biopharm",
            "sector": "Pharmaceutique",
            "sectorKey": "Pharmaceutique",
            "ipoYear": 2016,
            "ipoPrice": 1225,
            "description": "Biopharm est un laboratoire pharmaceutique algérien intégré, leader dans le secteur de la santé. Il exerce des activités de production et de distribution de médicaments.",
            "div2023": 180, "div2024": 160, "div2025": 170.00, "yield": 6.77, "yieldTarget": False,
            "history": {
                2023: {"price": 2400, "div": 180},
                2024: {"price": 2450, "div": 160},
                2025: {"price": 2500, "div": 170},
                2026: {"price": 2510.00, "div": None}
            }
        },
        "BDL": {
            "name": "Banque du Développement Local",
            "sector": "Bancaire",
            "sectorKey": "Bancaire",
            "ipoYear": 2024,
            "ipoPrice": 1400,
            "description": "La Banque du Développement Local (BDL) est une banque publique majeure introduite à la bourse d'Alger en 2024, orientée vers le financement du développement local.",
            "div2023": None, "div2024": 77, "div2025": 107.00, "yield": 7.64, "yieldTarget": False,
            "history": {
                2023: {"price": None, "div": None},
                2024: {"price": 1400, "div": 77},
                2025: {"price": 1402, "div": 107},
                2026: {"price": 1405.00, "div": None}
            }
        },
        "ALL": {
            "name": "Alliance Assurances",
            "sector": "Assurances",
            "sectorKey": "Assurances",
            "ipoYear": 2010,
            "ipoPrice": 830,
            "description": "Alliance Assurances est le pionnier des compagnies privées d'assurances cotées à la Bourse d'Alger, offrant des solutions de couverture diversifiées.",
            "div2023": 32, "div2024": 28, "div2025": 35.00, "yield": 10.14, "yieldTarget": False,
            "history": {
                2023: {"price": 330, "div": 32},
                2024: {"price": 340, "div": 28},
                2025: {"price": 342, "div": 35},
                2026: {"price": 345.00, "div": None}
            }
        },
        "SAI": {
            "name": "Saidal",
            "sector": "Pharmaceutique",
            "sectorKey": "Pharmaceutique",
            "ipoYear": 1999,
            "ipoPrice": 800,
            "description": "Saidal est le groupe pharmaceutique étatique historique d'Algérie, leader dans la fabrication de médicaments génériques.",
            "div2023": 15, "div2024": 21, "div2025": 24.00, "yield": 5.38, "yieldTarget": False,
            "history": {
                2023: {"price": 420, "div": 15},
                2024: {"price": 435, "div": 21},
                2025: {"price": 440, "div": 24},
                2026: {"price": 446.00, "div": None}
            }
        },
        "AUR": {
            "name": "EGH El Aurassi",
            "sector": "Hôtellerie",
            "sectorKey": "Immo/Hôtellerie",
            "ipoYear": 1999,
            "ipoPrice": 400,
            "description": "L'Entreprise de Gestion Hôtelière (EGH) El Aurassi gère le célèbre hôtel 5 étoiles d'Alger, symbole d'hospitalité d'affaires.",
            "div2023": 0, "div2024": 0, "div2025": 0.00, "yield": 0.00, "yieldTarget": False,
            "history": {
                2023: {"price": 520, "div": 0},
                2024: {"price": 535, "div": 0},
                2025: {"price": 545, "div": 0},
                2026: {"price": 550.00, "div": None}
            }
        },
        "AYRD": {
            "name": "AYRADE",
            "sector": "Technologie",
            "sectorKey": "Technologie",
            "ipoYear": 2026,
            "ipoPrice": 800,
            "description": "Ayrade est une société technologique dynamique spécialisée dans les solutions d'hébergement web cloud et de transformation digitale.",
            "div2023": None, "div2024": None, "div2025": 0.00, "yield": 9.45, "yieldTarget": True,
            "history": {
                2023: {"price": None, "div": None},
                2024: {"price": None, "div": None},
                2025: {"price": None, "div": 0},
                2026: {"price": 810.00, "div": None}
            }
        },
        "CREX": {
            "name": "CRAPC EXPERTISE",
            "sector": "Conseil / Audit",
            "sectorKey": "Services",
            "ipoYear": 2026,
            "ipoPrice": 1600,
            "description": "CRAPC (Expertise) est un cabinet de premier plan spécialisé dans les conseils stratégiques, d'audit comptable et de gouvernance d'entreprise.",
            "div2023": None, "div2024": None, "div2025": 0.00, "yield": 0.00, "yieldTarget": False,
            "history": {
                2023: {"price": None, "div": None},
                2024: {"price": None, "div": None},
                2025: {"price": None, "div": 0},
                2026: {"price": 1600.00, "div": None}
            }
        },
        "MST": {
            "name": "Moustachir",
            "sector": "Conseil PME",
            "sectorKey": "Services",
            "ipoYear": 2024,
            "ipoPrice": 750,
            "description": "Moustachir est un intermédiaire et cabinet conseil dédié aux projets de restructuration et d'ingénierie financière des PME.",
            "div2023": None, "div2024": 0, "div2025": 0.00, "yield": 0.00, "yieldTarget": False,
            "history": {
                2023: {"price": None, "div": None},
                2024: {"price": 750, "div": 0},
                2025: {"price": 765, "div": 0},
                2026: {"price": 780.00, "div": None}
            }
        },
        "AOM": {
            "name": "AOM Invest",
            "sector": "Tourisme / Immo",
            "sectorKey": "Immo/Hôtellerie",
            "ipoYear": 2018,
            "ipoPrice": 400,
            "description": "AOM Invest est une entreprise privée d'investissement à vocation touristique et immobilière, gérant des complexes de loisir.",
            "div2023": 0, "div2024": 0, "div2025": 0.00, "yield": 0.00, "yieldTarget": False,
            "history": {
                2023: {"price": 310, "div": 0},
                2024: {"price": 300, "div": 0},
                2025: {"price": 295, "div": 0},
                2026: {"price": 290.00, "div": None}
            }
        }
    }

    # Charger ou initialiser les compagnies
    updated_companies = existing_data.get("companies", {})
    if not updated_companies:
        updated_companies = default_profiles
        
    # Mettre à jour avec les cotations du jour
    for ticker, info in default_profiles.items():
        company = updated_companies.get(ticker, info)
        
        # Mettre à jour avec les données scrapées si disponibles
        if ticker in scraped_quotes:
            quote = scraped_quotes[ticker]
            # Si clôture est NC (non coté), le cours actuel reste le dernier connu (close_p)
            if quote["close"] is not None:
                company["currentPrice"] = quote["close"]
                company["change"] = quote["change"]
                # Mettre à jour l'historique 2026
                if "history" in company and 2026 in company["history"]:
                    company["history"]["2026"]["price"] = quote["close"]
            else:
                # Non coté aujourd'hui, la variation est nulle pour cette séance
                company["change"] = "0,00 %"
                
            company["open"] = quote["open"]
            company["close"] = quote["close"]
        else:
            # Pas trouvé dans le rapport de négociation de cette séance
            company["change"] = "0,00 %"
            company["open"] = None
            company["close"] = None
            
        updated_companies[ticker] = company

    existing_data["companies"] = updated_companies
    existing_data["bonds"] = scraped_bonds
    existing_data["orders"] = scraped_orders

    # 5.5 Récupérer les 9 derniers bulletins (BOM)
    avis_url = "https://www.sgbv.dz/?page=avis&lang=fr"
    scraped_bulletins = []
    try:
        req_avis = urllib.request.Request(avis_url, headers=headers)
        with urllib.request.urlopen(req_avis, timeout=15) as response:
            avis_html = response.read().decode('utf-8')
        
        avis_parser = SGBVAvisParser()
        avis_parser.feed(avis_html)
        scraped_bulletins = avis_parser.bulletins[:9]
        print(f"Scrapé avec succès {len(scraped_bulletins)} bulletins (BOM).")
    except Exception as e:
        print(f"Erreur lors de la récupération des avis (BOM) : {e}")

    if scraped_bulletins:
        existing_data["bulletins"] = scraped_bulletins
    else:
        if "bulletins" not in existing_data:
            existing_data["bulletins"] = []

    # 6. Mettre à jour l'historique du Dzair Index
    # Si nous avons extrait l'historique Highcharts
    if raw_history:
        # Filtrer pour s'assurer que c'est propre
        existing_data["index_history"] = raw_history
    else:
        # Sinon, on procède de manière incrémentale
        index_history = existing_data.get("index_history", [])
        # Ajouter le point actuel si la date est nouvelle
        # Pour cet exemple local, on génère un timestamp basé sur le jour de séance
        import datetime
        try:
            # Tenter d'analyser la date scrapée (Ex: "15 Juillet 2026")
            months = {"Janvier": 1, "Février": 2, "Mars": 3, "Avril": 4, "Mai": 5, "Juin": 6, 
                      "Juillet": 7, "Août": 8, "Septembre": 9, "Octobre": 10, "Novembre": 11, "Décembre": 12}
            parts = session_date.split()
            day = int(parts[0])
            month = months[parts[1]]
            year = int(parts[2])
            dt = datetime.datetime(year, month, day)
            ts = int(dt.timestamp() * 1000)
            
            # Ajouter si non présent
            if not any(point[0] == ts for point in index_history):
                index_history.append([ts, index_val if index_val else 3843.95])
                # Garder trié
                index_history.sort(key=lambda x: x[0])
        except Exception:
            pass
            
        existing_data["index_history"] = index_history

    # Sauvegarder dans le JSON
    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=4, ensure_ascii=False)
        
    print(f"Base de données '{db_file}' actualisée avec succès pour la séance du {formatted_date}.")

    # Mettre à jour index.html avec le nouveau fallback local
    html_file = "index.html"
    if os.path.exists(html_file):
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            start_marker = "const localMarketDataFallback = {"
            end_marker = "let marketData = localMarketDataFallback;"
            
            start_idx = html_content.find(start_marker)
            end_idx = html_content.find(end_marker)
            
            if start_idx != -1 and end_idx != -1:
                fallback_js = "const localMarketDataFallback = " + json.dumps(existing_data, indent=4, ensure_ascii=False) + ";"
                new_html_content = html_content[:start_idx] + fallback_js + "\n\n        " + html_content[end_idx:]
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(new_html_content)
                print(f"Fallback local de '{html_file}' mis à jour avec succès.")
        except Exception as e:
            print(f"Impossible de mettre à jour le fallback local dans index.html : {e}")

if __name__ == "__main__":
    run_scraper()
