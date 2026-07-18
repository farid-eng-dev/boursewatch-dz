# Guide & Bilan de Livraison - BourseWatch DZ

Ce document détaille l'architecture technique complète et les guides d'installation de la plateforme web autonome et automatisée **BourseWatch DZ**.

---

## 🏗️ Architecture du Système Serverless

Le projet utilise une architecture **JAMstack 100% serverless et gratuite** :
1. **Source de données :** Le site officiel de la bourse (`sgbv.dz`).
2. **Scraper (Python) :** `scraper.py` extrait la séance, les cours des actions, les obligations OAT et les bulletins officiels quotidiens.
3. **Base de données (JSON) :** `market_data.json` sert de stockage structulé local (contenant l'historique complet réel du *Dzair Index* sur 769 points).
4. **Automatisation (GitHub Actions) :** Un workflow `.github/workflows/auto_update.yml` exécute le scraper tous les jours de bourse à 13h00 (après la clôture) et pousse les modifications JSON sur le dépôt Git.
5. **Hébergement & Déploiement (Vercel / Netlify / Cloudflare Pages) :** Connecté au dépôt Git privé, l'hébergeur redéploie le site statique instantanément à chaque push de données (durée de build : ~5 secondes).

---

## 📁 Fichiers du Projet et Rôles

*   📁 **[.github/workflows/auto_update.yml](file:///d:/DEV%20APP%20GRAVITY/Nouveau%20dossier%20(2)/.github/workflows/auto_update.yml) :** Script d'automatisation (workflow GitHub Actions) programmé du lundi au vendredi à 13h00 (heure d'Alger).
*   🐍 **[scraper.py](file:///d:/DEV%20APP%20GRAVITY/Nouveau%20dossier%20(2)/scraper.py) :** Script Python d'extraction robuste (sans dépendance externe requise, utilise uniquement les bibliothèques standard de Python).
*   💾 **[market_data.json](file:///d:/DEV%20APP%20GRAVITY/Nouveau%20dossier%20(2)/market_data.json) :** La base de données JSON structurée. Contient **769 points d'historique réel** de l'indice Dzair Index.
*   📄 **[index.html](file:///d:/DEV%20APP%20GRAVITY/Nouveau%20dossier%20(2)/index.html) :** L'interface utilisateur web monopage avec styles CSS intégrés (Sombre premium à l'écran, Clair haute fidélité pour impression).
*   ⚙️ **[vercel.json](file:///d:/DEV%20APP%20GRAVITY/Nouveau%20dossier%20(2)/vercel.json) :** Configuration de déploiement interdisant la mise en cache HTTP de `market_data.json` pour garantir des cours toujours frais.

---

## 🎨 Fonctionnalités Visuelles et Dashboard

### 1. Mode Écran : Outils de Visualisation Financière
*   **Indicateurs clés (KPIs) :** Blocs en haut de page affichant la valeur de l'indice, la capitalisation globale des actions, le volume de transaction du jour, et la valeur des échanges actions/obligations.
*   **Graphique Dzair Index (SVG Interactif) :** Un graphique de tendance de l'indice avec filtres de période (**1 Mois**, **3 Mois**, **1 Année**, **Tout**), tracé avec un dégradé lumineux sous la courbe. **Curseur interactif (Crosshair) :** Le survol du graphique affiche une ligne de visée et un tooltip détaillant la valeur exacte et la date.
*   **Répartition Sectorielle (SVG Donut) :** Un diagramme circulaire montrant la part de capitalisation de chaque secteur d'activité (Bancaire, Pharma, Assurances, Services, Tech, Tourisme).
*   **Palmarès de Séance :** Bloc mettant en évidence le classement des plus fortes variations (hausses/baisses) de la journée.
*   **Tableaux à Onglets :**
    *   *Actions :* Tableau triable par colonne, filtrable par secteur, et avec barre de recherche.
    *   *Obligations OAT :* Tableau complet des lignes obligataires d'État et des cours de clôture.
    *   *Bulletins :* Accès en un clic aux PDF officiels de la bourse.
*   **Drawer (Panneau Latéral Actif) :** Cliquer sur une ligne de tableau affiche la description de la société, l'historique d'admission, le rendement, la performance globale depuis l'introduction (calculée automatiquement) et le graphique SVG de ses dividendes (2023-2025).

### 2. Mode Impression : Rapport Financier de 2 Pages
La feuille de style d'impression (`@media print`) convertit l'interface sombre en un document blanc haute fidélité :
*   **Page 1 :** Récapitulatif de séance, tableau de la cote officielle des actions, tableau du marché obligataire OAT.
*   **Page 2 :** Fiches d'identité individuelles de chaque entreprise listée (historiques, descriptions, graphiques de dividendes).

---

## 🚀 Guide de Déploiement Étape par Étape

Pour mettre en ligne le projet gratuitement dans un dépôt privé :

### Étape 1 : Créer le Dépôt sur GitHub
1. Connectez-vous sur votre compte GitHub.
2. Créez un nouveau dépôt et choisissez l'option **Private** (Privé).
3. Poussez les fichiers locaux de votre dossier `d:\DEV APP GRAVITY\Nouveau dossier (2)` sur ce dépôt (fichiers `.github/`, `scraper.py`, `market_data.json`, `index.html`, `vercel.json`).

### Étape 2 : Connecter et Héberger Gratuitement sur Vercel
1. Rendez-vous sur [vercel.com](https://vercel.com/) et connectez-vous avec votre compte GitHub.
2. Cliquez sur **Add New** > **Project**.
3. Importez votre dépôt privé fraîchement créé.
4. Dans les paramètres de configuration, laissez tout par défaut (aucun build step requis, il détectera l'index.html statique).
5. Cliquez sur **Deploy**. Votre site est maintenant en ligne !

### Étape 3 : Autoriser l'Action d'Écriture sur GitHub
Pour que GitHub Actions puisse pousser le fichier JSON mis à jour par le scraper, donnez-lui les droits d'écriture :
1. Sur la page de votre dépôt GitHub, allez dans **Settings** > **Actions** > **General**.
2. Faites défiler vers le bas jusqu'à la section **Workflow permissions**.
3. Sélectionnez **Read and write permissions**.
4. Cochez **Allow GitHub Actions to create and approve pull requests** et cliquez sur **Save**.

Désormais, tous les jours à 13h00 heure d'Alger, le scraper s'exécutera sur GitHub, mettra à jour `market_data.json` avec les données officielles réelles, poussera le fichier, et Vercel reconstruira instantanément le site sans que vous n'ayez à lever le petit doigt.

---

## 🎨 Actifs de Marque (Brand Assets)

Les fichiers d'identité de marque suivants ont été générés et configurés :
- **[logo.png](file:///d:/DEV%20APP%20GRAVITY/Nouveau%20dossier%20(2)/logo.png)** : Le logo officiel de la plateforme, affiché dans l'en-tête du site.
- **[favicon.png](file:///d:/DEV%20APP%20GRAVITY/Nouveau%20dossier%20(2)/favicon.png)** : L'icône de favori (favicon) du site, affichée dans l'onglet du navigateur de vos utilisateurs.
