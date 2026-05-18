import pandas as pd
from textblob import TextBlob

FRAMEWORKS = ['langchain', 'crewai', 'autogen', 'langgraph', 'haystack']

def count_mentions(df: pd.DataFrame) -> pd.DataFrame:
    """Compte les mentions de chaque framework."""
    mentions = {fw: 0 for fw in FRAMEWORKS}
    
    for _, row in df.iterrows():
        text = str(row['content']) + ' ' + str(row['title'])
        for fw in FRAMEWORKS:
            if fw in text.lower():
                mentions[fw] += 1
    
    result = pd.DataFrame({
        'framework': list(mentions.keys()),
        'mentions': list(mentions.values())
    })
    return result

def calculate_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    """Analyse de sentiment pour chaque framework."""
    sentiments = {fw: [] for fw in FRAMEWORKS}
    
    for _, row in df.iterrows():
        text = str(row['content'])
        for fw in FRAMEWORKS:
            if fw in text.lower():
                score = TextBlob(text).sentiment.polarity
                sentiments[fw].append(score)
    
    result = pd.DataFrame({
        'framework': FRAMEWORKS,
        'sentiment_moyen': [
            round(sum(v)/len(v), 3) if v else 0
            for v in sentiments.values()
        ]
    })
    return result

def calculate_growth(df: pd.DataFrame) -> pd.DataFrame:
    """Calcule la croissance des mentions par mois."""
    df['month'] = df['date'].dt.to_period('M')
    growth = {}
    
    for fw in FRAMEWORKS:
        monthly = df[df['content'].str.contains(fw, na=False)]\
                    .groupby('month').size()
        growth[fw] = monthly
    
    return pd.DataFrame(growth).fillna(0)