import streamlit as st
import json
import time
from retrieval_system import RetrievalSystem
from response_generator import ResponseGenerator
from login import show_login_page, check_authentication, logout
from auth_system import auth_system

# Configuration de la page
st.set_page_config(
    page_title="ZamaPay - Assistant Client",
    page_icon="💳",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS personnalisé pour une apparence professionnelle
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6B7280;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-container {
        background: #F8FAFC;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #E2E8F0;
    }
    .user-message {
        background: #1E3A8A;
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        max-width: 80%;
        margin-left: auto;
    }
    .assistant-message {
        background: white;
        color: #1F2937;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        border: 1px solid #E5E7EB;
        max-width: 80%;
    }
    .confidence-high {
        color: #10B981;
        font-size: 0.8rem;
    }
    .confidence-medium {
        color: #F59E0B;
        font-size: 0.8rem;
    }
    .quick-questions {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 1rem 0;
    }
    .quick-question-btn {
        background: #EDF2FF;
        border: 1px solid #3B82F6;
        color: #1E40AF;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    .quick-question-btn:hover {
        background: #3B82F6;
        color: white;
    }
    .footer {
        text-align: center;
        color: #6B7280;
        font-size: 0.8rem;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #E5E7EB;
    }
    .source-badge {
        font-size: 0.7rem;
        color: #6B7280;
        margin-top: 4px;
    }
    .user-info {
        background: linear-gradient(135deg, #1E3A8A, #3B82F6);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation des systèmes
@st.cache_resource
def initialize_systems():
    try:
        retrieval = RetrievalSystem("knowledge_base.json")
        response_gen = ResponseGenerator(retrieval)
        return retrieval, response_gen
    except Exception as e:
        st.error(f"Erreur d'initialisation: {e}")
        return None, None

def show_main_application():
    """Affiche l'application principale après connexion"""
    
    # Initialisation
    retrieval, response_gen = initialize_systems()
    
    if retrieval is None or response_gen is None:
        st.error("❌ Service temporairement indisponible. Veuillez réessayer.")
        return
    
    # En-tête avec informations utilisateur
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.markdown('<div class="main-header">💳 ZamaPay Support</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sub-header">Bonjour {st.session_state.user_name} ! 👋 • Assistant client intelligent</div>', unsafe_allow_html=True)
    
    with col2:
        # Afficher le compteur de conversations
        user_profile = auth_system.get_user_profile(st.session_state.user_email)
        conversation_count = user_profile.get("conversation_count", 0) if user_profile else 0
        st.metric("💬 Conversations", conversation_count)
    
    with col3:
        if st.button("🚪 Déconnexion", key="logout_btn", use_container_width=True):
            logout()
            return
    
    # Indicateur de statut système MIS À JOUR
    with st.expander("🔧 Statut du Système", expanded=False):
        # Vérifier Gemini
        if hasattr(response_gen, 'gemini_model') and response_gen.gemini_model is not None:
            st.success("✅ Gemini Flash Actif - IA Google")
        else:
            st.warning("⚠️ Gemini Désactivé - Mode Templates")
        
        # Statistiques dynamiques
        kb_count = len(retrieval.knowledge_base['qa_pairs']) if retrieval else 0
        st.metric("Base de Connaissances", f"{kb_count} Q/R")
        
        # Performance système
        if hasattr(response_gen, 'conversation_memory'):
            active_users = len(response_gen.conversation_memory)
            st.metric("Utilisateurs Actifs", active_users)
        
        # Sources de réponses
        sources_used = set()
        if "messages" in st.session_state and st.session_state.messages:
            for msg in st.session_state.messages:
                if "source" in msg:
                    sources_used.add(msg["source"])
        
        if sources_used:
            st.info(f"📊 Sources utilisées: {', '.join(sources_used)}")
    
    # Informations utilisateur
    user_profile = auth_system.get_user_profile(st.session_state.user_email)
    if user_profile:
        with st.container():
            st.markdown(f"""
            <div class="user-info">
                <strong>👤 Compte : {st.session_state.user_name}</strong><br>
                📧 {st.session_state.user_email} | 📅 Inscrit le {time.strftime('%d/%m/%Y', time.localtime(user_profile.get('created_at', time.time())))}
            </div>
            """, unsafe_allow_html=True)
    
    # Questions rapides - CORRECTION : éviter les doublons
    st.markdown("**💡 Questions fréquentes :**")
    
    quick_questions = [
        "Quels sont vos frais ?",
        "Délai d'un transfert ?", 
        "Sécurité des données ?",
        "Vérification compte ?",
        "Problème de connexion ?",
        "Comparaison avec les banques ?"
    ]
    
    cols = st.columns(3)
    for i, question in enumerate(quick_questions):
        with cols[i % 3]:
            if st.button(question, key=f"quick_{i}", use_container_width=True):
                # VÉRIFIER SI LA QUESTION EST DÉJÀ DANS L'HISTORIQUE
                question_already_asked = False
                if "messages" in st.session_state and st.session_state.messages:
                    for msg in st.session_state.messages:
                        if msg.get("role") == "user" and msg.get("content") == question:
                            question_already_asked = True
                            break
                
                if not question_already_asked:
                    process_user_input(question, response_gen)
                else:
                    st.warning("⚠️ Cette question a déjà été posée dans cette conversation")
    
    # Zone de chat
    st.markdown("---")
    st.markdown("**💬 Dialogue en direct :**")
    
    # Initialisation de l'historique
    if "messages" not in st.session_state or st.session_state.messages is None:
        st.session_state.messages = [
            {"role": "assistant", "content": f"Bonjour {st.session_state.user_name} ! Je suis l'assistant ZamaPay. Comment puis-je vous aider aujourd'hui ?"}
        ]
    
    # Affichage des messages
    chat_container = st.container()
    
    with chat_container:
        if st.session_state.messages:
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="assistant-message">{message["content"]}</div>', unsafe_allow_html=True)
                    
                    # Indicateur de confiance et source
                    if "confidence" in message and message["confidence"] > 0:
                        confidence_class = "confidence-high" if message["confidence"] > 0.7 else "confidence-medium"
                        st.markdown(f'<div class="{confidence_class}">✓ Confiance: {message["confidence"]:.0%}</div>', unsafe_allow_html=True)
                    
                    if "source" in message:
                        source_badges = {
                            'knowledge_base': '📚 Base de connaissances',
                            'gemini': '🤖 IA Gemini',
                            'gemini_fallback': '🤖 IA Gemini',
                            'template': '💼 Réponse Expert',
                            'template_improved': '💼 Réponse Expert',
                            'escalation': '👤 Support Humain'
                        }
                        st.markdown(f'<div class="source-badge">Source: {source_badges.get(message["source"], "Système")}</div>', unsafe_allow_html=True)
        else:
            st.info("💬 Commencez une conversation en tapant un message ci-dessous !")
    
    # Input utilisateur
    st.markdown("---")
    user_input = st.text_input(
        "Tapez votre message...",
        placeholder="Exemple : Quels sont les avantages de ZamaPay vs les banques traditionnelles ?",
        key="user_input"
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("🚀 Envoyer", use_container_width=True, type="primary") and user_input:
            # VÉRIFIER SI LA QUESTION EST DÉJÀ POSÉE
            question_already_asked = False
            if "messages" in st.session_state and st.session_state.messages:
                for msg in st.session_state.messages:
                    if msg.get("role") == "user" and msg.get("content") == user_input:
                        question_already_asked = True
                        break
            
            if not question_already_asked:
                process_user_input(user_input, response_gen)
            else:
                st.warning("⚠️ Vous avez déjà posé cette question dans cette conversation")
    
    with col2:
        if st.button("🔄 Nouvelle Discussion", use_container_width=True):
            # Réinitialiser pour une nouvelle conversation
            st.session_state.messages = [
                {"role": "assistant", "content": f"Bonjour {st.session_state.user_name} ! Nouvelle discussion démarrée. Comment puis-je vous aider ?"}
            ]
            st.rerun()
    
    # Pied de page professionnel
    st.markdown("---")
    st.markdown("""
    <div class="footer">
        <strong>ZamaPay Support</strong><br>
        📞 70 123 456 • 📧 support@zamapay.com<br>
        🕒 Lun-Ven 8h-20h | Sam 9h-18h<br>
        © 2025 ZamaPay - Tous droits réservés
    </div>
    """, unsafe_allow_html=True)

def process_user_input(user_input, response_gen):
    """Traite l'entrée utilisateur et génère une réponse"""
    try:
        # Ajout du message utilisateur
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Génération de la réponse avec indicateur de chargement
        with st.spinner("🔍 Analyse en cours..."):
            start_time = time.time()
            response_data = response_gen.generate_response(user_input, st.session_state.user_name)
            response_time = time.time() - start_time
        
        # Mettre à jour le compteur de conversations
        auth_system.update_user_conversation_count(st.session_state.user_email)
        
        # Affichage de la réponse
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response_data['response'],
            "confidence": response_data.get('confidence', 0),
            "source": response_data.get('source', 'system')
        })
        
        # Réafficher le chat
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Erreur lors du traitement: {e}")
        st.session_state.messages.append({
            "role": "assistant", 
            "content": f"Désolé {st.session_state.user_name}, une erreur s'est produite. Veuillez réessayer ou contacter le support au 70 123 456.",
            "confidence": 0.3,
            "source": "error"
        })
        st.rerun()

def main():
    """Fonction principale avec gestion de l'authentification"""
    
    # Vérification de l'authentification
    if not check_authentication():
        # Afficher la page de connexion
        show_login_page()
    else:
        # Afficher l'application principale
        show_main_application()

if __name__ == "__main__":
    main()

    
