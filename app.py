import streamlit as st
import json
import time
from datetime import datetime
from retrieval_system import RetrievalSystem
from response_generator import ResponseGenerator
from login import show_login_page, check_authentication, logout
from auth_system import auth_system

# ---------------------------------------------------------------------------
# CONFIGURATION ET STYLE GLOBAUX
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="ZamaPay - Finance Inclusive Africaine",
    page_icon="💳",
    layout="wide",
    # La barre latérale est repliée par défaut pour éviter qu'elle
    # n'apparaisse à l'écran. Les contenus latéraux sont déplacés
    # dans un onglet dédié dans le corps de la page.
    initial_sidebar_state="collapsed",
)

# Masquer complètement le contrôle qui permettrait de rouvrir la barre
# latérale après l'avoir repliée. Sans ce style, l'icône de
# « hamburger » resterait visible et permettrait de réactiver la sidebar.
st.markdown(
    """
    <style>
    [data-testid="collapsedControl"] {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# CSS professionnel ultra‑moderne copié depuis la version d'origine.
st.markdown(
    """
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

        /* FORCE LA POLICE PARTOUT - Solution au problème de police différente */
        * {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        }

        /* Forcer la police sur tous les éléments Streamlit */
        .stApp, .stApp * {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        }

        /* Forcer sur les messages spécifiquement */
        .user-message, .user-message *,
        .assistant-message, .assistant-message * {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        }

        /* Forcer sur tous les textes */
        p, span, div, h1, h2, h3, h4, h5, h6, a, button, input, textarea, label {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        }

        /* Palette de couleurs ZamaPay */
        :root {
            --primary-color: #2563EB;
            --primary-dark: #1E40AF;
            --primary-light: #60A5FA;
            --secondary-color: #10B981;
            --accent-color: #F59E0B;
            --danger-color: #EF4444;
            --text-primary: #0F172A;
            --text-secondary: #475569;
            --text-muted: #64748B;
            --bg-primary: #FFFFFF;
            --bg-secondary: #F8FAFC;
            --bg-tertiary: #F1F5F9;
            --border-color: #E2E8F0;
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        }

        /* Reset et base */
        .stApp {
            background: linear-gradient(135deg, #F8FAFC 0%, #EEF2FF 100%);
        }

        /* Header principal avec animation */
        .main-header {
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-align: center;
            margin-bottom: 0.5rem;
            letter-spacing: -0.03em;
            animation: fadeInDown 0.8s ease-out;
        }

        .sub-header {
            font-size: 1.2rem;
            color: var(--text-secondary);
            text-align: center;
            margin-bottom: 2.5rem;
            font-weight: 500;
            animation: fadeInUp 0.8s ease-out 0.2s both;
        }

        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }

        /* Container principal moderne */
        .chat-container {
            background: var(--bg-primary);
            border-radius: 20px;
            padding: 2.5rem;
            margin-bottom: 2rem;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow-lg);
            backdrop-filter: blur(10px);
            animation: fadeIn 0.6s ease-out;
            transition: box-shadow 0.3s ease;
        }

        .chat-container:hover {
            box-shadow: var(--shadow-xl);
        }

        /* Messages utilisateur avec design moderne */
        .user-message {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
            color: white !important;
            padding: 16px 24px;
            border-radius: 24px 24px 6px 24px;
            margin: 16px 0;
            max-width: 75%;
            margin-left: auto;
            box-shadow: 0 4px 16px rgba(37, 99, 235, 0.3);
            font-size: 0.95rem !important;
            line-height: 1.7;
            animation: slideInRight 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
            position: relative;
            word-wrap: break-word;
        }

        .user-message * {
            color: white !important;
            font-size: 0.95rem !important;
        }

        .user-message::before {
            content: '👤';
            position: absolute;
            left: -35px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 1.5rem;
            opacity: 0.8;
        }

        /* Messages assistant avec design élégant */
        .assistant-message {
            background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
            color: var(--text-primary) !important;
            padding: 16px 24px;
            border-radius: 24px 24px 24px 6px;
            margin: 16px 0;
            border: 1px solid var(--border-color);
            max-width: 75%;
            box-shadow: var(--shadow-md);
            font-size: 0.95rem !important;
            line-height: 1.7;
            animation: slideInLeft 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
            position: relative;
            word-wrap: break-word;
        }

        .assistant-message * {
            color: var(--text-primary) !important;
            font-size: 0.95rem !important;
        }

        .assistant-message::before {
            content: '🤖';
            position: absolute;
            right: -35px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 1.5rem;
            opacity: 0.8;
        }

        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(50px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        @keyframes slideInLeft {
            from {
                opacity: 0;
                transform: translateX(-50px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        /* Badges de confiance avec icônes */
        .confidence-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.75rem !important;
            font-weight: 600;
            margin-top: 8px;
            margin-right: 8px;
            transition: transform 0.2s ease;
        }

        .confidence-badge:hover {
            transform: scale(1.05);
        }

        .confidence-high {
            background: linear-gradient(135deg, #10B981 0%, #059669 100%);
            color: white !important;
        }

        .confidence-high * {
            color: white !important;
        }

        .confidence-medium {
            background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
            color: white !important;
        }

        .confidence-medium * {
            color: white !important;
        }

        .confidence-low {
            background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
            color: white !important;
        }

        .confidence-low * {
            color: white !important;
        }

        /* Section questions rapides modernisée */
        .quick-questions-container {
            background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);
            padding: 2rem;
            border-radius: 16px;
            margin: 2rem 0;
            border: 2px solid #C7D2FE;
            box-shadow: var(--shadow-md);
            animation: fadeIn 0.8s ease-out 0.4s both;
        }

        .quick-questions-title {
            font-size: 1.2rem !important;
            font-weight: 700;
            color: var(--primary-dark) !important;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 12px;
            letter-spacing: -0.01em;
        }

        .quick-questions-title::before {
            content: '💡';
            font-size: 1.8rem;
        }

        /* Boutons de questions rapides */
        .stButton > button {
            border-radius: 12px !important;
            font-weight: 600 !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            border: 2px solid transparent !important;
            box-shadow: var(--shadow-sm) !important;
        }

        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: var(--shadow-lg) !important;
            border-color: var(--primary-color) !important;
        }

        /* Badge de source élégant */
        .source-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 0.7rem !important;
            color: var(--text-muted) !important;
            background: var(--bg-tertiary);
            padding: 6px 14px;
            border-radius: 20px;
            margin-top: 8px;
            font-weight: 600;
            border: 1px solid var(--border-color);
            transition: all 0.2s ease;
        }

        .source-badge * {
            color: var(--text-muted) !important;
            font-size: 0.7rem !important;
        }

        .source-badge:hover {
            background: var(--bg-secondary);
            transform: scale(1.05);
        }

        /* Carte utilisateur premium */
        .user-info-card {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
            color: white !important;
            padding: 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(37, 99, 235, 0.4);
            position: relative;
            overflow: hidden;
            animation: fadeIn 0.8s ease-out 0.3s both;
        }

        .user-info-card * {
            color: white !important;
        }

        .user-info-card::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: pulse 3s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% {
                transform: scale(1);
                opacity: 1;
            }
            50% {
                transform: scale(1.1);
                opacity: 0.8;
            }
        }

        .user-info-header {
            font-size: 1.4rem !important;
            font-weight: 800;
            margin-bottom: 0.8rem;
            display: flex;
            align-items: center;
            gap: 12px;
            position: relative;
            z-index: 1;
        }

        .user-info-details {
            font-size: 0.95rem !important;
            opacity: 0.95;
            line-height: 2;
            position: relative;
            z-index: 1;
        }

        /* Statut système moderne */
        .system-status {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            margin-bottom: 1.5rem;
            box-shadow: var(--shadow-sm);
            transition: box-shadow 0.3s ease;
        }

        .system-status:hover {
            box-shadow: var(--shadow-md);
        }

        .status-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 14px 0;
            border-bottom: 1px solid var(--bg-tertiary);
            transition: background 0.2s ease;
        }

        .status-item:hover {
            background: var(--bg-secondary);
            padding-left: 10px;
            padding-right: 10px;
            border-radius: 8px;
        }

        .status-item:last-child {
            border-bottom: none;
        }

        .status-label {
            font-size: 0.9rem !important;
            color: var(--text-muted) !important;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .status-value {
            font-size: 1rem !important;
            color: var(--text-primary) !important;
            font-weight: 700;
        }

        /* Section À propos */
        .about-section {
            background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
            padding: 2.5rem;
            border-radius: 20px;
            margin: 2rem 0;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow-lg);
            animation: fadeIn 1s ease-out 0.5s both;
        }

        .about-header {
            font-size: 1.8rem !important;
            font-weight: 800;
            color: var(--primary-dark) !important;
            margin-bottom: 1.5rem;
            text-align: center;
            letter-spacing: -0.02em;
        }

        .about-content {
            font-size: 1rem !important;
            line-height: 1.8;
            color: var(--text-secondary) !important;
            margin-bottom: 1.5rem;
            text-align: justify;
        }

        .value-card {
            background: linear-gradient(135deg, var(--bg-secondary) 0%, #FFFFFF 100%);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            margin-bottom: 1rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
        }

        .value-card:hover {
            transform: translateY(-5px);
            box-shadow: var(--shadow-lg);
            border-color: var(--primary-color);
        }

        .value-title {
            font-size: 1.1rem !important;
            font-weight: 700;
            color: var(--primary-color) !important;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .value-description {
            font-size: 0.9rem !important;
            color: var(--text-muted) !important;
            line-height: 1.6;
        }

        /* Piliers d'expertise */
        .pillar-card {
            background: white;
            padding: 2rem;
            border-radius: 16px;
            border: 2px solid var(--border-color);
            text-align: center;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            height: 100%;
            position: relative;
            overflow: hidden;
        }

        .pillar-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
            transform: scaleX(0);
            transition: transform 0.3s ease;
        }

        .pillar-card:hover {
            transform: translateY(-8px);
            box-shadow: var(--shadow-xl);
            border-color: var(--primary-color);
        }

        .pillar-card:hover::before {
            transform: scaleX(1);
        }

        .pillar-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            display: block;
        }

        .pillar-title {
            font-size: 1.3rem !important;
            font-weight: 800;
            color: var(--primary-dark) !important;
            margin-bottom: 1rem;
        }

        .pillar-description {
            font-size: 0.9rem !important;
            color: var(--text-secondary) !important;
            line-height: 1.7;
        }

        /* Footer premium */
        .footer {
            text-align: center;
            color: var(--text-muted) !important;
            font-size: 0.9rem !important;
            margin-top: 4rem;
            padding: 3rem 1rem;
            border-top: 2px solid var(--border-color);
            background: linear-gradient(to top, var(--bg-secondary), transparent);
            animation: fadeIn 1s ease-out 0.8s both;
        }

        .footer * {
            color: var(--text-muted) !important;
        }

        .footer-title {
            font-weight: 800;
            color: var(--primary-dark) !important;
            font-size: 1.3rem !important;
            margin-bottom: 1rem;
            letter-spacing: -0.01em;
        }

        .footer-tagline {
            font-size: 1rem !important;
            color: var(--text-secondary) !important;
            margin-bottom: 1.5rem;
            font-style: italic;
        }

        .footer-links {
            display: flex;
            justify-content: center;
            gap: 25px;
            margin: 1.5rem 0;
            flex-wrap: wrap;
        }

        .footer-link {
            color: var(--primary-color) !important;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.2s ease;
            position: relative;
        }

        .footer-link::after {
            content: '';
            position: absolute;
            bottom: -2px;
            left: 0;
            right: 0;
            height: 2px;
            background: var(--primary-color);
            transform: scaleX(0);
            transition: transform 0.2s ease;
        }

        .footer-link:hover {
            color: var(--primary-dark) !important;
        }

        .footer-link:hover::after {
            transform: scaleX(1);
        }

        .footer-contact {
            background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%);
            padding: 1.5rem;
            border-radius: 12px;
            margin: 1.5rem auto;
            max-width: 600px;
            border: 1px solid var(--border-color);
        }

        /* Metrics cards améliorées */
        .metric-card {
            background: linear-gradient(135deg, #FFFFFF 0%, var(--bg-secondary) 100%);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            text-align: center;
            box-shadow: var(--shadow-sm);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }

        .metric-card::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(37, 99, 235, 0.1) 0%, transparent 70%);
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .metric-card:hover {
            transform: translateY(-5px) scale(1.02);
            box-shadow: var(--shadow-lg);
            border-color: var(--primary-color);
        }

        .metric-card:hover::before {
            opacity: 1;
        }

        .metric-value {
            font-size: 2.2rem !important;
            font-weight: 800;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            position: relative;
            z-index: 1;
        }

        .metric-label {
            font-size: 0.85rem !important;
            color: var(--text-muted) !important;
            margin-top: 6px;
            font-weight: 600;
            position: relative;
            z-index: 1;
        }

        /* Zone de saisie améliorée */
        .stTextArea textarea {
            border-radius: 12px !important;
            border: 2px solid var(--border-color) !important;
            font-size: 0.95rem !important;
            transition: all 0.3s ease !important;
            padding: 1rem !important;
        }

        .stTextArea textarea:focus {
            border-color: var(--primary-color) !important;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
        }

        /* Indicateur de typing */
        .typing-indicator {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 12px 20px;
            background: var(--bg-tertiary);
            border-radius: 20px;
            animation: pulse 1.5s ease-in-out infinite;
        }

        .typing-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--primary-color);
            animation: bounce 1.4s ease-in-out infinite;
        }

        .typing-dot:nth-child(2) {
            animation-delay: 0.2s;
        }

        .typing-dot:nth-child(3) {
            animation-delay: 0.4s;
        }

        @keyframes bounce {
            0%, 60%, 100% {
                transform: translateY(0);
            }
            30% {
                transform: translateY(-10px);
            }
        }

        /* Alert boxes personnalisées */
        .stAlert {
            border-radius: 12px !important;
            border: none !important;
            box-shadow: var(--shadow-md) !important;
        }

        /* Badge notification */
        .notification-badge {
            display: inline-block;
            background: var(--danger-color);
            color: white !important;
            font-size: 0.7rem !important;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 10px;
            margin-left: 6px;
            animation: pulse 2s ease-in-out infinite;
        }

        /* Section divider élégant */
        .section-divider {
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--primary-color), transparent);
            margin: 3rem 0;
            animation: fadeIn 0.8s ease-out;
        }

        /* Fix pour les expanders Streamlit */
        .streamlit-expanderHeader {
            font-size: 1rem !important;
            font-weight: 600 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# FONCTIONS UTILITAIRES
# ---------------------------------------------------------------------------

@st.cache_resource
def initialize_systems():
    """Initialise les systèmes de récupération et de génération de réponses"""
    try:
        import os
        if not os.path.exists("knowledge_base.json"):
            st.error("❌ Fichier de base de connaissances introuvable")
            with open("knowledge_base.json", "w", encoding="utf-8") as f:
                json.dump({"qa_pairs": []}, f, ensure_ascii=False, indent=2)
        retrieval = RetrievalSystem("knowledge_base.json")
        response_gen = ResponseGenerator(retrieval)
        return retrieval, response_gen
    except Exception as e:
        st.error(f"❌ Erreur d'initialisation: {str(e)}")
        return None, None

def render_sidebar_user_info():
    """Affiche les informations utilisateur (précédemment en sidebar)"""
    user_profile = auth_system.get_user_profile(st.session_state.user_email)
    conversation_count = user_profile.get("conversation_count", 0) if user_profile else 0
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #2563EB, #1E40AF); color: white; padding: 1.2rem; border-radius: 12px; margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);">
            <div style="font-weight: 800; font-size: 1.15rem; margin-bottom: 0.6rem; display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.8rem;">👤</span>
                <span>{st.session_state.user_name}</span>
            </div>
            <div style="font-size: 0.85rem; opacity: 0.95; word-break: break-word;">{st.session_state.user_email}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return conversation_count

def render_sidebar_metrics(conversation_count):
    """Affiche les métriques utilisateur (conversations, messages)"""
    st.markdown("#### 📊 Vos Statistiques")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{conversation_count}</div>
                <div class="metric-label">💬 Conversations</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        messages_count = max(0, len(st.session_state.get("messages", [])) - 1)
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{messages_count}</div>
                <div class="metric-label">💭 Messages</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

def render_sidebar_system_status(retrieval, response_gen):
    """Affiche le statut des systèmes IA"""
    st.markdown("---")
    st.markdown("#### 🔧 Statut Système")
    if hasattr(response_gen, 'gemini_model') and response_gen.gemini_model is not None:
        st.success("✅ IA Gemini Active")
    else:
        st.warning("⚠️ Mode Templates")
    kb_count = len(retrieval.knowledge_base['qa_pairs']) if retrieval else 0
    st.info(f"📚 {kb_count} Q/R Disponibles")
    if hasattr(response_gen, 'conversation_memory'):
        active_users = len(response_gen.conversation_memory)
        st.info(f"👥 {active_users} Session{'s' if active_users > 1 else ''}")

def render_sidebar_actions():
    """Affiche les actions rapides (nouvelle discussion, déconnexion)"""
    st.markdown("---")
    st.markdown("#### 🎯 Actions Rapides")
    if st.button("🔄 Nouvelle Discussion", key="new_chat", use_container_width=True, type="secondary"):
        st.session_state.messages = [
            {"role": "assistant", "content": f"Nouvelle discussion démarrée, {st.session_state.user_name}. Comment puis-je vous aider aujourd'hui ? 😊"}
        ]
        st.session_state.input_key += 1
        st.rerun()
    if st.button("🚪 Se Déconnecter", key="logout", use_container_width=True, type="primary"):
        logout()
        return True
    return False

def render_sidebar_support():
    """Affiche les informations de support (contact)"""
    st.markdown("---")
    st.markdown("#### 📞 Support Direct")
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #F1F5F9, #E2E8F0); padding: 1.2rem; border-radius: 12px; font-size: 0.9rem;">
            <strong style="color: #1E40AF; font-size: 1rem; display: block; margin-bottom: 0.8rem;">
                💬 Besoin d'aide ?
            </strong>
            <div style="margin-bottom: 0.6rem;">
                <strong>📱 Téléphone:</strong><br>
                <a href="tel:+22625409276" style="color: #2563EB; text-decoration: none; font-weight: 600;">
                    +226 25 40 92 76
                </a>
            </div>
            <div style="margin-bottom: 0.6rem;">
                <strong>📧 Email:</strong><br>
                <a href="mailto:contact@zamapay.com" style="color: #2563EB; text-decoration: none; font-weight: 600;">
                    contact@zamapay.com
                </a>
            </div>
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #CBD5E1;">
                <strong>🕒 Horaires:</strong><br>
                <span style="color: #475569;">
                    Lun-Ven: 8h-20h<br>
                    Samedi: 9h-18h
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_main_header():
    """Affiche l'en‑tête principal de l'application"""
    st.markdown('<div class="main-header">💳 ZamaPay Assistant Intelligent</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-header">Bonjour {st.session_state.user_name} ! 👋 Votre assistant personnel pour une finance inclusive et accessible</div>', unsafe_allow_html=True)

def render_user_welcome_card():
    """Affiche la carte de bienvenue utilisateur"""
    user_profile = auth_system.get_user_profile(st.session_state.user_email)
    if not user_profile:
        return
    created_timestamp = user_profile.get('created_at', time.time())
    created_date = datetime.fromtimestamp(created_timestamp).strftime('%d/%m/%Y')
    conversation_count = user_profile.get("conversation_count", 0)
    last_activity = datetime.now().strftime('%d/%m/%Y à %H:%M')
    st.markdown(
        f"""
        <div class="user-info-card">
            <div class="user-info-header">
                <span style="font-size: 2rem;">🎯</span>
                <span>Session Active</span>
            </div>
            <div class="user-info-details">
                <strong style="font-size: 1.1rem;">{st.session_state.user_name}</strong><br>
                <div style="margin-top: 0.5rem; opacity: 0.9;">
                    👤 Membre depuis le {created_date}<br>
                    💬 {conversation_count} conversation{'s' if conversation_count > 1 else ''} à votre actif<br>
                    🕐 Dernière activité: {last_activity}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_quick_questions(response_gen):
    """Affiche les questions rapides"""
    st.markdown(
        """
        <div class="quick-questions-container">
            <div class="quick-questions-title">
                Questions Fréquemment Posées
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    quick_questions = [
        ("💰", "Quels sont vos frais de transaction ?"),
        ("⏱️", "Délai d'exécution d'un transfert ?"),
        ("🔒", "Comment mes données sont-elles protégées ?"),
        ("✅", "Processus de vérification de compte"),
        ("🔑", "Aide pour problème de connexion"),
        ("📊", "Avantages vs banques traditionnelles"),
    ]
    cols = st.columns(3)
    for i, (emoji, question) in enumerate(quick_questions):
        with cols[i % 3]:
            if st.button(f"{emoji} {question}", key=f"quick_{i}", use_container_width=True):
                question_already_asked = any(
                    msg.get("role") == "user" and msg.get("content") == question
                    for msg in st.session_state.get("messages", [])
                )
                if not question_already_asked:
                    process_user_input(question, response_gen)
                else:
                    st.warning("⚠️ Cette question a déjà été posée dans cette conversation")

def render_chat_history():
    """Affiche l'historique de la conversation"""
    if "messages" not in st.session_state or not st.session_state.messages:
        st.info("💬 Démarrez la conversation en posant votre première question ci-dessous ! 👇")
        return
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="assistant-message">{message["content"]}</div>', unsafe_allow_html=True)
            render_message_indicators(message)

def render_message_indicators(message):
    """Affiche les badges (confiance, source, temps) pour un message assistant"""
    indicators_html = ""
    if "confidence" in message and message["confidence"] > 0:
        confidence = message["confidence"]
        if confidence > 0.7:
            badge_class = "confidence-high"
            icon = "✓"
            label = "Haute confiance"
        elif confidence > 0.5:
            badge_class = "confidence-medium"
            icon = "⚡"
            label = "Confiance moyenne"
        else:
            badge_class = "confidence-low"
            icon = "⚠"
            label = "Confiance faible"
        indicators_html += f'<span class="confidence-badge {badge_class}">{icon} {label}: {confidence:.0%}</span>'
    if "source" in message:
        source_badges = {
            'knowledge_base': ('📚', 'Base de Connaissances'),
            'gemini': ('🤖', 'IA Gemini Flash'),
            'gemini_fallback': ('🤖', 'IA Gemini Pro'),
            'template': ('💼', 'Réponse Standard'),
            'template_improved': ('💼', 'Réponse Enrichie'),
            'escalation': ('👤', 'Transfert Support Humain'),
        }
        icon, label = source_badges.get(message["source"], ('🔧', 'Système'))
        indicators_html += f'<span class="source-badge">{icon} {label}</span>'
    if "response_time" in message:
        response_time = message["response_time"]
        if response_time < 1:
            time_badge = f'<span class="source-badge">⚡ Instantané ({response_time:.2f}s)</span>'
        elif response_time < 3:
            time_badge = f'<span class="source-badge">🚀 Rapide ({response_time:.2f}s)</span>'
        else:
            time_badge = f'<span class="source-badge">⏱️ {response_time:.2f}s</span>'
        indicators_html += time_badge
    if indicators_html:
        st.markdown(f'<div style="margin-top: 8px;">{indicators_html}</div>', unsafe_allow_html=True)

def render_input_section(response_gen):
    """Affiche la zone de saisie utilisateur et les actions associées"""
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("### ✍️ Votre Message")
    if "input_key" not in st.session_state:
        st.session_state.input_key = 0
    with st.container():
        user_input = st.text_area(
            "Posez votre question ici...",
            placeholder="Exemple : Comment puis-je ouvrir un compte ZamaPay ? Quels sont les avantages de votre plateforme pour les commerces locaux ?",
            key=f"user_input_{st.session_state.input_key}",
            height=120,
            help="Tapez votre question et appuyez sur 'Envoyer' ou utilisez Ctrl+Entrée",
        )
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        send_button = st.button(
            "🚀 Envoyer le Message",
            key="send_btn",
            use_container_width=True,
            type="primary",
            help="Envoyer votre message",
        )
    with col2:
        clear_button = st.button(
            "🧹 Effacer",
            key="clear_btn",
            use_container_width=True,
            help="Effacer le champ de saisie",
        )
    with col3:
        help_button = st.button(
            "❓ Aide",
            key="help_btn",
            use_container_width=True,
            help="Afficher l'aide",
        )
    return user_input, send_button, clear_button, help_button

def render_about_section():
    """Affiche la section À propos de ZamaPay"""
    with st.expander("ℹ️ À Propos de ZamaPay", expanded=False):
        st.markdown(
            """
            <div class="about-section">
                <div class="about-header">🌍 Notre Mission</div>
                <div class="about-content">
                    <strong>ZamaPay</strong> est une entreprise de technologie au service de la finance inclusive et des services essentiels.
                    Nous modernisons les usages grâce à des services agiles et solidaires, financiers et non financiers,
                    pensés pour les communautés et l'économie locale africaine.
                </div>
                <div class="about-content">
                    <strong>🎯 Notre engagement:</strong> Créer des solutions qui simplifient la vie, avec une finance inclusive,
                    communautaire et digitale, ancrée dans les réalités africaines.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("### 🏛️ Nos 3 Piliers d'Expertise")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                """
                <div class="pillar-card">
                    <span class="pillar-icon">🌐</span>
                    <div class="pillar-title">Inclusion Financière</div>
                    <div class="pillar-description">
                        Permettre à chacun d'accéder à des services financiers simples, sécurisés et accessibles.
                        Nous démocratisons la finance pour favoriser l'autonomie économique.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                """
                <div class="pillar-card">
                    <span class="pillar-icon">💻</span>
                    <div class="pillar-title">Digitalisation</div>
                    <div class="pillar-description">
                        Accompagner les acteurs économiques locaux dans leur transition numérique avec des outils
                        qui facilitent les paiements et ouvrent de nouvelles opportunités.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                """
                <div class="pillar-card">
                    <span class="pillar-icon">🤝</span>
                    <div class="pillar-title">Communauté</div>
                    <div class="pillar-description">
                        Concevoir des solutions basées sur l'entraide et la solidarité, en valorisant les pratiques
                        communautaires pour renforcer la résilience économique locale.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("### 💎 Nos Valeurs Fondamentales")
        values = [
            ("🎯", "Engagement envers les utilisateurs", "Nous plaçons les besoins de nos utilisateurs au cœur de chaque décision"),
            ("💡", "Innovation ancrée dans les usages", "Nous innovons en partant des réalités et pratiques locales"),
            ("🔒", "Confiance dans les communautés", "Nous croyons au pouvoir de la solidarité et de l'entraide"),
            ("🌍", "Accessibilité pour tous", "Nous rendons la finance accessible sans barrières ni discrimination"),
        ]
        for icon, title, description in values:
            st.markdown(
                f"""
                <div class="value-card">
                    <div class="value-title">{icon} {title}</div>
                    <div class="value-description">{description}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

def render_footer():
    """Affiche le pied de page professionnel"""
    st.markdown(
        """
        <div class="footer">
            <div class="footer-title">💳 ZamaPay</div>
            <div class="footer-tagline">
                "Goodbye Old habits, Hello Future Payments!"
            </div>
            <div class="footer-content">
                Votre partenaire pour une finance inclusive, solidaire et ancrée dans les réalités africaines
            </div>
            <div class="footer-links">
                <a href="https://zamapay.com" class="footer-link" target="_blank">🏠 Site Web</a>
                <a href="#" class="footer-link">📖 À Propos</a>
                <a href="#" class="footer-link">📜 Conditions d'Utilisation</a>
                <a href="#" class="footer-link">🔒 Confidentialité</a>
                <a href="#" class="footer-link">🛡️ Sécurité</a>
                <a href="#" class="footer-link">❓ FAQ</a>
            </div>
            <div class="footer-contact">
                <strong style="color: #1E40AF; display: block; margin-bottom: 0.8rem;">📞 Contactez-nous</strong>
                <div style="color: #475569;">
                    📱 <a href="tel:+22625409276" style="color: #2563EB; text-decoration: none; font-weight: 600;">+226 25 40 92 76</a><br>
                    📧 <a href="mailto:contact@zamapay.com" style="color: #2563EB; text-decoration: none; font-weight: 600;">contact@zamapay.com</a><br>
                    📍 Ouagadougou, Burkina Faso
                </div>
                <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #CBD5E1; color: #64748B;">
                    🕒 <strong>Horaires:</strong> Lun-Ven 8h-20h | Sam 9h-18h
                </div>
            </div>
            <div style="margin-top: 2rem; font-size: 0.8rem; color: #94A3B8;">
                © 2025 ZamaPay. Tous droits réservés. | Version 2.0<br>
                <span style="font-size: 0.75rem;">Propulsé par IA Gemini • Assistant Intelligent Multilingue</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def process_user_input(user_input, response_gen):
    """Traite l'entrée utilisateur et génère une réponse"""
    try:
        if not user_input or not user_input.strip():
            st.warning("⚠️ Veuillez saisir un message avant d'envoyer")
            return False
        if len(user_input.strip()) < 2:
            st.warning("⚠️ Le message doit contenir au moins 2 caractères")
            return False
        if st.session_state.get("messages"):
            last_user_msg = None
            for msg in reversed(st.session_state.messages):
                if msg.get("role") == "user":
                    last_user_msg = msg.get("content", "")
                    break
            if last_user_msg and last_user_msg.strip() == user_input.strip():
                st.warning("⚠️ Vous venez de poser cette même question. Voulez-vous la reformuler ?")
                return False
        st.session_state.messages.append({"role": "user", "content": user_input.strip()})
        with st.spinner("🔍 Analyse de votre question en cours..."):
            start_time = time.time()
            if response_gen is None:
                raise Exception("Système de réponse non initialisé")
            response_data = response_gen.generate_response(user_input.strip(), st.session_state.user_name)
            response_time = time.time() - start_time
        try:
            if hasattr(auth_system, 'update_user_conversation_count'):
                auth_system.update_user_conversation_count(st.session_state.user_email)
        except Exception as e:
            print(f"Erreur mise à jour compteur: {e}")
        assistant_message = {
            "role": "assistant",
            "content": response_data.get('response', "Désolé, je n'ai pas pu générer une réponse pour le moment. Veuillez réessayer ou contacter notre support."),
            "confidence": response_data.get('confidence', 0),
            "source": response_data.get('source', 'system'),
            "response_time": response_time,
        }
        st.session_state.messages.append(assistant_message)
        st.session_state.conversation_started = True
        if response_time < 2:
            st.success(f"✅ Réponse générée en {response_time:.2f}s ⚡")
        elif response_time < 5:
            st.success(f"✅ Réponse générée en {response_time:.2f}s")
        else:
            st.info(f"✅ Réponse générée en {response_time:.2f}s")
        if response_data.get('confidence', 0) < 0.5:
            st.info("💡 Pour une réponse plus précise, essayez de reformuler votre question ou contactez notre support.")
        st.session_state.input_key += 1
        return True
    except Exception as e:
        error_msg = f"Erreur lors du traitement: {str(e)}"
        print(error_msg)
        st.error("❌ Une erreur s'est produite. Veuillez réessayer.")
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Je rencontre actuellement une difficulté technique, {st.session_state.user_name}. Notre équipe est alertée. En attendant, vous pouvez nous contacter directement au +226 25 40 92 76 pour une assistance immédiate. 🙏",
            "confidence": 0.1,
            "source": "error",
        })
        st.session_state.input_key += 1
        return False

# ---------------------------------------------------------------------------
# APPLICATION PRINCIPALE
# ---------------------------------------------------------------------------

def show_main_application():
    """Affiche l'application principale après connexion"""
    retrieval, response_gen = initialize_systems()
    if retrieval is None or response_gen is None:
        st.error("❌ Service temporairement indisponible. Veuillez rafraîchir la page ou réessayer dans quelques instants.")
        if st.button("🔄 Rafraîchir la page", type="primary"):
            st.rerun()
        return
    # Création des onglets : Chat et Menu
    tab_chat, tab_menu = st.tabs(["💬 Chat", "📋 Menu"])
    with tab_chat:
        render_main_header()
        render_user_welcome_card()
        render_quick_questions(response_gen)
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 💬 Conversation en Direct")
        if not st.session_state.get("messages") or not st.session_state.messages:
            welcome_message = {
                "role": "assistant",
                "content": f"Bonjour {st.session_state.user_name} ! 👋 Je suis votre assistant ZamaPay intelligent, spécialisé dans la finance inclusive africaine. Je peux vous aider avec :\n\n• 💰 Questions sur les tarifs et frais\n• 🔒 Sécurité et protection des données\n• ⚡ Processus de transactions\n• ✅ Vérification de compte\n• 🌍 Avantages de notre plateforme\n• 📱 Assistance technique\n\nComment puis-je vous aider aujourd'hui ?",
            }
            st.session_state.messages = [welcome_message]
        chat_container = st.container()
        with chat_container:
            render_chat_history()
        user_input, send_button, clear_button, help_button = render_input_section(response_gen)
        if send_button and user_input:
            if process_user_input(user_input, response_gen):
                st.rerun()
        if clear_button:
            st.session_state.input_key += 1
            st.rerun()
        if help_button:
            st.info(
                """
                **💡 Guide d'Utilisation**\n\n
                • Posez des questions claires et précises\n
                • Utilisez les boutons de questions rapides\n
                • Contactez notre support si besoin\n\n
                **Support :** 📱 +226 25 40 92 76 | 📧 contact@zamapay.com
                """
            )
    with tab_menu:
        st.markdown("### ⚙️ Tableau de Bord")
        conversation_count = render_sidebar_user_info()
        render_sidebar_metrics(conversation_count)
        render_sidebar_system_status(retrieval, response_gen)
        if render_sidebar_actions():
            return
        render_sidebar_support()
        render_about_section()
        render_footer()

def main():
    """Fonction principale avec gestion de l'authentification"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "input_key" not in st.session_state:
        st.session_state.input_key = 0
    if "conversation_started" not in st.session_state:
        st.session_state.conversation_started = False
    if not check_authentication():
        show_login_page()
    else:
        show_main_application()

if __name__ == "__main__":
    main()
    
