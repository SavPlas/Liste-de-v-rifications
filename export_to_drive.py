import streamlit as st
import datetime
import pytz
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def get_drive_service():
    """Initialise les services Google Drive et Docs avec les identifiants du compte de service."""
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gdrive"]["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/documents"
        ]
    )
    return build("drive", "v3", credentials=credentials), build("docs", "v1", credentials=credentials)

def generate_doc_title(base_name: str) -> str:
    """Ajoute un horodatage belge au nom du fichier."""
    now = datetime.datetime.now(pytz.timezone("Europe/Brussels"))
    return f"{base_name} - {now.strftime('%Y-%m-%d %Hh%M')}"

def formater_resume_en_google_doc_requests(intitule: str, code_regie: str, prof: str, resume_lignes: list[str]) -> list[dict]:
    """Génère les requêtes pour formater le document avec un titre, infos générales, et puces."""
    contenu = [
        {"insertText": {"location": {"index": 1}, "text": f"Voyage : {intitule}\n"}},
        {"insertText": {"location": {"index": 1}, "text": f"Code régie : {code_regie}\n"}},
        {"insertText": {"location": {"index": 1}, "text": f"Professeur-organisateur : {prof}\n\n"}},
    ]

    for ligne in reversed(resume_lignes):  # on insère en sens inverse pour que les lignes soient dans le bon ordre
        contenu.append({"insertText": {"location": {"index": 1}, "text": ligne + "\n"}})

    # Ajouter des puces aux lignes du résumé
    contenu.append({
        "createParagraphBullets": {
            "range": {
                "startIndex": len(f"Voyage : {intitule}\nCode régie : {code_regie}\nProfesseur-organisateur : {prof}\n\n"),
                "endIndex": len(f"Voyage : {intitule}\nCode régie : {code_regie}\nProfesseur-organisateur : {prof}\n\n" + "\n".join(resume_lignes)) + 1
            },
            "bulletPreset": "BULLET_DISC"
        }
    })

    return contenu

def export_resume_to_google_doc(resume_text: str, doc_name: str, infos_generales: dict = None):
    """Crée un document Google Docs structuré avec les données et l'enregistre dans un dossier spécifique."""
    drive_service, docs_service = get_drive_service()
    folder_id = st.secrets["gdrive"]["gdrive_folder_id"]
    title = generate_doc_title(doc_name)

    try:
        # 1. Création du document
        doc_metadata = {"title": title}
        doc = docs_service.documents().create(body=doc_metadata).execute()
        document_id = doc.get("documentId")

        # 2. Formatage du contenu
        resume_lignes = resume_text.split("\n")
        intitule = infos_generales.get("intitule", "À compléter")
        code_regie = infos_generales.get("code_regie", "-")
        prof = infos_generales.get("prof", "-")

        requests = formater_resume_en_google_doc_requests(intitule, code_regie, prof, resume_lignes)
        docs_service.documents().batchUpdate(documentId=document_id, body={"requests": requests}).execute()

        # 3. Déplacement dans le dossier Drive cible
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
