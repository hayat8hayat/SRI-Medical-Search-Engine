from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import re
import string
import math
import time
from collections import defaultdict
import joblib
import nltk
from nltk.corpus import stopwords


app = Flask(__name__)
CORS(app)

# Chemins des fichiers
BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
MODEL_FOLDER = os.path.join(BASE_FOLDER, "../ri_model")  
DOCS_FOLDER = os.path.join(BASE_FOLDER, "../med_md")
MEDICAMENTS_JSON_PATH = os.path.join(BASE_FOLDER, "../meta_data.json")

# Télécharger les ressources NLTK
try:
    nltk.data.find("tokenizers/punkt")
except:
    nltk.download("punkt")
try:
    nltk.data.find("corpora/stopwords")
except:
    nltk.download("stopwords")

french_stopwords = set(stopwords.words("french"))

# ✅ AJOUT : Afficher les stopwords pour vérification
print(f"📋 Nombre de stopwords français chargés: {len(french_stopwords)}")
print(f"📋 Exemples de stopwords: {list(french_stopwords)[:20]}")

# Variables globales
inverted_index = {}
idf = {}
tfidf_vectors = {}
documents = {}
medicaments_data = []
medicaments_by_id = {}


def clean_text(text: str) -> str:
    """Nettoie le texte : minuscules, suppression ponctuation"""
    text = text.lower()
    text = re.sub(r"[{}]".format(re.escape(string.punctuation)), " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def load_documents(folder: str) -> dict:
    """Charge les documents .md"""
    docs = {}
    if os.path.exists(folder):
        for f in sorted(os.listdir(folder)):
            if f.endswith(".md"):
                with open(os.path.join(folder, f), "r", encoding="utf-8") as file:
                    docs[f] = file.read()
    return docs


def load_medicaments_data(json_path: str) -> list:
    """Charge les données des médicaments depuis le JSON"""
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def initialize_search_engine():
    """Initialise le moteur de recherche avec le modèle sauvegardé"""
    global inverted_index, idf, tfidf_vectors, documents, medicaments_data, medicaments_by_id
    
    print("🔄 Initialisation du moteur de recherche...")
    
    # ✅ CHARGER LE MODÈLE DEPUIS LES FICHIERS .PKL
    tfidf_path = os.path.join(MODEL_FOLDER, "tfidf_vectors.pkl")
    idf_path = os.path.join(MODEL_FOLDER, "idf.pkl")
    index_path = os.path.join(MODEL_FOLDER, "inverted_index.pkl")
    
    if os.path.exists(tfidf_path) and os.path.exists(idf_path) and os.path.exists(index_path):
        print("📦 Chargement du modèle sauvegardé...")
        tfidf_vectors = joblib.load(tfidf_path)
        idf = joblib.load(idf_path)
        inverted_index = joblib.load(index_path)
        print(f"✅ Modèle chargé depuis {MODEL_FOLDER}")
        print(f"   - {len(tfidf_vectors)} vecteurs TF-IDF")
        print(f"   - {len(idf)} termes IDF")
        print(f"   - {len(inverted_index)} termes dans l'index")
    else:
        print("⚠️  Fichiers .pkl non trouvés, impossible de charger le modèle")
        print(f"   Vérifiez que ces fichiers existent :")
        print(f"   - {tfidf_path}")
        print(f"   - {idf_path}")
        print(f"   - {index_path}")
        return False
    
    # Charger les documents (pour les snippets)
    documents = load_documents(DOCS_FOLDER)
    print(f"✅ Documents chargés : {len(documents)}")
    
    # Charger les données des médicaments
    medicaments_data = load_medicaments_data(MEDICAMENTS_JSON_PATH)
    print(f"✅ Données médicaments chargées : {len(medicaments_data)}")
    
    # Créer un mapping id -> medicament
    for med in medicaments_data:
        med_id = med.get('id')
        if med_id:
            medicaments_by_id[str(med_id)] = med
    
    print("✅ Moteur de recherche initialisé\n")
    return True


def cosine_similarity_dict(v1, v2):
    """Calcule la similarité cosinus entre deux vecteurs (dictionnaires)"""
    common = set(v1.keys()) & set(v2.keys())
    if not common:
        return 0.0
    
    num = sum(v1[t] * v2[t] for t in common)
    denom1 = math.sqrt(sum(v**2 for v in v1.values()))
    denom2 = math.sqrt(sum(v**2 for v in v2.values()))
    
    if denom1 == 0 or denom2 == 0:
        return 0.0
    
    return num / (denom1 * denom2)


def build_query_vector(query: str) -> dict:
    """Construit le vecteur TF-IDF de la requête"""
    query = clean_text(query)
    tokens = [t for t in query.split() if t and t not in french_stopwords]
    
    # ✅ AJOUT : Log pour debugging
    print(f"🔍 Requête nettoyée: '{query}'")
    print(f"🔍 Tokens après stopwords: {tokens}")
    
    # Calculer TF pour la requête
    tf_query = defaultdict(int)
    for t in tokens:
        tf_query[t] += 1
    
    # Construire le vecteur TF-IDF
    q_vec = {}
    for term, tf in tf_query.items():
        if term in idf:
            q_vec[term] = tf * idf[term]
        else:
            print(f"⚠️  Terme '{term}' absent de l'index IDF")
    
    print(f"✅ Vecteur requête: {len(q_vec)} termes")
    return q_vec


def extract_id_from_filename(filename: str) -> str:
    """Extrait l'ID du nom de fichier (ex: '1.md' -> '1')"""
    return filename.replace('.md', '')


def search_engine(query: str, top_k: int = 10, min_score: float = 0.0):
    """Effectue la recherche - comportement identique au modèle Colab"""
    start_time = time.time()
    
    # Construire le vecteur de la requête
    q_vec = build_query_vector(query)
    if not q_vec:
        return [], 0
    
    # Calculer les scores de similarité pour TOUS les documents
    scores = {}
    for doc_id, d_vec in tfidf_vectors.items():
        score = cosine_similarity_dict(q_vec, d_vec)
        # ✅ Pas de filtrage par min_score, comme dans Colab
        scores[doc_id] = score
    
    # Trier par score décroissant
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    # ✅ MODIFICATION PRINCIPALE : Prendre exactement top_k documents
    # Sans déduplication complexe, juste les top_k premiers
    top_docs = ranked[:top_k]
    
    # Construire les résultats
    results = []
    
    for doc_id, score in top_docs:
        # ✅ Récupérer les infos sans filtrage supplémentaire
        med_id = extract_id_from_filename(doc_id)
        med_info = medicaments_by_id.get(med_id)
        
        # Préparer le résultat même si certaines infos manquent
        nom = med_info.get("nom", "Médicament inconnu") if med_info else "Médicament inconnu"
        snippet = med_info.get("snippet", "Aucune description disponible.") if med_info else "Aucune description disponible."
        url = med_info.get("url", "#") if med_info else "#"
        image_url = med_info.get("image_url", "") if med_info else ""
        
        result = {
            "doc_id": doc_id,
            "id": med_id,
            "score": round(score, 4),
            "snippet": snippet,
            "nom": nom,
            "url": url,
            "image_url": image_url
        }
        results.append(result)
    
    search_time = time.time() - start_time
    
    # ✅ Log pour debugging
    print(f"🔍 Query: '{query}' → {len(results)} résultats")
    print(f"   Top 5: {[r['doc_id'] for r in results[:5]]}")
    
    return results, search_time


# ==================== ROUTES API ====================

@app.route('/')
def home():
    """Page d'accueil de l'API"""
    return jsonify({
        "message": "API MediSearch - Système de Recherche d'Information",
        "status": "running",
        "version": "2.0.0",
        "model": "TF-IDF avec modèle sauvegardé",
        "endpoints": {
            "/api/search": "POST - Rechercher des médicaments",
            "/api/stats": "GET - Statistiques du système",
            "/api/medicaments": "GET - Liste de tous les médicaments"
        }
    })


@app.route('/api/search', methods=['POST', 'OPTIONS'])
def search():
    """Endpoint de recherche"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        query = data.get('query', '')
        top_k = data.get('top_k', 10)
        
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400
        
        results, search_time = search_engine(query, top_k)
        
        return jsonify({
            "query": query,
            "results": results,
            "total_results": len(results),
            "search_time": round(search_time, 3)
        })
    
    except Exception as e:
        print(f"❌ Erreur de recherche: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def stats():
    """Retourne les statistiques du système"""
    return jsonify({
        "total_terms": len(inverted_index),
        "total_documents": len(tfidf_vectors),
        "total_medicaments": len(medicaments_data),
        "indexed_medicaments": len(medicaments_by_id),
        "model_loaded": len(tfidf_vectors) > 0,
        "status": "operational"
    })


@app.route('/api/medicaments', methods=['GET'])
def get_medicaments():
    """Retourne la liste de tous les médicaments"""
    return jsonify({
        "medicaments": medicaments_data,
        "total": len(medicaments_data)
    })


# ==================== POINT D'ENTRÉE ====================

if __name__ == '__main__':
    # Initialiser le moteur de recherche
    success = initialize_search_engine()
    
    if not success:
        print("❌ Échec de l'initialisation du moteur de recherche")
        print("   Vérifiez que le dossier ri_model contient les fichiers .pkl")
        exit(1)
    
    # Démarrer le serveur Flask
    print("=" * 60)
    print("✅ Serveur Flask démarré")
    print(f"   🌐 http://localhost:5000")
    print(f"   🌐 http://127.0.0.1:5000")
    print(f"📊 {len(medicaments_data)} médicaments chargés")
    print(f"📚 {len(tfidf_vectors)} documents indexés")
    print(f"🔍 {len(inverted_index)} termes dans l'index")
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)