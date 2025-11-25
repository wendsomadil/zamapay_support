"""
Système de recherche sémantique avec FAISS et Gemini 2.5 Flash
Optimisé pour ZamaPay
"""

import os
import json
import numpy as np
import faiss
import google.generativeai as genai
from typing import List, Dict, Tuple
import pickle

class FAISSGeminiRetrieval:
    """
    Système de récupération hybride utilisant FAISS pour la recherche vectorielle
    et Gemini 2.5 Flash pour la génération d'embeddings et de réponses
    """
    
    def __init__(
        self, 
        knowledge_base_path: str = "knowledge_base.json",
        index_path: str = "faiss_index.bin",
        metadata_path: str = "faiss_metadata.pkl",
        gemini_api_key: str = None
    ):
        """
        Initialise le système FAISS + Gemini
        
        Args:
            knowledge_base_path: Chemin vers la base de connaissances JSON
            index_path: Chemin pour sauvegarder l'index FAISS
            metadata_path: Chemin pour les métadonnées des documents
            gemini_api_key: Clé API Gemini (ou via variable d'environnement)
        """
        self.knowledge_base_path = knowledge_base_path
        self.index_path = index_path
        self.metadata_path = metadata_path
        
        # Configuration Gemini
        api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("Clé API Gemini requise (via paramètre ou variable GEMINI_API_KEY)")
        
        genai.configure(api_key=api_key)
        
        # Utiliser Gemini 2.5 Flash pour les embeddings
        self.embed_model = genai.GenerativeModel('gemini-2.5-flash-exp')
        
        # Modèle pour génération de réponses
        self.chat_model = genai.GenerativeModel(
            'gemini-2.5-flash-exp',
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
        )
        
        # Charger ou créer l'index
        self.documents = []
        self.index = None
        self.dimension = 768  # Dimension des embeddings Gemini
        
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """Charge l'index existant ou en crée un nouveau"""
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            print("📚 Chargement de l'index FAISS existant...")
            self._load_index()
        else:
            print("🔨 Création d'un nouvel index FAISS...")
            self._create_index()
    
    def _create_index(self):
        """Crée un nouvel index FAISS depuis la base de connaissances"""
        # Charger la base de connaissances
        with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
            kb_data = json.load(f)
        
        qa_pairs = kb_data.get('qa_pairs', [])
        
        if not qa_pairs:
            print("⚠️ Aucune paire Q/R trouvée")
            self.index = faiss.IndexFlatL2(self.dimension)
            self.documents = []
            return
        
        # Préparer les documents
        self.documents = []
        texts_to_embed = []
        
        for pair in qa_pairs:
            question = pair.get('question', '')
            answer = pair.get('answer', '')
            category = pair.get('category', 'general')
            
            # Créer un texte enrichi pour de meilleurs embeddings
            combined_text = f"Question: {question}\nRéponse: {answer}\nCatégorie: {category}"
            
            self.documents.append({
                'question': question,
                'answer': answer,
                'category': category,
                'text': combined_text
            })
            
            texts_to_embed.append(combined_text)
        
        print(f"📝 Génération des embeddings pour {len(texts_to_embed)} documents...")
        
        # Générer les embeddings
        embeddings = self._generate_embeddings_batch(texts_to_embed)
        
        # Créer l'index FAISS
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(np.array(embeddings).astype('float32'))
        
        # Sauvegarder
        self._save_index()
        
        print(f"✅ Index créé avec {len(self.documents)} documents")
    
    def _generate_embeddings_batch(self, texts: List[str], batch_size: int = 10) -> np.ndarray:
        """
        Génère des embeddings pour une liste de textes par batch
        
        Args:
            texts: Liste de textes
            batch_size: Taille des batchs
            
        Returns:
            Array numpy des embeddings
        """
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = []
            
            for text in batch:
                try:
                    # Utiliser l'API d'embedding de Gemini
                    result = genai.embed_content(
                        model="models/text-embedding-004",
                        content=text,
                        task_type="retrieval_document"
                    )
                    embedding = result['embedding']
                    batch_embeddings.append(embedding)
                    
                except Exception as e:
                    print(f"⚠️ Erreur embedding: {e}")
                    # Embedding par défaut en cas d'erreur
                    batch_embeddings.append([0.0] * self.dimension)
            
            all_embeddings.extend(batch_embeddings)
            print(f"  Traité {min(i + batch_size, len(texts))}/{len(texts)}")
        
        return np.array(all_embeddings)
    
    def _generate_query_embedding(self, query: str) -> np.ndarray:
        """
        Génère l'embedding pour une requête
        
        Args:
            query: Texte de la requête
            
        Returns:
            Embedding numpy array
        """
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=query,
                task_type="retrieval_query"
            )
            return np.array([result['embedding']]).astype('float32')
        except Exception as e:
            print(f"⚠️ Erreur embedding requête: {e}")
            return np.zeros((1, self.dimension)).astype('float32')
    
    def search(self, query: str, top_k: int = 3) -> List[Tuple[Dict, float]]:
        """
        Recherche les documents les plus pertinents
        
        Args:
            query: Question de l'utilisateur
            top_k: Nombre de résultats à retourner
            
        Returns:
            Liste de (document, score) triée par pertinence
        """
        if self.index is None or len(self.documents) == 0:
            return []
        
        # Générer l'embedding de la requête
        query_embedding = self._generate_query_embedding(query)
        
        # Recherche dans FAISS
        distances, indices = self.index.search(query_embedding, min(top_k, len(self.documents)))
        
        # Préparer les résultats
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.documents):
                # Convertir distance en score de similarité (plus proche = meilleur)
                similarity_score = 1 / (1 + dist)
                results.append((self.documents[idx], similarity_score))
        
        return results
    
    def generate_response(
        self, 
        query: str, 
        user_name: str = "Utilisateur",
        context_k: int = 3
    ) -> Dict:
        """
        Génère une réponse en utilisant RAG (Retrieval-Augmented Generation)
        
        Args:
            query: Question de l'utilisateur
            user_name: Nom de l'utilisateur
            context_k: Nombre de documents de contexte
            
        Returns:
            Dictionnaire avec response, confidence, source
        """
        # Rechercher les documents pertinents
        results = self.search(query, top_k=context_k)
        
        if not results:
            return {
                'response': f"Désolé {user_name}, je n'ai pas trouvé d'information pertinente. Contactez notre support au +226 25 40 92 76.",
                'confidence': 0.3,
                'source': 'fallback'
            }
        
        # Construire le contexte
        context_parts = []
        max_confidence = 0
        
        for doc, score in results:
            context_parts.append(f"Q: {doc['question']}\nR: {doc['answer']}")
            max_confidence = max(max_confidence, score)
        
        context = "\n\n".join(context_parts)
        
        # Créer le prompt
        prompt = f"""Tu es l'assistant intelligent de ZamaPay, une plateforme de finance inclusive africaine.

CONTEXTE PERTINENT:
{context}

QUESTION DE L'UTILISATEUR ({user_name}):
{query}

INSTRUCTIONS:
- Réponds de manière claire, professionnelle et amicale
- Utilise le contexte fourni pour répondre précisément
- Personnalise avec le nom de l'utilisateur
- Si le contexte ne suffit pas, indique-le et suggère de contacter le support
- Reste dans le domaine de ZamaPay et de la finance inclusive
- Format: paragraphes courts et lisibles

RÉPONSE:"""

        try:
            # Générer la réponse avec Gemini
            response = self.chat_model.generate_content(prompt)
            answer = response.text.strip()
            
            # Calculer la confiance basée sur la pertinence des résultats
            confidence = min(max_confidence, 0.95)
            
            return {
                'response': answer,
                'confidence': confidence,
                'source': 'gemini_rag',
                'retrieved_docs': len(results)
            }
            
        except Exception as e:
            print(f"❌ Erreur génération: {e}")
            
            # Fallback: retourner la meilleure réponse du contexte
            best_doc = results[0][0]
            return {
                'response': f"{user_name}, {best_doc['answer']}",
                'confidence': results[0][1],
                'source': 'knowledge_base'
            }
    
    def _save_index(self):
        """Sauvegarde l'index FAISS et les métadonnées"""
        if self.index is not None:
            faiss.write_index(self.index, self.index_path)
            
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.documents, f)
            
            print(f"💾 Index sauvegardé: {self.index_path}")
    
    def _load_index(self):
        """Charge l'index FAISS et les métadonnées"""
        self.index = faiss.read_index(self.index_path)
        
        with open(self.metadata_path, 'rb') as f:
            self.documents = pickle.load(f)
        
        print(f"✅ Index chargé: {len(self.documents)} documents")
    
    def add_document(self, question: str, answer: str, category: str = "general"):
        """
        Ajoute un nouveau document à l'index
        
        Args:
            question: Question
            answer: Réponse
            category: Catégorie
        """
        combined_text = f"Question: {question}\nRéponse: {answer}\nCatégorie: {category}"
        
        # Générer l'embedding
        embedding = self._generate_query_embedding(combined_text)
        
        # Ajouter à l'index
        if self.index is None:
            self.index = faiss.IndexFlatL2(self.dimension)
        
        self.index.add(embedding)
        
        # Ajouter aux documents
        self.documents.append({
            'question': question,
            'answer': answer,
            'category': category,
            'text': combined_text
        })
        
        # Sauvegarder
        self._save_index()
        
        print(f"✅ Document ajouté: {question[:50]}...")
    
    def rebuild_index(self):
        """Reconstruit complètement l'index depuis la base de connaissances"""
        print("🔄 Reconstruction de l'index...")
        self._create_index()
        print("✅ Index reconstruit avec succès")


# Exemple d'utilisation
if __name__ == "__main__":
    # Initialiser le système
    retrieval = FAISSGeminiRetrieval(
        knowledge_base_path="knowledge_base.json",
        gemini_api_key="VOTRE_CLE_API_GEMINI"  # Ou via variable d'environnement
    )
    
    # Tester une recherche
    print("\n🔍 Test de recherche:")
    query = "Quels sont les frais de ZamaPay ?"
    results = retrieval.search(query, top_k=3)
    
    for i, (doc, score) in enumerate(results, 1):
        print(f"\n{i}. Score: {score:.3f}")
        print(f"   Q: {doc['question']}")
        print(f"   R: {doc['answer'][:100]}...")
    
    # Tester la génération de réponse
    print("\n\n💬 Test de génération:")
    response = retrieval.generate_response(query, user_name="Abdoul")
    print(f"\nRéponse: {response['response']}")
    print(f"Confiance: {response['confidence']:.2%}")
    print(f"Source: {response['source']}")
    