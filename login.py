import streamlit as st
import time
from auth_system import auth_system

def show_login_page():
    """Affiche la page de connexion/inscription sans conteneur visible"""
    
    st.markdown("""
    <style>
        .login-header {
            text-align: center;
            color: #1E3A8A;
            margin-bottom: 1rem;
        }
        .success-message {
            background: #D1FAE5;
            color: #065F46;
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid #A7F3D0;
            font-size: 0.9rem;
        }
        .error-message {
            background: #FEE2E2;
            color: #991B1B;
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid #FECACA;
            font-size: 0.9rem;
        }
        .info-message {
            background: #DBEAFE;
            color: #1E40AF;
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid #93C5FD;
            font-size: 0.9rem;
        }
        .tab-container {
            display: flex;
            background: #F3F4F6;
            border-radius: 12px;
            padding: 4px;
            margin-bottom: 1.5rem;
        }
        .tab-button {
            flex: 1;
            padding: 0.75rem;
            border: none;
            background: transparent;
            color: #6B7280;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        .tab-button.active {
            background: white;
            color: #1E3A8A;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .code-display {
            background: #1E3A8A;
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            font-size: 2rem;
            font-weight: bold;
            letter-spacing: 0.5rem;
            margin: 1rem 0;
            border: 3px dashed #3B82F6;
        }
        .dev-warning {
            background: #FEF3C7;
            border: 2px solid #F59E0B;
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
        }
        .smtp-status-mini {
            padding: 0.5rem;
            border-radius: 6px;
            margin: 0.5rem 0;
            font-size: 0.8rem;
            text-align: center;
        }
        .smtp-success-mini {
            background: #D1FAE5;
            color: #065F46;
            border: 1px solid #A7F3D0;
        }
        .smtp-error-mini {
            background: #FEE2E2;
            color: #991B1B;
            border: 1px solid #FECACA;
        }
        .debug-toggle {
            text-align: center;
            margin: 0.5rem 0;
        }
        .debug-toggle button {
            background: transparent;
            border: 1px solid #D1D5DB;
            color: #6B7280;
            padding: 0.25rem 0.75rem;
            border-radius: 6px;
            font-size: 0.8rem;
            cursor: pointer;
        }
        .debug-toggle button:hover {
            background: #F3F4F6;
        }
        /* Styles pour centrer le contenu sans conteneur visible */
        .main-content {
            max-width: 450px;
            margin: 30px auto;
            padding: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Utiliser un conteneur Streamlit naturel au lieu d'un div HTML personnalisé
    with st.container():
        # En-tête
        st.markdown("""
        <div class="login-header">
            <h1 style="margin-bottom: 0.5rem;">💳 ZamaPay</h1>
            <p style="color: #6B7280; margin-top: 0;">Votre assistant financier intelligent</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Test de connexion SMTP automatique (mais discret)
        if 'smtp_tested' not in st.session_state:
            with st.spinner("🔧 Vérification du système..."):
                success, message = auth_system.test_smtp_connection()
                st.session_state.smtp_tested = True
                st.session_state.smtp_status = success
                st.session_state.smtp_message = message
        
        # Affichage MINIMAL du statut SMTP - version discrète
        if st.session_state.smtp_status:
            # Si SMTP fonctionne, on n'affiche rien ou un indicateur très discret
            if st.session_state.get('show_smtp_details', False):
                status_class = "smtp-success-mini"
                st.markdown(f'<div class="smtp-status-mini {status_class}">📧 {st.session_state.smtp_message}</div>', unsafe_allow_html=True)
        else:
            # Si SMTP échoue, on affiche un avertissement discret
            status_class = "smtp-error-mini"
            st.markdown(f'<div class="smtp-status-mini {status_class}">⚠️ Emails désactivés - Code affiché à l\'écran</div>', unsafe_allow_html=True)
        
        # Bouton debug discret
        st.markdown('<div class="debug-toggle">', unsafe_allow_html=True)
        if st.button("🔧 Debug SMTP", key="debug_toggle"):
            st.session_state.show_smtp_details = not st.session_state.get('show_smtp_details', False)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Détails SMTP seulement si demandé
        if st.session_state.get('show_smtp_details', False):
            with st.expander("📧 Détails de configuration SMTP", expanded=False):
                st.write(f"**Statut :** {st.session_state.smtp_message}")
                st.write(f"**Email :** {auth_system.smtp_config['email']}")
                st.write("**Serveur :** smtp.gmail.com:587")
                
                if not st.session_state.smtp_status:
                    st.info("""
                    **Pour résoudre :**
                    - Vérifie que la **validation 2 facteurs** est activée
                    - Utilise un **mot de passe d'application** valide
                    - Les codes s'afficheront à l'écran en attendant
                    """)
        
        # Onglets Connexion/Inscription
        st.markdown('<div class="tab-container">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            login_clicked = st.button("🔐 Connexion", use_container_width=True, 
                                    key="login_tab")
        with col2:
            register_clicked = st.button("📝 Inscription", use_container_width=True,
                                    key="register_tab")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Gestion des onglets
        if 'auth_tab' not in st.session_state:
            st.session_state.auth_tab = 'login'
        
        if login_clicked:
            st.session_state.auth_tab = 'login'
            st.rerun()
        if register_clicked:
            st.session_state.auth_tab = 'register'
            st.rerun()
        
        # Formulaire de connexion
        if st.session_state.auth_tab == 'login':
            st.markdown("### 🔐 Connexion à votre compte")
            
            with st.form("login_form", clear_on_submit=False):
                email = st.text_input("📧 Adresse email", placeholder="votre@email.com")
                password = st.text_input("🔒 Mot de passe", type="password", placeholder="Votre mot de passe")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    submit_login = st.form_submit_button("Se connecter →", use_container_width=True, type="primary")
                with col2:
                    forgot_password = st.form_submit_button("Mot de passe oublié ?", use_container_width=True)
                
                if submit_login and email and password:
                    success, message = auth_system.login_user(email, password)
                    if success:
                        st.session_state.user_email = email
                        st.session_state.user_name = auth_system.get_user_profile(email)["name"]
                        st.session_state.authenticated = True
                        st.success("✅ Connexion réussie !")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                
                if forgot_password:
                    st.session_state.show_password_reset = True
                    st.rerun()
        
        # Formulaire d'inscription
        else:
            st.markdown("### 📝 Créer un compte")
            
            # Étape 1 : Formulaire d'inscription
            if 'register_step' not in st.session_state or st.session_state.register_step == 1:
                with st.form("register_form", clear_on_submit=False):
                    name = st.text_input("👤 Nom complet", placeholder="Votre nom et prénom")
                    email = st.text_input("📧 Adresse email", placeholder="votre@email.com")
                    password = st.text_input("🔒 Mot de passe", type="password", placeholder="Minimum 6 caractères")
                    confirm_password = st.text_input("🔒 Confirmer le mot de passe", type="password", placeholder="Retapez votre mot de passe")
                    
                    submit_register = st.form_submit_button("Créer mon compte →", use_container_width=True, type="primary")
                    
                    if submit_register and name and email and password:
                        if password != confirm_password:
                            st.error("❌ Les mots de passe ne correspondent pas")
                        elif len(password) < 6:
                            st.error("❌ Le mot de passe doit contenir au moins 6 caractères")
                        else:
                            success, message = auth_system.register_user(email, password, name)
                            if success:
                                st.session_state.register_step = 2
                                st.session_state.pending_email = email
                                st.session_state.pending_name = name
                                
                                # Vérifier si l'email a été envoyé ou si on affiche le code
                                if "Code de vérification:" in message:
                                    st.session_state.email_sent = False
                                    st.session_state.verification_code = message.split(": ")[1].split(" ")[0]
                                else:
                                    st.session_state.email_sent = True
                                
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
            
            # Étape 2 : Vérification par email
            elif st.session_state.register_step == 2:
                st.markdown("### 📧 Vérification de votre email")
                
                if st.session_state.get('email_sent', True):
                    st.success(f"**Email envoyé à :** {st.session_state.pending_email}")
                    st.info("💡 **Vérifiez vos spams si vous ne voyez pas l'email !**")
                    
                    # Indicateur discret que SMTP fonctionne
                    st.caption("✅ Service email actif - Vérifiez votre boîte de réception")
                else:
                    st.markdown('<div class="dev-warning">', unsafe_allow_html=True)
                    st.warning("**Mode Développement - Email non envoyé**")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Afficher le code en grand
                    st.markdown("**Utilisez ce code de vérification :**")
                    st.markdown(f'<div class="code-display">{st.session_state.verification_code}</div>', unsafe_allow_html=True)
                    
                    st.caption("🔧 Mode manuel activé - Le code s'affiche ici car l'envoi d'email est désactivé")
                
                with st.form("verification_form", clear_on_submit=False):
                    verification_code = st.text_input("🔑 Code de vérification à 6 chiffres", 
                                                    placeholder="Entrez le code reçu par email",
                                                    max_chars=6)
                    
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        submit_verification = st.form_submit_button("Vérifier le code →", use_container_width=True, type="primary")
                    with col2:
                        resend_code = st.form_submit_button("🔄 Renvoyer", use_container_width=True)
                    with col3:
                        back_to_register = st.form_submit_button("← Retour", use_container_width=True)
                    
                    if submit_verification and verification_code:
                        if len(verification_code) != 6:
                            st.error("❌ Le code doit contenir 6 chiffres")
                        else:
                            success, message = auth_system.verify_email(st.session_state.pending_email, verification_code)
                            if success:
                                st.session_state.user_email = st.session_state.pending_email
                                st.session_state.user_name = st.session_state.pending_name
                                st.session_state.authenticated = True
                                st.session_state.register_step = 1
                                st.success("✅ Compte créé avec succès !")
                                st.balloons()
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                    
                    if resend_code:
                        # Régénérer un code et renvoyer l'email
                        new_code = auth_system.generate_verification_code()
                        auth_system.users["pending_verification"][st.session_state.pending_email]["verification_code"] = new_code
                        auth_system.users["pending_verification"][st.session_state.pending_email]["created_at"] = time.time()
                        auth_system.save_users()
                        
                        email_sent, smtp_error = auth_system.send_verification_email(st.session_state.pending_email, new_code)
                        if email_sent:
                            st.session_state.email_sent = True
                            st.success("📧 Nouveau code envoyé !")
                        else:
                            st.session_state.email_sent = False
                            st.session_state.verification_code = new_code
                            st.info("📧 Nouveau code généré (voir ci-dessus)")
                    
                    if back_to_register:
                        st.session_state.register_step = 1
                        st.rerun()
        
        # Formulaire de réinitialisation de mot de passe
        if st.session_state.get('show_password_reset', False):
            st.markdown("---")
            st.markdown("### 🔄 Réinitialisation du mot de passe")
            
            with st.form("password_reset_form"):
                reset_email = st.text_input("📧 Entrez votre email", placeholder="votre@email.com")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    submit_reset = st.form_submit_button("Envoyer le lien de réinitialisation", use_container_width=True)
                with col2:
                    cancel_reset = st.form_submit_button("Annuler", use_container_width=True)
                
                if submit_reset and reset_email:
                    if auth_system.is_valid_email(reset_email):
                        st.info("📧 Un lien de réinitialisation a été envoyé à votre email (fonctionnalité en développement)")
                        st.session_state.show_password_reset = False
                        st.rerun()
                    else:
                        st.error("❌ Format d'email invalide")
                
                if cancel_reset:
                    st.session_state.show_password_reset = False
                    st.rerun()
    
    # Pied de page
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6B7280; font-size: 0.8rem; margin-top: 2rem;">
        <strong>ZamaPay Support</strong><br>
        📞 +226 25 40 92 76 • 📧 support@zamapay.com<br>
        © 2025 ZamaPay - Tous droits réservés
    </div>
    """, unsafe_allow_html=True)

def check_authentication():
    """Vérifie si l'utilisateur est authentifié"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    
    return st.session_state.authenticated

def logout():
    """Déconnexion de l'utilisateur"""
    # Réinitialiser proprement tous les états
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.session_state.user_name = None
    # Initialiser messages à une liste vide au lieu de None
    st.session_state.messages = []
    # Nettoyer les états d'inscription
    if 'register_step' in st.session_state:
        del st.session_state.register_step
    if 'pending_email' in st.session_state:
        del st.session_state.pending_email
    if 'pending_name' in st.session_state:
        del st.session_state.pending_name
    
    st.rerun()
    
