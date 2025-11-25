# 🤖 ZamaPay - Assistant Client Intelligent

## 📋 Description du Projet

ZamaPay est un assistant client intelligent spécialisé dans les services de transfert d'argent, conçu spécifiquement pour le marché burkinabé et ouest-africain. L'application combine une base de connaissances locale avec l'IA Gemini de Google pour fournir des réponses précises et contextuelles.

## 🚀 Fonctionnalités Principales

### 🔐 Système d'Authentification
- **Inscription sécurisée** avec vérification par email
- **Connexion utilisateur** avec gestion de sessions
- **Mot de passe hashé** et sécurisé
- **Compteur de conversations** par utilisateur

### 💬 Assistant Intelligent
- **Recherche RAG** (Retrieval-Augmented Generation) dans la base de connaissances
- **Fallback automatique** vers Gemini AI pour les questions hors base
- **Détection d'intention** automatique des questions
- **Mémoire conversationnelle** par utilisateur
- **Indicateurs de confiance** et sources des réponses

### 🎯 Interface Utilisateur
- **Design responsive** et professionnel
- **Questions rapides** pré-définies
- **Historique de conversation** en temps réel
- **Statut système** en direct
- **Support multi-langues** (Français, Mooré, Dioula)

## 🛠️ Architecture Technique

### Structure des Fichiers
zamapay-assistant/
├── app.py # Application principale Streamlit
├── response_generator.py # Générateur de réponses intelligent
├── retrieval_system.py # Système de recherche RAG
├── auth_system.py # Système d'authentification
├── login.py # Interface de connexion
├── knowledge_base.json # Base de connaissances Q/R
├── users.json # Base des utilisateurs
├── zama_pay.db # Base de données SQLite
├── requirements.txt # Dépendances Python
└── README.md # Documentation

### Composants Principaux

#### 1. **Système d'Authentification (`auth_system.py`)**
- Gestion des utilisateurs avec hachage de mots de passe
- Envoi d'emails de vérification via SMTP
- Sessions utilisateur sécurisées

#### 2. **Système de Recherche RAG (`retrieval_system.py`)**
- Recherche sémantique avec TF-IDF et cosine similarity
- Support des variations de questions
- Seuil de confiance configurable

#### 3. **Générateur de Réponses (`response_generator.py`)**
- Intégration Gemini AI avec fallback
- Analyse d'intention automatique
- Templates de réponse contextuels
- Mémoire conversationnelle

## 🔧 Installation et Configuration

### Prérequis
- Python 3.8+
- Compte Google Cloud avec API Gemini activée

### Installation

1. **Cloner le projet**
git clone <repository-url>
cd zamapay-assistant

2. **Créer l'environnement virtuel**
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

3. **Installer les dépendances**
pip install -r requirements.txt

4. **Configurer la clé API Gemini**
Obtenir une clé sur Google AI Studio
Remplacer dans response_generator.py:
  self.gemini_api_key = "VOTRE_CLE_API_ICI"

5. **Configurer l'email SMTP (optionnel)**
Modifier dans auth_system.py:
  self.smtp_config = {
      "email": "votre@email.com",
      "password": "votre_mot_de_passe_app"
  }

6. **Initialiser la base de données**
python fix_database.py

7. **Lancement de l'Application**
streamlit run app.py
