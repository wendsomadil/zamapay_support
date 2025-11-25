#!/usr/bin/env python3
"""
Test SMTP pour ZamaPay
Vérifie la configuration email avec tes identifiants Gmail
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys

def test_smtp_connection():
    """Test complet de la connexion SMTP"""
    
    # Configuration avec TES identifiants
    smtp_config = {
        "server": "smtp.gmail.com",
        "port": 587,
        "email": "wendsomadil@gmail.com",
        "password": "ljpxfjvuneyjpcie"  # Ton mot de passe d'application
    }
    
    print("🧪 TEST SMTP ZAMAPAY")
    print("=" * 50)
    
    try:
        # 1. Test de connexion basique
        print("1. 🔌 Test de connexion au serveur SMTP...")
        server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
        server.ehlo()
        print("   ✅ Connexion établie")
        
        # 2. Test STARTTLS
        print("2. 🔐 Test du chiffrement TLS...")
        server.starttls()
        server.ehlo()
        print("   ✅ Chiffrement TLS activé")
        
        # 3. Test d'authentification
        print("3. 🔑 Test d'authentification...")
        server.login(smtp_config['email'], smtp_config['password'])
        print("   ✅ Authentification réussie")
        
        # 4. Test d'envoi d'email
        print("4. 📧 Test d'envoi d'email...")
        
        # Création du message de test
        msg = MIMEMultipart()
        msg['From'] = smtp_config['email']
        msg['To'] = smtp_config['email']  # Envoi à toi-même pour le test
        msg['Subject'] = "🧪 Test SMTP ZamaPay - SUCCÈS"
        
        body = """
        <html>
        <body>
            <h2 style="color: #1E3A8A;">✅ Test SMTP Réussi !</h2>
            <p>Félicitations ! Votre configuration SMTP fonctionne correctement.</p>
            <div style="background: #f0f9ff; padding: 15px; border-radius: 8px; border-left: 4px solid #3B82F6;">
                <strong>Détails de configuration :</strong><br>
                - Serveur: smtp.gmail.com:587<br>
                - Email: wendsomadil@gmail.com<br>
                - Statut: ✅ Opérationnel
            </div>
            <p>Les emails de vérification ZamaPay seront envoyés avec succès.</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Envoi de l'email
        server.send_message(msg)
        server.quit()
        
        print("   ✅ Email de test envoyé avec succès !")
        print("\n🎉 TOUS LES TESTS SMTP ONT RÉUSSI !")
        print("\n📧 Vérifie ta boîte Gmail, tu devrais avoir reçu un email de test.")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"   ❌ ERREUR D'AUTHENTIFICATION: {e}")
        print("\n🔧 SOLUTIONS POSSIBLES:")
        print("   1. Vérifie que la validation 2 facteurs est activée")
        print("   2. Utilise un mot de passe d'application, pas ton mot de passe principal")
        print("   3. Génère un nouveau mot de passe d'application: https://myaccount.google.com/apppasswords")
        return False
        
    except smtplib.SMTPException as e:
        print(f"   ❌ ERREUR SMTP: {e}")
        return False
        
    except Exception as e:
        print(f"   ❌ ERREUR INATTENDUE: {e}")
        return False

def test_smtp_settings():
    """Test des paramètres SMTP uniquement"""
    print("\n🔍 VÉRIFICATION DES PARAMÈTRES SMTP")
    print("-" * 40)
    
    smtp_config = {
        "server": "smtp.gmail.com",
        "port": 587,
        "email": "wendsomadil@gmail.com",
        "password": "ljpxfjvuneyjpcie"
    }
    
    print(f"📧 Email: {smtp_config['email']}")
    print(f"🌐 Serveur: {smtp_config['server']}:{smtp_config['port']}")
    print(f"🔐 Mot de passe: {'*' * len(smtp_config['password'])}")
    print(f"   (Longueur: {len(smtp_config['password'])} caractères)")
    
    # Vérification basique
    issues = []
    
    if not smtp_config['email'] or '@' not in smtp_config['email']:
        issues.append("❌ Format d'email invalide")
    
    if not smtp_config['password']:
        issues.append("❌ Mot de passe vide")
    elif len(smtp_config['password']) < 8:
        issues.append("❌ Mot de passe trop court")
    
    if issues:
        print("\n⚠️ PROBLEMES DETECTES:")
        for issue in issues:
            print(f"   {issue}")
        return False
    else:
        print("✅ Paramètres SMTP valides")
        return True

if __name__ == "__main__":
    print("🚀 LANCEMENT DU TEST SMTP COMPLET\n")
    
    # Test 1: Vérification des paramètres
    if not test_smtp_settings():
        print("\n❌ Impossible de continuer, paramètres invalides.")
        sys.exit(1)
    
    # Test 2: Test complet SMTP
    print("\n" + "="*50)
    success = test_smtp_connection()
    
    if success:
        print("\n💡 CONSEIL: Les emails de vérification ZamaPay fonctionneront correctement.")
    else:
        print("\n🚨 ACTION REQUISE: Corrige la configuration SMTP avant de continuer.")
        print("   Le système ZamaPay utilisera l'affichage direct des codes en attendant.")
    
    print("\n" + "="*50)
    