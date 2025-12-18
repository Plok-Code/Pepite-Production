import streamlit as st

from utils.data_loader import load_movies
from utils.header import render_global_search
from utils.i18n import t
from utils.layout import common_page_setup
from utils.ui_components import section_title


def main():
    common_page_setup(page_title=t("cinemas_title"))

    df = load_movies()
    render_global_search(df, source_page="pages/5_Nos_salles_de_cinema.py")

    st.title(t("cinemas_title"))

    section_title("À quoi sert ce site ?")
    st.write(
        "Pepite Production est un site de recommandation personnalisée de films : "
        "il permet de découvrir des films, de créer une liste de favoris et d’obtenir des suggestions "
        "adaptées à vos goûts."
    )

    st.markdown("---")
    section_title("Ce que contient le site")
    st.markdown(
        """
        - **Accueil** : sélections éditoriales (Vedettes, Pépites, Niche)
        - **Par genre** : exploration des films par catégories
        - **Mes favoris** : tous les films que vous aimez
        - **Recommandations** : suggestions basées sur vos favoris
        - **Profil** : changer vos informations personnelles, vos identifiants et votre mot de passe
        - **Admin** (accessible via compte admin) : dashboards / KPIs + choix du modèle ML
        - **Recherche** (barre en haut de page) : recherche de films avec tolérance aux fautes
        - **Fiche film** (lorsque vous cliquez sur un film) : détails, ajout aux favoris, films similaires (recommandation ML + films du même genre)
        """
    )

    st.markdown("---")
    section_title("Modèles de recommandation (Admin)")
    st.write(
        "Dans **Admin > Modèles de recommandation**, l’administrateur peut choisir le modèle ML "
        "appliqué partout : **KNN cosine**, **KNN euclidean** ou **KNN manhattan**."
    )

    st.markdown("---")
    section_title("Gestion du cold start")
    st.write(
        "Au départ, sans favoris, il est difficile de personnaliser les recommandations. "
        "Le site propose donc des sélections sur l’accueil, la navigation par genre et la recherche. "
        "Dès que vous ajoutez des favoris, le moteur peut générer des recommandations."
    )
    st.markdown(
        """
        - **Films vedettes** : films bien notés et populaires
        - **Pépites** : films bien notés mais moins populaires
        - **Niche** : films très peu vus / très peu populaires mais bien notés
        """
    )

    st.markdown("---")
    section_title("Authentification & données")
    st.write(
        "La création de compte et la connexion se font via **email** et **mot de passe**. "
        "Vos favoris et vos informations de profil (optionnelles) sont utilisés pour personnaliser "
        "l’expérience et les dashboards côté Admin."
    )
    st.info(
        "Les données utilisateurs sont traitées de manière **confidentielle** : elles ne sont pas revendues "
        "et sont utilisées uniquement dans le cadre de l’application (recommandations et analyses). "
        "Les tableaux de bord côté Admin reposent sur des **statistiques agrégées** (anonymisées)."
    )

    st.markdown("---")
    section_title("Code source")
    st.markdown(
        """
        - Code source du projet : https://github.com/Plok-Code/Pepite-Production
        - Page projet : https://patrick-wampe.github.io/Synapse-Learners/wildprojet2wildflix.html
        """
    )

    st.markdown("---")
    section_title("Équipe de production")
    st.markdown(
        """
        - Idris NAULLEAU-AURIAL — https://www.linkedin.com/in/idris-naulleau-aurial-9278b711b/
        - Amélie TRAN — https://www.linkedin.com/in/am%C3%A9lie-tran-981325a5/
        - Eric MONGREVILLE — https://www.linkedin.com/in/eric-mongreville-a1a3a438a/
        - Yannis GRIS
        """
    )

    st.markdown("---")
    section_title("Contexte de ce projet")
    st.caption("Ce site a été réalisé dans le cadre d'un projet scolaire.")
    with st.expander("Voir le brief du projet"):
        st.markdown(
            """
            ## Introduction

            « Netflix est un service de diffusion en streaming qui permet à ses membres de regarder une grande variété de séries TV, films, documentaires, etc. sur des milliers d'appareils connectés à Internet. »

            Créé en 1998, Netflix pèse aujourd’hui plus de 20 milliards de dollars de chiffre d'affaires et consomme 12,6% de la bande passante Internet mondiale.

            Lorsqu’on accède au service Netflix, le système de recommandations aide l’utilisateur à trouver aussi facilement que possible les séries TV ou films qu’il pourrait apprécier, grâce à un système de recommandation. Netflix calcule ainsi la probabilité que l’utilisateur regarde un titre donné du catalogue de Netflix, et peut ainsi optimiser ses partenariats ou plus globalement sa stratégie marketing. Netflix est l'archétype de la société data-driven.

            Votre client n’est pas Netflix, mais il a de grandes ambitions !

            ## Objectif

            Vous êtes un Data Analyst freelance. Un cinéma en perte de vitesse situé dans la **Creuse** vous contacte. Il a décidé de passer le cap du digital en créant un site Internet taillé pour les locaux.

            Pour aller encore plus loin, il vous demande de créer un **moteur de recommandations de films**.

            Pour l’instant, aucun client n’a renseigné ses préférences : vous êtes dans une situation de **cold start**.

            Mais heureusement, le client vous donne une base de données de films basée sur la plateforme **IMDb**.

            ### Le client souhaite
            - Une application web avec **Streamlit** : l’utilisateur pourra indiquer un film et obtenir **5 recommandations**.
            - Un tableau de bord **Power BI** et un dashboard **Python** avec des filtres, pour analyser les données et définir des **KPIs** pertinents.

            ### BONUS (idées de fonctionnalités)
            - Compléter le jeu de données avec **OMDb API** (pochettes, infos supplémentaires).
            - Page de connexion (comptes **admin** et **client**), création de compte et modification de mot de passe.
            - Affichage des pochettes et informations sur les films.
            - Traduction FR/EN de l’application.
            - Page de paramétrage (filtres et réglages avancés).
            - Possibilité de choisir plusieurs modèles de recommandation.

            ### Choix du dataset
            Nous avons choisi **IMDb 5000 Movie Dataset - ZIP** : plus simple à gérer (moins de jointures), mais plus complexe à nettoyer. Cela nous a permis de travailler davantage le **nettoyage**, les **automatisations**, ainsi que l’enrichissement via **requêtes API** et la partie **prédiction/recommandation**.

            ### Lien projet
            https://patrick-wampe.github.io/Synapse-Learners/wildprojet2wildflix.html
            """
        )


if __name__ == "__main__":
    main()
