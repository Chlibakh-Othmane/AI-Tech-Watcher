# Importation du module json pour travailler avec des fichiers JSON
import json


# =========================================================
# 1. CHARGEMENT DE LA MEMOIRE INTERNE
# =========================================================
def load_memory(path="knowledge_base/data_internal.json"):
    """
    Charge les donnees internes de l'entreprise depuis un fichier JSON.
    Cette memoire represente le contexte interne du systeme.
    
    Argument:
        path: chemin vers le fichier JSON (valeur par defaut: "knowledge_base/data_internal.json")
    
    Retourne:
        Un dictionnaire Python contenant toutes les donnees de l'entreprise
    """
    # "with" ouvre le fichier et le ferme automatiquement a la fin
    # "r" signifie mode lecture (read)
    # encoding="utf-8" permet de lire correctement les accents et caracteres speciaux
    with open(path, "r", encoding="utf-8") as file:
        # json.load() convertit le contenu JSON du fichier en dictionnaire Python
        memory = json.load(file)
    
    # On retourne le dictionnaire charge
    return memory


# =========================================================
# 2. RECHERCHE SIMPLE DANS LA MEMOIRE
# =========================================================
def search_memory(memory, key):
    """
    Permet de recuperer une information precise dans la memoire interne.
    Exemple: stack_actuelle, frameworks_utilises, priorite, etc.
    
    Arguments:
        memory: le dictionnaire contenant les donnees internes
        key: la clef a rechercher (exemple: "frameworks_utilises")
    
    Retourne:
        La valeur associee a la clef, ou None si la clef n'existe pas
    """
    # La methode .get() est plus sure que memory[key] car elle ne plante pas si la clef n'existe pas
    # Si la clef n'existe pas, .get() retourne None (ou la valeur par defaut si on en donne une)
    return memory.get(key, None)


# =========================================================
# 3. RECHERCHE AVANCEE (MOTS-CLES)
# =========================================================
def search_memory_advanced(memory, query):
    """
    Recherche des informations dans la memoire interne
    en utilisant des mots-cles simples.
    
    Cette fonction parcourt TOUTES les valeurs du dictionnaire
    pour trouver celles qui contiennent le mot recherche.
    
    Arguments:
        memory: le dictionnaire contenant les donnees internes
        query: le mot ou texte a rechercher
    
    Retourne:
        Un dictionnaire contenant uniquement les entrees qui correspondent
    """
    # Dictionnaire vide qui va contenir les resultats
    results = {}
    
    # Conversion du terme de recherche en minuscules pour ignorer la casse
    # Exemple: "Python" et "python" seront consideres comme identiques
    query = query.lower()
    
    # .items() permet de parcourir chaque paire (clef, valeur) du dictionnaire
    # Exemple: ("entreprise", "AI Consulting Maroc"), ("stack_actuelle", ["Python", "FastAPI"])
    for key, value in memory.items():
        
        # isinstance() verifie le type de la valeur
        # CAS 1: la valeur est une liste (exemple: ["Python", "FastAPI"])
        if isinstance(value, list):
            # On parcourt chaque element de la liste
            for item in value:
                # On convertit l'element en string et en minuscules pour la comparaison
                # str(item) permet de convertir meme les nombres ou autres types
                if query in str(item).lower():
                    # Si trouve, on ajoute toute la liste au resultat
                    results[key] = value
        
        # CAS 2: la valeur est un texte simple (une string)
        elif query in str(value).lower():
            # On ajoute directement cette paire clef-valeur au resultat
            results[key] = value
    
    # On retourne le dictionnaire des resultats (peut etre vide)
    return results


# =========================================================
# 4. SIMULATION D'EMBEDDING (SIMILARITE SIMPLE)
# =========================================================
def simple_similarity(text1, text2):
    """
    Simule une mesure de similarite entre deux textes
    (approximation d'un embedding sans IA complexe).
    
    Cette fonction utilise l'indice de Jaccard:
    similarite = (mots communs) / (tous les mots)
    
    Arguments:
        text1: premier texte a comparer
        text2: deuxieme texte a comparer
    
    Retourne:
        Un nombre entre 0 et 1 (0 = pas similaire, 1 = identique)
    """
    
    # .split() decoupe le texte en mots sur les espaces
    # Exemple: "Bonjour le monde" -> ["Bonjour", "le", "monde"]
    # set() convertit la liste en ensemble (supprime les doublons)
    # .lower() convertit tout en minuscules pour ignorer la casse
    set1 = set(text1.lower().split())
    set2 = set(text2.lower().split())
    
    # .intersection() retourne les mots qui sont dans les DEUX ensembles
    # Exemple: {"python", "java"} ∩ {"python", "c++"} = {"python"}
    intersection = set1.intersection(set2)
    
    # .union() retourne tous les mots uniques des DEUX ensembles
    # Exemple: {"python", "java"} ∪ {"python", "c++"} = {"python", "java", "c++"}
    union = set1.union(set2)
    
    # Si l'union est vide (les deux textes sont vides), on evite la division par zero
    if len(union) == 0:
        return 0
    
    # On calcule le rapport: nombre de mots communs / nombre total de mots
    # Exemple: 1 mot commun sur 3 mots totaux = 0.33 (33% de similarite)
    return len(intersection) / len(union)


# =========================================================
# 5. COMPARAISON AVEC LES TENDANCES EXTERNES
# =========================================================
def compare_with_trends(memory, trends):
    """
    Compare les frameworks internes avec les tendances externes.
    
    Pour chaque framework populaire du marché, on regarde s'il est
    deja utilise dans l'entreprise ou non.
    
    Arguments:
        memory: dictionnaire interne de l'entreprise
        trends: dictionnaire contenant les tendances externes
    
    Retourne:
        Une liste de dictionnaires avec le framework et son statut
    """
    
    # Liste vide qui va contenir tous les resultats
    results = []
    
    # On recupere la liste des frameworks internes
    # Si la clef "frameworks_utilises" n'existe pas, on utilise une liste vide []
    internal_frameworks = memory.get("frameworks_utilises", [])
    
    # On recupere la liste des frameworks populaires externes
    # Si la clef "popular_frameworks" n'existe pas, on utilise une liste vide []
    popular_frameworks = trends.get("popular_frameworks", [])
    
    # On parcourt chaque framework populaire un par un
    for framework in popular_frameworks:
        
        # On verifie si ce framework est dans la liste interne
        # L'operateur "in" retourne True si l'element est dans la liste
        if framework in internal_frameworks:
            status = "deja utilise"  # Cas: l'entreprise l'utilise deja
        else:
            status = "opportunite"   # Cas: l'entreprise pourrait l'adopter
        
        # On cree un petit dictionnaire pour ce framework
        # Et on l'ajoute a la liste des resultats avec .append()
        results.append({
            "framework": framework,  # Le nom du framework
            "status": status         # Son statut (deja utilise ou opportunite)
        })
    
    # On retourne la liste complete des resultats
    return results


# =========================================================
# 6. ANALYSE INTELLIGENTE (VERSION AMELIOREE)
# =========================================================
def smart_matching(memory, trends):
    """
    Version amelioree de la comparaison utilisant une
    similarite simple (pseudo embedding).
    
    Au lieu d'une simple egalite, on calcule un score de similarite
    entre chaque framework tendance et les frameworks internes.
    
    Arguments:
        memory: dictionnaire interne de l'entreprise
        trends: dictionnaire contenant les tendances externes
    
    Retourne:
        Une liste de dictionnaires avec framework, score et statut
    """
    
    # Liste vide pour les resultats
    results = []
    
    # On recupere la liste des frameworks internes
    internal_frameworks = memory.get("frameworks_utilises", [])
    
    # .join() fusionne tous les elements de la liste en une seule chaine
    # Exemple: ["LangChain", "LlamaIndex"] -> "LangChain LlamaIndex"
    internal_text = " ".join(internal_frameworks)
    
    # On recupere la liste des frameworks populaires
    popular_frameworks = trends.get("popular_frameworks", [])
    
    # On parcourt chaque framework populaire
    for framework in popular_frameworks:
        
        # On calcule le score de similarite entre le framework et le texte interne
        # Exemple: "LangGraph" vs "LangChain LlamaIndex"
        score = simple_similarity(framework, internal_text)
        
        # Seuil a 0.3: si le score depasse 30% de similarite
        # On considere que le framework est lie a l'existant
        if score > 0.3:
            status = "lie a l'existant"  # Similarite partielle
        else:
            status = "opportunite"       # Pas ou peu similaire
        
        # On ajoute le resultat avec le score arrondi a 2 decimales
        # round(score, 2) arrondit: 0.333333 -> 0.33
        results.append({
            "framework": framework,
            "score": round(score, 2),
            "status": status
        })
    
    return results


# =========================================================
# 7. RECOMMANDATIONS STRATEGIQUES
# =========================================================
def strategic_recommendation(analysis):
    """
    Genere des recommandations strategiques
    basees sur les opportunites detectees.
    
    Arguments:
        analysis: la liste resultat de compare_with_trends()
    
    Retourne:
        Une liste de phrases de recommandations (une par opportunite)
    """
    
    # Liste vide pour stocker les recommandations
    recommendations = []
    
    # On parcourt chaque element de l'analyse
    for item in analysis:
        
        # Si le statut est "opportunite", on genere une recommandation
        if item["status"] == "opportunite":
            
            # On construit une phrase explicative
            # Le + sert a concatener (coller) les chaines de texte
            recommendation = "Explorer le framework " + item["framework"] + " pour renforcer la competitivite"
            
            # On ajoute cette phrase a la liste des recommandations
            recommendations.append(recommendation)
    
    # On retourne la liste des recommandations (peut etre vide)
    return recommendations


# =========================================================
# 8. CONSTRUCTION DE LA SORTIE FINALE
# =========================================================
def build_output(memory, smart_matching_results, recommendations):
    """
    Construit la sortie finale structuree avec toutes les analyses.
    
    Cette fonction rassemble toutes les informations dans un seul
    dictionnaire bien organise pour une utilisation facile.
    
    Arguments:
        memory: memoire interne de l'entreprise
        smart_matching_results: resultats de l'analyse intelligente
        recommendations: liste des recommandations strategiques
    
    Retourne:
        Un dictionnaire structure contenant tous les resultats
    """
    
    # On cree un dictionnaire principal qui contiendra tout
    output = {
        
        # Premiere section: informations sur l'entreprise
        "contexte_entreprise": {
            # .get() avec une valeur par defaut au cas ou la clef n'existe pas
            "nom": memory.get("entreprise", "Non specifie"),
            "stack_technique": memory.get("stack_actuelle", []),
            "frameworks_utilises": memory.get("frameworks_utilises", []),
            "priorite": memory.get("priorite", "Non specifiee"),
            "contraintes": memory.get("contraintes", [])
        },
        
        # Deuxieme section: resultats de l'analyse des tendances
        "analyse_tendances": smart_matching_results,
        
        # Troisieme section: recommandations generees
        "recommandations": recommendations,
        
        # Quatrieme section: resume chiffre pour avoir une vue d'ensemble
        "resume": {
            # sum() additionne les valeurs d'une liste
            # On cree une liste de 1 pour chaque opportunite, puis on additionne
            "total_opportunites": sum(1 for item in smart_matching_results if item["status"] == "opportunite"),
            
            # Pareil pour les technologies liees a l'existant
            "technologies_liees": sum(1 for item in smart_matching_results if item["status"] == "lie a l'existant")
        }
    }
    
    # On retourne le dictionnaire complet
    return output


# =========================================================
# 9. AFFICHAGE FORMATTE
# =========================================================
def print_formatted_output(output):
    """
    Affiche la sortie de maniere lisible et structuree dans la console.
    
    Cette fonction ne retourne rien, elle affiche directement a l'ecran.
    
    Arguments:
        output: le dictionnaire produit par build_output()
    """
    
    # \n signifie "nouvelle ligne"
    # =*60 cree une ligne de 60 signes "="
    print("\n" + "="*60)
    print("RAPPORT D'ANALYSE STRATEGIQUE")
    print("="*60)
    
    # --- SECTION CONTEXTE ENTREPRISE ---
    print("\n--- CONTEXTE ENTREPRISE ---")
    
    # On affiche chaque information avec son libelle
    print(f"Nom: {output['contexte_entreprise']['nom']}")
    
    # .join() transforme la liste en texte avec des virgules
    # Exemple: ["Python", "FastAPI"] -> "Python, FastAPI"
    print(f"Stack technique: {', '.join(output['contexte_entreprise']['stack_technique'])}")
    print(f"Frameworks utilises: {', '.join(output['contexte_entreprise']['frameworks_utilises'])}")
    print(f"Priorite: {output['contexte_entreprise']['priorite']}")
    print(f"Contraintes: {', '.join(output['contexte_entreprise']['contraintes'])}")
    
    # --- SECTION ANALYSE DES TENDANCES ---
    print("\n--- ANALYSE DES TENDANCES ---")
    
    # On parcourt chaque resultat d'analyse
    for item in output['analyse_tendances']:
        # On choisit un symbole different selon le statut
        if item['status'] == "lie a l'existant":
            status_icon = "✓"  # Checkmark pour lie a l'existant
        else:
            status_icon = "○"  # Cercle vide pour opportunite
        
        # f"..." est une f-string qui permet d'inserer des variables directement
        print(f"{status_icon} {item['framework']}: {item['status']} (score: {item['score']})")
    
    # --- SECTION RECOMMANDATIONS ---
    print("\n--- RECOMMANDATIONS STRATEGIQUES ---")
    
    # Si la liste des recommandations n'est pas vide
    if output['recommandations']:
        # enumerate() donne un numero automatique (1, 2, 3...)
        for i, rec in enumerate(output['recommandations'], 1):
            print(f"{i}. {rec}")
    else:
        print("Aucune recommandation pour le moment.")
    
    # --- SECTION RESUME ---
    print("\n--- RESUME ---")
    print(f"Opportunites identifiees: {output['resume']['total_opportunites']}")
    print(f"Technologies liees a l'existant: {output['resume']['technologies_liees']}")
    
    # Ligne de fermeture
    print("="*60 + "\n")


# =========================================================
# 10. TEST LOCAL DU MODULE
# =========================================================
# Cette condition est TRES importante en Python
# __name__ est une variable speciale qui vaut "__main__"
# quand le script est execute DIRECTEMENT (pas importe)
if __name__ == "__main__":
    
    # ETAPE 1: Chargement des donnees internes
    # On appelle load_memory() qui retourne le dictionnaire
    # Ce dictionnaire est stocke dans la variable "memory"
    memory = load_memory()
    
    # On affiche le contenu de la memoire pour verification
    print("\n=== MEMOIRE INTERNE ===")
    print(memory)
    
    # ETAPE 2: Simulation de tendances externes
    # On cree un dictionnaire qui simule ce qu'un agent externe pourrait fournir
    fake_trends = {
        "popular_frameworks": [
            "LangGraph",   # Framework tendance 1
            "AutoGen",     # Framework tendance 2
            "LangChain"    # Framework tendance 3
        ]
    }
    
    # ETAPE 3: Recherche avancee
    # On cherche tous les endroits ou le mot "python" apparait
    print("\n=== RECHERCHE AVANCEE ===")
    print(search_memory_advanced(memory, "python"))
    
    # ETAPE 4: Comparaison simple (egalite exacte)
    # On compare frameworks internes vs tendances
    print("\n=== COMPARAISON ===")
    analysis = compare_with_trends(memory, fake_trends)
    print(analysis)
    
    # ETAPE 5: Analyse intelligente (avec scores de similarite)
    # Version plus sophistiquee qui donne des scores
    print("\n=== SMART MATCHING ===")
    smart = smart_matching(memory, fake_trends)
    print(smart)
    
    # ETAPE 6: Generation des recommandations
    # A partir de l'analyse simple, on genere des actions a prendre
    print("\n=== RECOMMANDATIONS ===")
    recommendations = strategic_recommendation(analysis)
    print(recommendations)
    
    # ETAPE 7: Construction de la sortie finale structuree
    # On rassemble TOUT dans un seul dictionnaire bien organise
    print("\n=== SORTIE FINALE STRUCTUREE ===")
    final_output = build_output(memory, smart, recommendations)
    print(final_output)
    
    # ETAPE 8: Affichage formate et lisible
    # On affiche le rapport de maniere professionnelle
    print_formatted_output(final_output)