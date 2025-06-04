import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def get_google_services():
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

        # 1. Créer le document
        doc = docs_service.documents().create(body={"title": nom_fichier}).execute()
        doc_id = doc.get("documentId")

        # 2. Préparer les requêtes dans l’ordre
        requests = []

        # Ajouter le titre du document (centré, mais ici simplement en haut)
        requests.append({
            "insertText": {
                "location": {"index": 1},
                "text": f"{nom_fichier}\n\n"
            }
        })

        # Ajouter les infos générales
        for key, value in infos_generales.items():
            ligne = f"{key} : {value.strip()}\n"
            requests.append({
                "insertText": {
                    "location": {"index": 1},
                    "text": ligne
                }
            })

        # Ajouter une ligne vide de séparation
        requests.append({
            "insertText": {
                "location": {"index": 1},
                "text": "\n"
            }
        })

        # Ajouter le contenu du résumé ligne par ligne
        for ligne in reversed(resume_text.split("\n")):
            if ligne.strip():
                requests.append({
                    "insertText": {
                        "location": {"index": 1},
                        "text": f"{ligne.strip()}\n"
                    }
                })

        # 3. Exécuter les requêtes (ordre inversé car index 1)
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": list(reversed(requests))}
        ).execute()

        # 4. Déplacer dans le bon dossier Drive
        folder_id = st.secrets["gdrive"]["gdrive_folder_id"]
        file = drive_service.files().get(fileId=doc_id, fields='parents').execute()
        previous_parents = ",".join(file.get('parents', []))

        drive_service.files().update(
            fileId=doc_id,
            addParents=folder_id,
            removeParents=previous_parents,
            fields='id, parents'
        ).execute()

        return f"https://docs.google.com/document/d/{doc_id}/edit"

    except HttpError as error:
        st.error(f"Une erreur s'est produite lors de l'export : {error}")
        return ""
    except Exception as e:
        st.error(f"Erreur inattendue : {e}")
        return ""
