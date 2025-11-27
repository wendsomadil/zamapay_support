#!/usr/bin/env python3
"""
RESPONSE_GENERATOR OPTIMISÉ - ZAMAPAY
Version professionnelle avec gestion du contenu enrichi et tontine digitale
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
    """Générateur de réponses sécurisé avec gestion de contenu enrichi"""
    
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
            print("💡 Créez un fichier .env avec: GEMINI_API_KEY=AIzaSyAenI3o19n0WGQDU41CSojv3DWg6QMhTWs")
            self.gemini_model = None
        else:
            self._setup_gemini()
        
        print("✅ ResponseGenerator initialisé avec contenu enrichi")

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
                    "max_output_tokens": 2048,  # Augmenté pour contenu enrichi
                }
            )
            print("✅ Gemini 2.5 Flash configuré pour contenu enrichi")
            
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
            
            # 2. Détection spécifique tontine
            if self._detect_tontine_query(user_message):
                return self._handle_tontine_query(user_message, user_name)
            
            # 3. Recherche dans la base de connaissances enrichie
            kb_results = self._search_knowledge_base(user_message)
            
            # 4. Si résultats insuffisants, utiliser Gemini
            if self._should_use_gemini(kb_results, user_message):
                gemini_response = self._generate_with_gemini(user_message, user_name, kb_results)
                if gemini_response:
                    return gemini_response
            
            # 5. Formater et retourner la meilleure réponse
            final_response = self._format_best_response(kb_results, user_message, user_name)
            
            # 6. Mettre à jour la mémoire conversationnelle
            self._update_conversation_memory(user_name, user_message, final_response)
            
            return final_response
            
        except Exception as e:
            print(f"❌ Erreur dans generate_response: {e}")
            return self._create_error_response(user_name)

    def _detect_tontine_query(self, message: str) -> bool:
        """Détecte les questions spécifiques sur la tontine"""
        tontine_keywords = [
            "tontine", "épargne collective", "cagnotte", "groupe épargne",
            "rotative", "cotisation collective", "épargne groupe",
            "tontine digitale", "tontine en ligne", "tontine numérique"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in tontine_keywords)

    def _handle_tontine_query(self, query: str, user_name: str) -> Dict:
        """Gère spécifiquement les questions sur la tontine"""
        # Recherche ciblée dans la base de connaissances
        kb_results = self._search_knowledge_base(query)
        
        if kb_results:
            best_match = kb_results[0]
            confidence = best_match.get('score', 0.7)
            
            # Si confiance élevée, utiliser directement la KB
            if confidence > 0.8:
                return self._format_knowledge_response(best_match, user_name, confidence)
        
        # Sinon, utiliser le template tontine
        return self._generate_tontine_template_response(query, user_name)

    def _generate_tontine_template_response(self, query: str, user_name: str) -> Dict:
        """Génère une réponse template pour la tontine"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["créer", "démarrer", "commencer", "lancer"]):
            return {
                'response': f"""**🔄 Créer une Tontine ZamaPay - Guide Complet**

Bonjour {user_name} ! Voici comment créer votre tontine digitale :

## 📱 Étapes de Création :
1. **Ouvrez l'application ZamaPay** → Section **Tontines**
2. **Cliquez sur \"Créer un groupe\"**
3. **Configurez les paramètres :**
   - Nom du groupe
   - Montant de cotisation (1 000 - 50 000 F CFA)
   - Nombre de membres (5-30 personnes)
   - Fréquence (quotidienne, hebdomadaire, mensuelle)

## ⚙️ Configuration Avancée :
- **Ordre de bénéfice :** Aléatoire, vote ou ancienneté
- **Règles personnalisables :** Tolérance retard, sanctions
- **Options de sécurité :** Validation des membres

## 🎯 Avantages Exclusifs :
- **Frais réduits :** 1.5% seulement
- **Sécurité maximale :** Fonds garantis jusqu'à 5 millions F CFA
- **Automatisation :** Rappels, prélèvements auto
- **Support dédié :** Conseiller tontine disponible

**💡 Prêt à démarrer ?** 
📱 **Application ZamaPay** → **Tontines** → **Créer un groupe**
📞 **Assistance :** +226 25 40 92 76 (Section Tontines)""",
                'confidence': 0.9,
                'source': 'template_tontine'
            }
        
        elif any(word in query_lower for word in ["avantage", "bénéfice", "sécurité", "garantie"]):
            return {
                'response': f"""**🛡️ Avantages & Sécurité Tontine ZamaPay**

{user_name}, découvrez pourquoi choisir nos tontines digitales :

## 💰 Avantages Financiers :
- **Frais réduits :** 1.5% vs 5-10% en manuel
- **Cashback :** 0.5% sur volume du groupe
- **Points fidélité :** Cumul avec programme principal
- **Intérêts :** Jusqu'à 8% annuel sur certains modèles

## 🔒 Sécurité Maximale :
- **Fonds sécurisés :** Comptes séquestres chez partenaires bancaires
- **Garantie :** Jusqu'à 5 millions F CFA par groupe
- **Assurance :** Couverture décès, invalidité, chômage
- **Audit :** Vérification quotidienne indépendante

## 📊 Chiffres Clés 2024 :
- **2 500 groupes actifs** - **45 000 membres**
- **98.7% de réussite** - **0 incident majeur**
- **850 millions F CFA** d'épargne collective gérée

**🚀 Rejoignez la révolution de l'épargne collective sécurisée !**""",
                'confidence': 0.9,
                'source': 'template_tontine'
            }
        
        else:
            return {
                'response': f"""**👥 Tontine Digitale ZamaPay**

{user_name}, voici nos services de tontine digitale :

## 💡 Nos Modèles de Tontine :

**1. Tontine Rotative Classique :**
- Groupe de 10-30 membres
- Cotisation : 1 000 - 50 000 F CFA
- Ordre de bénéfice : Aléatoire ou accord mutuel

**2. Tontine avec Intérêts :**
- Fonds commun générant des intérêts
- Partage équitable des bénéfices
- Taux : 3% à 8% annuel

**3. Tontine Projet :**
- Épargne ciblée (construction, business)
- Accompagnement conseillers
- Suivi dédié du projet

## 🎯 Pourquoi Choisir ZamaPay ?
- ✅ **Sécurité bancaire** des fonds
- ✅ **Transparence totale** des operations
- ✅ **Automatisation complète** de la gestion
- ✅ **Support dédié** 24h/24

**📞 En savoir plus ?** 
Contactez notre équipe tontine : +226 25 40 92 76
🌐 **Application ZamaPay** → Section **Tontines**""",
                'confidence': 0.85,
                'source': 'template_tontine'
            }

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
• **Section Tontines**: +226 70 123 456

**🕒 Temps de réponse garanti:**
- Téléphone : Immédiat
- WhatsApp : Moins de 5 minutes  
- Email : Moins de 30 minutes
- Tontines : Moins de 15 minutes

Notre équipe est là pour vous aider personnellement ! 💙""",
            'confidence': 0.95,
            'source': 'escalation'
        }

    def _search_knowledge_base(self, query: str) -> List[Dict]:
        """
        Recherche optimisée avec support pour tous les systèmes
        """
        cache_key = query.lower().strip()
        current_time = time.time()
        
        # Vérifier le cache
        if cache_key in self.kb_cache:
            cached = self.kb_cache[cache_key]
            if current_time - cached['time'] < self.cache_timeout:
                print("💾 Cache hit")
                return cached['results']
        
        try:
            # ✅ CORRECTION: Gestion unifiée de tous les systèmes
            results = []
            
            # Système UnifiedRetrievalSystem ou RetrievalSystem standard
            if hasattr(self.retrieval_system, 'search') and hasattr(self.retrieval_system, 'use_faiss'):
                results = self.retrieval_system.search(query, top_k=3, confidence_threshold=0.1)
            
            # Système FAISSGeminiRetrieval
            elif hasattr(self.retrieval_system, 'search'):
                try:
                    # Essayer sans confidence_threshold d'abord
                    search_results = self.retrieval_system.search(query, top_k=3)
                    # Convertir le format
                    for doc, score in search_results:
                        results.append({
                            'qa_data': {
                                'question_principale': doc['question'],
                                'reponse': doc['answer'],
                                'categorie': doc['category'],
                                'id': hash(doc['question'])
                            },
                            'score': score,
                            'match_type': 'semantic'
                        })
                except TypeError as e:
                    # Si l'erreur persiste, essayer avec confidence_threshold
                    if "confidence_threshold" in str(e):
                        search_results = self.retrieval_system.search(query, top_k=3)
                        for doc, score in search_results:
                            results.append({
                                'qa_data': {
                                    'question_principale': doc['question'],
                                    'reponse': doc['answer'], 
                                    'categorie': doc['category'],
                                    'id': hash(doc['question'])
                                },
                                'score': score,
                                'match_type': 'semantic'
                            })
            
            # Filtrer et trier
            relevant_results = []
            for result in results:
                if isinstance(result, dict) and result.get('score', 0) > 0.1:
                    relevant_results.append(result)
            
            relevant_results.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            # Mettre en cache
            self.kb_cache[cache_key] = {
                'results': relevant_results[:3],
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
                
                # ✅ CORRECTION: Calcul de confiance amélioré pour Gemini
                # Base de confiance plus élevée pour Gemini
                base_confidence = 0.85  # Augmenté de 0.8 à 0.85
                
                # Ajustement basé sur les résultats KB (plus favorable)
                if kb_results:
                    best_score = kb_results[0].get('score', 0)
                    # Si la KB a des résultats pertinents, on augmente la confiance
                    if best_score > 0.3:  # Seuil abaissé
                        base_confidence = max(0.8, min(0.95, base_confidence + (best_score * 0.3)))
                
                # ✅ CORRECTION: Ajustement temps de réponse plus favorable
                # Temps de réponse optimal entre 2-5 secondes
                if response_time < 2.0:
                    time_boost = 0.1  # Réponse très rapide
                elif response_time < 5.0:
                    time_boost = 0.05  # Réponse rapide
                elif response_time > 10.0:
                    time_boost = -0.1  # Réponse lente
                else:
                    time_boost = 0.0  # Temps normal
                
                final_confidence = base_confidence + time_boost
                
                # ✅ CORRECTION: Confiance minimale garantie pour Gemini
                final_confidence = max(0.75, min(0.95, final_confidence))
                
                print(f"📊 Confiance Gemini: base={base_confidence:.2f}, temps={response_time:.2f}s, final={final_confidence:.2f}")
                
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
        
    def _should_use_gemini(self, kb_results: List[Dict], user_message: str) -> bool:
        """
        Détermine si Gemini doit être utilisé - Version améliorée
        
        Args:
            kb_results: Résultats de la base de connaissances
            user_message: Message original de l'utilisateur
            
        Returns:
            True si Gemini doit être utilisé
        """
        # Si Gemini n'est pas disponible
        if not self.gemini_model:
            return False
        
        # ✅ CORRECTION: Utiliser Gemini pour les questions complexes même avec des résultats KB
        question_complexity = self._assess_question_complexity(user_message)
        
        # Si pas de résultats dans la KB
        if not kb_results:
            return True
        
        # Si le meilleur score est faible
        best_score = kb_results[0].get('score', 0) if kb_results else 0
        if best_score < 0.6:  # Seuil augmenté de 0.5 à 0.6
            return True
        
        # ✅ CORRECTION: Questions complexes -> toujours utiliser Gemini
        if question_complexity == "high":
            return True
        
        # Si la question est longue ou avec plusieurs aspects
        if len(user_message.split()) > 15:  # Augmenté de 10 à 15
            return True
        
        return False

    def _assess_question_complexity(self, message: str) -> str:
        """
        Évalue la complexité de la question
        
        Returns:
            "low", "medium", "high"
        """
        message_lower = message.lower()
        word_count = len(message.split())
        
        # Mots indiquant une question complexe
        complex_indicators = [
            "comparer", "différence", "avantage", "inconvénient", "quelle est la meilleure",
            "recommander", "conseiller", "pourquoi", "comment fonctionne", "étape par étape",
            "guide complet", "tutoriel", "expliquer en détail"
        ]
        
        complex_count = sum(1 for indicator in complex_indicators if indicator in message_lower)
        
        if complex_count >= 2 or word_count > 20:
            return "high"
        elif complex_count >= 1 or word_count > 12:
            return "medium"
        else:
            return "low"
    
    def _build_gemini_prompt(self, query: str, user_name: str, kb_results: List[Dict]) -> str:
        """
        Construit un prompt optimisé pour Gemini - Version améliorée
        """
        # Construire le contexte à partir des résultats KB
        context_lines = []
        if kb_results:
            context_lines.append("**INFORMATIONS ZAMAPAY PERTINENTES:**")
            for i, result in enumerate(kb_results[:3]):  # Prendre les 3 meilleurs maintenant
                qa_data = result.get('qa_data', {})
                question = qa_data.get('question_principale', '')
                answer = qa_data.get('reponse', '')
                score = result.get('score', 0)
                
                if question and answer:
                    relevance_note = "📊 Pertinence élevée" if score > 0.7 else "📊 Information connexe"
                    context_lines.append(f"{i+1}. **Q**: {question}")
                    context_lines.append(f"   **R**: {answer[:400]}...")  # Limiter moins strictement
                    context_lines.append(f"   *{relevance_note}*")
                    context_lines.append("")  # Ligne vide pour la lisibilité
        
        context_text = "\n".join(context_lines) if context_lines else "Aucune information spécifique trouvée dans la base de connaissances ZamaPay."

        return f"""Tu es l'assistant expert de ZamaPay, plateforme leader de finance inclusive en Afrique de l'Ouest.

    **INFORMATIONS ENTREPRISE ZAMAPAY:**
    - Siège: Ouagadougou, Burkina Faso
    - Zone de couverture: UEMOA (8 pays)
    - Devise: Franc CFA (XOF)
    - Services principaux: Transferts d'argent, Mobile Money, Paiements digitaux, Tontines digitales sécurisées
    - Partenaires Mobile Money: Orange Money, Moov Money, Wave
    - Tontine digitale: Épargne collective avec sécurité bancaire
    - Support client: +226 25 40 92 76
    - Email officiel: contact@zamapay.com
    - Site web: www.zamapay.com

    **CONTEXTE DISPONIBLE:**
    {context_text}

    **QUESTION DE L'UTILISATEUR ({user_name}):**
    "{query}"

    **INSTRUCTIONS DE RÉPONSE:**
    - Réponds en français professionnel et chaleureux
    - Utilise les montants en F CFA pour tous les exemples financiers
    - Sois précis, concret et orienté solution
    - Structure ta réponse avec des parties claires si nécessaire
    - Mentionne les avantages ZamaPay quand c'est pertinent
    - Pour les tontines: souligne la sécurité des fonds et les frais réduits
    - Si l'information manque, oriente vers le support dédié
    - Personnalise avec le nom {user_name} si naturel
    - Limite ta réponse à 300-400 mots maximum

    **TONE:**
    - Expert mais accessible
    - Enthousiaste mais professionnel  
    - Confiant et rassurant
    - Orienté service client

    **RÉPONSE ZAMAPAY (format structuré et utile):**"""

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

    def _format_knowledge_response(self, result: Dict, user_name: str, confidence: float) -> Dict:
        """Formate une réponse directement depuis la KB enrichie"""
        qa_data = result['qa_data']
        
        response_template = f"""**{qa_data.get('question_principale', 'Information ZamaPay')}**

{qa_data.get('reponse', 'Information non disponible.')}

---

**📊 Informations complémentaires:**
- **Catégorie :** {qa_data.get('categorie', 'Général')}
- **Confiance :** {confidence:.1%}
- **Source :** Base de connaissances ZamaPay
- **Mise à jour :** 2024

**💡 Besoin de précisions ?** 
📞 Contactez notre équipe au +226 25 40 92 76
🕒 7j/7 de 8h à 20h"""

        return {
            'response': response_template,
            'confidence': confidence,
            'source': 'knowledge_base_enhanced',
            'chunks_used': 1
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

Je suis l'assistant ZamaPay, votre expert en services financiers digitaux.

**Je peux vous aider avec:**
• 💰 **Frais et tarifs** des transferts
• ⏱️ **Délais** de traitement  
• 🔒 **Sécurité** des transactions
• 📱 **Mobile Money** (Orange, Moov, Wave)
• 👥 **Tontines digitales** sécurisées
• ✅ **Vérification** de compte
• 🏦 **Services** bancaires
• 🎁 **Programmes fidélité** et parrainage

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

**Tontines Digitales:**
• **1.5%** du fonds géré seulement
• **Sécurité bancaire** incluse

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
• **Tontines** : Traitement immédiat

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
• ✅ **Fonds tontines séquestrés** chez banques partenaires

**Vos Garanties:**
• Données **cryptées** et sécurisées
• Transactions **traçables** et vérifiables
• Support **anti-fraude** dédié
• **Remboursement** garanti en cas d'erreur
• **Assurance** tontines jusqu'à 5 millions F CFA

🛡️ **100% Sécurisé - Garanti ZamaPay**

📞 **Signalement fraude**: +226 25 40 92 76""",
                'confidence': 0.9,
                'source': 'template'
            }
        
        # Tontine spécifique
        elif any(w in query_lower for w in ["tontine", "épargne collective", "cagnotte"]):
            return self._generate_tontine_template_response(query, user_name)
        
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
• 👥 **Tontines digitales** sécurisées
• ✅ **Vérification** de compte
• 🎁 **Programmes fidélité** et avantages

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
👥 **Section Tontines**: +226 70 123 456

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
            'transfert': ['transfert', 'envoyer', 'envoi', 'argent'],
            'tontine': ['tontine', 'épargne collective', 'cagnotte', 'rotative']
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
    print("🧪 Test ResponseGenerator Optimisé avec Tontines\n")
    
    # Mock du système de récupération
    class MockRetrievalSystem:
        def search(self, query, top_k=3, confidence_threshold=0.1):
            # Simuler des résultats différents selon la requête
            if "tontine" in query.lower():
                return [{
                    'score': 0.9,
                    'qa_data': {
                        'question_principale': 'Services de tontine digitale ZamaPay',
                        'reponse': 'Nos services de tontine digitale offrent sécurité et transparence...',
                        'categorie': 'tontine_digitale'
                    }
                }]
            elif "frais" in query.lower():
                return [{
                    'score': 0.9,
                    'qa_data': {
                        'question_principale': 'Politique détaillée des frais et tarifs ZamaPay',
                        'reponse': 'Nos frais sont compétitifs et transparents...',
                        'categorie': 'frais_tarifs'
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
        "Quels sont vos frais pour les tontines ?",
        "Comment créer une tontine digitale ?",
        "Est-ce que les tontines sont sécurisées ?",
        "Je veux parler à un conseiller tontine"
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
    
