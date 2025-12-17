import msal
import requests
import streamlit as st


def get_access_token(client_id, client_secret, tenant_id):
    """Authenticates with Azure AD using Service Principal to get an Access Token."""
    authority_url = f"https://login.microsoftonline.com/{tenant_id}"
    scope = ["https://analysis.windows.net/powerbi/api/.default"]

    app = msal.ConfidentialClientApplication(
        client_id, authority=authority_url, client_credential=client_secret
    )
    result = app.acquire_token_for_client(scopes=scope)

    if "access_token" in result:
        return result["access_token"]

    # Log error if possible
    return None


def get_powerbi_embed_info():
    """
    Retrieves the Embed Token, Embed URL, and Report ID using the configured secrets.
    Returns:
        tuple: (embed_config_dict, error_message)
    """
    # 1. Load Secrets
    # Support both nested [powerbi] section or flat keys
    secrets = st.secrets.get("powerbi", st.secrets)

    client_id = secrets.get("CLIENT_ID")
    client_secret = secrets.get("CLIENT_SECRET")
    tenant_id = secrets.get("TENANT_ID")
    workspace_id = secrets.get("WORKSPACE_ID")
    report_id = secrets.get("REPORT_ID")

    if not all([client_id, client_secret, tenant_id, workspace_id, report_id]):
        return None, "Configuration incomplète (Secrets manquants)."

    # 2. Get Azure AD Access Token
    ad_token = get_access_token(client_id, client_secret, tenant_id)
    if not ad_token:
        return None, "Echec authentification Azure AD."

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ad_token}"
    }

    # 3. Get Report Details (to get the Embed URL)
    report_url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}"
    resp = requests.get(report_url, headers=headers)

    if resp.status_code != 200:
        return None, f"Erreur API PowerBI (Get Report): {resp.status_code}"

    report_data = resp.json()
    embed_url = report_data.get("embedUrl")
    if not embed_url:
        return None, "Embed URL introuvable."

    # 4. Generate Embed Token (Safe for frontend)
    token_url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}/GenerateToken"
    body = {"accessLevel": "View"}

    token_resp = requests.post(token_url, headers=headers, json=body)

    if token_resp.status_code != 200:
        return None, f"Erreur API PowerBI (Generate Token): {token_resp.status_code}"

    token_data = token_resp.json()
    embed_token = token_data.get("token")

    return {
        "type": "report",
        "tokenType": 1,  # Embed Token
        "accessToken": embed_token,
        "embedUrl": embed_url,
        "id": report_id,
        "settings": {
            "filterPaneEnabled": False,
            "navContentPaneEnabled": True
        }
    }, None
