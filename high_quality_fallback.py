from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch
import requests
import random

class HighQualityFallback:
    def __init__(self):
        self.models_priority = [
            {
                "name": "mistralai/Mistral-7B-Instruct-v0.2",
                "type": "instruction",
                "description": "Très bon modèle français/anglais"
            },
            {
                "name": "microsoft/DialoGPT-large", 
                "type": "dialog",
                "description": "Dialogues naturels"
            },
            {
                "name": "google/flan-t5-large",
                "type": "instruction", 
                "description": "Bon suivi d'instructions"
            }
        ]
        
        self.pipe = None
        self.current_model = None
        self.setup_high_quality_model()
        
        # Templates de haute qualité en backup
        self.quality_templates = self._init_quality_templates()
    
    def setup_high_quality_model(self):
        """Tente de charger le meilleur modèle disponible"""
        print("🚀 Recherche du meilleur modèle disponible...")
        
        # Essayer d'abord Mistral 7B (excellent équilibre)
        if self._try_load_model("mistralai/Mistral-7B-Instruct-v0.2"):
            return
            
        # Ensuite DialoGPT large
        if self._try_load_model("microsoft/DialoGPT-large"):
            return
            
        # En dernier Flan-T5
        if self._try_load_model("google/flan-t5-large"):
            return
            
        print("🔧 Utilisation des templates haute qualité")
        self.pipe = None
    
    def _try_load_model(self, model_name):
        """Tente de charger un modèle spécifique"""
        try:
            print(f"🔄 Tentative: {model_name}")
            
            # Chargement optimisé selon le modèle
            if "mistral" in model_name.lower():
                self.pipe = pipeline(
                    "text-generation",
                    model=model_name,
                    torch_dtype=torch.float16,
                    device_map="auto",
                    trust_remote_code=True
                )
            else:
                self.pipe = pipeline(
                    "text-generation", 
                    model=model_name,
                    device_map="auto" if torch.cuda.is_available() else None,
                    torch_dtype=torch.float32
                )
                
            self.current_model = model_name
            print(f"✅ {model_name} chargé avec succès")
            return True
            
        except Exception as e:
            print(f"❌ {model_name}: {e}")
            return False
    
    def generate_response(self, user_message, context=None, reasoning_level="medium"):
        """Génère une réponse de haute qualité"""
        # Essayer d'abord le modèle AI
        if self.pipe is not None:
            ai_response = self._generate_ai_response(user_message, context, reasoning_level)
            if ai_response and len(ai_response) > 20: 
                # Vérifier que la réponse est substantielle
                return ai_response
        
        # Sinon utiliser les templates de haute qualité
        return self._generate_quality_template(user_message, context)
    
    def _generate_ai_response(self, user_message, context, reasoning_level):
        """Génération avec le modèle AI"""
        try:
            prompt = self._build_quality_prompt(user_message, context, reasoning_level)
            
            generation_params = {
                "max_new_tokens": 250,
                "temperature": 0.7,
                "do_sample": True,
                "top_p": 0.9,
                "repetition_penalty": 1.1,
                "num_return_sequences": 1
            }
            
            # Ajustements spécifiques par modèle
            if "mistral" in self.current_model.lower():
                generation_params["max_new_tokens"] = 300
            
            output = self.pipe(prompt, **generation_params)
            response = output[0]["generated_text"]
            
            # Nettoyer la réponse
            return self._clean_response(response, prompt)
            
        except Exception as e:
            print(f"❌ Erreur génération AI: {e}")
            return None
    
    def _build_quality_prompt(self, user_message, context, reasoning_level):
        """Construit un prompt de haute qualité"""
        base_system = """Tu es un assistant client expert pour ZamaPay, une plateforme de transfert d'argent. 
Tu dois fournir des réponses PRÉCISES, UTILES et PROFESSIONNELLES.

CARACTÉRISTIQUES:
- Réponses détaillées mais concises
- Ton professionnel et empathique
- Informations structurées et claires
- Propositions d'actions concrètes
- Reconnaissance des limites et orientation vers le support si nécessaire

EXEMPLES DE BONNES RÉPONSES:
❌ MAUVAIS: "Contactez le support."
✅ BON: "Pour cette situation spécifique, je vous recommande de contacter notre support au 01 23 45 67 89. Ils pourront vérifier votre compte et résoudre ce problème sous 24 heures."

MAINTENANT, RÉPONDS À:"""
        
        if context:
            prompt = f"{base_system}\n\nCONTEXTE: {context}\nQUESTION: {user_message}\nRÉPONSE:"
        else:
            prompt = f"{base_system}\n\nQUESTION: {user_message}\nRÉPONSE:"
        
        return prompt
    
    def _clean_response(self, response, prompt):
        """Nettoie et améliore la réponse générée"""
        # Retirer le prompt de la réponse
        if prompt in response:
            response = response.replace(prompt, "").strip()
        
        # Nettoyer les artefacts de génération
        response = response.split("RÉPONSE:")[-1].strip()
        response = response.split("QUESTION:")[0].strip()
        
        # S'assurer que la réponse se termine proprement
        if response and not response.endswith(('.', '!', '?')):
            response += "."
            
        return response
    
    def _init_quality_templates(self):
        """Initialise des templates de haute qualité"""
        return {
            "password": [
                """Pour réinitialiser votre mot de passe ZamaPay :

1. **Application Mobile** : 
   - Allez dans "Paramètres" → "Sécurité"
   - Cliquez sur "Mot de passe oublié ?"
   - Suivez les instructions de vérification

2. **Site Web** :
   - Page de connexion → "Mot de passe oublié"
   - Entrez votre email associé
   - Cliquez sur le lien dans l'email reçu

⏱️ **Délai** : Réinitialisation instantanée après vérification
🔒 **Sécurité** : Le lien expire après 1 heure pour votre protection

Besoin d'aide supplémentaire ? Contactez notre support sécurité : security@zamapay.com""",
                
                """La réinitialisation de mot de passe est simple et sécurisée :

**Procédure immédiate** :
- Rendez-vous sur la page de connexion ZamaPay
- Cliquez sur "Mot de passe oublié"
- Saisissez votre adresse email professionnelle
- Consultez votre boîte mail pour le lien de réinitialisation
- Créez un nouveau mot de passe fort (8 caractères minimum, avec majuscules/chiffres)

📞 **Support dédié** : Si vous ne recevez pas l'email sous 5 minutes, appelez le 01 23 45 67 89 (service sécurité)"""
            ],
            
            "account_closure": [
                """Pour fermer votre compte ZamaPay :

**Étapes à suivre** :
1. **Vérifiez le solde** : Assurez-vous que votre solde est à 0€
2. **Transferts en cours** : Aucun transfert ne doit être en attente
3. **Contactez le support** : Envoyez un email à fermeture@zamapay.com avec :
   - Votre numéro de compte
   - La raison de la fermeture
   - Une pièce d'identité recto-verso

**Délais** :
- Traitement sous 48 heures ouvrables
- Email de confirmation envoyé
- Données conservées 5 ans (obligation légale)

💡 **Alternative** : Vous pouvez mettre en pause votre compte via Paramètres → "Suspendre temporairement" """,
                
                """Fermeture de compte ZamaPay - Processus détaillé :

**Pré-requis** :
✅ Solde à 0€
✅ Aucune transaction en attente  
✅ Documents d'identité à jour

**Procédure** :
1. Contactez exclusivement fermeture@zamapay.com
2. Objet : "Demande de fermeture de compte - [VotreNom]"
3. Joindre copie CNI/passeport
4. Confirmation sous 48h

**Conséquences** :
- Accès immédiatement désactivé après confirmation
- Historique conservé 5 ans (RGPD)
- Possibilité de réouverture sous 30 jours"""
            ],
            
            "general": [
                """Je comprends parfaitement votre question. En tant qu'assistant spécialisé ZamaPay, je vais vous orienter vers la meilleure solution :

**Pour une réponse immédiate et précise** :
📞 **Support téléphonique** : 01 23 45 67 89 (8h-20h)
📧 **Email prioritaire** : support@zamapay.com (réponse sous 2h)
💬 **Chat en direct** : Disponible sur notre application

**Notre engagement** :
- Réponse sous 2 heures maximum
- Conseillers experts ZamaPay
- Résolution garantie sous 24h

N'hésitez pas à nous contacter pour une assistance personnalisée !""",
                
                """Excellente question ! Notre équipe support dispose des informations les plus récentes et pourra vous accompagner personnellement.

**Canaux de support disponibles** :
🔹 **Téléphone** : 01 23 45 67 89 - Du lundi au vendredi 8h-20h
🔹 **Email** : support@zamapay.com - Réponse sous 2 heures
🔹 **Application** : Chat en direct dans la section "Aide"

**Avantages** :
✓ Conseillers formés spécifiquement
✓ Historique de vos transactions disponible
✓ Solutions personnalisées selon votre profil

Nous sommes là pour vous aider !"""
            ],
            
            "technical": [
                """Problème technique détecté - Voici la procédure optimale :

**Solution immédiate** :
1. **Redémarrez l'application** : Fermez et rouvrez ZamaPay
2. **Vérifiez la connexion** : WiFi/4G stable requis
3. **Mise à jour** : Vérifiez les mises à jour dans App Store/Play Store

**Si le problème persiste** :
📱 **Support technique dédié** : technique@zamapay.com
☎️ **Hotline technique** : 01 23 45 67 89 (poste 2)

**Informations à préparer** :
- Version de l'application
- Modèle de téléphone
- Capture d'écran de l'erreur

Notre équipe technique intervient généralement en moins de 30 minutes !""",
                
                """Assistance technique ZamaPay - Procédure accélérée :

**Diagnostic rapide** :
• Application à jour ? (Paramètres → À propos)
• Connexion internet stable ?
• Espace stockage suffisant ?

**Support spécialisé** :
🛠️ **Email technique** : technique@zamapay.com
🚨 **Urgences** : 01 23 45 67 89 - option 2

**Pour une résolution express** :
- Décrivez précisément l'erreur
- Heure exacte du problème
- Actions effectuées avant l'erreur

Temps de résolution moyen : moins de 1 heure !"""
            ]
        }
    
    def _generate_quality_template(self, user_message, context):
        """Génère une réponse template de haute qualité"""
        category = self._categorize_question(user_message)
        templates = self.quality_templates.get(category, self.quality_templates["general"])
        
        # Sélection aléatoire mais cohérente
        selected_template = random.choice(templates)
        
        # Personnalisation basique
        personalized_response = selected_template
        
        # Ajout d'informations de contact cohérentes
        contact_info = """
        
📞 **Support ZamaPay** : 01 23 45 67 89
📧 **Email** : support@zamapay.com  
🕒 **Horaires** : Lundi-Vendredi 8h-20h | Samedi 9h-18h
🚀 **Engagement** : Réponse sous 2 heures maximum"""

        return personalized_response + contact_info
    
    def _categorize_question(self, message):
        """Catégorise la question pour le template approprié"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["mot de passe", "password", "oublié", "connexion"]):
            return "password"
        elif any(word in message_lower for word in ["fermer", "clôturer", "supprimer", "compte"]):
            return "account_closure"
        elif any(word in message_lower for word in ["technique", "bug", "erreur", "planté", "fonctionne pas"]):
            return "technical"
        else:
            return "general"
    
    def is_available(self):
        return True  # Toujours disponible avec les templates
    