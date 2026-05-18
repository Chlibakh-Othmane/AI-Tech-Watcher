import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import plotly.graph_objects as go

def plot_mentions_bar(mentions_df: pd.DataFrame, save_path: str):
    """Graphique barres — popularité des frameworks."""
    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=mentions_df.sort_values('mentions', ascending=False),
        x='framework', y='mentions',
        palette='viridis'
    )
    plt.title('🔥 Popularité des Frameworks IA', fontsize=16)
    plt.xlabel('Framework')
    plt.ylabel('Nombre de mentions')
    plt.tight_layout()
    plt.savefig(f"{save_path}/mentions_bar.png", dpi=150)
    plt.close()
    print("✅ Graphique barres sauvegardé")

def plot_growth_line(growth_df: pd.DataFrame, save_path: str):
    """Graphique lignes — évolution dans le temps."""
    plt.figure(figsize=(12, 6))
    for col in growth_df.columns:
        plt.plot(growth_df.index.astype(str),
                 growth_df[col], marker='o', label=col)
    plt.title('📈 Croissance des Frameworks IA', fontsize=16)
    plt.xlabel('Mois')
    plt.ylabel('Mentions')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{save_path}/growth_line.png", dpi=150)
    plt.close()
    print("✅ Graphique croissance sauvegardé")

def plot_sentiment_radar(sentiment_df: pd.DataFrame, save_path: str):
    """Graphique radar — sentiment par framework."""
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=sentiment_df['sentiment_moyen'],
        theta=sentiment_df['framework'],
        fill='toself',
        name='Sentiment'
    ))
    fig.update_layout(
        title='🎯 Analyse de Sentiment par Framework',
        polar=dict(radialaxis=dict(visible=True, range=[-1, 1]))
    )
    fig.write_html(f"{save_path}/sentiment_radar.html")
    print("✅ Radar sentiment sauvegardé")

def generate_comparison_table(mentions_df, sentiment_df) -> pd.DataFrame:
    """Tableau comparatif final."""
    table = mentions_df.merge(sentiment_df, on='framework')
    table['score_global'] = (
        table['mentions'] * 0.7 +
        table['sentiment_moyen'] * 10 * 0.3
    ).round(2)
    table = table.sort_values('score_global', ascending=False)
    table['rang'] = range(1, len(table) + 1)
    table.to_csv('outputs/tables/tableau_comparatif.csv', index=False)
    print("✅ Tableau comparatif exporté")
    return table