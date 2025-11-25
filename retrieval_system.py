import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import re

class RetrievalSystem:
    def __init__(self, knowledge_base_path="knowledge_base.json"):
        self.vectorizer = TfidfVectorizer(stop_words=None)
        self.knowledge_base = self.load_knowledge_base(knowledge_base_path)
        self.qa_vectors = None
        self.build_vectors()
    
    def load_knowledge_base(self, path):
        """Charge la base de connaissances avec gestion d'erreurs améliorée"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Vérifier la structure
            if isinstance(data, dict) and 'qa_pairs' in data:
                print(f"✅ Base de connaissances chargée: {len(data['qa_pairs'])} Q&A")
                return data
            else:
                print("❌ Structure invalide, utilisation de la structure par défaut")
                return self.create_default_structure()
                
        except Exception as e:
            print(f"❌ Erreur chargement base: {e}")
            return self.create_default_structure()
    
    def create_default_structure(self):
        """Crée une structure par défaut si le fichier est corrompu"""
        return {
            "qa_pairs": [
                {
                    "id": 1,
                    "question_principale": "Quels sont vos frais ?",
                    "reponse": "Réponse par défaut sur les frais",
                    "variations": []
                }
            ]
        }
    
    def preprocess_text(self, text):
        if not text:
            return ""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)
        return text
    
    def build_vectors(self):
        """Construit les vecteurs TF-IDF avec gestion d'erreurs"""
        texts_to_vectorize = []
        self.qa_references = []
        
        # Vérifier que knowledge_base a la bonne structure
        if not isinstance(self.knowledge_base, dict) or 'qa_pairs' not in self.knowledge_base:
            print("❌ Structure knowledge_base invalide")
            return
        
        for qa in self.knowledge_base['qa_pairs']:
            # Vérifier que qa est un dictionnaire valide
            if not isinstance(qa, dict):
                print("⚠️ Q&A ignoré: n'est pas un dictionnaire")
                continue
                
            if 'question_principale' not in qa:
                print("⚠️ Q&A ignoré: question_principale manquante")
                continue
            
            # Question principale
            question_text = self.preprocess_text(qa['question_principale'])
            if question_text:
                texts_to_vectorize.append(question_text)
                self.qa_references.append({
                    'id': qa.get('id', len(self.qa_references)),
                    'type': 'main',
                    'qa_data': qa
                })
            
            # Variations
            variations = qa.get('variations', [])
            if isinstance(variations, list):
                for variation in variations:
                    if variation:  # Ne pas ajouter de chaînes vides
                        variation_text = self.preprocess_text(variation)
                        if variation_text:
                            texts_to_vectorize.append(variation_text)
                            self.qa_references.append({
                                'id': qa.get('id', len(self.qa_references)),
                                'type': 'variation', 
                                'qa_data': qa
                            })
        
        if texts_to_vectorize:
            try:
                self.qa_vectors = self.vectorizer.fit_transform(texts_to_vectorize)
                print(f"✅ Système TF-IDF initialisé avec {len(texts_to_vectorize)} questions")
            except Exception as e:
                print(f"❌ Erreur initialisation TF-IDF: {e}")
                self.qa_vectors = None
        else:
            print("❌ Aucun texte à vectoriser")
            self.qa_vectors = None
    
    def search(self, query, top_k=3, confidence_threshold=0.5):
        """Recherche avec seuil de confiance plus élevé"""
        if self.qa_vectors is None or self.qa_vectors.shape[0] == 0:
            return []
        
        try:
            query_vec = self.vectorizer.transform([self.preprocess_text(query)])
            similarities = cosine_similarity(query_vec, self.qa_vectors)
            
            top_indices = np.argsort(similarities[0])[-top_k:][::-1]
            
            results = []
            for idx in top_indices:
                score = similarities[0][idx]
                if score >= confidence_threshold:  # Seuil plus strict
                    qa_ref = self.qa_references[idx]
                    
                    # Vérifier que qa_data existe
                    if 'qa_data' not in qa_ref:
                        continue
                    
                    # Éviter les doublons
                    qa_id = qa_ref['qa_data'].get('id')
                    if not any(r['qa_data'].get('id') == qa_id for r in results):
                        results.append({
                            'qa_data': qa_ref['qa_data'],
                            'score': float(score),
                            'match_type': qa_ref['type']
                        })
            
            return results
            
        except Exception as e:
            print(f"❌ Erreur recherche: {e}")
            return []
    
    def get_qa_by_id(self, qa_id):
        """Récupère une Q&A par son ID"""
        if not isinstance(self.knowledge_base, dict) or 'qa_pairs' not in self.knowledge_base:
            return None
            
        for qa in self.knowledge_base['qa_pairs']:
            if qa.get('id') == qa_id:
                return qa
        return None
    
