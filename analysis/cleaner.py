import pandas as pd
import re

def clean_data(raw_data: list) -> pd.DataFrame:
    df = pd.DataFrame(raw_data)
    
    # Supprimer les doublons
    df.drop_duplicates(subset=['title'], inplace=True)
    
    # Nettoyer le texte
    df['content'] = df['content'].str.lower()
    df['content'] = df['content'].apply(
        lambda x: re.sub(r'[^a-zA-Z0-9\s]', '', str(x))
    )
    
    # Valeurs manquantes
    df.fillna('unknown', inplace=True)
    
    # Convertir les dates
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    print(f"✅ Données nettoyées : {len(df)} entrées")
    return df