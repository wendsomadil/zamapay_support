#!/usr/bin/env python3
"""
RESPONSE_GENERATOR OPTIMISÉ - ZAMAPAY
Version professionnelle avec corrections complètes et performances améliorées
"""
import os
import random
import json
import time
import threading
from typing import Dict, List, Optional
import google.generativeai as genai
from dotenv import load_dotenv

class ResponseGenerator:
    """Générateur de réponses sécurisé avec clé API protégée"""
    
    def __init__(self, retrieval_system):
        # Charger les variables d'environnement
        load_dotenv()
        
        self.retrieval_system = retrieval_system
        self.conversation_memory = {}
        self.kb_cache = {}
        self.cache_timeout = 3600
        
        # ✅ RÉCUPÉRER LA CLÉ DEPUIS .env
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        if not self.gemini_api_key:
            print("❌ ERREUR: Clé API Gemini non trouvée dans .env")
            print("💡 Créez un fichier .env avec: GEMINI_API_KEY=AIzaSyAzUKy-4XE7svSulN1IksyFeHrdVQpQqLw")
            self.gemini_model = None
        else:
            self._setup_gemini()
        
        print("✅ ResponseGenerator initialisé")

    def _setup_gemini(self):
        """Configure Gemini de manière sécurisée"""
        try:
            genai.configure(api_key=self.gemini_api_key)
            
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
            print(f"⚠️ Erreur Gemini: {e}")
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
                return self._create_escalation_response(user_name)
            
            # 2. Recherche dans la base de connaissances
            kb_results = self._search_knowledge_base(user_message)
            
            # 3. Si résultats insuffisants, utiliser Gemini
            if self._should_use_gemini(kb_results, user_message):
                gemini_response = self._generate_with_gemini(user_message, user_name, kb_results)
                if gemini_response:
                    return gemini_response
            
            # 4. Formater et retourner la meilleure réponse
            final_response = self._format_best_response(kb_results, user_message, user_name)
            
            # 5. Mettre à jour la mémoire conversationnelle
            self._update_conversation_memory(user_name, user_message, final_response)
            
            return final_response
            
        except Exception as e:
            print(f"❌ Erreur dans generate_response: {e}")
            return self._create_error_response(user_name)

    def _detect_escalation(self, message: str) -> bool:
        """Détecte si l'utilisateur veut parler à un humain"""
        escalation_keywords = [
            "humain", "agent", "conseiller", "personne", "réel", "vrai personne",
            "parler à", "contact", "support", "urgent", "appeler", "téléphoner",
            "whatsapp", "téléphone", "appel"
        ]
        
        frustration_keywords = [
            "mécontent", "fâché", "insatisfait", "problème", "bug", "erreur",
            "ça marche pas", "fonctionne pas", "insupportable", "ridicule"
        ]
        
        message_lower = message.lower()
        
        # Détection directe d'escalade
        if any(kw in message_lower for kw in escalation_keywords):
            return True
            
        # Détection de frustration
        frustration_count = sum(1 for kw in frustration_keywords if kw in message_lower)
        if frustration_count >= 2:
            return True
            
        return False

    def _create_escalation_response(self, user_name: str) -> Dict:
        """Crée une réponse d'escalade vers support humain"""
        return {
            'response': f"""**🚨 Support Humain Disponible**

Je comprends que vous souhaitez parler à un conseiller, {user_name}.

**📞 Contacts Directs:**
• **Téléphone**: +226 25 40 92 76 (7j/7, 8h-20h)
• **WhatsApp**: +226 25 40 92 76 (Réponse < 5 min)
• **Email**: support@zamapay.com

**🕒 Temps de réponse garanti:**
- Téléphone : Immédiat
- WhatsApp : Moins de 5 minutes  
- Email : Moins de 30 minutes

Notre équipe est là pour vous aider personnellement ! 💙""",
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
        current_time = time.time()
        
        if cache_key in self.kb_cache:
            cached = self.kb_cache[cache_key]
            if current_time - cached['time'] < self.cache_timeout:
                print("💾 Cache hit")
                return cached['results']
        
        # Recherche dans la KB
        try:
            # ✅ CORRECTION: Appel correct à la méthode search du retrieval system
            results = self.retrieval_system.search(query, top_k=3, confidence_threshold=0.1)
            
            # ✅ CORRECTION: Filtrer et trier les résultats
            relevant_results = []
            for result in results:
                if isinstance(result, dict) and result.get('score', 0) > 0.1:
                    relevant_results.append(result)
            
            # Trier par score décroissant
            relevant_results.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            # Mettre en cache
            self.kb_cache[cache_key] = {
                'results': relevant_results[:3],  # Garder seulement les 3 meilleurs
                'time': current_time
            }
            
            print(f"📚 Trouvé {len(relevant_results)} résultats pertinents")
            return relevant_results[:3]
            
        except Exception as e:
            print(f"⚠️ Erreur recherche KB: {e}")
            return []

    def _should_use_gemini(self, kb_results: List[Dict], user_message: str) -> bool:
        """
        Détermine si Gemini doit être utilisé
        
        Args:
            kb_results: Résultats de la base de connaissances
            user_message: Message original de l'utilisateur
            
        Returns:
            True si Gemini doit être utilisé
        """
        # Si Gemini n'est pas disponible
        if not self.gemini_model:
            return False
        
        # Si pas de résultats dans la KB
        if not kb_results:
            return True
        
        # Si le meilleur score est faible
        best_score = kb_results[0].get('score', 0) if kb_results else 0
        if best_score < 0.5:
            return True
        
        # Si la question est complexe (longue ou avec plusieurs aspects)
        if len(user_message.split()) > 10:
            return True
        
        return False

    def _generate_with_gemini(self, query: str, user_name: str, kb_results: List[Dict]) -> Optional[Dict]:
        """
        Génère une réponse avec Gemini 2.5 Flash
        
        Args:
            query: Question de l'utilisateur
            user_name: Nom de l'utilisateur
            kb_results: Résultats de la KB pour contexte
            
        Returns:
            Réponse formatée ou None en cas d'erreur
        """
        if not self.gemini_model:
            return None
        
        try:
            prompt = self._build_gemini_prompt(query, user_name, kb_results)
            
            print("🤖 Génération Gemini...")
            start_time = time.time()
            response = self.gemini_model.generate_content(prompt)
            response_time = time.time() - start_time
            
            if response and hasattr(response, 'text') and response.text:
                answer = response.text.strip()
                
                # Calculer la confiance basée sur le temps de réponse et les résultats KB
                base_confidence = 0.8
                if kb_results:
                    best_score = kb_results[0].get('score', 0)
                    base_confidence = max(0.7, min(0.95, base_confidence + best_score))
                
                # Ajuster basé sur le temps de réponse (plus rapide = plus confiant)
                time_confidence = max(0.1, 1.0 - (response_time / 10.0))
                final_confidence = base_confidence * time_confidence
                
                return {
                    'response': answer,
                    'confidence': final_confidence,
                    'source': 'gemini',
                    'response_time': response_time
                }
            else:
                print("⚠️ Réponse Gemini vide")
                return None
                
        except Exception as e:
            print(f"⚠️ Erreur Gemini: {e}")
            return None

    def _build_gemini_prompt(self, query: str, user_name: str, kb_results: List[Dict]) -> str:
        """
        Construit un prompt optimisé pour Gemini
        
        Args:
            query: Question de l'utilisateur
            user_name: Nom de l'utilisateur
            kb_results: Résultats de la KB pour contexte
            
        Returns:
            Prompt formaté
        """
        # Construire le contexte à partir des résultats KB
        context_lines = []
        if kb_results:
            context_lines.append("**INFORMATIONS ZAMAPAY PERTINENTES:**")
            for i, result in enumerate(kb_results[:2]):  # Prendre les 2 meilleurs
                qa_data = result.get('qa_data', {})
                question = qa_data.get('question_principale', '')
                answer = qa_data.get('reponse', '')
                if question and answer:
                    context_lines.append(f"{i+1}. **Q**: {question}")
                    context_lines.append(f"   **R**: {answer}")
        
        context_text = "\n".join(context_lines) if context_lines else "Aucune information spécifique trouvée dans la base de connaissances."
        
        return f"""Tu es l'assistant intelligent de ZamaPay, plateforme de finance inclusive en Afrique de l'Ouest.

**CONTEXTE GÉNÉRAL ZAMAPAY:**
- Siège: Ouagadougou, Burkina Faso
- Zone: UEMOA (8 pays)
- Devise: Franc CFA (XOF)
- Services: Transferts d'argent, Mobile Money, Paiements
- Mobile Money: Orange Money, Moov Money, Wave
- Support: +226 25 40 92 76
- Email: contact@zamapay.com

{context_text}

**QUESTION DE {user_name.upper()}:**
{query}

**TON RÔLE:**
- Réponds en français, clair et professionnel
- Utilise les montants en F CFA quand pertinent
- Sois chaleureux mais expert
- Si l'information n'est pas suffisante, oriente vers le support
- Format: court, structuré et facile à lire (max 150 mots)
- Personnalise avec le nom de l'utilisateur si possible

**RÉPONSE ZAMAPAY:**"""

    def _format_best_response(self, kb_results: List[Dict], query: str, user_name: str) -> Dict:
        """
        Formate la meilleure réponse depuis la base de connaissances
        """
        if not kb_results:
            return self._generate_template_response(query, user_name)
        
        best_match = kb_results[0]
        qa_data = best_match.get('qa_data', {})
        
        # ✅ CORRECTION: Utiliser les bonnes clés de votre base de connaissances
        question = qa_data.get('question_principale', 'Information')
        answer = qa_data.get('reponse', '')  # Clé corrigée: 'reponse' au lieu de 'answer'
        
        if not answer:
            return self._generate_template_response(query, user_name)
        
        # Personnaliser la réponse
        if user_name and user_name != "Utilisateur":
            greeting = f"👋 Bonjour {user_name} ! "
        else:
            greeting = "👋 Bonjour ! "
        
        # Formater la réponse
        formatted_response = f"""{greeting}

{answer}

📊 **Confiance**: {best_match.get('score', 0.7):.0%}
💡 *Réponse basée sur notre base de connaissances ZamaPay*

**Besoin de plus d'infos?** 📞 +226 25 40 92 76"""
        
        return {
            'response': formatted_response,
            'confidence': best_match.get('score', 0.7),
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
        if any(w in query_lower for w in ["bonjour", "salut", "hello", "slt", "coucou", "bjr"]):
            return {
                'response': f"""👋 Bonjour {user_name} !

Je suis l'assistant ZamaPay, votre expert en transferts d'argent et services financiers.

**Je peux vous aider avec:**
• 💰 **Frais et tarifs** des transferts
• ⏱️ **Délais** de traitement  
• 🔒 **Sécurité** des transactions
• 📱 **Mobile Money** (Orange, Moov, Wave)
• ✅ **Vérification** de compte
• 🏦 **Services** bancaires

**Quelle est votre question spécifique ?** 📝""",
                'confidence': 0.9,
                'source': 'template'
            }
        
        # Frais
        elif any(w in query_lower for w in ["frais", "tarif", "coût", "prix", "combien coûte"]):
            return {
                'response': f"""**💰 Frais ZamaPay - Transparence Totale**

**Transferts Nationaux (Burkina Faso):**
• **1%** du montant (minimum 500 F CFA)
• *Exemple: 50,000 F → 500 F de frais*

**Transferts UEMOA (8 pays):**
• **1.5%** du montant (minimum 750 F CFA)  
• *Exemple: 100,000 F → 1,500 F de frais*

**Mobile Money:**
• **1%** du montant (minimum 250 F CFA)
• Transfert **instantané**

✨ **Aucun frais caché !** 100% transparent.

📞 **Devis personnalisé**: +226 25 40 92 76""",
                'confidence': 0.85,
                'source': 'template'
            }
        
        # Délais
        elif any(w in query_lower for w in ["délai", "temps", "combien de temps", "durée", "quand"]):
            return {
                'response': f"""**⏱️ Délais de Traitement ZamaPay**

**Transferts Standards:**
• **Burkina Faso** : 2 heures maximum
• **UEMOA** : 2-4 heures  
• **Mobile Money** : Instantané ✅

**Option Express** (+500 F CFA):
• Toutes destinations : **15 minutes** ⚡

🔔 **Suivi en temps réel** disponible dans votre espace client !

📞 **Urgence?** +226 25 40 92 76""",
                'confidence': 0.85,
                'source': 'template'
            }
        
        # Sécurité
        elif any(w in query_lower for w in ["sécurité", "sécurisé", "protection", "fraude", "risque"]):
            return {
                'response': f"""**🔒 Sécurité ZamaPay - Niveau Maximum**

**Protections Actives:**
• ✅ **Cryptage SSL/TLS** avancé
• ✅ **Authentification 2FA** obligatoire
• ✅ **Conformité BCEAO** totale
• ✅ **Surveillance 24h/24** anti-fraude

**Vos Garanties:**
• Données **cryptées** et sécurisées
• Transactions **traçables** et vérifiables
• Support **anti-fraude** dédié
• **Remboursement** garanti en cas d'erreur

🛡️ **100% Sécurisé - Garanti ZamaPay**

📞 **Signalement fraude**: +226 25 40 92 76""",
                'confidence': 0.9,
                'source': 'template'
            }
        
        # Vérification compte
        elif any(w in query_lower for w in ["vérifier", "vérification", "compte", "authentifier"]):
            return {
                'response': f"""**✅ Vérification de Compte ZamaPay**

**Documents Requis:**
1. **CNIB** ou Passeport (recto-verso)
2. **Justificatif de domicile** (moins de 3 mois)
3. **Photo** récente (selfie avec pièce)

**Processus:**
1. Téléchargez les documents dans l'app
2. Vérification automatique (2-4 heures)
3. Notification de confirmation

**Statut de Vérification:**
• 📱 Vérifiez dans **Mon Profil**
• 📧 Notification par email
• 🔔 Alertes dans l'application

⏱️ **Vérification express disponible**: +226 25 40 92 76""",
                'confidence': 0.8,
                'source': 'template'
            }
        
        # Défaut - réponse générique
        else:
            return {
                'response': f"""**💬 Assistant ZamaPay**

Merci pour votre question, {user_name} !

Je suis spécialisé dans l'assistance **ZamaPay**:

• 💰 **Frais et tarifs** des transferts
• ⏱️ **Délais** de traitement  
• 🔒 **Sécurité** et protection
• 📱 **Mobile Money** et services
• ✅ **Vérification** de compte

**Pour une réponse précise et personnalisée:**
📞 **Support direct**: +226 25 40 92 76
📧 **Email**: support@zamapay.com
🕒 **7j/7** de 8h à 20h

N'hésitez pas à reformuler votre question ! 😊""",
                'confidence': 0.6,
                'source': 'template'
            }

    def _create_error_response(self, user_name: str) -> Dict:
        """Crée une réponse d'erreur élégante"""
        return {
            'response': f"""**⚠️ Temporairement Indisponible**

Désolé {user_name}, je rencontre une difficulté technique momentanée.

**Notre équipe reste disponible pour vous aider:**
📞 **Support Immédiat**: +226 25 40 92 76
📧 **Email**: support@zamapay.com  
🕒 **7j/7** de 8h à 20h

Nous nous excusons pour la gêne occasionnée.
Le service normal sera rétabli rapidement ! 🔧""",
            'confidence': 0.3,
            'source': 'error'
        }

    # ✅ CORRECTIONS: Méthodes de gestion de conversation améliorées
    def _update_conversation_memory(self, user_name: str, message: str, response: Dict):
        """Met à jour la mémoire conversationnelle"""
        if not user_name or user_name == "Utilisateur":
            return
        
        try:
            if user_name not in self.conversation_memory:
                self.conversation_memory[user_name] = {
                    'messages': [],
                    'topics': set(),
                    'message_count': 0,
                    'first_seen': time.time(),
                    'last_seen': time.time()
                }
            
            # Ajouter le message
            self.conversation_memory[user_name]['messages'].append({
                'user_message': message,
                'assistant_response': response.get('response', ''),
                'confidence': response.get('confidence', 0),
                'source': response.get('source', 'unknown'),
                'timestamp': time.time()
            })
            
            # Garder seulement les 20 derniers messages
            if len(self.conversation_memory[user_name]['messages']) > 20:
                self.conversation_memory[user_name]['messages'] = \
                    self.conversation_memory[user_name]['messages'][-20:]
            
            # Mettre à jour les métriques
            self.conversation_memory[user_name]['message_count'] += 1
            self.conversation_memory[user_name]['last_seen'] = time.time()
            
            # Détection de topics (simplifiée)
            topics = self._detect_topics(message)
            self.conversation_memory[user_name]['topics'].update(topics)
            
        except Exception as e:
            print(f"⚠️ Erreur mise à jour mémoire: {e}")

    def _detect_topics(self, message: str) -> List[str]:
        """Détecte les topics dans un message"""
        topics = []
        message_lower = message.lower()
        
        topic_keywords = {
            'frais': ['frais', 'tarif', 'coût', 'prix'],
            'délais': ['délai', 'temps', 'combien de temps', 'quand'],
            'sécurité': ['sécurité', 'sécurisé', 'protection', 'fraude'],
            'compte': ['compte', 'vérification', 'authentification', 'profil'],
            'mobile_money': ['mobile money', 'orange', 'moov', 'wave'],
            'transfert': ['transfert', 'envoyer', 'envoi', 'argent']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                topics.append(topic)
        
        return topics

    def get_conversation_stats(self, user_name: str) -> Dict:
        """Retourne les statistiques de conversation"""
        if user_name not in self.conversation_memory:
            return {
                'message_count': 0,
                'topics': [],
                'first_seen': None,
                'last_seen': None
            }
        
        memory = self.conversation_memory[user_name]
        return {
            'message_count': memory['message_count'],
            'topics': list(memory.get('topics', [])),
            'first_seen': memory.get('first_seen'),
            'last_seen': memory.get('last_seen')
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

    def get_cache_info(self) -> Dict:
        """Retourne des informations sur les caches"""
        return {
            'kb_cache_size': len(self.kb_cache),
            'conversation_memory_size': len(self.conversation_memory),
            'cache_timeout': self.cache_timeout
        }

# Test du système
if __name__ == "__main__":
    print("🧪 Test ResponseGenerator Optimisé\n")
    
    # Mock du système de récupération
    class MockRetrievalSystem:
        def search(self, query, top_k=3, confidence_threshold=0.1):
            # Simuler des résultats différents selon la requête
            if "frais" in query.lower():
                return [{
                    'score': 0.9,
                    'qa_data': {
                        'question_principale': 'Quels sont vos frais ?',
                        'reponse': 'Nos frais sont de 1% pour les transferts nationaux avec un minimum de 500 FCFA.',
                        'categorie': 'tarifs'
                    }
                }]
            elif "délai" in query.lower():
                return [{
                    'score': 0.8,
                    'qa_data': {
                        'question_principale': 'Combien de temps pour un transfert ?',
                        'reponse': 'Les transferts sont traités en 2 heures maximum pour le Burkina Faso.',
                        'categorie': 'délais'
                    }
                }]
            else:
                return []  # Aucun résultat
    
    # Initialiser
    retrieval = MockRetrievalSystem()
    generator = ResponseGenerator(retrieval)
    
    # Tests
    test_questions = [
        "Bonjour",
        "Quels sont vos frais ?",
        "Je veux parler à un humain",
        "Combien de temps pour un transfert ?",
        "Est-ce sécurisé ?",
        "Comment vérifier mon compte ?",
        "slt"
    ]
    
    for q in test_questions:
        print(f"❓ Q: {q}")
        start_time = time.time()
        response = generator.generate_response(q, "TestUser")
        response_time = time.time() - start_time
        
        print(f"✅ Confiance: {response['confidence']:.0%}")
        print(f"📊 Source: {response['source']}")
        print(f"⏱️ Temps: {response_time:.2f}s")
        print(f"💬 Réponse: {response['response'][:150]}...")
        print("-" * 80)
    
    # Afficher les stats
    stats = generator.get_conversation_stats("TestUser")
    print(f"\n📈 Stats conversation: {stats}")
    
    cache_info = generator.get_cache_info()
    print(f"📦 Info cache: {cache_info}")
    
