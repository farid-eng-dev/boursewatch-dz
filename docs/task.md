# Plan de Travail - Refonte Bourse d'Alger

Ce document suit l'avancement de la construction de la plateforme automatisée de la Bourse d'Alger.

- `[x]` **Étape 1 : Moteur de Scraping (Backend)**
  - `[x]` Créer `scraper.py` pour extraire les données de `sgvb.dz` (Séance, Dzair Index, Actions, Obligations OAT, Bulletins PDF).
  - `[x]` Écrire un mécanisme de mise à jour incrémentale de l'historique dans `market_data.json` (sans données fictives).
  - `[x]` Tester localement le scraper et valider le format JSON généré.
- `[x]` **Étape 2 : Initialisation des Données**
  - `[x]` Lancer le scraper une première fois pour générer le fichier initial `market_data.json` avec des données réelles.
- `[x]` **Étape 3 : Interface Utilisateur (Frontend)**
  - `[x]` Refondre `index.html` pour charger dynamiquement `market_data.json`.
  - `[x]` Intégrer les indicateurs clés de séance (KPIs).
  - `[x]` Développer le graphique dynamique (SVG) du *Dzair Index* alimenté par l'historique réel accumulé.
  - `[x]` Créer l'onglet Actions (avec recherche, tri, filtrage sectoriel) et l'onglet Obligations OAT.
  - `[x]` Créer le module Palmarès (Hausse / Baisse) et le graphique sectoriel en anneau (SVG).
  - `[x]` Intégrer les fiches d'identité détaillées dans le panneau latéral (drawer).
- `[x]` **Étape 4 : Automatisation & Déploiement**
  - `[x]` Créer le workflow GitHub Actions `.github/workflows/auto_update.yml` pour le lancement quotidien automatique du scraper.
  - `[x]` Créer les configurations pour un déploiement Vercel/Netlify.
- `[x]` **Étape 5 : Validation & Walkthrough**
  - `[x]` Faire un test complet d'impression PDF.
  - `[x]` Mettre à jour le guide de livraison final.
