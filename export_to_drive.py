import streamlit as st
import datetime
import pytz
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def get_drive_service():
    """Initialise le service Google Drive avec les identifiants du compte de service."""
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gdrive"]["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/documents"]
    )
    return build("drive", "v3", credentials=credentials), build("docs", "v1", credentials=credentials)

def generate_doc_title(base_name: str) -> str:
    """Ajoute l'horodatage belge au nom du fichier."""
    now = datetime.datetime.now(pytz.timezone("Europe/Brussels"))
    return f"{base_name} - {now.strftime('%Y-%m-%d %Hh%M')}"

def export_resume_to_google_doc(resume_text: str, doc_name: str):
    """Crée un document Google Docs avec le contenu du résumé et le stocke dans le dossier Drive spécifié."""
    drive_service, docs_service = get_drive_service()
    folder_id = st.secrets["gdrive"]["gdrive_folder_id"]
    title = generate_doc_title(doc_name)

    try:
        # Étape 1 : créer le document
        doc_metadata = {"title": title}
        doc = docs_service.documents().create(body=doc_metadata).execute()
        document_id = doc.get("documentId")

        # Étape 2 : insérer le texte dans le document
        requests = [{"insertText": {"location": {"index": 1}, "text": resume_text}}]
        docs_service.documents().batchUpdate(documentId=document_id, body={"requests": requests}).execute()

        # Étape 3 : déplacer le fichier dans le bon dossier
        drive_service.files().update(
            fileId=document_id,
            addParents=folder_id,
            removeParents="root",
            fields="id, parents"
        ).execute()

        return f"https://docs.google.com/document/d/{document_id}/edit"

    except HttpError as error:
        st.error(f"Une erreur est survenue : {error}")
        return None
