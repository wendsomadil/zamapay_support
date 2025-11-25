#!/usr/bin/env python3
"""
RESPONSE_GENERATOR OPTIMISÉ - ZAMAPAY
Version professionnelle avec corrections complètes et performances améliorées
"""

import random
import json
import time
import threading
from typing import Dict, List, Optional
import google.generativeai as genai

class ResponseGenerator:
    """Générateur de réponses intelligent pour ZamaPay"""
    
    def __init__(self, retrieval_system):
        """Initialise le générateur avec tous les composants nécessaires"""
        self.retrieval_system = retrieval_system
        self.conversation_memory = {}
        self.escalation_threshold = 0.4
        
        # Cache optimisé
        self.kb_cache = {}
        self.cache_timeout = 3600  # 1 heure
        
        # Configuration Gemini avec votre clé
        self.gemini_api_key = "AIzaSyD_LCuo-aeXD4kaXVl__R1JKMLdQm04kRw"
        self._setup_gemini()
        
        print("✅ ResponseGenerator initialisé")

    def _setup_gemini(self):
        """Configure Gemini 2.5 Flash avec gestion d'erreurs robuste"""
        try:
            genai.configure(api_key=self.gemini_api_key)
            
            # Configuration optimale pour Gemini 2.5 Flash
            self.gemini_model = genai.GenerativeModel(
                'gemini-2.5-flash',
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 1024,
                }
            )
            print("✅ Gemini 2.5 Flash configuré")
            
        except Exception as e:
            print(f"⚠️ Gemini non disponible: {e}")
            self.gemini_model = None
            
    def generate_response(self, user_message: str, user_name: str = "Utilisateur") -> Dict:
        """
        Génère une réponse intelligente avec gestion multi-source
        
        Args:
            user_message: Question de l'utilisateur
            user_name: Nom de l'utilisateur
            
        Returns:
            Dict avec response, confidence, source
        """
        print(f"💬 Question: '{user_message[:50]}...'")
        
        try:
            # 1. Détection prioritaire d'escalade
            if self._detect_escalation(user_message):
                return self._create_escalation_response()
            
            # 2. Recherche dans la base de connaissances
            kb_results = self._search_knowledge_base(user_message)
            
            # 3. Si résultats insuffisants, utiliser Gemini
            if self._should_use_gemini(kb_results):
                return self._generate_with_gemini(user_message, user_name)
            
            # 4. Formater et retourner la meilleure réponse
            return self._format_best_response(kb_results, user_message, user_name)
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return self._create_error_response(user_name)

    def _detect_escalation(self, message: str) -> bool:
        """Détecte si l'utilisateur veut parler à un humain"""
        keywords = [
            "humain", "agent", "conseiller", "personne", "réel",
            "vrai", "parler à", "contact", "support", "urgent"
        ]
        message_lower = message.lower()
        return any(kw in message_lower for kw in keywords)

    def _create_escalation_response(self) -> Dict:
        """Crée une réponse d'escalade vers support humain"""
        return {
            'response': """**🚨 Support Humain Disponible**

Je comprends que vous souhaitez parler à un conseiller.

**📞 Contacts Directs:**
• Téléphone: **+226 25 40 92 76** (7j/7)
• WhatsApp: **+226 25 40 92 76**
• Email: contact@zamapay.com

**⏱️ Temps de réponse:**
- Téléphone: Immédiat
- WhatsApp: < 5 minutes
- Email: < 30 minutes

Notre équipe est là pour vous aider ! 💙""",
            'confidence': 0.95,
            'source': 'escalation'
        }

    def _search_knowledge_base(self, query: str) -> List[Dict]:
        """
        Recherche optimisée dans la base de connaissances avec cache
        
        Args:
            query: Question à rechercher
            
        Returns:
            Liste des résultats pertinents
        """
        # Vérifier le cache
        cache_key = query.lower().strip()
        if cache_key in self.kb_cache:
            cached = self.kb_cache[cache_key]
            if time.time() - cached['time'] < self.cache_timeout:
                print("💾 Cache hit")
                return cached['results']
        
        # Recherche dans la KB
        try:
            results = self.retrieval_system.search(query)
            
            # Filtrer les résultats pertinents (score > 0.3)
            relevant = [
                r for r in results 
                if isinstance(r, dict) and r.get('score', 0) > 0.3
            ]
            
            # Trier par score
            relevant.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            # Mettre en cache
            self.kb_cache[cache_key] = {
                'results': relevant[:3],
                'time': time.time()
            }
            
            print(f"📚 Trouvé {len(relevant)} résultats pertinents")
            return relevant[:3]
            
        except Exception as e:
            print(f"⚠️ Erreur recherche KB: {e}")
            return []

    def _should_use_gemini(self, kb_results: List[Dict]) -> bool:
        """
        Détermine si Gemini doit être utilisé
        
        Args:
            kb_results: Résultats de la base de connaissances
            
        Returns:
            True si Gemini doit être utilisé
        """
        if not self.gemini_model:
            return False
        
        # Si pas de résultats
        if not kb_results:
            return True
        
        # Si le meilleur score est faible
        best_score = kb_results[0].get('score', 0)
        if best_score < 0.6:
            return True
        
        return False

    def _generate_with_gemini(self, query: str, user_name: str) -> Dict:
        """
        Génère une réponse avec Gemini 2.0 Flash
        
        Args:
            query: Question de l'utilisateur
            user_name: Nom de l'utilisateur
            
        Returns:
            Réponse formatée
        """
        if not self.gemini_model:
            return self._generate_template_response(query, user_name)
        
        try:
            prompt = self._build_gemini_prompt(query, user_name)
            
            print("🤖 Génération Gemini...")
            response = self.gemini_model.generate_content(prompt)
            
            if response and hasattr(response, 'text') and response.text:
                answer = response.text.strip()
                return {
                    'response': answer,
                    'confidence': 0.85,
                    'source': 'gemini'
                }
            else:
                raise ValueError("Réponse Gemini vide")
                
        except Exception as e:
            print(f"⚠️ Erreur Gemini: {e}")
            return self._generate_template_response(query, user_name)

    def _build_gemini_prompt(self, query: str, user_name: str) -> str:
        """
        Construit un prompt optimisé pour Gemini
        
        Args:
            query: Question de l'utilisateur
            user_name: Nom de l'utilisateur
            
        Returns:
            Prompt formaté
        """
        return f"""Tu es l'assistant intelligent de ZamaPay, plateforme de finance inclusive en Afrique de l'Ouest.

**CONTEXTE ZAMAPAY:**
- Siège: Ouagadougou, Burkina Faso
- Zone: UEMOA (8 pays)
- Devise: Franc CFA (XOF)
- Mobile Money: Orange Money, Moov Money
- Support: +226 25 40 92 76
- Email: contact@zamapay.com

**TARIFS STANDARDS:**
- Transferts nationaux BF: 1% (min 500 F CFA)
- Transferts UEMOA: 1.5% (min 750 F CFA)
- Mobile Money: 1% (min 250 F CFA)

**DÉLAIS:**
- National: 2h max
- UEMOA: 2-4h
- Mobile Money: Instantané

**QUESTION DE {user_name.upper()}:**
{query}

**TON RÔLE:**
- Réponds en français, clair et professionnel
- Utilise les montants en F CFA
- Sois chaleureux mais expert
- Si tu ne sais pas, oriente vers le support
- Format: court et structuré (max 200 mots)

**RÉPONSE:**"""

    def _format_best_response(
        self, 
        kb_results: List[Dict], 
        query: str, 
        user_name: str
    ) -> Dict:
        """
        Formate la meilleure réponse depuis la base de connaissances
        
        Args:
            kb_results: Résultats de recherche
            query: Question originale
            user_name: Nom de l'utilisateur
            
        Returns:
            Réponse formatée
        """
        if not kb_results:
            return self._generate_template_response(query, user_name)
        
        best = kb_results[0]
        qa_data = best.get('qa_data', {})
        
        # Extraire les informations
        question = qa_data.get('question', 'Information')
        answer = qa_data.get('answer', qa_data.get('reponse', ''))
        
        if not answer:
            return self._generate_template_response(query, user_name)
        
        # Formater la réponse
        formatted = f"**{question}**\n\n{answer}"
        
        # Ajouter suggestions si disponibles
        related = qa_data.get('questions_connexes', [])
        if related and len(related) > 0:
            formatted += "\n\n**💡 Questions connexes:** Posez-moi d'autres questions sur ZamaPay !"
        
        return {
            'response': formatted,
            'confidence': best.get('score', 0.7),
            'source': 'knowledge_base'
        }

    def _generate_template_response(self, query: str, user_name: str) -> Dict:
        """
        Génère une réponse template quand aucune autre source n'est disponible
        
        Args:
            query: Question de l'utilisateur
            user_name: Nom de l'utilisateur
            
        Returns:
            Réponse template
        """
        query_lower = query.lower()
        
        # Salutations
        if any(w in query_lower for w in ["bonjour", "salut", "hello", "slt"]):
            return {
                'response': f"""👋 Bonjour {user_name} !

Je suis l'assistant ZamaPay, votre expert en transferts d'argent.

**Je peux vous aider avec:**
• 💰 Frais et tarifs
• ⏱️ Délais de transfert
• 🔒 Sécurité
• 📱 Mobile Money
• ✅ Vérification de compte

Quelle est votre question ?""",
                'confidence': 0.9,
                'source': 'template'
            }
        
        # Frais
        elif any(w in query_lower for w in ["frais", "tarif", "coût", "prix"]):
            return {
                'response': """**💰 Frais ZamaPay**

**Transferts Nationaux (BF):**
• 1% du montant (min 500 F CFA)
• Ex: 50,000 F → 500 F de frais

**Transferts UEMOA:**
• 1.5% du montant (min 750 F CFA)
• Ex: 100,000 F → 1,500 F de frais

**Mobile Money:**
• 1% du montant (min 250 F CFA)
• Transfert instantané

✨ **Aucun frais caché !**

📞 Pour un devis personnalisé: +226 25 40 92 76""",
                'confidence': 0.8,
                'source': 'template'
            }
        
        # Délais
        elif any(w in query_lower for w in ["délai", "temps", "combien", "durée"]):
            return {
                'response': """**⏱️ Délais ZamaPay**

**Standard:**
• Burkina Faso: 2h maximum
• UEMOA: 2-4h
• Mobile Money: Instantané

**Express (+500 F):**
• Toutes destinations: 15 minutes

🔔 **Suivi en temps réel** dans l'app !

📞 Questions: +226 25 40 92 76""",
                'confidence': 0.8,
                'source': 'template'
            }
        
        # Sécurité
        elif any(w in query_lower for w in ["sécurité", "sécurisé", "protection", "fraude"]):
            return {
                'response': """**🔒 Sécurité ZamaPay**

**Protection Maximum:**
• ✅ Cryptage SSL/TLS
• ✅ Authentification 2FA
• ✅ Conforme BCEAO
• ✅ Surveillance 24/7

**Vos Garanties:**
• Données cryptées
• Transactions traçables
• Support anti-fraude
• Remboursement si erreur

🛡️ **100% Sécurisé**

📞 Rapport de fraude: +226 25 40 92 76""",
                'confidence': 0.8,
                'source': 'template'
            }
        
        # Défaut
        else:
            return {
                'response': f"""**💬 Assistant ZamaPay**

Merci pour votre question, {user_name}.

Je suis spécialisé dans:
• 💰 Frais et tarifs
• ⏱️ Délais
• 🔒 Sécurité
• 📱 Mobile Money

**Pour une réponse précise:**
📞 +226 25 40 92 76
📧 contact@zamapay.com

Reformulez votre question ou contactez notre support !""",
                'confidence': 0.6,
                'source': 'template'
            }

    def _create_error_response(self, user_name: str) -> Dict:
        """Crée une réponse d'erreur élégante"""
        return {
            'response': f"""**⚠️ Erreur Technique**

Désolé {user_name}, je rencontre un problème.

**Contactez notre support:**
📞 +226 25 40 92 76 (immédiat)
📧 contact@zamapay.com

Nos conseillers sont disponibles 7j/7 !""",
            'confidence': 0.3,
            'source': 'error'
        }

    # Méthodes de gestion de conversation
    def _update_conversation_memory(
        self, 
        user_name: str, 
        message: str, 
        response: Dict
    ):
        """Met à jour la mémoire conversationnelle"""
        if not user_name:
            return
        
        if user_name not in self.conversation_memory:
            self.conversation_memory[user_name] = {
                'messages': [],
                'topics': [],
                'count': 0
            }
        
        self.conversation_memory[user_name]['messages'].append({
            'user': message,
            'assistant': response.get('response', ''),
            'time': time.time()
        })
        
        # Garder seulement les 10 derniers messages
        if len(self.conversation_memory[user_name]['messages']) > 10:
            self.conversation_memory[user_name]['messages'] = \
                self.conversation_memory[user_name]['messages'][-10:]
        
        self.conversation_memory[user_name]['count'] += 1

    def get_conversation_stats(self, user_name: str) -> Dict:
        """Retourne les statistiques de conversation"""
        if user_name not in self.conversation_memory:
            return {'message_count': 0, 'topics': []}
        
        return {
            'message_count': self.conversation_memory[user_name]['count'],
            'topics': self.conversation_memory[user_name].get('topics', [])
        }

    def clear_conversation(self, user_name: str):
        """Efface l'historique de conversation"""
        if user_name in self.conversation_memory:
            del self.conversation_memory[user_name]
            print(f"🧹 Conversation effacée pour {user_name}")

    def clear_all_caches(self):
        """Efface tous les caches"""
        self.kb_cache.clear()
        self.conversation_memory.clear()
        print("🧹 Tous les caches effacés")


# Test du système
if __name__ == "__main__":
    print("🧪 Test ResponseGenerator Optimisé\n")
    
    # Mock du système de récupération
    class MockRetrievalSystem:
        def search(self, query):
            return [{
                'score': 0.9,
                'qa_data': {
                    'question': 'Quels sont les frais ?',
                    'answer': 'Les frais sont de 1% pour le national.',
                    'questions_connexes': []
                }
            }]
    
    # Initialiser
    retrieval = MockRetrievalSystem()
    generator = ResponseGenerator(retrieval)
    
    # Tests
    test_questions = [
        "Bonjour",
        "Quels sont vos frais ?",
        "Je veux parler à un humain",
        "Combien de temps pour un transfert ?",
        "Est-ce sécurisé ?"
    ]
    
    for q in test_questions:
        print(f"❓ Q: {q}")
        response = generator.generate_response(q, "TestUser")
        print(f"✅ Confiance: {response['confidence']:.0%}")
        print(f"📊 Source: {response['source']}")
        print(f"💬 Réponse: {response['response'][:100]}...")
        print("-" * 60)
        

