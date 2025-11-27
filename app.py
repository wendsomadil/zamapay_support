import streamlit as st
import json
import time
from datetime import datetime
from unified_retrieval import UnifiedRetrievalSystem
from response_generator import ResponseGenerator
from login import show_login_page, check_authentication, logout
from auth_system import auth_system
from conversation_manager import conversation_manager
from config import APP_NAME, VERSION

# Configuration de la page
st.set_page_config(
    page_title="ZamaPay - Finance Inclusive",
    page_icon="💳",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS Ultra-Professionnel avec POLICE FIXE
st.markdown("""
<style>
    /* FORCE LA POLICE PARTOUT - SOLUTION DÉFINITIVE */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    html, body, div, span, p, a, button, input, textarea, h1, h2, h3, h4, h5, h6,
    .stApp, .stApp *, .user-message, .user-message *, .assistant-message, .assistant-message *,
    [class*="st"], [class*="stMarkdown"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Variables de couleur */
    :root {
        --primary: #2563EB;
        --primary-dark: #1E40AF;
        --secondary: #10B981;
        --text-dark: #0F172A;
        --text-gray: #475569;
        --bg-light: #F8FAFC;
        --border: #E2E8F0;
    }
    
    /* Background général */
    .stApp {
        background: linear-gradient(135deg, #F8FAFC 0%, #EEF2FF 100%);
    }
    
    /* En-tête */
    .main-header {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin: 2rem 0 0.5rem 0;
        font-family: 'Inter', sans-serif !important;
    }
    
    .sub-header {
        font-size: 1rem !important;
        color: var(--text-gray) !important;
        text-align: center;
        margin-bottom: 2rem;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Menu de navigation */
    .nav-menu {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin: 1rem 0 2rem 0;
        flex-wrap: wrap;
    }
    
    .nav-button {
        background: white !important;
        border: 2px solid var(--border) !important;
        color: var(--text-dark) !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .nav-button:hover {
        border-color: var(--primary) !important;
        color: var(--primary) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15) !important;
    }
    
    .nav-button.active {
        background: linear-gradient(135deg, var(--primary), var(--primary-dark)) !important;
        color: white !important;
        border-color: var(--primary) !important;
    }
    
    /* Carte utilisateur */
    .user-card {
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        color: white !important;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 16px rgba(37, 99, 235, 0.3);
    }
    
    .user-card * {
        color: white !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Messages - POLICE FIXE GARANTIE */
    .message-wrapper {
        margin: 1rem 0;
        animation: fadeIn 0.4s ease-out;
    }
    
    .user-message {
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        color: white !important;
        padding: 1rem 1.25rem;
        border-radius: 18px 18px 4px 18px;
        margin-left: 15%;
        box-shadow: 0 2px 12px rgba(37, 99, 235, 0.25);
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
        word-wrap: break-word;
    }
    
    .user-message, .user-message * {
        color: white !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
    }
    
    .assistant-message {
        background: white;
        color: var(--text-dark) !important;
        padding: 1rem 1.25rem;
        border-radius: 18px 18px 18px 4px;
        margin-right: 15%;
        border: 1px solid var(--border);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
        word-wrap: break-word;
    }
    
    .assistant-message, .assistant-message * {
        color: var(--text-dark) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.35rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        margin: 0.5rem 0.5rem 0 0;
        font-family: 'Inter', sans-serif !important;
    }
    
    .badge-high {
        background: linear-gradient(135deg, #10B981, #059669);
        color: white !important;
    }
    
    .badge-medium {
        background: linear-gradient(135deg, #F59E0B, #D97706);
        color: white !important;
    }
    
    .badge-low {
        background: linear-gradient(135deg, #EF4444, #DC2626);
        color: white !important;
    }
    
    .badge-source {
        background: #F1F5F9;
        color: var(--text-gray) !important;
        border: 1px solid var(--border);
    }
    
    /* Questions rapides */
    .quick-section {
        background: linear-gradient(135deg, #EEF2FF, #E0E7FF);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        border: 1px solid #C7D2FE;
    }
    
    .quick-title {
        font-size: 1rem !important;
        font-weight: 700 !important;
        color: var(--primary-dark) !important;
        margin-bottom: 1rem;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Boutons Streamlit */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* Historique */
    .history-item {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border: 1px solid var(--border);
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .history-item:hover {
        border-color: var(--primary);
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.1);
    }
    
    .history-preview {
        color: var(--text-gray) !important;
        font-size: 0.85rem !important;
        margin-top: 0.25rem;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: var(--text-gray) !important;
        font-size: 0.85rem !important;
        margin-top: 3rem;
        padding: 2rem 1rem;
        border-top: 2px solid var(--border);
        font-family: 'Inter', sans-serif !important;
    }
    
    .footer * {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .user-message, .assistant-message {
            margin-left: 0 !important;
            margin-right: 0 !important;
            max-width: 100% !important;
        }
        
        .main-header {
            font-size: 2rem !important;
        }
        
        .nav-menu {
            flex-direction: column;
            align-items: center;
        }
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #F1F5F9;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #CBD5E1;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_systems():
    try:
        # Essayer FAISS d'abord, fallback sur TF-IDF
        retrieval = UnifiedRetrievalSystem("knowledge_base.json", use_faiss=True)
        
        # Vérifier quelle technologie est utilisée
        if retrieval.use_faiss:
            print("🚀 FAISS activé - Recherche sémantique avancée")
        else:
            print("🔍 TF-IDF activé - Recherche standard")
            
        response_gen = ResponseGenerator(retrieval)
        return retrieval, response_gen
        
    except Exception as e:
        st.error(f"❌ Erreur initialisation: {str(e)}")
        return None, None

def show_navigation():
    """Affiche le menu de navigation avec des boutons Streamlit"""
    st.markdown('<div class="nav-menu">', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("💬 Assistant", use_container_width=True, 
                    type="primary" if st.session_state.current_page == "chat" else "secondary"):
            st.session_state.current_page = "chat"
            st.rerun()
    
    with col2:
        if st.button("📊 Historique", use_container_width=True,
                    type="primary" if st.session_state.current_page == "history" else "secondary"):
            st.session_state.current_page = "history"
            st.rerun()
    
    with col3:
        if st.button("👨‍💼 Agent", use_container_width=True,
                    type="primary" if st.session_state.current_page == "agent" else "secondary"):
            st.session_state.current_page = "agent"
            st.rerun()
    
    with col4:
        if st.button("ℹ️ À Propos", use_container_width=True,
                    type="primary" if st.session_state.current_page == "about" else "secondary"):
            st.session_state.current_page = "about"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def load_user_messages():
    """Charge les messages de l'utilisateur depuis la sauvegarde"""
    if "messages_loaded" not in st.session_state:
        try:
            saved_messages = conversation_manager.load_conversation(st.session_state.user_email)
            if saved_messages:
                st.session_state.messages = saved_messages
                print(f"✅ Messages chargés: {len(saved_messages)} messages")
            else:
                st.session_state.messages = [{
                    "role": "assistant",
                    "content": f"Bonjour {st.session_state.user_name} ! 👋 Je suis votre assistant ZamaPay. Comment puis-je vous aider aujourd'hui ?",
                    "timestamp": datetime.now().isoformat()
                }]
                print("✅ Nouvelle conversation créée")
            st.session_state.messages_loaded = True
        except Exception as e:
            print(f"❌ Erreur chargement messages: {e}")
            st.session_state.messages = [{
                "role": "assistant",
                "content": f"Bonjour {st.session_state.user_name} ! 👋 Je suis votre assistant ZamaPay.",
                "timestamp": datetime.now().isoformat()
            }]
            st.session_state.messages_loaded = True

def save_user_messages():
    """Sauvegarde les messages de l'utilisateur"""
    try:
        if st.session_state.get('user_email') and st.session_state.get('messages'):
            success = conversation_manager.save_conversation(
                st.session_state.user_email, 
                st.session_state.messages
            )
            if success:
                print("✅ Messages sauvegardés avec succès")
            else:
                print("❌ Échec sauvegarde messages")
    except Exception as e:
        print(f"❌ Erreur sauvegarde: {e}")

def process_message(text, response_gen):
    """Traite un message utilisateur et sauvegarde"""
    try:
        # Ajouter le message utilisateur
        user_message = {
            "role": "user", 
            "content": text,
            "timestamp": datetime.now().isoformat()
        }
        st.session_state.messages.append(user_message)
        print(f"💬 Message utilisateur ajouté: {text[:50]}...")
        
        with st.spinner("🔍 Analyse..."):
            start = time.time()
            response = response_gen.generate_response(text, st.session_state.user_name)
            duration = time.time() - start
        
        # Mettre à jour le compteur de conversations
        auth_system.update_user_conversation_count(st.session_state.user_email)
        
        # Ajouter la réponse de l'assistant
        assistant_message = {
            "role": "assistant",
            "content": response.get('response', 'Erreur'),
            "confidence": response.get('confidence', 0),
            "source": response.get('source', 'system'),
            "time": duration,
            "timestamp": datetime.now().isoformat()
        }
        st.session_state.messages.append(assistant_message)
        print(f"🤖 Réponse assistant ajoutée: {response.get('source', 'unknown')}")
        
        # SAUVEGARDER LA CONVERSATION
        save_user_messages()
        
        st.session_state.input_key += 1
        st.rerun()
        
    except Exception as e:
        error_msg = f"❌ Erreur traitement message: {str(e)}"
        print(error_msg)
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Désolé {st.session_state.user_name}, une erreur est survenue.",
            "confidence": 0,
            "source": "error",
            "timestamp": datetime.now().isoformat()
        })
        save_user_messages()
        st.rerun()
        
def show_chat_page(response_gen):
    """Page principale du chat"""
    # Charger les messages au début
    load_user_messages()
    
    # En-tête
    st.markdown('<div class="main-header">💳 ZamaPay</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-header">Assistant Intelligent • Finance Inclusive Africaine</div>', unsafe_allow_html=True)
    
    # Carte utilisateur
    user_profile = auth_system.get_user_profile(st.session_state.user_email)
    conv_count = user_profile.get("conversation_count", 0) if user_profile else 0
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"""
        <div class="user-card">
            <div style="font-size: 1.1rem; font-weight: 700; margin-bottom: 0.5rem;">
                👋 Bonjour, {st.session_state.user_name}
            </div>
            <div style="font-size: 0.85rem; opacity: 0.95;">
                📧 {st.session_state.user_email}<br>
                💬 {conv_count} conversations • {len(st.session_state.messages)} messages
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("🚪 Quitter", use_container_width=True):
            logout()
            st.rerun()
    
    # Questions rapides
    st.markdown("""
    <div class="quick-section">
        <div class="quick-title">💡 Questions fréquentes</div>
    </div>
    """, unsafe_allow_html=True)
    
    questions = [
        "💰 Frais de transaction",
        "⏱️ Délai de transfert", 
        "🔒 Sécurité des données",
        "✅ Vérification compte",
        "🔑 Problème connexion",
        "📊 Avantages ZamaPay"
    ]
    
    cols = st.columns(3)
    for i, q in enumerate(questions):
        with cols[i % 3]:
            if st.button(q, key=f"q_{i}", use_container_width=True):
                if not any(msg.get("content") == q for msg in st.session_state.get("messages", []) if msg.get("role") == "user"):
                    process_message(q, response_gen)
    
    st.markdown("---")
    
    # Affichage des messages
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="message-wrapper"><div class="user-message">{msg["content"]}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="message-wrapper"><div class="assistant-message">{msg["content"]}</div></div>', unsafe_allow_html=True)
            
            # Badges
            badges_html = ""
            if "confidence" in msg and msg["confidence"] > 0:
                conf = msg["confidence"]
                if conf > 0.7:
                    badge_class = "badge-high"
                    label = "✓ Haute"
                elif conf > 0.5:
                    badge_class = "badge-medium"
                    label = "⚡ Moyenne"
                else:
                    badge_class = "badge-low"
                    label = "⚠ Faible"
                badges_html += f'<span class="badge {badge_class}">{label}: {conf:.0%}</span>'
            
            if "source" in msg:
                sources = {
                    'knowledge_base': '📚 Base',
                    'gemini': '🤖 IA', 
                    'template': '💼 Expert',
                    'fallback': '🔍 Système'
                }
                label = sources.get(msg["source"], "Système")
                badges_html += f'<span class="badge badge-source">{label}</span>'
            
            if badges_html:
                st.markdown(badges_html, unsafe_allow_html=True)
    
    # Zone de saisie
    st.markdown("---")
    
    if "input_key" not in st.session_state:
        st.session_state.input_key = 0
    
    user_input = st.text_input(
        "Votre question...",
        placeholder="Posez votre question ici",
        key=f"input_{st.session_state.input_key}"
    )
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        send = st.button("🚀 Envoyer", use_container_width=True, type="primary")
    
    with col2:
        if st.button("🧹 Effacer", use_container_width=True):
            st.session_state.input_key += 1
            st.rerun()
    
    with col3:
        if st.button("🔄 Nouvelle Discussion", use_container_width=True):
            st.session_state.messages = [{
                "role": "assistant", 
                "content": f"Nouvelle discussion, {st.session_state.user_name}. Comment puis-je vous aider ?",
                "timestamp": datetime.now().isoformat()
            }]
            save_user_messages()
            st.session_state.input_key += 1
            st.rerun()
    
    if send and user_input:
        if not any(msg.get("content") == user_input for msg in st.session_state.messages if msg.get("role") == "user"):
            process_message(user_input, response_gen)
        else:
            st.warning("⚠️ Question déjà posée")

def show_history_page():
    """Page d'historique des conversations"""
    st.markdown('<div class="main-header">📊 Historique des Conversations</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Retrouvez toutes vos conversations précédentes</div>', unsafe_allow_html=True)
    
    # Charger l'historique
    history = conversation_manager.get_user_conversations(st.session_state.user_email)
    
    if not history:
        st.info("📝 Aucune conversation dans l'historique.")
        if st.button("💬 Commencer une conversation", use_container_width=True):
            st.session_state.current_page = "chat"
            st.rerun()
        return
    
    st.markdown(f"### 📋 Vos dernières conversations ({len(history)})")
    
    for i, conv in enumerate(history[-10:]):  # Les 10 dernières
        with st.expander(f"🗓️ {conv['date']} - {conv['question'][:50]}...", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**❓ Question :** {conv['question']}")
                st.markdown(f"**💡 Réponse :** {conv['response'][:200]}...")
            
            with col2:
                if st.button("💬 Reprendre", key=f"resume_{i}"):
                    st.session_state.current_page = "chat"
                    st.session_state.messages = [
                        {"role": "user", "content": conv['question'], "timestamp": conv['date']},
                        {"role": "assistant", "content": conv['response'], "timestamp": conv['date']}
                    ]
                    save_user_messages()
                    st.rerun()
                    
def show_agent_page():
    """Page pour parler à un agent"""
    st.markdown('<div class="main-header">👨‍💼 Parler à un Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Notre équipe est là pour vous aider personnellement</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #FFFBEB, #FEF3C7); padding: 2rem; border-radius: 12px; border: 1px solid #FCD34D; margin: 2rem 0;">
        <div style="font-size: 1.1rem; font-weight: 700; color: #92400E; margin-bottom: 1rem;">
            🎯 Contactez nos experts
        </div>
        <div style="color: #92400E; line-height: 1.6;">
            Nos agents sont disponibles pour vous accompagner dans toutes vos démarches. 
            Choisissez le mode de contact qui vous convient le mieux.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📞 Contact Immédiat")
        st.write("**Téléphone:** +226 25 40 92 76")
        st.write("**Disponibilité:** Lun-Ven 8h-20h")
        st.write("**WhatsApp:** +226 25 40 92 76")
        
        if st.button("📞 Appeler maintenant", use_container_width=True):
            st.success("📞 Composition du numéro...")
            st.info("🔗 Ouverture de votre application téléphonique...")
    
    with col2:
        st.markdown("### 📧 Contact en Ligne")
        st.write("**Email:** support@zamapay.com")
        st.write("**Réponse:** Sous 2h")
        st.write("**Urgence:** 24h/24 disponible")
        
        if st.button("📧 Envoyer un email", use_container_width=True):
            st.success("📧 Ouverture de votre client email...")
            st.info("✉️ Adresse pré-remplie: support@zamapay.com")
    
    st.markdown("---")
    
    # Formulaire de contact
    st.markdown("### 📝 Formulaire de Contact")
    
    with st.form("contact_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Nom complet", value=st.session_state.user_name)
            email = st.text_input("Email", value=st.session_state.user_email)
        
        with col2:
            phone = st.text_input("Téléphone", placeholder="+226 XX XX XX XX")
            urgency = st.selectbox("Urgence", ["Normal", "Élevée", "Critique"])
        
        subject = st.selectbox(
            "Sujet",
            ["Problème technique", "Question sur les frais", "Vérification de compte", "Plainte", "Autre"]
        )
        
        message = st.text_area("Description détaillée", height=120, 
                            placeholder="Décrivez votre problème ou question en détail...")
        
        submitted = st.form_submit_button("🚀 Envoyer la demande", use_container_width=True)
        
        if submitted:
            if message.strip():
                st.success("✅ Votre demande a été envoyée ! Un agent vous contactera dans les plus brefs délais.")
                st.balloons()
                
                # Afficher le récapitulatif
                st.markdown("### 📋 Récapitulatif de votre demande")
                st.write(f"**Nom:** {name}")
                st.write(f"**Email:** {email}")
                st.write(f"**Téléphone:** {phone}")
                st.write(f"**Urgence:** {urgency}")
                st.write(f"**Sujet:** {subject}")
                st.write(f"**Message:** {message}")
            else:
                st.error("❌ Veuillez décrire votre problème.")

def show_about_page():
    """Page À Propos de ZamaPay"""
    st.markdown('<div class="main-header">ℹ️ À Propos de ZamaPay</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Moderniser les usages grâce à des services agiles et solidaires</div>', unsafe_allow_html=True)
    
    # Section principale
    st.markdown("""
    <div style="background: white; padding: 2rem; border-radius: 12px; border: 1px solid #E2E8F0; margin: 1rem 0;">
        <div style="font-size: 1.1rem; font-weight: 600; color: #1E40AF; margin-bottom: 1rem;">
            🚀 Notre Mission
        </div>
        <div style="color: #475569; line-height: 1.7;">
            Moderniser les usages grâce à des services agiles et solidaires, financiers et non financiers, 
            pensés pour les communautés et l'économie locale.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Description ZamaPay
    st.markdown("""
    <div style="background: linear-gradient(135deg, #EEF2FF, #E0E7FF); padding: 2rem; border-radius: 12px; margin: 1.5rem 0;">
        <div style="font-size: 1.2rem; font-weight: 700; color: #1E40AF; margin-bottom: 1rem; text-align: center;">
            💳 ZamaPay
        </div>
        <div style="color: #374151; line-height: 1.7; text-align: center; font-size: 1.05rem;">
            Des solutions technologiques au service d'une offre inclusive, financière et non financière, 
            au cœur des réalités africaines.
        </div>
        <div style="color: #6B7280; line-height: 1.6; text-align: center; margin-top: 1rem;">
            Zamapay est une entreprise de technologie au service de la finance inclusive et des services essentiels
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Notre engagement
    st.markdown("""
    <div style="background: white; padding: 2rem; border-radius: 12px; border-left: 4px solid #10B981; margin: 1.5rem 0;">
        <div style="font-size: 1.1rem; font-weight: 700; color: #047857; margin-bottom: 1rem;">
            ✅ Notre Engagement
        </div>
        <div style="color: #475569; line-height: 1.7; font-style: italic;">
            "Créer des solutions qui simplifient la vie, avec une finance inclusive, communautaire et digitale, 
            ancrée dans les réalités africaines."
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Domaines d'expertise
    st.markdown("### 🎯 Nos Domaines d'Expertise")
    st.markdown("**3 axes pour transformer les pratiques financières en Afrique**")
    st.markdown("*Chez Zamapay, nous croyons qu'une technologie n'a de valeur que si elle répond aux réalités locales.*")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #E2E8F0; height: 100%;">
            <div style="font-size: 2rem; margin-bottom: 1rem;">🌍</div>
            <div style="font-weight: 700; color: #1E40AF; margin-bottom: 0.5rem;">Inclusion Financière</div>
            <div style="color: #475569; font-size: 0.9rem; line-height: 1.6;">
                Permettre à chacun, en particulier les populations non ou sous-bancarisées, d'accéder à des services 
                financiers simples, sécurisés et accessibles. Nous démocratisons la finance en la rendant disponible 
                partout, pour tous.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #E2E8F0; height: 100%;">
            <div style="font-size: 2rem; margin-bottom: 1rem;">📱</div>
            <div style="font-weight: 700; color: #1E40AF; margin-bottom: 0.5rem;">Digitalisation</div>
            <div style="color: #475569; font-size: 0.9rem; line-height: 1.6;">
                Accompagner les petits commerces, artisans et acteurs économiques locaux dans leur transition numérique. 
                Nous proposons des outils adaptés qui facilitent les paiements et améliorent la gestion quotidienne.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #E2E8F0; height: 100%;">
            <div style="font-size: 2rem; margin-bottom: 1rem;">👥</div>
            <div style="font-weight: 700; color: #1E40AF; margin-bottom: 0.5rem;">Communauté</div>
            <div style="color: #475569; font-size: 0.9rem; line-height: 1.6;">
                Concevoir des solutions qui s'appuient sur les dynamiques d'entraide, de solidarité et de gestion 
                collective propres aux communautés africaines. Nous valorisons ces pratiques pour renforcer la 
                résilience économique locale.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Slogan
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #1E40AF, #3730A3); 
                color: white; border-radius: 12px; margin: 2rem 0;">
        <div style="font-size: 1.5rem; font-weight: 800; margin-bottom: 1rem;">
            🚀 Goodbye Old Habits, Hello Future Payments!
        </div>
        <div style="font-size: 1rem; opacity: 0.9;">
            Chez zamapay, nous innovons pour et avec nos utilisateurs, en confiance avec les communautés
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Nos valeurs
    st.markdown("### 💎 Nos Valeurs")
    
    valeurs = [
        {"emoji": "🎯", "titre": "Engagement utilisateurs", "desc": "Au cœur de nos priorités"},
        {"emoji": "💡", "titre": "Innovation dans les usages", "desc": "Ancrée dans la réalité"},
        {"emoji": "🤝", "titre": "Confiance communautaire", "desc": "Partenaire des communautés"},
        {"emoji": "🌍", "titre": "Accessibilité pour tous", "desc": "Solutions inclusives"}
    ]
    
    cols = st.columns(2)
    for i, valeur in enumerate(valeurs):
        with cols[i % 2]:
            st.markdown(f"""
            <div style="background: white; padding: 1.5rem; border-radius: 10px; border: 1px solid #E2E8F0; margin: 0.5rem 0;">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{valeur['emoji']}</div>
                <div style="font-weight: 700; color: #1E40AF;">{valeur['titre']}</div>
                <div style="color: #475569; font-size: 0.9rem;">{valeur['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Contact
    st.markdown("---")
    st.markdown("### 📞 Rejoignez le train de la finance inclusive")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: #F8FAFC; padding: 1.5rem; border-radius: 10px; border: 1px solid #E2E8F0;">
            <div style="font-weight: 700; color: #1E40AF; margin-bottom: 1rem;">📧 Contact</div>
            <div style="color: #475569;">
                <div>📧 <strong>Email:</strong> contact@zamapay.com</div>
                <div>📞 <strong>Téléphone:</strong> (226) 25 40 92 76</div>
                <div>🏢 <strong>Adresse:</strong> Ouagadougou, Burkina Faso</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Formulaire de contact simplifié
        with st.form("about_contact_form"):
            st.markdown("**📝 Contactez-nous**")
            
            col_a, col_b = st.columns(2)
            with col_a:
                name = st.text_input("Nom & Prénom", placeholder="Votre nom complet")
            with col_b:
                email = st.text_input("Email", placeholder="votre@email.com")
            
            message = st.text_area("Message", placeholder="Votre message...", height=100)
            
            submitted = st.form_submit_button("🚀 Envoyer le message", use_container_width=True)
            
            if submitted:
                if name and email and message:
                    st.success("✅ Message envoyé ! Nous vous recontacterons rapidement.")
                else:
                    st.error("❌ Veuillez remplir tous les champs.")

def show_footer():
    """Affiche le footer commun"""
    st.markdown(f"""
    <div class="footer">
        <div style="font-weight: 700; font-size: 1.1rem; color: #1E40AF; margin-bottom: 0.5rem;">
            💳 {APP_NAME}
        </div>
        <div style="font-style: italic; margin-bottom: 1rem; color: #475569;">
            "Goodbye Old Habits, Hello Future Payments!"
        </div>
        📱 <a href="tel:+22625409276" style="color: #2563EB; text-decoration: none;">+226 25 40 92 76</a> • 
        📧 <a href="mailto:contact@zamapay.com" style="color: #2563EB; text-decoration: none;">contact@zamapay.com</a><br>
        🕒 Lun-Ven 8h-20h | Sam 9h-18h<br>
        <small style="color: #94A3B8; margin-top: 1rem; display: block;">
            © 2025 {APP_NAME} • Version {VERSION} • Propulsé par l'IA
        </small>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Point d'entrée"""
    # Initialiser l'état de session
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "input_key" not in st.session_state:
        st.session_state.input_key = 0
    if "current_page" not in st.session_state:
        st.session_state.current_page = "chat"
    if "messages_loaded" not in st.session_state:
        st.session_state.messages_loaded = False
    
    if not check_authentication():
        show_login_page()
    else:
        # Initialiser les systèmes
        retrieval, response_gen = initialize_systems()
        
        if retrieval is None or response_gen is None:
            st.error("❌ Service indisponible")
            if st.button("🔄 Recharger"):
                st.rerun()
            return
        
        # Afficher la navigation
        show_navigation()
        
        # Afficher la page appropriée
        if st.session_state.current_page == 'history':
            show_history_page()
        elif st.session_state.current_page == 'agent':
            show_agent_page()
        elif st.session_state.current_page == 'about':
            show_about_page()
        else:  # Page chat par défaut
            show_chat_page(response_gen)
        
        # Footer commun
        show_footer()

if __name__ == "__main__":
    main()
    
