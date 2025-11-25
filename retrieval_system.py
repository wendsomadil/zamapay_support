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
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def preprocess_text(self, text):
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)
        return text
    
    def build_vectors(self):
        texts_to_vectorize = []
        self.qa_references = []
        
        for qa in self.knowledge_base['qa_pairs']:
            texts_to_vectorize.append(self.preprocess_text(qa['question_principale']))
            self.qa_references.append({'id': qa['id'], 'type': 'main'})
            
            for variation in qa.get('variations', []):
                texts_to_vectorize.append(self.preprocess_text(variation))
                self.qa_references.append({'id': qa['id'], 'type': 'variation'})
        
        if texts_to_vectorize:
            self.qa_vectors = self.vectorizer.fit_transform(texts_to_vectorize)
            print(f"✅ Système TF-IDF initialisé avec {len(texts_to_vectorize)} questions")
    
    def search(self, query, top_k=3, confidence_threshold=0.4):
        if self.qa_vectors is None or self.qa_vectors.shape[0] == 0:
            return []
        
        query_vec = self.vectorizer.transform([self.preprocess_text(query)])
        similarities = cosine_similarity(query_vec, self.qa_vectors)
        
        top_indices = np.argsort(similarities[0])[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            score = similarities[0][idx]
            if score >= confidence_threshold:
                qa_ref = self.qa_references[idx]
                qa_data = self.get_qa_by_id(qa_ref['id'])
                if qa_data and not any(r['qa_data']['id'] == qa_data['id'] for r in results):
                    results.append({
                        'qa_data': qa_data,
                        'score': float(score),
                        'match_type': qa_ref['type']
                    })
        
        return results
    
    def get_qa_by_id(self, qa_id):
        for qa in self.knowledge_base['qa_pairs']:
            if qa['id'] == qa_id:
                return qa
        return None
    