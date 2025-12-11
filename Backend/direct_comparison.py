"""
Script pour comparer directement les résultats API vs Colab
"""
import requests
import json

# Résultats attendus du modèle Colab
EXPECTED_RESULTS = {
    "amoxicilline suspension buvable enfant": ['1.md', '32.md', '2.md', '29.md', '19.md'],
    "antibiotique amoxicilline acide clavulanique": ['1.md', '2.md', '29.md', '28.md', '6.md'],
    "antibiotique infection respiratoire adulte": ['6.md', '5.md', '29.md', '7.md', '9.md'],
    "antibiotique infection ORL": ['5.md', '6.md', '29.md', '7.md', '9.md']
}

def test_api_vs_colab():
    """Compare les résultats de l'API avec ceux du modèle Colab"""
    
    print("=" * 80)
    print("🔬 COMPARAISON DIRECTE API vs MODÈLE COLAB")
    print("=" * 80)
    
    for query, expected_docs in EXPECTED_RESULTS.items():
        print(f"\n{'='*80}")
        print(f"📝 Requête: '{query}'")
        print(f"{'='*80}")
        
        # Résultats attendus (Colab)
        print(f"\n✅ ATTENDU (Colab):")
        for i, doc in enumerate(expected_docs, 1):
            print(f"   {i}. {doc}")
        
        # Appel à l'API
        try:
            response = requests.post(
                'http://localhost:5000/api/search',
                json={'query': query, 'top_k': 5},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                actual_docs = [r['doc_id'] for r in results]
                
                print(f"\n🔍 OBTENU (API Flask):")
                for i, result in enumerate(results, 1):
                    doc_id = result['doc_id']
                    score = result['score']
                    nom = result['nom']
                    print(f"   {i}. {doc_id} (score: {score:.4f}) - {nom}")
                
                # Comparaison
                print(f"\n📊 ANALYSE:")
                print(f"   Nombre attendu: {len(expected_docs)}")
                print(f"   Nombre obtenu:  {len(actual_docs)}")
                
                # Vérifier si les documents correspondent
                if actual_docs == expected_docs:
                    print(f"   ✅ ORDRE IDENTIQUE !")
                else:
                    print(f"   ⚠️  ORDRE DIFFÉRENT")
                    
                    # Vérifier les documents présents
                    matching = [doc for doc in actual_docs if doc in expected_docs]
                    missing = [doc for doc in expected_docs if doc not in actual_docs]
                    extra = [doc for doc in actual_docs if doc not in expected_docs]
                    
                    if matching:
                        print(f"   ✓ Documents corrects: {matching}")
                    if missing:
                        print(f"   ✗ Documents manquants: {missing}")
                    if extra:
                        print(f"   + Documents en trop: {extra}")
                    
                    # Calculer la précision
                    precision = len(matching) / len(actual_docs) if actual_docs else 0
                    recall = len(matching) / len(expected_docs) if expected_docs else 0
                    print(f"\n   📈 Précision: {precision:.2%}")
                    print(f"   📈 Rappel: {recall:.2%}")
                
            else:
                print(f"\n❌ Erreur API: {response.status_code}")
                print(f"   {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"\n❌ Impossible de se connecter à l'API")
            print(f"   Assurez-vous que le serveur Flask tourne sur http://localhost:5000")
        except Exception as e:
            print(f"\n❌ Erreur: {str(e)}")
    
    print("\n" + "=" * 80)


def test_single_query(query: str):
    """Teste une seule requête avec détails"""
    
    print("=" * 80)
    print(f"🔍 TEST DÉTAILLÉ: '{query}'")
    print("=" * 80)
    
    try:
        response = requests.post(
            'http://localhost:5000/api/search',
            json={'query': query, 'top_k': 10},  # Demander 10 pour voir
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            print(f"\n📊 Résultats complets (top 10):")
            print(f"{'#':<4} {'Doc ID':<15} {'Score':<10} {'Nom du médicament'}")
            print("-" * 80)
            
            for i, result in enumerate(results, 1):
                doc_id = result['doc_id']
                score = result['score']
                nom = result['nom'][:50]  # Tronquer si trop long
                print(f"{i:<4} {doc_id:<15} {score:<10.4f} {nom}")
            
            print(f"\n⏱️  Temps de recherche: {data.get('search_time', 0):.3f}s")
            
        else:
            print(f"❌ Erreur: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")


if __name__ == "__main__":
    # Test 1: Comparaison complète
    test_api_vs_colab()
    
    # Test 2: Requête détaillée
    print("\n\n")
    test_single_query("amoxicilline suspension buvable enfant")
    
    print("\n✅ Tests terminés\n")