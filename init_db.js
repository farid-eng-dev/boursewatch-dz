const fs = require('fs');
const path = require('path');

// Paths
const contentPath = 'C:\\Users\\HIGH TECH\\.gemini\\antigravity\\brain\\5158daca-75da-45d7-b596-d66eb9acb3a4\\.system_generated\\logs\\../steps/104/content.md';
const dbPath = path.join(__dirname, 'market_data.json');

try {
    // Read the html content file
    const content = fs.readFileSync(contentPath, 'utf8');
    console.log("Lecture du fichier HTML effectuée.");

    // 1. Extract Dzair Index History
    const historyRegex = /name\s*:\s*'Dzair Indice',\s*data\s*:\s*(\[\[.*?\]\])/s;
    const historyMatch = content.match(historyRegex);
    let indexHistory = [];
    
    if (historyMatch) {
        try {
            // Clean up whitespace to parse as JSON
            const cleanJsonStr = historyMatch[1].replace(/\s+/g, '');
            indexHistory = JSON.parse(cleanJsonStr);
            console.log(`Historique extrait : ${indexHistory.length} points de données réels.`);
        } catch (e) {
            console.error("Erreur de parsing de l'historique Highcharts :", e.message);
        }
    } else {
        console.warn("Historique de l'indice non trouvé dans l'HTML.");
    }

    // 2. Default Company Profiles (with historical dividends and static profile)
    const defaultProfiles = {
        "CPA": {
            "ticker": "CPA",
            "name": "Crédit Populaire d'Algérie",
            "sector": "Bancaire",
            "sectorKey": "Bancaire",
            "ipoYear": 2024,
            "ipoPrice": 2300,
            "currentPrice": 2300.00,
            "change": "0,00 %",
            "open": 2300.00,
            "close": 2300.00,
            "volume": 120,
            "value": 276000.00,
            "description": "Le Crédit Populaire d'Algérie (CPA) est l'une des plus importantes institutions bancaires publiques en Algérie. Son introduction en bourse en 2024 a constitué la plus grande opération historique de la place d'Alger, ouvrant avec succès 30% de son capital au public.",
            "div2023": 125, "div2024": 125, "div2025": 175.00, "yield": 7.61, "yieldTarget": false,
            "history": {
                "2023": { "price": null, "div": 125 },
                "2024": { "price": 2300, "div": 125 },
                "2025": { "price": 2300, "div": 175 },
                "2026": { "price": 2300.00, "div": null }
            }
        },
        "BIO": {
            "ticker": "BIO",
            "name": "Biopharm",
            "sector": "Pharmaceutique",
            "sectorKey": "Pharmaceutique",
            "ipoYear": 2016,
            "ipoPrice": 1225,
            "currentPrice": 2510.00,
            "change": "0,00 %",
            "open": 2510.00,
            "close": 2510.00,
            "volume": 450,
            "value": 1129500.00,
            "description": "Biopharm est un laboratoire pharmaceutique algérien intégré, leader dans le secteur de la santé. Il exerce des activités de développement, production, distribution et d'information médicale. C'est l'un des titres les plus dynamiques en termes de valorisation boursière.",
            "div2023": 180, "div2024": 160, "div2025": 170.00, "yield": 6.77, "yieldTarget": false,
            "history": {
                "2023": { "price": 2400, "div": 180 },
                "2024": { "price": 2450, "div": 160 },
                "2025": { "price": 2500, "div": 170 },
                "2026": { "price": 2510.00, "div": null }
            }
        },
        "BDL": {
            "ticker": "BDL",
            "name": "Banque du Développement Local",
            "sector": "Bancaire",
            "sectorKey": "Bancaire",
            "ipoYear": 2024,
            "ipoPrice": 1400,
            "currentPrice": 1405.00,
            "change": "0,00 %",
            "open": 1405.00,
            "close": 1405.00,
            "volume": 12000,
            "value": 16860000.00,
            "description": "La Banque du Développement Local (BDL) est une banque publique majeure introduite à la bourse d'Alger en 2024. Elle se concentre sur le financement du tissu industriel local, de l'artisanat, des PME ainsi que des services bancaires de proximité.",
            "div2023": null, "div2024": 77, "div2025": 107.00, "yield": 7.64, "yieldTarget": false,
            "history": {
                "2023": { "price": null, "div": null },
                "2024": { "price": 1400, "div": 77 },
                "2025": { "price": 1402, "div": 107 },
                "2026": { "price": 1405.00, "div": null }
            }
        },
        "ALL": {
            "ticker": "ALL",
            "name": "Alliance Assurances",
            "sector": "Assurances",
            "sectorKey": "Assurances",
            "ipoYear": 2010,
            "ipoPrice": 830,
            "currentPrice": 345.00,
            "change": "0,00 %",
            "open": 345.00,
            "close": 345.00,
            "volume": 80,
            "value": 27600.00,
            "description": "Alliance Assurances est le pionnier des compagnies privées d'assurances cotées à la Bourse d'Alger. Elle fournit un catalogue complet d'offres de couverture (automobile, risques industriels, santé) pour les particuliers et le corporate.",
            "div2023": 32, "div2024": 28, "div2025": 35.00, "yield": 10.14, "yieldTarget": false,
            "history": {
                "2023": { "price": 330, "div": 32 },
                "2024": { "price": 340, "div": 28 },
                "2025": { "price": 342, "div": 35 },
                "2026": { "price": 345.00, "div": null }
            }
        },
        "SAI": {
            "ticker": "SAI",
            "name": "Saidal",
            "sector": "Pharmaceutique",
            "sectorKey": "Pharmaceutique",
            "ipoYear": 1999,
            "ipoPrice": 800,
            "currentPrice": 446.00,
            "change": "0,00 %",
            "open": 446.00,
            "close": 446.00,
            "volume": 500,
            "value": 223000.00,
            "description": "Saidal est le groupe pharmaceutique étatique historique et pionnier de la bourse depuis 1999. Saidal joue un rôle stratégique national dans la production de médicaments génériques et le développement de la souveraineté sanitaire algérienne.",
            "div2023": 15, "div2024": 21, "div2025": 24.00, "yield": 5.38, "yieldTarget": false,
            "history": {
                "2023": { "price": 420, "div": 15 },
                "2024": { "price": 435, "div": 21 },
                "2025": { "price": 440, "div": 24 },
                "2026": { "price": 446.00, "div": null }
            }
        },
        "AUR": {
            "ticker": "AUR",
            "name": "EGH El Aurassi",
            "sector": "Hôtellerie",
            "sectorKey": "Immo/Hôtellerie",
            "ipoYear": 1999,
            "ipoPrice": 400,
            "currentPrice": 360.00,
            "change": "0,00 %",
            "open": 360.00,
            "close": 360.00,
            "volume": 0,
            "value": 0.00,
            "description": "L'Entreprise de Gestion Hôtelière (EGH) El Aurassi gère le prestigieux Hôtel Aurassi à Alger. Introduite en 1999, la société tire ses revenus de l'hôtellerie d'affaires, des congrès officiels et des services haut de gamme de restauration.",
            "div2023": 0, "div2024": 0, "div2025": 0.00, "yield": 0.00, "yieldTarget": false,
            "history": {
                "2023": { "price": 520, "div": 0 },
                "2024": { "price": 535, "div": 0 },
                "2025": { "price": 545, "div": 0 },
                "2026": { "price": 360.00, "div": null }
            }
        },
        "AYRD": {
            "ticker": "AYRD",
            "name": "AYRADE",
            "sector": "Technologie",
            "sectorKey": "Technologie",
            "ipoYear": 2026,
            "ipoPrice": 800,
            "currentPrice": 810.00,
            "change": "+1,25 %",
            "open": 800.00,
            "close": 810.00,
            "volume": 20,
            "value": 16200.00,
            "description": "Ayrade est une société technologique dynamique introduite en 2026. Actrice majeure dans les solutions logicielles, d'hébergement web cloud et de transformation digitale en Algérie, elle vise à dynamiser le compartiment technologique de la bourse.",
            "div2023": null, "div2024": null, "div2025": 0.00, "yield": 9.45, "yieldTarget": true,
            "history": {
                "2023": { "price": null, "div": null },
                "2024": { "price": null, "div": null },
                "2025": { "price": null, "div": 0 },
                "2026": { "price": 810.00, "div": null }
            }
        },
        "CREX": {
            "ticker": "CREX",
            "name": "CRAPC EXPERTISE",
            "sector": "Conseil / Audit",
            "sectorKey": "Services",
            "ipoYear": 2026,
            "ipoPrice": 1600,
            "currentPrice": 1600.00,
            "change": "0,00 %",
            "open": 1600.00,
            "close": 1600.00,
            "volume": 0,
            "value": 0.00,
            "description": "Le CRAPC (Expertise) est un cabinet de premier plan spécialisé dans les conseils stratégiques, d'audit comptable et financier et de gouvernance d'entreprise. Il s'agit d'une des récentes introductions boursières de 2026.",
            "div2023": null, "div2024": null, "div2025": 0.00, "yield": 0.00, "yieldTarget": false,
            "history": {
                "2023": { "price": null, "div": null },
                "2024": { "price": null, "div": null },
                "2025": { "price": null, "div": 0 },
                "2026": { "price": 1600.00, "div": null }
            }
        },
        "MST": {
            "ticker": "MST",
            "name": "Moustachir",
            "sector": "Conseil PME",
            "sectorKey": "Services",
            "ipoYear": 2024,
            "ipoPrice": 750,
            "currentPrice": 780.00,
            "change": "0,00 %",
            "open": 780.00,
            "close": 780.00,
            "volume": 0,
            "value": 0.00,
            "description": "Moustachir est un intermédiaire et cabinet conseil dédié aux projets de restructuration, d'ingénierie financière et d'accompagnement des petites et moyennes entreprises pour l'accès aux financements et marchés de capitaux.",
            "div2023": null, "div2024": 0, "div2025": 0.00, "yield": 0.00, "yieldTarget": false,
            "history": {
                "2023": { "price": null, "div": null },
                "2024": { "price": 750, "div": 0 },
                "2025": { "price": 765, "div": 0 },
                "2026": { "price": 780.00, "div": null }
            }
        },
        "AOM": {
            "ticker": "AOM",
            "name": "AOM Invest",
            "sector": "Tourisme / Immo",
            "sectorKey": "Immo/Hôtellerie",
            "ipoYear": 2018,
            "ipoPrice": 400,
            "currentPrice": 290.00,
            "change": "0,00 %",
            "open": 290.00,
            "close": 290.00,
            "volume": 0,
            "value": 0.00,
            "description": "AOM Invest est une entreprise privée d'investissement à vocation touristique et immobilière. Introduite sur la bourse des PME en 2018, elle gère des actifs de loisir, d'hôtellerie balnéaire et des programmes de promotion touristique.",
            "div2023": 0, "div2024": 0, "div2025": 0.00, "yield": 0.00, "yieldTarget": false,
            "history": {
                "2023": { "price": 310, "div": 0 },
                "2024": { "price": 300, "div": 0 },
                "2025": { "price": 295, "div": 0 },
                "2026": { "price": 290.00, "div": null }
            }
        }
    };

    // 3. Extract Session Date
    const dateRegex = /<center><h2>\s*(\d+\s+\w+\s+\d{4})\s*<\/h2><\/center>/s;
    const dateMatch = content.match(dateRegex);
    let sessionDate = "15 Juillet 2026";
    if (dateMatch) {
        sessionDate = dateMatch[1].trim().replace(/\s+/g, ' ');
    }
    
    const dayRegex = /Séance du (\w+)/;
    const dayMatch = content.match(dayRegex);
    let sessionDay = "Mercredi";
    if (dayMatch) {
        sessionDay = dayMatch[1];
    }
    
    const formattedDate = `${sessionDay} ${sessionDate}`;
    console.log(`Séance détectée : ${formattedDate}`);

    // 4. Extract current Dzair Index
    const indexValRegex = /<div id="indice-var">.*?<span>\s*([\d\s,.]+)\s*<\/span>/s;
    const indexValMatch = content.match(indexValRegex);
    let indexValue = 3843.95;
    if (indexValMatch) {
        indexValue = parseFloat(indexValMatch[1].replace(/\s+/g, '').replace(',', '.'));
    }

    const indexVarRegex = /<div id="indice-var">.*?<span class="black">\s*([\d\s,.-]+)\s*%\s*<\/span>/s;
    const indexVarMatch = content.match(indexVarRegex);
    let indexChange = "0,00 %";
    if (indexVarMatch) {
        indexChange = indexVarMatch[1].trim().replace('.', ',') + " %";
    }

    console.log(`Dzair Index : ${indexValue} (${indexChange})`);

    // 5. Structure market statistics
    const sessionData = {
        "session": {
            "date": formattedDate,
            "index_name": "Dzair Index",
            "index_value": indexValue,
            "index_change": indexChange,
            "total_volume_equities": 15040,
            "total_value_equities": 21119300.00,
            "total_volume_bonds": 4000,
            "total_value_bonds": 3577880000.00,
            "market_cap": 744881789920.00 // Cap globale
        },
        "companies": defaultProfiles,
        "bonds": [
            { "ticker": "AL30", "name": "ARAB LEASING CORPORATION", "open": 100.00, "close": 100.00, "change": "0,00 %", "coupon": "OBLIG 6.5%" },
            { "ticker": "ML30", "name": "MAGHREB LEASING ALGERIE", "open": 100.00, "close": 100.00, "change": "0,00 %", "coupon": "OBLIG 6.25%" },
            { "ticker": "TS30", "name": "TOSYALI ALGERIE", "open": 99.00, "close": 99.00, "change": "0,00 %", "coupon": "OBLIG 5.75%" }
        ],
        "index_history": indexHistory
    };

    // Write to market_data.json
    fs.writeFileSync(dbPath, JSON.stringify(sessionData, null, 4), 'utf8');
    console.log("Fichier 'market_data.json' créé et initialisé avec succès !");

} catch (err) {
    console.error("Erreur générale :", err.message);
}
