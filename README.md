# Wildflix (Streamlit)

## Lancer l'app

1. Installer les dépendances : `pip install -r requirements.txt`
2. Démarrer : `streamlit run Home.py`

## Configuration (prod)

- **Power BI (Admin)** : dans `.streamlit/secrets.toml` :
  - `[powerbi] SIMPLE_URL="https://app.powerbi.com/reportEmbed?..."`
  - ou via variable d'env `WILDFLIX_POWERBI_SIMPLE_URL`
- **Signature des tokens** : définir `SECRET_KEY` (secrets ou env `WILDFLIX_SECRET_KEY`)
- **MySQL (optionnel)** : secrets `[mysql] ...` ou env `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`

## Admin (backend local)

- Par défaut, aucun compte n'est pré-créé. Pour créer/forcer un admin :
  - `python scripts/ensure_admin.py --email admin@wildflix.com --password "..." --pseudo "Admin"`
- Pour générer des comptes de démo au 1er lancement (non recommandé en prod) :
  - `WILDFLIX_SEED_DEMO_USERS=1`

## Migration local -> MySQL

1. Vérifie que `data/users.json` contient bien tes comptes (sur ton PC).
2. Exporte les variables MySQL Railway en env (`MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`) ou mets-les dans `.streamlit/secrets.toml`.
3. Lance : `python scripts/migrate_local_users_to_mysql.py`
