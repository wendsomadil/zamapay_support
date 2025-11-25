#!/usr/bin/env python3
"""
RESPONSE_GENERATOR - ZAMAPAY
Générateur de réponses intelligentes avec RAG et Gemini
"""

import random
import json
import time
import google.generativeai as genai
from web_searcher import WebSearcher

class ResponseGenerator:
    def __init__(self, retrieval_system):
        """
        Initialise le générateur de réponses
        
        Args:
            retrieval_system: Système RAG pour la recherche de connaissances
        """
        self.retrieval_system = retrieval_system
        self.web_searcher = WebSearcher()
        self.conversation_memory = {}
        self.escalation_threshold = 0.4
        
        # Cache pour optimiser les performances
        self.web_cache = {}
        self.cache_timeout = 3600  # 1 heure
        
        # Configuration Gemini
        self.gemini_api_key = "AIzaSyBge8Q1B4g-rT5nIuhIb4Dc99BuIZXy7Ak"
        self._setup_gemini()
        
        # Templates conversationnels
        self.conversation_templates = self._init_quality_templates()

    def _setup_gemini(self):
        """Configure l'API Gemini avec gestion d'erreurs"""
        try:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
            print("✅ Gemini configuré avec succès")
        except Exception as e:
            print(f"❌ Erreur configuration Gemini: {e}")
            self.gemini_model = None

    def generate_response(self, user_message, user_name=None):
        """
        Génère une réponse conversationnelle naturelle avec RAG
        
        Args:
            user_message (str): Message de l'utilisateur
            user_name (str, optional): Nom de l'utilisateur pour le contexte
            
        Returns:
            dict: Réponse structurée avec métadonnées
        """
        print(f"💬 Conversation: '{user_message}'")
        
        # 1. Analyse du contexte et de l'intention
        conversation_context = self._get_conversation_context(user_name)
        intent = self._analyze_intent(user_message)
        
        # 2. Recherche RAG optimisée
        rag_results = self._enhanced_rag_search(user_message, intent)
        
        # 3. Fallback Gemini si nécessaire
        if self._should_use_gemini_fallback(rag_results):
            print("🔍 Aucune réponse trouvée, utilisation de Gemini...")
            gemini_response = self._generate_with_gemini_fallback(user_message)
            if gemini_response:
                return self._format_gemini_response(gemini_response)
        
        # 4. Génération de réponse adaptée à l'intention
        response = self._generate_intent_based_response(user_message, rag_results, intent, conversation_context)
        
        # 5. Mise à jour du contexte conversationnel
        self._update_conversation_memory(user_name, user_message, response)
        
        return response

    def _should_use_gemini_fallback(self, rag_results):
        """Détermine si on doit utiliser Gemini comme fallback"""
        return (not rag_results["knowledge_base"] and 
                not rag_results["web_search"] and 
                self.gemini_model)

    def _format_gemini_response(self, response_text):
        """Formate une réponse Gemini"""
        return {
            'type': 'success',
            'response': response_text,
            'confidence': 0.8,
            'source': 'gemini_fallback'
        }

    def _enhanced_rag_search(self, user_message, intent):
        """
        Recherche RAG améliorée avec cache et multiples sources
        
        Args:
            user_message (str): Question de l'utilisateur
            intent (str): Intention détectée
            
        Returns:
            dict: Résultats de recherche avec scores de confiance
        """
        results = {
            "knowledge_base": [],
            "web_search": [],
            "gemini_analysis": None,
            "confidence": 0.0
        }
        
        # Recherche dans la base de connaissances
        self._search_knowledge_base(user_message, results)
        
        # Recherche web avec cache
        self._search_web_with_cache(user_message, intent, results)
        
        # Analyse Gemini pour questions complexes
        self._search_gemini_analysis(user_message, intent, results)
        
        return results

    def _search_knowledge_base(self, user_message, results):
        """Recherche dans la base de connaissances"""
        kb_results = self.retrieval_system.search(user_message)
        if kb_results:
            results["knowledge_base"] = kb_results
            results["confidence"] = max(results["confidence"], kb_results[0]['score'])

    def _search_web_with_cache(self, user_message, intent, results):
        """Recherche web avec système de cache"""
        cache_key = user_message.lower().strip()
        current_time = time.time()
        
        # Vérifier le cache
        if (cache_key in self.web_cache and 
            current_time - self.web_cache[cache_key]['timestamp'] < self.cache_timeout):
            print("💾 Utilisation du cache web")
            results["web_search"] = self.web_cache[cache_key]['results']
            if results["web_search"]:
                results["confidence"] = max(results["confidence"], 0.6)
        else:
            # Recherche web si nécessaire
            if intent in ["complex_analysis", "comparison"] or results["confidence"] < 0.5:
                try:
                    print("🌐 Recherche web pour:", user_message)
                    web_results = self.web_searcher.search_web(user_message, num_results=2)
                    results["web_search"] = web_results
                    
                    # Mettre en cache
                    self.web_cache[cache_key] = {
                        'results': web_results,
                        'timestamp': current_time
                    }
                    
                    if web_results:
                        results["confidence"] = max(results["confidence"], 0.6)
                except Exception as e:
                    print(f"⚠️ Recherche web échouée: {e}")

    def _search_gemini_analysis(self, user_message, intent, results):
        """Analyse Gemini pour questions complexes"""
        if intent in ["complex_analysis", "problem_solving"] and self.gemini_model:
            try:
                context = self._build_rag_context(results)
                gemini_response = self._generate_with_gemini(user_message, context)
                if gemini_response:
                    results["gemini_analysis"] = gemini_response
                    results["confidence"] = max(results["confidence"], 0.9)
            except Exception as e:
                print(f"⚠️ Analyse Gemini échouée: {e}")

    def _generate_intent_based_response(self, user_message, rag_results, intent, context):
        """
        Génère une réponse basée sur l'intention détectée
        """
        response_strategies = {
            "simple_fact": lambda: self._generate_simple_response(user_message, rag_results),
            "complex_analysis": lambda: self._generate_analytical_response(user_message, rag_results, context),
            "comparison": lambda: self._generate_comparison_response(user_message, rag_results),
            "problem_solving": lambda: self._generate_solution_response(user_message, rag_results),
            "general": lambda: self._generate_natural_response(user_message, rag_results)
        }
        
        strategy = response_strategies.get(intent, response_strategies["general"])
        return strategy()

    # === MÉTHODES DE GÉNÉRATION DE RÉPONSES ===

    def _generate_natural_response(self, user_message, rag_results):
        """Génère une réponse conversationnelle naturelle"""
        if rag_results["gemini_analysis"]:
            return self._create_response(rag_results["gemini_analysis"], 0.9, 'gemini')
        elif rag_results["knowledge_base"] and rag_results["knowledge_base"][0]['score'] > 0.5:
            best_match = rag_results["knowledge_base"][0]
            response_text = self._format_conversational_kb_response(best_match['qa_data'])
            return self._create_response(response_text, best_match['score'], 'knowledge_base')
        else:
            response_text = self._generate_improved_template_response(user_message)
            return self._create_response(response_text, 0.7, 'template_improved')

    def _generate_simple_response(self, user_message, rag_results):
        """Génère une réponse simple et factuelle"""
        if rag_results["gemini_analysis"]:
            return self._create_response(rag_results["gemini_analysis"], 0.9, 'gemini')
        elif rag_results["knowledge_base"] and rag_results["knowledge_base"][0]['score'] > 0.6:
            best_match = rag_results["knowledge_base"][0]
            response_text = self._format_knowledge_response(best_match['qa_data'])
            return self._create_response(response_text, best_match['score'], 'knowledge_base')
        else:
            response_text = self._generate_factual_template(user_message, rag_results)
            return self._create_response(response_text, 0.7, 'template')

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

    def _create_response(self, response_text, confidence, source):
        """Crée une réponse standardisée"""
        return {
            'type': 'success',
            'response': response_text,
            'confidence': confidence,
            'source': source
        }

    # === MÉTHODES GEMINI ===

    def _generate_with_gemini_fallback(self, user_message):
        """Utilise Gemini comme fallback quand aucune réponse n'est trouvée"""
        try:
            prompt = self._build_gemini_fallback_prompt(user_message)
            response = self.gemini_model.generate_content(prompt)
            return response.text.strip()
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

        Réponse:
        """

    def _generate_with_gemini(self, user_message, context):
        """Génère une réponse avec Gemini pour les questions complexes"""
        try:
            prompt = self._build_gemini_context_prompt(user_message, context)
            response = self.gemini_model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"❌ Erreur Gemini: {e}")
            return None

    def _build_gemini_context_prompt(self, user_message, context):
        """Construit le prompt contextuel pour Gemini"""
        return f"""
        Tu es un assistant expert pour ZamaPay, une plateforme de transfert d'argent 
        spécialisée pour le Burkina Faso et l'Afrique de l'Ouest.
        
        Contexte Burkina Faso:
        - Devise: Franc CFA (XOF)
        - Opérateurs mobile money: Orange Money, Moov Money
        - Pays UEMOA: BF, CI, ML, SN, NE, TG, BJ, GW
        - Réglementation: BCEAO
        - Support: 70 123 456

        CONTEXTE SUPPLÉMENTAIRE:
        {context}

        QUESTION UTILISATEUR:
        {user_message}

        Réponds en français, sois précis sur les montants en F CFA, 
        mentionne les délais réels et les procédures spécifiques au Burkina.
        Si tu ne sais pas, oriente vers le support au 70 123 456.

        Ton style: Professionnel mais accessible, structuré avec des sections claires.
        """

    def _build_rag_context(self, rag_results):
        """Construit un contexte RAG pour Gemini"""
        context_parts = []
        
        # Contexte de la base de connaissances
        if rag_results["knowledge_base"]:
            kb_context = "**Informations de la base ZamaPay :**\n"
            for i, result in enumerate(rag_results["knowledge_base"][:2], 1):
                kb_context += f"{i}. {result['qa_data']['reponse']}\n"
            context_parts.append(kb_context)
        
        # Contexte de la recherche web
        if rag_results["web_search"]:
            web_context = "**Informations web récentes :**\n"
            for i, result in enumerate(rag_results["web_search"][:2], 1):
                web_context += f"{i}. {result['content'][:300]}...\n"
            context_parts.append(web_context)
        
        return "\n\n".join(context_parts) if context_parts else None

    # === TEMPLATES ET FORMATTAGE ===

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
        """Génère une réponse template améliorée"""
        message_lower = user_message.lower()
        
        # Détection de salutation
        if any(word in message_lower for word in ["bonjour", "salut", "slt", "hello", "coucou"]):
            return random.choice([
                "👋 Bonjour ! Je suis l'assistant ZamaPay. Je peux vous aider avec :\n• Transferts d'argent\n• Frais et tarifs\n• Délais de traitement\n• Sécurité des transactions\n\nComment puis-je vous aider aujourd'hui ?",
                "👋 Salut ! Ravie de vous aider. Je suis spécialisé dans les services ZamaPay : transferts, frais, délais, sécurité. Quelle est votre question ?",
                "👋 Hello ! Assistant ZamaPay à votre service. Je peux vous renseigner sur nos transferts, tarifs, délais. Que souhaitez-vous savoir ?"
            ])
        
        # Détection de question sur ZamaPay
        elif any(word in message_lower for word in ["zamapay", "c'est quoi", "qu'est ce", "présentation"]):
            return self._get_zamapay_presentation()
        
        # Réponse par défaut améliorée
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

    def _get_default_response(self, user_message):
        """Retourne une réponse par défaut"""
        return f"""🤖 **Assistant ZamaPay**

Je vois que vous demandez : "{user_message}"

Je suis spécialisé dans l'assistance ZamaPay. Pour une réponse précise et personnalisée, je vous recommande de :

**📞 Contacter notre support :**
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
        """Formate une réponse KB de façon conversationnelle"""
        return f"""**{qa_data['question_principale']}**

{qa_data['reponse']}

{self._get_conversational_suggestions(qa_data)}"""

    def _format_knowledge_response(self, qa_data):
        """Formate une réponse de base de connaissances"""
        return f"""**{qa_data['question_principale']}**

{qa_data['reponse']}

{self._get_related_suggestions(qa_data)}"""

    def _get_conversational_suggestions(self, qa_data):
        """Suggère des questions de façon conversationnelle"""
        related = []
        for related_id in qa_data.get('questions_connexes', []):
            related_qa = self.retrieval_system.get_qa_by_id(related_id)
            if related_qa:
                related.append(f"\"{related_qa['question_principale']}\"")
        
        if related:
            return f"\n**🤔 Questions connexes :** {', '.join(related[:2])}"
        return "\n**💬 Besoin de plus de détails ?** Je suis là pour vous aider !"

    def _get_related_suggestions(self, qa_data):
        """Suggère des questions connexes"""
        related = []
        for related_id in qa_data.get('questions_connexes', []):
            related_qa = self.retrieval_system.get_qa_by_id(related_id)
            if related_qa:
                related.append(f"• {related_qa['question_principale']}")
        
        if related:
            return "\n**💡 Vous pourriez aussi aimer :**\n" + "\n".join(related[:2])
        return ""

    # === TEMPLATES SPÉCIALISÉS ===

    def _generate_factual_template(self, user_message, rag_results):
        """Génère un template factuel"""
        return self._generate_improved_template_response(user_message)

    def _generate_analytical_template(self, user_message, rag_results, context):
        """Génère un template analytique"""
        return f"""**🔍 Analyse ZamaPay**

Votre question nécessite une analyse approfondie. Pour une réponse complète et personnalisée, je vous recommande de contacter notre équipe d'experts.

**📞 Support spécialisé :** 70 123 456
**📧 Email technique :** experts@zamapay.com

Notre équipe pourra vous fournir une analyse détaillée adaptée à votre situation spécifique."""

    def _generate_comparison_template(self, user_message, rag_results):
        """Génère un template comparatif"""
        return f"""**🔄 Comparaison ZamaPay**

Pour une comparaison détaillée avec d'autres solutions, notre équipe commerciale peut vous préparer une étude personnalisée.

**🎯 Contact comparaison :** 70 123 456
**💼 Rendez-vous expert :** www.zamapay.com/rdv

Nous pouvons comparer : frais, délais, sécurité, fonctionnalités selon vos besoins."""

    def _generate_solution_template(self, user_message, rag_results):
        """Génère un template de résolution de problème"""
        return f"""**🛠️ Support Technique ZamaPay**

Notre équipe technique est disponible pour résoudre votre problème rapidement.

**🚨 Support immédiat :**
• Téléphone : 70 123 456
• Email : support@zamapay.com  
• Chat : Application ZamaPay

**⏱️ Délai d'intervention :** Moins de 30 minutes

*Merci de décrire précisément le problème pour une résolution plus rapide.*"""

    # === ANALYSE ET CONTEXTE ===

    def _analyze_intent(self, user_message):
        """Analyse l'intention de l'utilisateur"""
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
        """Récupère le contexte de conversation"""
        if user_name and user_name in self.conversation_memory:
            return self.conversation_memory[user_name].get('last_topics', [])
        return []

    def _update_conversation_memory(self, user_name, user_message, response):
        """Met à jour la mémoire conversationnelle"""
        if user_name:
            if user_name not in self.conversation_memory:
                self.conversation_memory[user_name] = {'last_topics': [], 'message_count': 0}
            
            # Garder les 3 derniers sujets
            topic = self._extract_topic(user_message)
            if topic and topic not in self.conversation_memory[user_name]['last_topics']:
                self.conversation_memory[user_name]['last_topics'].insert(0, topic)
                self.conversation_memory[user_name]['last_topics'] = self.conversation_memory[user_name]['last_topics'][:3]
            
            self.conversation_memory[user_name]['message_count'] += 1

    def _extract_topic(self, message):
        """Extrait le sujet principal du message"""
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

# Exemple d'utilisation
if __name__ == "__main__":
    # Test rapide de la classe
    from retrieval_system import RetrievalSystem  # À adapter selon votre implémentation
    
    print("🧪 Test ResponseGenerator...")
    retrieval = RetrievalSystem()
    generator = ResponseGenerator(retrieval)
    
    test_questions = [
        "Bonjour",
        "Quels sont vos frais ?",
        "Comment ça marche ?"
    ]
    
    for question in test_questions:
        print(f"\nQ: {question}")
        response = generator.generate_response(question)
        print(f"A: {response['response'][:100]}...")
        print(f"Confiance: {response['confidence']}")
        
    
