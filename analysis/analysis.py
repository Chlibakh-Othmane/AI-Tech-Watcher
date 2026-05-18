"""
Personne 2 — Agent d'analyse IA
Point d'entrée principal de l'agent d'analyse.
"""

import sys
import os
import json
import pandas as pd

# Ajouter le dossier analysis au path
sys.path.append(os.path.dirname(__file__))

from cleaner import clean_data
from scorer import count_mentions, calculate_sentiment, calculate_growth
from visualizer import (
    plot_mentions_bar,
    plot_growth_line,
    plot_sentiment_radar,
    generate_comparison_table
)

GRAPH_PATH = "outputs/graphs"
TABLE_PATH = "outputs/tables"


def load_raw_data(filepath: str) -> list:
    """Charge les données JSON de Personne 1."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ {len(data)} articles chargés")
        return data
    except FileNotFoundError:
        print("⚠️  Fichier introuvable — données de test utilisées")
        return [
            {"title": "LangChain new release", "source": "HuggingFace",
             "date": "2024-03-01", "content": "langchain is growing fast"},
            {"title": "AutoGen vs CrewAI", "source": "Reddit",
             "date": "2024-03-05", "content": "crewai autogen comparison"},
            {"title": "LangGraph tutorial", "source": "OpenAI",
             "date": "2024-03-10", "content": "langgraph workflow tutorial"},
            {"title": "Haystack update", "source": "GitHub",
             "date": "2024-03-15", "content": "haystack new features"},
            {"title": "LangChain vs LangGraph", "source": "Reddit",
             "date": "2024-04-01", "content": "langchain langgraph comparison"},
        ]


def run_analysis(data_filepath: str = "data/raw_data.json"):
    print("\n🚀 Démarrage de l'analyse IA...\n")

    # 1. Charger et nettoyer
    raw = load_raw_data(data_filepath)
    df  = clean_data(raw)

    # 2. Calculer les scores
    mentions  = count_mentions(df)
    sentiment = calculate_sentiment(df)
    growth    = calculate_growth(df)

    # 3. Générer les visuels
    plot_mentions_bar(mentions, GRAPH_PATH)
    plot_growth_line(growth, GRAPH_PATH)
    plot_sentiment_radar(sentiment, GRAPH_PATH)

    # 4. Tableau comparatif final
    table = generate_comparison_table(mentions, sentiment)

    print("\n📊 TABLEAU COMPARATIF FINAL :")
    print(table.to_string(index=False))
    print("\n✅ Analyse terminée — résultats dans /outputs")

    return {
        "dataframe"    : df,
        "mentions"     : mentions,
        "sentiment"    : sentiment,
        "growth"       : growth,
        "tableau_final": table
    }


if __name__ == "__main__":
    run_analysis()