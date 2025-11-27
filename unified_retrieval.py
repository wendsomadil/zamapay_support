# unified_retrieval.py
import os
import json
import faiss
import pickle
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

class UnifiedRetrievalSystem:
    def __init__(self, knowledge_base_path="knowledge_base.json", use_faiss=True):
        self.knowledge_base_path = knowledge_base_path
        self.use_faiss = use_faiss
        self.knowledge_base = self.load_knowledge_base(knowledge_base_path)
        
        # ✅ CORRECTION: Toujours initialiser le modèle si FAISS est activé
        if use_faiss:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                print("✅ Modèle SentenceTransformer chargé")
            except Exception as e:
                print(f"❌ Erreur chargement modèle: {e}")
                self.use_faiss = False
        
        if use_faiss:
            # Essayer de charger l'index existant d'abord
            if not self.load_index():
                # Sinon créer un nouvel index
                self._initialize_faiss()
                self.save_index()  # Sauvegarder après création
        else:
            self._initialize_tfidf()
    
    def load_knowledge_base(self, path):
        """Charge la base de connaissances"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, dict) and 'qa_pairs' in data:
                print(f"✅ Base de connaissances chargée: {len(data['qa_pairs'])} Q&A")
                return data
            else:
                print("❌ Structure invalide")
                return self.create_default_structure()
                
        except Exception as e:
            print(f"❌ Erreur chargement base: {e}")
            return self.create_default_structure()
    
    def create_default_structure(self):
        """Crée une structure par défaut"""
        return {"qa_pairs": []}
    
    def _initialize_faiss(self):
        """Initialise FAISS si disponible"""
        try:
            # ✅ CORRECTION: Vérifier que le modèle est chargé
            if not hasattr(self, 'model') or self.model is None:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                print("✅ Modèle SentenceTransformer chargé dans _initialize_faiss")
            
            # Préparer les textes pour l'embedding
            self.texts = []
            self.qa_mapping = []
            
            for qa in self.knowledge_base['qa_pairs']:
                # Question principale
                self.texts.append(qa['question_principale'])
                self.qa_mapping.append({
                    'type': 'main',
                    'qa_data': qa
                })
                
                # Variations
                for variation in qa.get('variations', []):
                    self.texts.append(variation)
                    self.qa_mapping.append({
                        'type': 'variation', 
                        'qa_data': qa
                    })
            
            # Générer les embeddings
            if self.texts:
                embeddings = self.model.encode(self.texts, convert_to_numpy=True)
                
                # Créer l'index FAISS
                dimension = embeddings.shape[1]
                self.index = faiss.IndexFlatIP(dimension)  # Produit scalaire interne
                faiss.normalize_L2(embeddings)  # Normaliser pour similarité cosinus
                self.index.add(embeddings)
                
                print(f"✅ FAISS initialisé avec {len(self.texts)} embeddings")
            else:
                print("❌ Aucun texte à vectoriser")
                self.use_faiss = False
                self._initialize_tfidf()
                
        except ImportError as e:
            print(f"⚠️ FAISS non disponible: {e}")
            self.use_faiss = False
            self._initialize_tfidf()
        except Exception as e:
            print(f"❌ Erreur initialisation FAISS: {e}")
            self.use_faiss = False
            self._initialize_tfidf()
    
    def _initialize_tfidf(self):
        """Initialise TF-IDF (fallback)"""
        self.vectorizer = TfidfVectorizer(stop_words=None)
        
        # Préparer les textes pour TF-IDF
        texts_to_vectorize = []
        self.qa_references = []
        
        for qa in self.knowledge_base['qa_pairs']:
            # Question principale
            question_text = self.preprocess_text(qa['question_principale'])
            if question_text:
                texts_to_vectorize.append(question_text)
                self.qa_references.append({
                    'type': 'main',
                    'qa_data': qa
                })
            
            # Variations
            for variation in qa.get('variations', []):
                variation_text = self.preprocess_text(variation)
                if variation_text:
                    texts_to_vectorize.append(variation_text)
                    self.qa_references.append({
                        'type': 'variation',
                        'qa_data': qa
                    })
        
        if texts_to_vectorize:
            self.qa_vectors = self.vectorizer.fit_transform(texts_to_vectorize)
            print(f"✅ TF-IDF initialisé avec {len(texts_to_vectorize)} questions")
        else:
            self.qa_vectors = None
            print("❌ Aucun texte à vectoriser")
    
    def preprocess_text(self, text):
        """Prétraitement du texte"""
        if not text:
            return ""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)
        return text
    
    def search(self, query, top_k=3, confidence_threshold=0.1):
        """Recherche unifiée - utilise FAISS ou TF-IDF"""
        if self.use_faiss:
            return self._search_faiss(query, top_k, confidence_threshold)
        else:
            return self._search_tfidf(query, top_k, confidence_threshold)
    
    def _search_faiss(self, query, top_k, confidence_threshold):
        """Recherche avec FAISS"""
        # ✅ CORRECTION: Vérifier que tous les composants sont disponibles
        if not hasattr(self, 'index') or self.index.ntotal == 0:
            print("⚠️ Index FAISS non disponible, utilisation TF-IDF")
            return self._search_tfidf(query, top_k, confidence_threshold)
        
        if not hasattr(self, 'model') or self.model is None:
            print("⚠️ Modèle non disponible, utilisation TF-IDF")
            return self._search_tfidf(query, top_k, confidence_threshold)
        
        try:
            # Générer l'embedding de la requête
            query_embedding = self.model.encode([query], convert_to_numpy=True)
            
            # Normaliser pour similarité cosinus
            faiss.normalize_L2(query_embedding)
            
            # Recherche
            scores, indices = self.index.search(query_embedding, min(top_k, len(self.texts)))
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.texts) and score >= confidence_threshold:
                    qa_ref = self.qa_mapping[idx]
                    results.append({
                        'qa_data': qa_ref['qa_data'],
                        'score': float(score),
                        'match_type': qa_ref['type'],
                        'matched_text': self.texts[idx]
                    })
            
            return results
            
        except Exception as e:
            print(f"⚠️ Erreur recherche FAISS: {e}, utilisation TF-IDF")
            return self._search_tfidf(query, top_k, confidence_threshold)
    
    def _search_tfidf(self, query, top_k, confidence_threshold):
        """Recherche avec TF-IDF"""
        if self.qa_vectors is None or self.qa_vectors.shape[0] == 0:
            return []
        
        try:
            query_vec = self.vectorizer.transform([self.preprocess_text(query)])
            similarities = cosine_similarity(query_vec, self.qa_vectors)
            
            top_indices = np.argsort(similarities[0])[-top_k:][::-1]
            
            results = []
            for idx in top_indices:
                score = similarities[0][idx]
                if score >= confidence_threshold:
                    qa_ref = self.qa_references[idx]
                    
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
            print(f"⚠️ Erreur recherche TF-IDF: {e}")
            return []

    def save_index(self, index_path="unified_faiss_index.bin", metadata_path="unified_faiss_metadata.pkl"):
        """Sauvegarde l'index FAISS et les métadonnées"""
        if hasattr(self, 'index') and self.use_faiss:
            try:
                faiss.write_index(self.index, index_path)
                
                # Sauvegarder les métadonnées
                metadata = {
                    'texts': self.texts,
                    'qa_mapping': self.qa_mapping,
                    'knowledge_base_path': self.knowledge_base_path
                }
                with open(metadata_path, 'wb') as f:
                    pickle.dump(metadata, f)
                
                print(f"💾 Index Unified sauvegardé: {index_path}")
                return True
                
            except Exception as e:
                print(f"❌ Erreur sauvegarde index: {e}")
                return False
        return False

    def load_index(self, index_path="unified_faiss_index.bin", metadata_path="unified_faiss_metadata.pkl"):
        """Charge l'index FAISS et les métadonnées"""
        if self.use_faiss and os.path.exists(index_path) and os.path.exists(metadata_path):
            try:
                self.index = faiss.read_index(index_path)
                
                with open(metadata_path, 'rb') as f:
                    metadata = pickle.load(f)
                    self.texts = metadata['texts']
                    self.qa_mapping = metadata['qa_mapping']
                
                print(f"✅ Index Unified chargé: {len(self.texts)} embeddings")
                return True
                
            except Exception as e:
                print(f"❌ Erreur chargement index: {e}")
                return False
        return False

# Test du système unifié
if __name__ == "__main__":
    print("🔍 TEST SYSTÈME UNIFIÉ")
    print("=" * 50)
    
    # Test avec FAISS
    retrieval_faiss = UnifiedRetrievalSystem("knowledge_base.json", use_faiss=True)
    results_faiss = retrieval_faiss.search("Quels sont vos frais ?")
    print(f"FAISS: {len(results_faiss)} résultats")
    
    # Test avec TF-IDF
    retrieval_tfidf = UnifiedRetrievalSystem("knowledge_base.json", use_faiss=False)
    results_tfidf = retrieval_tfidf.search("Quels sont vos frais ?")
    print(f"TF-IDF: {len(results_tfidf)} résultats")
    
    print("=" * 50)
    
