#!/usr/bin/env python3
"""
RESPONSE_GENERATOR CORRIGÉ - ZAMAPAY
Version optimisée avec corrections des bugs et améliorations des performances

Cette version inclut une mise à jour de la logique de fallback Gemini
afin d'utiliser plus fréquemment le modèle Gemini lorsqu'aucune réponse
pertinente n'est trouvée dans la base de connaissances ou lorsque les
résultats de celle‑ci sont jugés trop faibles. Le reste du code est
repris tel que fourni par l'utilisateur, avec les améliorations
d'origine.
"""

import random
import json
import time
import threading
import google.generativeai as genai
from web_searcher import WebSearcher

class ResponseGenerator:
    def __init__(self, retrieval_system):
        """
        Initialise le générateur de réponses corrigé
        """
        self.retrieval_system = retrieval_system
        self.web_searcher = WebSearcher()
        self.conversation_memory = {}
        self.escalation_threshold = 0.4
        
        # Cache optimisé pour les performances
        self.web_cache = {}
        self.cache_timeout = 3600  # 1 heure
        self.kb_cache = {}  # Nouveau cache pour la base de connaissances
        
        # Configuration Gemini robuste
        self.gemini_api_key = "VOTRE_CLE_API_GEMINI"
        self._setup_gemini()
        
        print("✅ ResponseGenerator initialisé avec succès")

    def _setup_gemini(self):
        """Configure l'API Gemini avec gestion d'erreurs robuste"""
        try:
            # Configurez correctement l'API Gemini avec la clé API
            genai.configure(api_key=self.gemini_api_key)  # Simplement passer la clé API
            # Utilisation du modèle Gemini sans 'headers'
            self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
            print("✅ Gemini configuré avec succès")
        except Exception as e:
            print(f"❌ Erreur configuration Gemini: {e}")
            self.gemini_model = None
            
    def generate_response(self, user_message, user_name=None):
        """Génère une réponse avec détection prioritaire d'escalade"""
        print(f"💬 Conversation: '{user_message}'")
        
        # 🔥 NOUVEAU: Détection PRIORITAIRE d'escalade
        escalation_intent = self._detect_escalation_intent(user_message)
        if escalation_intent:
            print("🚨 Détection d'escalade prioritaire - Passage direct au support")
            return self._create_escalation_response()
        
        try:
            # 1. Analyse du contexte et de l'intention
            conversation_context = self._get_conversation_context(user_name)
            intent = self._analyze_intent(user_message)
            
            # 2. Recherche RAG optimisée avec timeout
            rag_results = self._enhanced_rag_search(user_message, intent)
            
            # 3. Fallback Gemini si nécessaire
            if self._should_use_gemini_fallback(rag_results):
                print("🔍 Aucune réponse pertinente trouvée ou score insuffisant, utilisation de Gemini...")
                gemini_response = self._generate_with_gemini_fallback(user_message)
                if gemini_response:
                    return self._format_gemini_response(gemini_response)
            
            # 4. Génération de réponse adaptée à l'intention
            response = self._generate_intent_based_response(user_message, rag_results, intent, conversation_context)
            
            # 5. Mise à jour du contexte conversationnel
            self._update_conversation_memory(user_name, user_message, response)
            
            return response
            
        except Exception as e:
            print(f"❌ Erreur critique dans generate_response: {e}")
            return self._create_error_response()

    def _detect_escalation_intent(self, user_message):
        """Détecte les intentions d'escalade prioritaires"""
        message_lower = user_message.lower()
        
        # Mots-clés pour escalade immédiate
        escalation_keywords = [
            "parler à un humain", "conseiller humain", "agent réel", "vrai personne",
            "support humain", "assistant humain", "parler à quelqu'un", "contact humain",
            "je veux un humain", "pas un robot", "escalader", "urgence", "frustré",
            "énervé", "mécontent", "insatisfait", "problème grave", "urgence"
        ]
        
        return any(keyword in message_lower for keyword in escalation_keywords)

    def _create_escalation_response(self):
        """Crée une réponse d'escalade prioritaire"""
        return {
            'type': 'escalation',
            'response': """**🚨 Support Humain - Priorité**

    Je comprends que vous souhaitez parler à un conseiller humain. Voici nos contacts directs :

    **📞 Contact Immédiat :**
    • Téléphone : **70 123 456** (24h/24)
    • WhatsApp : **+226 70 123 456**
    • Email : support@zamapay.com

    **🕒 Délai de réponse :**
    - Téléphone : **Immédiat**
    - WhatsApp : **Moins de 5 minutes**
    - Email : **Moins de 30 minutes**

    Notre équipe est là pour vous aider personnellement !""",
            'confidence': 0.95,
            'source': 'escalation_detection'
        }

    def _should_use_gemini_fallback(self, rag_results):
        """
        Détermine si l'on doit utiliser Gemini comme fallback.
        
        Cette version déclenche Gemini plus fréquemment :
        - si aucun résultat de base de connaissances n'est disponible
        - ou si le meilleur résultat est jugé trop faible (< 0.5)
        - et s'il n'y a pas déjà eu d'analyse Gemini
        - et si le modèle Gemini est correctement initialisé
        
        Args:
            rag_results: résultats de la recherche RAG
        Returns:
            bool indiquant si Gemini doit être utilisé
        """
        # S'assurer que le modèle est disponible
        if not self.gemini_model:
            return False
        # Vérifier les résultats de la base de connaissances
        has_kb_results = bool(rag_results.get("knowledge_base")) and len(rag_results["knowledge_base"]) > 0
        kb_score = 0.0
        if has_kb_results:
            top_kb = rag_results["knowledge_base"][0]
            if isinstance(top_kb, dict) and 'score' in top_kb:
                kb_score = top_kb['score']
        # Vérifier si une analyse Gemini a déjà été effectuée
        has_gemini_analysis = rag_results.get("gemini_analysis") is not None
        # Utiliser Gemini si pas de KB ou score faible, et pas d'analyse Gemini existante
        return ((not has_kb_results) or (kb_score < 0.5)) and not has_gemini_analysis

    def _format_gemini_response(self, response_text):
        """Formate une réponse Gemini"""
        return {
            'type': 'success',
            'response': response_text,
            'confidence': 0.8,
            'source': 'gemini_fallback'
        }

    def _create_error_response(self):
        """Crée une réponse d'erreur élégante"""
        return {
            'type': 'error',
            'response': "🚨 Désolé, je rencontre un problème technique. Veuillez contacter notre support au 70 123 456 pour une assistance immédiate.",
            'confidence': 0.0,
            'source': 'error_handler'
        }

    def _enhanced_rag_search(self, user_message, intent):
        """
        Recherche RAG améliorée avec gestion d'erreurs et timeout - VERSION CORRIGÉE
        """
        results = {
            "knowledge_base": [],
            "web_search": [],
            "gemini_analysis": None,
            "confidence": 0.0
        }
        try:
            self._search_knowledge_base_optimized(user_message, results)
            if results["confidence"] < 0.5:
                self._search_web_with_timeout(user_message, intent, results)
            if (intent in ["complex_analysis", "problem_solving"] and 
                self.gemini_model and 
                results["confidence"] < 0.7):
                self._search_gemini_analysis(user_message, results)
        except Exception as e:
            print(f"⚠️ Erreur lors de la recherche RAG: {e}")
        return results

    def _search_knowledge_base_optimized(self, user_message, results):
        """Recherche optimisée dans la base de connaissances avec cache"""
        try:
            cache_key = f"kb_{user_message.lower().strip()}"
            if cache_key in self.kb_cache:
                cached_data = self.kb_cache[cache_key]
                if time.time() - cached_data['timestamp'] < self.cache_timeout:
                    results["knowledge_base"] = cached_data['results']
                    if results["knowledge_base"]:
                        results["confidence"] = max(results["confidence"], results["knowledge_base"][0]['score'])
                    return
            kb_results = self.retrieval_system.search(user_message)
            if kb_results and isinstance(kb_results, list) and len(kb_results) > 0:
                relevant_results = []
                for result in kb_results:
                    if isinstance(result, dict) and 'score' in result and 'qa_data' in result:
                        if result['score'] > 0.3:
                            relevant_results.append(result)
                if relevant_results:
                    relevant_results.sort(key=lambda x: x['score'], reverse=True)
                    results["knowledge_base"] = relevant_results[:3]
                    results["confidence"] = max(results["confidence"], relevant_results[0]['score'])
                    self.kb_cache[cache_key] = {
                        'results': results["knowledge_base"],
                        'timestamp': time.time()
                    }
        except Exception as e:
            print(f"⚠️ Erreur recherche base connaissances: {e}")

    def _search_web_with_timeout(self, user_message, intent, results):
        """Recherche web avec timeout et gestion d'erreurs - VERSION CORRIGÉE"""
        cache_key = user_message.lower().strip()
        current_time = time.time()
        if (cache_key in self.web_cache and 
            current_time - self.web_cache[cache_key]['timestamp'] < self.cache_timeout):
            print("💾 Utilisation du cache web")
            results["web_search"] = self.web_cache[cache_key]['results']
            if results["web_search"]:
                results["confidence"] = max(results["confidence"], 0.6)
            return
        should_search_web = (
            intent in ["complex_analysis", "comparison"] or 
            results["confidence"] < 0.4
        )
        if should_search_web:
            print("🌐 Lancement recherche web optimisée...")
            web_results = []
            search_completed = threading.Event()
            search_error = None
            def search_thread():
                nonlocal web_results, search_error
                try:
                    web_results = self.web_searcher.search_web(user_message, num_results=1)
                except Exception as e:
                    search_error = e
                finally:
                    search_completed.set()
            thread = threading.Thread(target=search_thread)
            thread.start()
            search_completed.wait(timeout=3)
            if search_error:
                print(f"⚠️ Erreur recherche web: {search_error}")
            elif not search_completed.is_set():
                print("⏱️  Timeout recherche web - annulation")
                thread.join(timeout=1)
            else:
                results["web_search"] = web_results
                if web_results:
                    self.web_cache[cache_key] = {
                        'results': web_results,
                        'timestamp': current_time
                    }
                    results["confidence"] = max(results["confidence"], 0.6)

    def _search_gemini_analysis(self, user_message, results):
        """Analyse Gemini pour questions complexes avec gestion d'erreurs"""
        try:
            context = self._build_rag_context(results)
            gemini_response = self._generate_with_gemini(user_message, context)
            if gemini_response:
                results["gemini_analysis"] = gemini_response
                results["confidence"] = max(results["confidence"], 0.8)
        except Exception as e:
            print(f"⚠️ Analyse Gemini échouée: {e}")

    def _generate_intent_based_response(self, user_message, rag_results, intent, context):
        """
        Génère une réponse basée sur l'intention détectée - VERSION CORRIGÉE
        """
        try:
            response_strategies = {
                "simple_fact": lambda: self._generate_simple_response(user_message, rag_results),
                "complex_analysis": lambda: self._generate_analytical_response(user_message, rag_results, context),
                "comparison": lambda: self._generate_comparison_response(user_message, rag_results),
                "problem_solving": lambda: self._generate_solution_response(user_message, rag_results),
                "general": lambda: self._generate_natural_response(user_message, rag_results)
            }
            strategy = response_strategies.get(intent, response_strategies["general"])
            return strategy()
        except Exception as e:
            print(f"❌ Erreur dans la génération de réponse: {e}")
            return self._generate_fallback_response(user_message)

    # === MÉTHODES DE GÉNÉRATION DE RÉPONSES CORRIGÉES ===

    def _generate_natural_response(self, user_message, rag_results):
        """Génère une réponse conversationnelle naturelle - VERSION CORRIGÉE"""
        try:
            if rag_results["gemini_analysis"]:
                return self._create_response(rag_results["gemini_analysis"], 0.9, 'gemini')
            elif (rag_results["knowledge_base"] and 
                len(rag_results["knowledge_base"]) > 0 and 
                rag_results["knowledge_base"][0]['score'] > 0.5):
                best_match = rag_results["knowledge_base"][0]
                if 'qa_data' in best_match and isinstance(best_match['qa_data'], dict):
                    response_text = self._format_conversational_kb_response(best_match['qa_data'])
                    return self._create_response(response_text, best_match['score'], 'knowledge_base')
                else:
                    response_text = self._generate_improved_template_response(user_message)
                    return self._create_response(response_text, 0.6, 'template_fallback')
            else:
                response_text = self._generate_improved_template_response(user_message)
                return self._create_response(response_text, 0.7, 'template_improved')
        except Exception as e:
            print(f"❌ Erreur dans _generate_natural_response: {e}")
            return self._generate_fallback_response(user_message)

    def _generate_simple_response(self, user_message, rag_results):
        """Génère une réponse simple et factuelle - VERSION CORRIGÉE"""
        try:
            if rag_results["gemini_analysis"]:
                return self._create_response(rag_results["gemini_analysis"], 0.9, 'gemini')
            elif (rag_results["knowledge_base"] and 
                len(rag_results["knowledge_base"]) > 0 and 
                rag_results["knowledge_base"][0]['score'] > 0.6):
                best_match = rag_results["knowledge_base"][0]
                if 'qa_data' in best_match and isinstance(best_match['qa_data'], dict):
                    response_text = self._format_knowledge_response(best_match['qa_data'])
                    return self._create_response(response_text, best_match['score'], 'knowledge_base')
                else:
                    response_text = self._generate_factual_template(user_message, rag_results)
                    return self._create_response(response_text, 0.6, 'template')
            else:
                response_text = self._generate_factual_template(user_message, rag_results)
                return self._create_response(response_text, 0.7, 'template')
        except Exception as e:
            print(f"❌ Erreur dans _generate_simple_response: {e}")
            return self._generate_fallback_response(user_message)

    def _generate_analytical_response(self, user_message, rag_results, context):
        """Génère une réponse analytique approfondie"""
        if rag_results["gemini_analysis"]:
            return self._create_response(rag_results["gemini_analysis"], 0.9, 'gemini')
        else:
            response_text = self._generate_analytical_template(user_message, rag_results, context)
            return self._create_response(response_text, 0.75, 'template')

    def _generate_comparison_response(self, user_message, rag_results):
        """Génère une réponse comparative"""
        if rag_results["gemini_analysis"]:
            return self._create_response(rag_results["gemini_analysis"], 0.9, 'gemini')
        else:
            response_text = self._generate_comparison_template(user_message, rag_results)
            return self._create_response(response_text, 0.7, 'template')

    def _generate_solution_response(self, user_message, rag_results):
        """Génère une réponse de résolution de problème"""
        response_text = self._generate_solution_template(user_message, rag_results)
        return self._create_response(response_text, 0.8, 'template')

    def _generate_fallback_response(self, user_message):
        """Génère une réponse de fallback en cas d'erreur"""
        fallback_text = self._generate_improved_template_response(user_message)
        return self._create_response(fallback_text, 0.5, 'fallback')

    def _create_response(self, response_text, confidence, source):
        """Crée une réponse standardisée"""
        return {
            'type': 'success',
            'response': response_text,
            'confidence': confidence,
            'source': source
        }

    # === MÉTHODES GEMINI CORRIGÉES ===

    def _generate_with_gemini_fallback(self, user_message):
        """Utilise Gemini comme fallback avec gestion d'erreurs améliorée"""
        try:
            prompt = self._build_gemini_fallback_prompt(user_message)
            response = self.gemini_model.generate_content(prompt)
            if response and hasattr(response, 'text') and response.text:
                return response.text.strip()
            else:
                raise ValueError("Réponse Gemini vide")
        except Exception as e:
            print(f"❌ Erreur Gemini fallback: {e}")
            return self._generate_improved_template_response(user_message)

    def _build_gemini_fallback_prompt(self, user_message):
        """Construit le prompt pour le fallback Gemini"""
        return f"""
        Tu es un assistant expert pour ZamaPay, une plateforme de transfert d'argent 
        spécialisée pour le Burkina Faso et l'Afrique de l'Ouest.
        
        Contexte Burkina Faso:
        - Devise: Franc CFA (XOF)
        - Opérateurs mobile money: Orange Money, Moov Money
        - Pays UEMOA: BF, CI, ML, SN, NE, TG, BJ, GW
        - Réglementation: BCEAO
        - Support: 70 123 456
        - Langues: Français, Mooré, Dioula

        L'utilisateur pose la question suivante, mais elle n'est pas dans notre base de connaissances.
        Réponds de manière utile et professionnelle en français, adaptée au contexte burkinabé.

        QUESTION: {user_message}

        Si la question concerne les transferts d'argent, les frais, les délais, la sécurité,
        donne une réponse générale mais précise en F CFA. Si c'est hors sujet, redirige gentiment vers le support.

        IMPORTANT: Sois concis, utile et professionnel. Utilise un ton chaleureux mais expert.
        Réponds en français uniquement.

        Réponse:
        """

    def _generate_with_gemini(self, user_message, context):
        """Génère une réponse avec Gemini pour les questions complexes"""
        try:
            prompt = self._build_gemini_context_prompt(user_message, context)
            response = self.gemini_model.generate_content(prompt)
            if response and hasattr(response, 'text') and response.text:
                return response.text.strip()
            return None
        except Exception as e:
            print(f"❌ Erreur Gemini: {e}")
            return None

    def _build_gemini_context_prompt(self, user_message, context):
        """Construit le prompt contextuel pour Gemini"""
        context_part = f"CONTEXTE SUPPLÉMENTAIRE:\n{context}\n\n" if context else ""
        return f"""
        Tu es un assistant expert pour ZamaPay, une plateforme de transfert d'argent 
        spécialisée pour le Burkina Faso et l'Afrique de l'Ouest.
        
        Contexte Burkina Faso:
        - Devise: Franc CFA (XOF)
        - Opérateurs mobile money: Orange Money, Moov Money
        - Pays UEMOA: BF, CI, ML, SN, NE, TG, BJ, GW
        - Réglementation: BCEAO
        - Support: 70 123 456

        {context_part}
        QUESTION UTILISATEUR:
        {user_message}

        Réponds en français, sois précis sur les montants en F CFA, 
        mentionne les délais réels et les procédures spécifiques au Burkina.
        Si tu ne sais pas, oriente vers le support au 70 123 456.

        Ton style: Professionnel mais accessible, structuré avec des sections claires.
        Réponds en français uniquement.
        """

    def _build_rag_context(self, rag_results):
        """Construit un contexte RAG pour Gemini - VERSION CORRIGÉE"""
        context_parts = []
        if rag_results["knowledge_base"]:
            kb_context = "**Informations de la base ZamaPay :**\n"
            for i, result in enumerate(rag_results["knowledge_base"][:2], 1):
                if 'qa_data' in result and isinstance(result['qa_data'], dict):
                    kb_context += f"{i}. {result['qa_data'].get('reponse', 'Information non disponible')}\n"
            context_parts.append(kb_context)
        if rag_results["web_search"]:
            web_context = "**Informations web récentes :**\n"
            for i, result in enumerate(rag_results["web_search"][:2], 1):
                if isinstance(result, dict) and 'content' in result:
                    web_context += f"{i}. {result['content'][:300]}...\n"
            context_parts.append(web_context)
        return "\n\n".join(context_parts) if context_parts else "Aucun contexte supplémentaire disponible."

    # === TEMPLATES ET FORMATTAGE CORRIGÉS ===

    def _init_quality_templates(self):
        """Initialise des templates de haute qualité"""
        return {
            "frais": [
                """**💰 Frais ZamaPay - Transparence Totale**

## Transferts Nationaux (Burkina Faso)
- **1%** du montant (minimum 500 F CFA)
- Exemple : 50,000 F CFA → 500 F CFA de frais

## Transferts UEMOA (Côte d'Ivoire, Mali, Sénégal...)
- **1.5%** du montant (minimum 750 F CFA) 
- Exemple : 100,000 F CFA → 1,500 F CFA de frais

## Mobile Money (Orange Money, Moov Money)
- **1%** du montant (minimum 250 F CFA)
- Transfert instantané

💡 **Aucun frais caché** - Tout est visible avant validation !""",
            ],
            "delais": [
                """**⏱️ Délais de Traitement**

## Transferts Standards
- **Burkina Faso** : 2 heures maximum
- **UEMOA** : 2-4 heures
- **Mobile Money** : Instantané

## Transferts Express (+500 F CFA)
- **15 minutes** pour toutes destinations UEMOA

🔄 **Suivi en temps réel** dans l'application !""",
            ]
        }

    def _generate_improved_template_response(self, user_message):
        """Génère une réponse template améliorée - VERSION CORRIGÉE"""
        message_lower = user_message.lower()
        if any(word in message_lower for word in ["bonjour", "salut", "slt", "hello", "coucou"]):
            return random.choice([
                "👋 Bonjour ! Je suis l'assistant ZamaPay. Je peux vous aider avec :\n• Transferts d'argent\n• Frais et tarifs\n• Délais de traitement\n• Sécurité des transactions\n\nComment puis-je vous aider aujourd'hui ?",
                "👋 Salut ! Ravie de vous aider. Je suis spécialisé dans les services ZamaPay : transferts, frais, délais, sécurité. Quelle est votre question ?",
                "👋 Hello ! Assistant ZamaPay à votre service. Je peux vous renseigner sur nos transferts, tarifs, délais. Que souhaitez-vous savoir ?"
            ])
        elif any(word in message_lower for word in ["zamapay", "c'est quoi", "qu'est ce", "présentation"]):
            return self._get_zamapay_presentation()
        elif any(word in message_lower for word in ["humain", "agent", "parler à", "support", "réel", "vrai personne"]):
            return self._get_human_support_response()
        else:
            return self._get_default_response(user_message)

    def _get_zamapay_presentation(self):
        """Retourne la présentation de ZamaPay"""
        return """**💳 ZamaPay - Votre partenaire de transfert d'argent en Afrique de l'Ouest**

🌟 **Qui sommes-nous ?**
ZamaPay est une plateforme de transfert d'argent innovante, spécialisée pour le Burkina Faso et toute l'Afrique de l'Ouest.

🎯 **Nos services principaux :**
- Transferts nationaux et internationaux
- Support multi-devises (F CFA, Euro, Dollar)
- Intégration Mobile Money (Orange Money, Moov Money)
- Transactions 100% sécurisées

💸 **Nos tarifs transparents :**
- Transferts nationaux : 1% (min. 500 F CFA)
- Transferts UEMOA : 1.5% (min. 750 F CFA)
- Mobile Money : 1% (min. 250 F CFA)

📞 **Support client :** 70 123 456
🌍 **Site web :** www.zamapay.com"""

    def _get_human_support_response(self):
        """Retourne une réponse pour parler à un humain"""
        return """**👨‍💻 Support Humain - ZamaPay**

Je comprends que vous souhaitez parler à un conseiller. Voici comment nous contacter :

**📞 Contact Immédiat :**
• Téléphone : 70 123 456 (24h/24)
• Email : support@zamapay.com
• Chat en direct : Application ZamaPay

**🕒 Horaires Support :**
• Lundi-Vendredi : 7h-22h
• Samedi-Dimanche : 8h-20h

Notre équipe est là pour vous aider personnellement !"""

    def _get_default_response(self, user_message):
        """Retourne une réponse par défaut améliorée"""
        return f"""🤖 **Assistant ZamaPay**

Je vois que vous demandez : "{user_message}"

Je suis spécialisé dans l'assistance ZamaPay. Pour une réponse précise et personnalisée :

**📞 Contactez notre support :**
• Téléphone : 70 123 456
• Email : support@zamapay.com
• Application : Chat en direct

**🔍 Domaines où je peux vous aider :**
✓ Transferts d'argent et frais
✓ Délais de traitement  
✓ Sécurité des transactions
✓ Support compte et application

N'hésitez pas à poser une question spécifique sur nos services !"""

    def _format_conversational_kb_response(self, qa_data):
        """Formate une réponse KB de façon conversationnelle - VERSION CORRIGÉE"""
        try:
            question = qa_data.get('question_principale', 'Question')
            reponse = qa_data.get('reponse', 'Réponse non disponible')
            suggestions = self._get_conversational_suggestions(qa_data)
            return f"""**{question}**

{reponse}

{suggestions}"""
        except Exception as e:
            print(f"❌ Erreur formatage conversationnel: {e}")
            return "Désolé, je rencontre un problème pour afficher cette information."

    def _format_knowledge_response(self, qa_data):
        """Formate une réponse de base de connaissances - VERSION CORRIGÉE"""
        try:
            question = qa_data.get('question_principale', 'Question')
            reponse = qa_data.get('reponse', 'Réponse non disponible')
            suggestions = self._get_related_suggestions(qa_data)
            return f"""**{question}**

{reponse}

{suggestions}"""
        except Exception as e:
            print(f"❌ Erreur formatage connaissance: {e}")
            return "Information temporairement indisponible."

    def _get_conversational_suggestions(self, qa_data):
        """Suggère des questions de façon conversationnelle - VERSION CORRIGÉE"""
        try:
            related = []
            questions_connexes = qa_data.get('questions_connexes', [])
            if questions_connexes and hasattr(self.retrieval_system, 'get_qa_by_id'):
                for related_id in questions_connexes[:2]:
                    try:
                        related_qa = self.retrieval_system.get_qa_by_id(related_id)
                        if related_qa and isinstance(related_qa, dict):
                            related.append(f"\"{related_qa.get('question_principale', 'Question connexe')}\"")
                    except:
                        continue
            if related:
                return f"\n**🤔 Questions connexes :** {', '.join(related)}"
            return "\n**💬 Besoin de plus de détails ?** Je suis là pour vous aider !"
        except Exception as e:
            print(f"❌ Erreur suggestions conversationnelles: {e}")
            return ""

    def _get_related_suggestions(self, qa_data):
        """Suggère des questions connexes - VERSION CORRIGÉE"""
        try:
            related = []
            questions_connexes = qa_data.get('questions_connexes', [])
            if questions_connexes and hasattr(self.retrieval_system, 'get_qa_by_id'):
                for related_id in questions_connexes[:2]:
                    try:
                        related_qa = self.retrieval_system.get_qa_by_id(related_id)
                        if related_qa and isinstance(related_qa, dict):
                            related.append(f"• {related_qa.get('question_principale', 'Question connexe')}")
                    except:
                        continue
            if related:
                return "\n**💡 Vous pourriez aussi aimer :**\n" + "\n".join(related)
            return ""
        except Exception as e:
            print(f"❌ Erreur suggestions connexes: {e}")
            return ""

    # === TEMPLATES SPÉCIALISÉS ===
    def _generate_factual_template(self, user_message, rag_results):
        return self._generate_improved_template_response(user_message)

    def _generate_analytical_template(self, user_message, rag_results, context):
        return """**🔍 Analyse ZamaPay**

Votre question nécessite une analyse approfondie. Pour une réponse complète et personnalisée, je vous recommande de contacter notre équipe d'experts.

**📞 Support spécialisé :** 70 123 456
**📧 Email technique :** experts@zamapay.com

Notre équipe pourra vous fournir une analyse détaillée adaptée à votre situation spécifique."""

    def _generate_comparison_template(self, user_message, rag_results):
        return """**🔄 Comparaison ZamaPay**

Pour une comparaison détaillée avec d'autres solutions, notre équipe commerciale peut vous préparer une étude personnalisée.

**🎯 Contact comparaison :** 70 123 456
**💼 Rendez-vous expert :** www.zamapay.com/rdv

Nous pouvons comparer : frais, délais, sécurité, fonctionnalités selon vos besoins."""

    def _generate_solution_template(self, user_message, rag_results):
        return """**🛠️ Support Technique ZamaPay**

Notre équipe technique est disponible pour résoudre votre problème rapidement.

**🚨 Support immédiat :**
• Téléphone : 70 123 456
• Email : support@zamapay.com  
• Chat : Application ZamaPay

**⏱️ Délai d'intervention :** Moins de 30 minutes

*Merci de décrire précisément le problème pour une résolution plus rapide.*"""

    # === ANALYSE ET CONTEXTE ===
    def _analyze_intent(self, user_message):
        message_lower = user_message.lower()
        intent_patterns = {
            "simple_fact": [
                "combien", "quel est", "quels sont", "quelle est", 
                "frais", "tarif", "délai", "temps", "coût", "prix"
            ],
            "complex_analysis": [
                "pourquoi", "comment", "explique", "détaillé",
                "analyse", "comprendre", "fonctionne", "mécanisme"
            ],
            "comparison": [
                "comparer", "différence", "avantage", "inconvénient",
                "mieux", "meilleur", "vs", "contre", "opposé"
            ],
            "problem_solving": [
                "problème", "erreur", "bug", "marche pas", "ne fonctionne pas",
                "aide", "solution", "résoudre", "corriger", "réparer"
            ]
        }
        for intent, patterns in intent_patterns.items():
            if any(pattern in message_lower for pattern in patterns):
                return intent
        return "general"

    def _get_conversation_context(self, user_name):
        if user_name and user_name in self.conversation_memory:
            return self.conversation_memory[user_name].get('last_topics', [])
        return []

    def _update_conversation_memory(self, user_name, user_message, response):
        if user_name:
            if user_name not in self.conversation_memory:
                self.conversation_memory[user_name] = {'last_topics': [], 'message_count': 0}
            topic = self._extract_topic(user_message)
            if topic and topic not in self.conversation_memory[user_name]['last_topics']:
                self.conversation_memory[user_name]['last_topics'].insert(0, topic)
                self.conversation_memory[user_name]['last_topics'] = self.conversation_memory[user_name]['last_topics'][:3]
            self.conversation_memory[user_name]['message_count'] += 1

    def _extract_topic(self, message):
        topics = {
            "frais": ["frais", "tarif", "coût", "prix", "combien"],
            "delais": ["délai", "temps", "quand", "durée", "rapide"],
            "securite": ["sécurité", "protéger", "fraude", "crypté", "données"],
            "compte": ["compte", "profil", "connexion", "mot de passe", "inscription"],
            "transfert": ["transfert", "envoyer", "recevoir", "argent", "paiement"]
        }
        message_lower = message.lower()
        for topic, keywords in topics.items():
            if any(keyword in message_lower for keyword in keywords):
                return topic
        return "general"


if __name__ == "__main__":
    print("🧪 Test ResponseGenerator corrigé...")
    class MockRetrievalSystem:
        def search(self, query):
            return [{
                'score': 0.9,
                'qa_data': {
                    'question_principale': 'Question test',
                    'reponse': 'Réponse test',
                    'questions_connexes': []
                }
            }]
    retrieval = MockRetrievalSystem()
    generator = ResponseGenerator(retrieval)
    test_questions = ["Bonjour", "Quels sont vos frais ?", "Comment ça marche ?"]
    for question in test_questions:
        print(f"\nQ: {question}")
        response = generator.generate_response(question)
        print(f"A: {response['response'][:100]}...")
        print(f"Confiance: {response['confidence']} | Source: {response['source']}")
        

