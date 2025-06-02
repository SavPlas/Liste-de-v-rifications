import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_google_services():
    # Authentification via secrets
    credentials_info = st.secrets["gdrive"]["gcp_service_account"]
    credentials = service_account.Credentials.from_service_account_info(credentials_info, scopes=[
        "https://www.googleapis.com/auth/documents",
        "https://www.googleapis.com/auth/drive"
    ])

    docs_service = build("docs", "v1", credentials=credentials)
    drive_service = build("drive", "v3", credentials=credentials)
    return docs_service, drive_service


def export_resume_to_google_doc(resume_text: str, nom_fichier: str, infos_generales: dict) -> str:
    try:
        docs_service, drive_service = get_google_services()

        # Créer un nouveau document
        doc_title = nom_fichier
        doc = docs_service.documents().create(body={"title": doc_title}).execute()
        doc_id = doc.get("documentId")

        # Créer le contenu du document
        contenu = []
        contenu.append({"insertText": {"location": {"index": 1}, "text": f"{doc_title}\n\n"}})

        for cle, valeur in infos_generales.items():
            contenu.append({"insertText": {"location": {"index": 1}, "text": f"{cle} : {valeur}\n"}})
        contenu.append({"insertText": {"location": {"index": 1}, "text": "\n"}})

        for ligne in resume_text.split("\n"):
            contenu.append({"insertText": {"location": {"index": 1}, "text": f"- {ligne}\n"}})

        # Appliquer les mises à jour au document
        docs_service.documents().batchUpdate(documentId=doc_id, body={"requests": list(reversed(contenu))}).execute()

        # Déplacer le document dans le dossier spécifié
        folder_id = st.secrets["gdrive"]["gdrive_folder_id"]
        file = drive_service.files().get(fileId=doc_id, fields='parents').execute()
        previous_parents = ",".join(file.get('parents'))
        drive_service.files().update(
            fileId=doc_id,
            addParents=folder_id,
            removeParents=previous_parents,
            fields='id, parents'
        ).execute()

        # Retourner le lien vers le document créé
        return f"https://docs.google.com/document/d/{doc_id}/edit"

    except HttpError as error:
        st.error(f"Une erreur s'est produite lors de l'export : {error}")
        return ""
    except Exception as e:
        st.error(f"Erreur inattendue : {e}")
        return ""
