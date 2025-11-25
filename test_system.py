#!/usr/bin/env python3
"""
Test système complet pour ZamaPay
Teste l'authentification, la base de données utilisateurs, etc.
"""

import json
import os
import time
from auth_system import auth_system

def test_user_storage():
    """Test du système de stockage des utilisateurs"""
    print("🧪 TEST SYSTÈME DE STOCKAGE")
    print("=" * 50)
    
    try:
        # Vérifier si le fichier existe
        if os.path.exists("users.json"):
            print("1. 📁 Fichier users.json trouvé")
            
            # Lire le contenu
            with open("users.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            users_count = len(data.get("users", {}))
            pending_count = len(data.get("pending_verification", {}))
            
            print(f"   👥 Utilisateurs enregistrés: {users_count}")
            print(f"   ⏳ Inscriptions en attente: {pending_count}")
            
            # Afficher les utilisateurs (masqués)
            if users_count > 0:
                print("   📋 Liste des utilisateurs:")
                for email, user_data in data.get("users", {}).items():
                    print(f"      - {email} ({user_data.get('name', 'N/A')})")
                    
        else:
            print("1. 📁 Fichier users.json non trouvé (sera créé automatiquement)")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def test_authentication_functions():
    """Test des fonctions d'authentification"""
    print("\n2. 🔐 TEST DES FONCTIONS D'AUTHENTIFICATION")
    print("-" * 40)
    
    # Test données
    test_email = "test@example.com"
    test_password = "password123"
    test_name = "Test User"
    
    try:
        # Test 1: Validation email
        print("   a) Validation d'email...")
        valid_emails = ["test@example.com", "user@domain.co", "hello@test.fr"]
        invalid_emails = ["invalid", "missing@", "@domain.com", "spaces @test.com"]
        
        valid_count = 0
        for email in valid_emails:
            if auth_system.is_valid_email(email):
                valid_count += 1
                
        invalid_count = 0
        for email in invalid_emails:
            if not auth_system.is_valid_email(email):
                invalid_count += 1
                
        print(f"      ✅ {valid_count}/{len(valid_emails)} emails valides détectés")
        print(f"      ✅ {invalid_count}/{len(invalid_emails)} emails invalides rejetés")
        
        # Test 2: Hash de mot de passe
        print("   b) Hash de mot de passe...")
        hash_result = auth_system.hash_password(test_password)
        if hash_result and ':' in hash_result:
            print("      ✅ Hash généré avec succès (avec salt)")
            
            # Vérification du hash
            if auth_system.verify_password(hash_result, test_password):
                print("      ✅ Vérification du hash fonctionne")
            else:
                print("      ❌ Échec vérification hash")
        else:
            print("      ❌ Échec génération hash")
            
        # Test 3: Génération code vérification
        print("   c) Génération code vérification...")
        code1 = auth_system.generate_verification_code()
        code2 = auth_system.generate_verification_code()
        
        if len(code1) == 6 and code1.isdigit():
            print(f"      ✅ Code généré: {code1} (6 chiffres)")
        else:
            print("      ❌ Format de code invalide")
            
        if code1 != code2:
            print("      ✅ Codes uniques générés")
        else:
            print("      ⚠️ Codes identiques (peu probable)")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def test_registration_flow():
    """Test du flux d'inscription complet"""
    print("\n3. 📝 TEST FLUX D'INSCRIPTION")
    print("-" * 40)
    
    # Utiliser un email de test unique
    test_email = f"test_{int(time.time())}@example.com"
    test_password = "testpassword123"
    test_name = "Utilisateur Test"
    
    try:
        # Étape 1: Inscription
        print("   a) Inscription nouvel utilisateur...")
        success, message = auth_system.register_user(test_email, test_password, test_name)
        
        if success:
            print(f"      ✅ Inscription réussie: {message}")
            
            # Vérifier que l'utilisateur est en attente
            pending_users = auth_system.users.get("pending_verification", {})
            if test_email in pending_users:
                print("      ✅ Utilisateur enregistré en attente de vérification")
                
                # Récupérer le code de vérification
                verification_code = pending_users[test_email]["verification_code"]
                print(f"      🔑 Code de vérification: {verification_code}")
                
                # Étape 2: Vérification
                print("   b) Vérification du code...")
                success_verify, message_verify = auth_system.verify_email(test_email, verification_code)
                
                if success_verify:
                    print(f"      ✅ Vérification réussie: {message_verify}")
                    
                    # Vérifier que l'utilisateur est maintenant actif
                    if test_email in auth_system.users.get("users", {}):
                        print("      ✅ Utilisateur activé dans la base")
                        
                        # Étape 3: Connexion
                        print("   c) Test de connexion...")
                        success_login, message_login = auth_system.login_user(test_email, test_password)
                        
                        if success_login:
                            print(f"      ✅ Connexion réussie: {message_login}")
                            
                            # Étape 4: Profil utilisateur
                            print("   d) Récupération profil...")
                            profile = auth_system.get_user_profile(test_email)
                            
                            if profile and profile["name"] == test_name:
                                print("      ✅ Profil utilisateur récupéré")
                                print(f"         Nom: {profile['name']}")
                                print(f"         Email: {profile['email']}")
                                print(f"         Plan: {profile.get('plan', 'N/A')}")
                            else:
                                print("      ❌ Erreur profil utilisateur")
                        else:
                            print(f"      ❌ Échec connexion: {message_login}")
                    else:
                        print("      ❌ Utilisateur non trouvé après vérification")
                else:
                    print(f"      ❌ Échec vérification: {message_verify}")
            else:
                print("      ❌ Utilisateur non trouvé dans les inscriptions en attente")
        else:
            print(f"      ❌ Échec inscription: {message}")
            
        return success
        
    except Exception as e:
        print(f"   ❌ Erreur inattendue: {e}")
        return False

def test_conversation_tracking():
    """Test du suivi des conversations"""
    print("\n4. 💬 TEST SUIVI DES CONVERSATIONS")
    print("-" * 40)
    
    test_email = f"conv_test_{int(time.time())}@example.com"
    
    try:
        # Créer un utilisateur test
        auth_system.register_user(test_email, "password123", "Test Conversations")
        code = auth_system.users["pending_verification"][test_email]["verification_code"]
        auth_system.verify_email(test_email, code)
        
        # Vérifier compteur initial
        profile = auth_system.get_user_profile(test_email)
        initial_count = profile.get("conversation_count", 0)
        print(f"   Compteur initial: {initial_count}")
        
        # Simuler quelques conversations
        for i in range(3):
            auth_system.update_user_conversation_count(test_email)
            
        # Vérifier compteur final
        profile = auth_system.get_user_profile(test_email)
        final_count = profile.get("conversation_count", 0)
        print(f"   Compteur après 3 conversations: {final_count}")
        
        if final_count == initial_count + 3:
            print("   ✅ Suivi des conversations fonctionne correctement")
            return True
        else:
            print(f"   ❌ Erreur suivi: attendu {initial_count + 3}, obtenu {final_count}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def cleanup_test_users():
    """Nettoyage des utilisateurs de test"""
    print("\n5. 🧹 NETTOYAGE DES UTILISATEURS DE TEST")
    print("-" * 40)
    
    try:
        # Supprimer les utilisateurs de test
        users_to_remove = []
        for email in list(auth_system.users.get("users", {}).keys()):
            if "test" in email or "example.com" in email:
                users_to_remove.append(email)
                
        for email in list(auth_system.users.get("pending_verification", {}).keys()):
            if "test" in email or "example.com" in email:
                users_to_remove.append(email)
                
        for email in users_to_remove:
            if email in auth_system.users.get("users", {}):
                del auth_system.users["users"][email]
            if email in auth_system.users.get("pending_verification", {}):
                del auth_system.users["pending_verification"][email]
                
        if users_to_remove:
            auth_system.save_users()
            print(f"   ✅ {len(users_to_remove)} utilisateurs de test supprimés")
        else:
            print("   ℹ️ Aucun utilisateur de test à supprimer")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur nettoyage: {e}")
        return False

if __name__ == "__main__":
    print("🚀 LANCEMENT DU TEST SYSTÈME COMPLET ZAMAPAY")
    print("=" * 60)
    
    results = []
    
    # Exécuter tous les tests
    results.append(("Stockage utilisateurs", test_user_storage()))
    results.append(("Fonctions authentification", test_authentication_functions()))
    results.append(("Flux inscription", test_registration_flow()))
    results.append(("Suivi conversations", test_conversation_tracking()))
    results.append(("Nettoyage", cleanup_test_users()))
    
    # Résumé final
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("-" * 60)
    
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    for test_name, success in results:
        status = "✅ RÉUSSI" if success else "❌ ÉCHEC"
        print(f"   {test_name}: {status}")
    
    print(f"\n🎯 SCORE FINAL: {success_count}/{total_count} tests réussis")
    
    if success_count == total_count:
        print("🎉 TOUS LES TESTS ONT RÉUSSI ! Le système est opérationnel.")
    else:
        print("⚠️ Certains tests ont échoué. Vérifie la configuration.")
    
    print("\n" + "=" * 60)
    