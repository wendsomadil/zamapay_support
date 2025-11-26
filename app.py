import streamlit as st
import json
import time
from datetime import datetime
from retrieval_system import RetrievalSystem
from response_generator import ResponseGenerator
from login import show_login_page, check_authentication, logout
from auth_system import auth_system

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

# Initialisation
@st.cache_resource
def initialize_systems():
    try:
        import os
        if not os.path.exists("knowledge_base.json"):
            with open("knowledge_base.json", "w", encoding="utf-8") as f:
                json.dump({"qa_pairs": []}, f, ensure_ascii=False, indent=2)
        retrieval = RetrievalSystem("knowledge_base.json")
        response_gen = ResponseGenerator(retrieval)
        return retrieval, response_gen
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
        return None, None

def show_main_application():
    """Application principale"""
    retrieval, response_gen = initialize_systems()
    
    if retrieval is None or response_gen is None:
        st.error("❌ Service indisponible")
        if st.button("🔄 Recharger"):
            st.rerun()
        return
    
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
                💬 {conv_count} conversations
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
    
    # Initialiser messages
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": f"Bonjour {st.session_state.user_name} ! 👋 Je suis votre assistant ZamaPay. Comment puis-je vous aider aujourd'hui ?"
        }]
    
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
                    'template': '💼 Expert'
                }
                label = sources.get(msg["source"], "Système")
                badges_html += f'<span class="badge badge-source">{label}</span>'
            
            if badges_html:
                st.markdown(badges_html, unsafe_allow_html=True)
    
    # Zone de saisie
    st.markdown("---")
    
    # Initialiser clé si nécessaire
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
        # Bouton Effacer
        if st.button("🧹 Effacer", use_container_width=True):
            st.session_state.input_key += 1
            st.rerun()
    
    with col3:
        # Bouton pour réinitialiser
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.messages = [{
                "role": "assistant",
                "content": f"Nouvelle conversation, {st.session_state.user_name}. Comment puis-je vous aider ?"
            }]
            st.session_state.input_key += 1
            st.rerun()
    
    if send and user_input:
        if not any(msg.get("content") == user_input for msg in st.session_state.messages if msg.get("role") == "user"):
            process_message(user_input, response_gen)
        else:
            st.warning("⚠️ Question déjà posée")
    
    # Footer
    st.markdown("""
    <div class="footer">
        <div style="font-weight: 700; font-size: 1.1rem; color: #1E40AF; margin-bottom: 0.5rem;">
            💳 ZamaPay
        </div>
        <div style="font-style: italic; margin-bottom: 1rem; color: #475569;">
            "Goodbye Old Habits, Hello Future Payments!"
        </div>
        📱 <a href="tel:+22625409276" style="color: #2563EB; text-decoration: none;">+226 25 40 92 76</a> • 
        📧 <a href="mailto:contact@zamapay.com" style="color: #2563EB; text-decoration: none;">contact@zamapay.com</a><br>
        🕒 Lun-Ven 8h-20h | Sam 9h-18h<br>
        <small style="color: #94A3B8; margin-top: 1rem; display: block;">
            © 2025 ZamaPay • Version 2.0 • Propulsé par Gemini AI
        </small>
    </div>
    """, unsafe_allow_html=True)

def process_message(text, response_gen):
    """Traite un message utilisateur"""
    try:
        st.session_state.messages.append({"role": "user", "content": text})
        
        with st.spinner("🔍 Analyse..."):
            start = time.time()
            response = response_gen.generate_response(text, st.session_state.user_name)
            duration = time.time() - start
        
        auth_system.update_user_conversation_count(st.session_state.user_email)
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": response.get('response', 'Erreur'),
            "confidence": response.get('confidence', 0),
            "source": response.get('source', 'system'),
            "time": duration
        })
        
        st.session_state.input_key += 1
        st.rerun()
        
    except Exception as e:
        st.error("❌ Erreur de traitement")
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Désolé {st.session_state.user_name}, une erreur est survenue. Contactez le support.",
            "confidence": 0,
            "source": "error"
        })
        st.rerun()

def main():
    """Point d'entrée"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "input_key" not in st.session_state:
        st.session_state.input_key = 0
    
    if not check_authentication():
        show_login_page()
    else:
        show_main_application()

if __name__ == "__main__":
    main()
