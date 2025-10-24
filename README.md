# 🤖 AI Trading Assistant — Projet de fin de formation Python

Un mini-projet de **trading algorithmique** développé en Python, combinant :
- Programmation orientée objet (OOP)
- Gestion de fichiers
- Gestion des erreurs
- Préparation pour intégration IA (GPT, DeepSeek, Claude)

## 🎯 Objectif du projet

L’objectif est de créer un **robot de trading modulaire et évolutif**, capable d’exécuter des stratégies simples fondées sur la **convergence entre les bandes de Bollinger et les canaux de Keltner**, sur des créneaux horaires précis (Killzone 03h00–06h30).

Ce projet sert de **base** pour :
- Étendre vers d’autres stratégies (Ichimoku, RSI, Fibonacci…)
- Ajouter des modules d’IA (analyse automatique des signaux)
- Réaliser des backtests complets et traçables

---

## 🧱 Architecture du projet


---

## ⚙️ Fonctionnalités

- 🧠 **Stratégie de convergence Bollinger + Keltner**
- ⏰ **Killzone filtrée** : ne trade qu’entre 03h00 et 06h30
- 🧩 **Architecture modulaire** (extensible pour d’autres stratégies)
- 💾 **Lecture automatique** de fichiers CSV (OHLC)
- 📊 **Backtest rapide** avec affichage des signaux générés

---

# Projet Final Python – Stratégie BB + Keltner + GPT

Ce projet contient deux modes :

1. **Backtest historique** sur CSV  
2. **Démo journalière** avec analyse fondamentale + confirmation GPT  

---

## 1️⃣ Prérequis

- Python 3.11+  
- Git  
- Connexion Internet (pour scraping et GPT)  

---

## 2️⃣ Cloner le projet

git clone https://github.com/<votre_user>/Projet_final_formation.git
cd Projet_final_formation

3️⃣ Créer l'environnement Python
Windows :

python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt


Linux / Mac :

^python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt^

4️⃣ Backtest historique
Le backtest utilise les CSV dans data/ pour XAUUSD et EURUSD.

python main.py

Ce que cela fait:
Charge les données CSV (data/XAUUSD.csv, data/EURUSD.csv)
Exécute la stratégie BB + Keltner
Génère les signaux de trade
Calcule le money management sur un compte fictif de 100 000 €
Sauvegarde les résultats dans data/results_XAUUSD.csv et data/results_EURUSD.csv
Les fichiers historiques ne sont pas modifiés et peuvent être remplacés si besoin.

5️⃣ Démo journalière (_demo)

Cette démo montre un trade hypothétique pour un jour spécifique avec confirmation GPT.

Structure des fichiers démo :

core/strategy_demo.py
indicators/bollinger_bands_demo.py
indicators/keltner_channel_demo.py
utils/fundamental_scraper_demo.py
utils/gpt_analyzer_trade_demo.py
main_demo.py

Lancer la démo
python main_demo.py

Ce que cela fait
Scrape les données fondamentales du jour (annonces économiques)
Définit un trade hypothétique (signal, entry, stop, TP)
Envoie le trade + fondamentaux à GPT (gpt_analyzer_trade_demo)
Affiche dans le terminal :
Résumé de l’analyse fondamentale
Confirmation si le trade est cohérent ou non








