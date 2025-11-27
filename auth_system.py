import streamlit as st
import json
import hashlib
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import re

class AuthenticationSystem:
    def __init__(self, users_file="users.json"):
        self.users_file = users_file
        self.users = self.load_users()
        
        # ✅ CONFIGURATION EMAIL ZAMAPAY OFFICIEL
        self.smtp_config = {
            "server": "smtp.gmail.com",
            "port": 587,
            "email": "noreply.zamapay@gmail.com",  # Email officiel ZamaPay
            "password": "xbibigugdjvfkkpr"         # Mot de passe d'application (sans espaces)
        }
    
    def load_users(self):
        """Charge les utilisateurs depuis le fichier JSON"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"users": {}}
    
    def save_users(self):
        """Sauvegarde les utilisateurs dans le fichier JSON"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, indent=2, ensure_ascii=False)
    
    def hash_password(self, password):
        """Hash le mot de passe avec salt"""
        salt = secrets.token_hex(16)
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex() + ':' + salt
    
    def verify_password(self, stored_password, provided_password):
        """Vérifie le mot de passe"""
        stored_hash, salt = stored_password.split(':')
        computed_hash = hashlib.pbkdf2_hmac('sha256', provided_password.encode(), salt.encode(), 100000).hex()
        return computed_hash == stored_hash
    
    def is_valid_email(self, email):
        """Valide le format de l'email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def generate_verification_code(self):
        """Génère un code de vérification à 6 chiffres"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(6)])
    
    def test_smtp_connection(self):
        """Test la connexion SMTP et retourne le statut"""
        try:
            server = smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port'])
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.smtp_config['email'], self.smtp_config['password'])
            server.quit()
            return True, "✅ Connexion SMTP réussie - Emails fonctionnels !"
        except smtplib.SMTPAuthenticationError as e:
            return False, f"❌ Erreur d'authentification: Vérifiez le mot de passe d'application"
        except Exception as e:
            return False, f"❌ Erreur de connexion: {str(e)[:100]}"
    
    def send_verification_email(self, email, code):
        """Envoie un email de vérification via Gmail SMTP"""
        email_sent = False
        smtp_error = ""
        
        try:
            # Configuration du message
            msg = MIMEMultipart()
            msg['From'] = "ZamaPay Support <noreply.zamapay@gmail.com>"  # ✅ Email officiel
            msg['To'] = email
            msg['Subject'] = "🔐 Votre code de vérification ZamaPay"
            
            # Corps du message avec design professionnel
            body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: 'Arial', sans-serif;
                        background-color: #f6f9fc;
                        margin: 0;
                        padding: 0;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background: white;
                        border-radius: 12px;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                        overflow: hidden;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #1E3A8A, #3B82F6);
                        color: white;
                        padding: 2rem;
                        text-align: center;
                    }}
                    .content {{
                        padding: 2rem;
                        color: #333;
                    }}
                    .verification-code {{
                        background: #f8fafc;
                        border: 2px dashed #1E3A8A;
                        border-radius: 8px;
                        padding: 1.5rem;
                        text-align: center;
                        font-size: 2rem;
                        font-weight: bold;
                        color: #1E3A8A;
                        margin: 1.5rem 0;
                    }}
                    .footer {{
                        background: #f8fafc;
                        padding: 1.5rem;
                        text-align: center;
                        color: #6B7280;
                        font-size: 0.9rem;
                    }}
                    .warning {{
                        background: #FEF3C7;
                        border: 1px solid #F59E0B;
                        border-radius: 6px;
                        padding: 1rem;
                        margin: 1rem 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>💳 ZamaPay</h1>
                        <p>Votre assistant financier intelligent</p>
                    </div>
                    <div class="content">
                        <h2>Vérification de votre adresse email</h2>
                        <p>Bonjour,</p>
                        <p>Pour finaliser votre inscription sur ZamaPay, veuillez utiliser le code de vérification suivant :</p>
                        
                        <div class="verification-code">
                            {code}
                        </div>
                        
                        <div class="warning">
                            <strong>⚠️ Important :</strong> Ce code expirera dans <strong>10 minutes</strong>.
                        </div>
                        
                        <p>Si vous n'êtes pas à l'origine de cette demande, veuillez ignorer cet email.</p>
                    </div>
                    <div class="footer">
                        <p><strong>ZamaPay Support</strong><br>
                        📞 +226 25 40 92 76 • 📧 support@zamapay.com</p>
                        <p>© 2025 ZamaPay - Tous droits réservés</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Connexion au serveur SMTP
            print(f"🔄 Tentative d'envoi d'email depuis noreply.zamapay@gmail.com vers {email}")
            server = smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port'])
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.smtp_config['email'], self.smtp_config['password'])
            server.send_message(msg)
            server.quit()
            
            email_sent = True
            print(f"✅ Email envoyé avec succès à {email}")
            
        except smtplib.SMTPAuthenticationError as e:
            smtp_error = f"Erreur d'authentification Gmail: {e}"
            print(f"❌ {smtp_error}")
            print("💡 Vérifie que le mot de passe d'application est correct")
            
        except smtplib.SMTPException as e:
            smtp_error = f"Erreur SMTP: {e}"
            print(f"❌ {smtp_error}")
            
        except Exception as e:
            smtp_error = f"Erreur inattendue: {e}"
            print(f"❌ {smtp_error}")
        
        # Retourner le statut et l'erreur
        return email_sent, smtp_error
    
    def register_user(self, email, password, name):
        """Inscription d'un nouvel utilisateur"""
        # Validation de l'email
        if not self.is_valid_email(email):
            return False, "Format d'email invalide"
        
        # Vérifier si l'email existe déjà
        if email in self.users.get("users", {}):
            return False, "Cet email est déjà utilisé"
        
        # Validation du mot de passe
        if len(password) < 6:
            return False, "Le mot de passe doit contenir au moins 6 caractères"
        
        # Générer le code de vérification
        verification_code = self.generate_verification_code()
        
        # Stocker temporairement l'utilisateur en attente de vérification
        if "pending_verification" not in self.users:
            self.users["pending_verification"] = {}
            
        self.users["pending_verification"][email] = {
            "name": name,
            "password_hash": self.hash_password(password),
            "verification_code": verification_code,
            "created_at": time.time()
        }
        
        self.save_users()
        
        # Envoyer l'email de vérification
        email_sent, smtp_error = self.send_verification_email(email, verification_code)
        
        if email_sent:
            return True, "Code de vérification envoyé par email"
        else:
            # En mode développement, on retourne quand même le code
            return True, f"Code de vérification: {verification_code} (Email échoué: {smtp_error})"
    
    def verify_email(self, email, code):
        """Vérifie le code de vérification"""
        pending = self.users.get("pending_verification", {})
        
        if email not in pending:
            return False, "Aucune inscription en attente pour cet email"
        
        user_data = pending[email]
        
        # Vérifier l'expiration (10 minutes)
        if time.time() - user_data["created_at"] > 600:
            del pending[email]
            self.save_users()
            return False, "Le code a expiré, veuillez recommencer l'inscription"
        
        # Vérifier le code
        if user_data["verification_code"] != code:
            return False, "Code de vérification incorrect"
        
        # S'assurer que la clé "users" existe
        if "users" not in self.users:
            self.users["users"] = {}
        
        # Activer l'utilisateur
        self.users["users"][email] = {
            "name": user_data["name"],
            "password_hash": user_data["password_hash"],
            "created_at": time.time(),
            "last_login": time.time(),
            "plan": "standard",  # Plan par défaut
            "conversation_count": 0  # Compteur de conversations
        }
        
        # Supprimer de l'attente
        del pending[email]
        self.save_users()
        
        return True, "Compte activé avec succès"
    
    def login_user(self, email, password):
        """Connexion d'un utilisateur"""
        if email not in self.users.get("users", {}):
            return False, "Email ou mot de passe incorrect"
        
        user_data = self.users["users"][email]
        
        if not self.verify_password(user_data["password_hash"], password):
            return False, "Email ou mot de passe incorrect"
        
        # Mettre à jour la dernière connexion
        user_data["last_login"] = time.time()
        self.save_users()
        
        return True, "Connexion réussie"
    
    def get_user_profile(self, email):
        """Récupère le profil utilisateur"""
        if email in self.users.get("users", {}):
            user_data = self.users["users"][email].copy()
            user_data["email"] = email
            # Ne pas renvoyer le hash du mot de passe
            user_data.pop("password_hash", None)
            return user_data
        return None
    
    def update_user_conversation_count(self, email):
        """Met à jour le compteur de conversations"""
        if email in self.users.get("users", {}):
            if "conversation_count" not in self.users["users"][email]:
                self.users["users"][email]["conversation_count"] = 0
            self.users["users"][email]["conversation_count"] += 1
            self.save_users()

# Instance globale du système d'authentification
auth_system = AuthenticationSystem()
