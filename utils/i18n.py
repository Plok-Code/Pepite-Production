import streamlit as st

# Dictionary of translations
TRANSLATIONS = {
    "fr": {
        # General
        "app_title": "Pepite Production",
        "home_intro": "Découvrez des films, ajoutez vos favoris et obtenez des recommandations personnalisées - site réalisé dans le cadre d'un projet scolaire.",
        "home_title": "Accueil",
        "genre_title": "Par genre",
        "library_title": "Ma bibliothèque",
        "favorites_title": "Mes favoris",
        "recos_title": "Recommandations",
        "settings_title": "Paramètres",
        "profile_title": "Mon profil",
        "cinemas_title": "Nos salles de cinéma",
        "admin_title": "Admin",
        "search_submit": "Rechercher",
        "search_page_title": "Recherche",
        "search_results_for": "Résultats pour : {}",
        "search_hint": "Tapez un nom de film puis appuyez sur Entrée ou Rechercher.",
        "back_button": "Retour",
        "admin_home_tab": "Accueil",
        "admin_filters_title": "Filtres utilisateurs",
        "admin_age_filter": "Âge",
        "admin_include_unknown": "Inclure inconnus",
        "admin_gender_filter": "Genre",
        "admin_in_creuse_filter": "Creuse",
        "admin_cinema_filter": "Cinéma (12 mois)",
        "admin_all": "Tous",
        "admin_unknown": "Inconnu",
        "admin_top_liked": "Films les plus likés",
        "admin_top_liked_desc": "Classement basé sur les favoris (après filtres).",
        "admin_selected_users": "Utilisateurs",
        "admin_total_likes": "Likes (favoris)",
        "admin_unique_movies": "Films uniques",
        "admin_no_likes": "Aucun favori pour cette sélection.",
        "admin_top_n": "Nombre de films",
        "admin_python_tab": "Dashboard Python",
        "admin_likes_by_genre": "Likes par genre",
        "admin_likes_by_language": "Likes par langue",
        "admin_powerbi_note": "Note : l'iframe Power BI ne peut pas être filtrée automatiquement depuis Streamlit sans intégration via l'API Power BI.",
        "admin_settings_tab": "Modèles de recommandation",
        "admin_reco_model_label": "Modèle de recommandation",
        "admin_reco_model_help": "Choisissez le modèle ML utilisé partout dans l'application.",
        "admin_settings_saved": "Réglages enregistrés.",
        "admin_reco_backend_status": "Moteur : {} — {}",
        "search_placeholder": "Rechercher un film…",
        "search_no_result": "Aucun résultat.",
        "search_open": "Ouvrir",
        "search_clear": "Effacer",
        "search_results": "Résultats",
        "search_choose": "Choisir un film…",

        # Sections
        "featured_section": "Films vedettes",
        "gems_section": "Nos Pépites",
        "niche_section": "Niche",
        "top_n_genre": "Top {} en {}",
        "click_to_open": "Cliquez sur un titre pour ouvrir la fiche du film.",

        # Movie Card
        "genre_label": "Genre :",
        "rating_label": "Note :",
        "director_label": "Réalisateur :",
        "actors_label": "Acteurs :",
        "language_label": "Langue :",
        "duration_label": "Durée :",
        "minutes": "min",

        # Auth
        "login_tab": "Connexion",
        "signup_tab": "Inscription",
        "email_label": "Email",
        "password_label": "Mot de passe",
        "password_confirm": "Confirmer le mot de passe",
        "login_submit": "Se connecter",
        "signup_submit": "Créer mon compte",
        "dob_label": "Date de naissance (optionnel)",
        "gender_label": "Genre (optionnel)",
        "gender_male": "Homme",
        "gender_female": "Femme",
        "gender_other": "Autre",
        "in_creuse_label": "Habitez-vous dans la Creuse ? (optionnel)",
        "cinema_12m_label": "Sorti au cinéma dans les 12 derniers mois ? (optionnel)",
        "optional_placeholder": "Optionnel",
        "yes": "Oui",
        "no": "Non",
        "logout_button": "Se déconnecter",
        "logged_in_as": "Connecté en tant que {}",
        "welcome_back": "Bon retour, {} !",
        "auth_required": "Vous devez être connecté.",
        "auth_required_favs": "Vous devez être connecté pour accéder à vos favoris.",
        "auth_required_recos": "Vous devez être connecté pour voir vos recommandations.",
        "auth_required_profile": "Vous devez être connecté pour accéder à votre profil.",
        "admin_access_denied": "Accès réservé aux administrateurs.",
        "invalid_credentials": "Identifiants invalides",
        "passwords_mismatch": "Les mots de passe ne correspondent pas.",
        "account_created": "Compte créé. Bienvenue !",
        "mysql_fallback": "MySQL configuré, mais pymysql n'est pas installé. Fallback en stockage local.",
        "mysql_unavailable": "MySQL configuré, mais indisponible. Fallback en stockage local.",
        "disconnected": "Déconnecté",

        # Profile
        "profile_info_section": "Informations",
        "profile_info_desc": "Modifiez vos données.",
        "profile_security_section": "Sécurité",
        "profile_security_desc": "Changez votre mot de passe.",
        "pseudo_label": "Pseudo",
        "save_button": "Enregistrer",
        "update_button": "Mettre à jour",
        "current_password": "Mot de passe actuel",
        "new_password": "Nouveau mot de passe",
        "confirm_new_password": "Confirmer",

        # Cinemas
        "cinemas_context_title": "Contexte du projet",
        "cinemas_context_body": "Vous êtes un Data Analyst freelance. Un cinéma en perte de vitesse situé dans la Creuse vous contacte. Il a décidé de passer le cap du digital en créant un site Internet taillé pour les locaux. Pour aller encore plus loin, il vous demande de créer un moteur de recommandations de films.\n\nPour l’instant, aucun client n’a renseigné ses préférences, vous êtes dans une situation de cold start.",
        "cinemas_construction_title": "Page en construction",
        "cinemas_construction_body": "Cette page affichera bientôt la programmation du cinéma (films à l’affiche) ainsi que les événements et animations.",
        "contact_title": "Contact",
        "contact_name_label": "Nom",
        "contact_message_label": "Message",
        "contact_send": "Envoyer",
        "contact_sent": "Merci ! Votre message a été enregistré (démo).",
        "contact_disclaimer": "Ce formulaire est en cours de construction et n’envoie pas encore d’email.",

        # Favorites/Recos
        "your_collection": "Votre collection",
        "your_collection_desc": "Retrouvez ici tous les films que vous aimez.",
        "no_favorites": "Vous n'avez pas encore de favoris. Ajoutez-en depuis l'accueil en cliquant sur le coeur !",
        "for_you": "Pour vous",
        "for_you_desc": "Sélection basée sur vos goûts.",
        "no_favorites_hint": "Pour commencer, ajoutez des films à vos favoris (bouton coeur).",
        "more_favorites_needed": "Ajoutez plus de favoris pour affiner nos suggestions.",
        "reco_backend_in_use": "Algorithme : KNN cosine (ML)",
        "reco_fallback_warning": "Mode fallback (ML indisponible) : {}",
        "reco_fallback_short": "Mode fallback : {}",
        "reco_install_hint": "Pour activer le modèle ML, installez les dépendances (ex: `pip install -r requirements.txt`).",
        "similar_movies_title": "Films similaires",
        "no_similar_movies": "Aucun film similaire trouvé.",
        "added_to_favs": "Ajouté aux favoris.",
        "removed_from_favs": "Retiré des favoris.",
        "fav_saved_mysql": "Sauvegardé sur MySQL.",
        "fav_saved_local": "Sauvegardé localement (MySQL indisponible).",
    },
    "en": {
        # General
        "app_title": "Pepite Production",
        "home_intro": "Discover movies, add favorites, and get personalized recommendations - a site created as part of a school project.",
        "home_title": "Home",
        "genre_title": "By Genre",
        "library_title": "My Library",
        "favorites_title": "My Favorites",
        "recos_title": "Recommendations",
        "settings_title": "Settings",
        "profile_title": "My Profile",
        "cinemas_title": "Our cinemas",
        "admin_title": "Admin",
        "search_submit": "Search",
        "search_page_title": "Search",
        "search_results_for": "Results for: {}",
        "search_hint": "Type a movie name then press Enter or Search.",
        "back_button": "Back",
        "admin_home_tab": "Home",
        "admin_filters_title": "User filters",
        "admin_age_filter": "Age",
        "admin_include_unknown": "Include unknown",
        "admin_gender_filter": "Gender",
        "admin_in_creuse_filter": "Creuse",
        "admin_cinema_filter": "Cinema (12 months)",
        "admin_all": "All",
        "admin_unknown": "Unknown",
        "admin_top_liked": "Most liked movies",
        "admin_top_liked_desc": "Ranking based on favorites (after filters).",
        "admin_selected_users": "Users",
        "admin_total_likes": "Likes (favorites)",
        "admin_unique_movies": "Unique movies",
        "admin_no_likes": "No favorites for this selection.",
        "admin_top_n": "Number of movies",
        "admin_python_tab": "Python dashboard",
        "admin_likes_by_genre": "Likes by genre",
        "admin_likes_by_language": "Likes by language",
        "admin_powerbi_note": "Note: the Power BI iframe can't be auto-filtered from Streamlit without using the Power BI API integration.",
        "admin_settings_tab": "Recommendation models",
        "admin_reco_model_label": "Recommendation model",
        "admin_reco_model_help": "Choose the ML model used across the app.",
        "admin_settings_saved": "Settings saved.",
        "admin_reco_backend_status": "Engine: {} — {}",
        "search_placeholder": "Search for a movie...",
        "search_no_result": "No results found.",
        "search_open": "Open",
        "search_clear": "Clear",
        "search_results": "Results",
        "search_choose": "Choose a movie...",

        # Sections
        "featured_section": "Featured Movies",
        "gems_section": "Our Selection",
        "niche_section": "Niche Picks",
        "top_n_genre": "Top {} in {}",
        "click_to_open": "Click a title to open movie details.",

        # Movie Card
        "genre_label": "Genre:",
        "rating_label": "Rating:",
        "director_label": "Director:",
        "actors_label": "Cast:",
        "language_label": "Language:",
        "duration_label": "Duration:",
        "minutes": "min",

        # Auth
        "login_tab": "Login",
        "signup_tab": "Sign Up",
        "email_label": "Email",
        "password_label": "Password",
        "password_confirm": "Confirm Password",
        "login_submit": "Log In",
        "signup_submit": "Create Account",
        "dob_label": "Date of birth (optional)",
        "gender_label": "Gender (optional)",
        "gender_male": "Male",
        "gender_female": "Female",
        "gender_other": "Other",
        "in_creuse_label": "Do you live in Creuse? (optional)",
        "cinema_12m_label": "Went to the cinema in the last 12 months? (optional)",
        "optional_placeholder": "Optional",
        "yes": "Yes",
        "no": "No",
        "logout_button": "Log Out",
        "logged_in_as": "Logged in as {}",
        "welcome_back": "Welcome back, {}!",
        "auth_required": "You must be logged in.",
        "auth_required_favs": "You must be logged in to access your favorites.",
        "auth_required_recos": "You must be logged in to see recommendations.",
        "auth_required_profile": "You must be logged in to access your profile.",
        "admin_access_denied": "Access reserved for administrators.",
        "invalid_credentials": "Invalid credentials",
        "passwords_mismatch": "Passwords do not match.",
        "account_created": "Account created. Welcome!",
        "mysql_fallback": "MySQL configured but pymysql not installed. Falling back to local storage.",
        "mysql_unavailable": "MySQL configured but unavailable. Falling back to local storage.",
        "disconnected": "Logged out",

        # Profile
        "profile_info_section": "Information",
        "profile_info_desc": "Edit your details.",
        "profile_security_section": "Security",
        "profile_security_desc": "Change your password.",
        "pseudo_label": "Username",
        "save_button": "Save",
        "update_button": "Update",
        "current_password": "Current Password",
        "new_password": "New Password",
        "confirm_new_password": "Confirm",

        # Cinemas
        "cinemas_context_title": "Project context",
        "cinemas_context_body": "You are a freelance Data Analyst. A struggling cinema located in Creuse contacts you. It has decided to go digital by creating a website tailored for locals. To go even further, it asks you to build a movie recommendation engine.\n\nFor now, no customer has provided preferences: you are in a cold start situation.",
        "cinemas_construction_title": "Page under construction",
        "cinemas_construction_body": "This page will soon show the cinema’s schedule (now showing) as well as events and special screenings.",
        "contact_title": "Contact",
        "contact_name_label": "Name",
        "contact_message_label": "Message",
        "contact_send": "Send",
        "contact_sent": "Thanks! Your message has been saved (demo).",
        "contact_disclaimer": "This form is under construction and does not send emails yet.",

        # Favorites/Recos
        "your_collection": "Your Collection",
        "your_collection_desc": "Find all the movies you love here.",
        "no_favorites": "You have no favorites yet. Add some from the homepage by clicking the heart!",
        "for_you": "For You",
        "for_you_desc": "Selection based on your tastes.",
        "no_favorites_hint": "To start, add movies to your favorites (heart button).",
        "more_favorites_needed": "Add more favorites to refine our suggestions.",
        "reco_backend_in_use": "Algorithm: KNN cosine (ML)",
        "reco_fallback_warning": "Fallback mode (ML unavailable): {}",
        "reco_fallback_short": "Fallback mode: {}",
        "reco_install_hint": "To enable the ML model, install dependencies (e.g. `pip install -r requirements.txt`).",
        "similar_movies_title": "Similar movies",
        "no_similar_movies": "No similar movies found.",
        "added_to_favs": "Added to favorites.",
        "removed_from_favs": "Removed from favorites.",
        "fav_saved_mysql": "Saved to MySQL.",
        "fav_saved_local": "Saved locally (MySQL unavailable).",
    }
}


def get_current_language():
    if "language" not in st.session_state:
        st.session_state.language = "fr"
    return st.session_state.language


def set_language(lang):
    st.session_state.language = lang


def get_text(key, *args):
    lang = get_current_language()
    text = TRANSLATIONS.get(lang, TRANSLATIONS["fr"]).get(key, key)
    if args:
        return text.format(*args)
    return text


# Alias for brevity
t = get_text


def render_sidebar_flags():
    # CSS for Sidebar Flags (smaller than before, ~40px)

    # Layout - simpler 2 columns
    c1, c2 = st.sidebar.columns(2)
    with c1:
        if st.button("🇫🇷", key="side_lang_fr", use_container_width=True):
            set_language("fr")
            st.rerun()
    with c2:
        if st.button("🇺🇸", key="side_lang_en", use_container_width=True):
            set_language("en")
            st.rerun()
