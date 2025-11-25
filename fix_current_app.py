import sqlite3
import os

print("🔧 Correction de la base de données...")

# Supprimer l'ancienne base de données problématique
if os.path.exists('zama_pay.db'):
    os.remove('zama_pay.db')
    print("✅ Ancienne base de données supprimée")

# Recréer la base avec la correction
conn = sqlite3.connect('zama_pay.db')
cursor = conn.cursor()

# Table qa_pairs corrigée
cursor.execute('''
    CREATE TABLE IF NOT EXISTS qa_pairs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_principale TEXT NOT NULL,
        variations TEXT,
        reponse TEXT NOT NULL,
        categorie TEXT,
        sous_categorie TEXT,
        mots_cles TEXT,
        niveau_complexite INTEGER DEFAULT 1,
        questions_connexes TEXT,
        likes INTEGER DEFAULT 0,
        dislikes INTEGER DEFAULT 0,
        nombre_vues INTEGER DEFAULT 0,
        note_moyenne REAL DEFAULT 0,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        date_derniere_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        est_faq BOOLEAN DEFAULT FALSE,
        langue TEXT DEFAULT 'fr',
        auteur TEXT DEFAULT 'system',
        produit_concerne TEXT,
        public_cible TEXT,
        pays_cibles TEXT DEFAULT 'BF',
        devise TEXT DEFAULT 'XOF',
        region TEXT DEFAULT 'Afrique de l''Ouest'
    )
''')

print("✅ Table qa_pairs créée avec succès")

# Créer les autres tables
cursor.execute('''
    CREATE TABLE IF NOT EXISTS feedback_utilisateurs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_question INTEGER,
        type_feedback TEXT,
        utilisateur TEXT,
        date_feedback TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        commentaire TEXT,
        note INTEGER,
        FOREIGN KEY (id_question) REFERENCES qa_pairs (id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS suggestions_utilisateurs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_question INTEGER,
        suggestion_texte TEXT NOT NULL,
        date_suggestion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        utilisateur TEXT,
        statut TEXT DEFAULT 'en_attente',
        votes_positifs INTEGER DEFAULT 0,
        votes_negatifs INTEGER DEFAULT 0,
        categorie_suggestion TEXT,
        FOREIGN KEY (id_question) REFERENCES qa_pairs (id)
    )
''')

conn.commit()
conn.close()

print("🎉 Base de données corrigée avec succès!")
print("🔄 Redémarrez maintenant: streamlit run app.py")
