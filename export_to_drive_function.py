from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import streamlit as st

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

        # 2. Nettoyage et traitement du texte
        lines = resume_text.split("\n")

        # Isoler la partie "Statut de la Checklist"
        try:
            index_statut = lines.index("### Statut de la Checklist")
            lines_infos = lines[:index_statut + 1]
            lines_checklist = lines[index_statut + 1:]
        except ValueError:
            lines_infos = lines
            lines_checklist = []

        # Inverser les lignes principales de checklist mais garder l’indentation
        final_lines = lines_infos[:]
        buffer_item = []

        for line in lines_checklist:
            if line.startswith("   - "):
                buffer_item.append(line)
            else:
                if buffer_item:
                    # On ajoute les sous-lignes après l’item précédent
                    final_lines.extend(reversed(buffer_item))
                    buffer_item = []
                final_lines.append(line)
        if buffer_item:
            final_lines.extend(reversed(buffer_item))  # cas du dernier item

        # Inverser l’ordre global des lignes checklist
        checklist_items_reversed = []
        buffer = []

        for line in final_lines[index_statut + 1:]:
            if not line.startswith("   - "):
                if buffer:
                    checklist_items_reversed.insert(0, buffer)
                    buffer = []
                buffer = [line]
            else:
                buffer.append(line)
        if buffer:
            checklist_items_reversed.insert(0, buffer)

        # 3. Construire les requêtes Google Docs
        requests = []

        # Titre du document
        requests.append({
            "insertText": {
                "location": {"index": 1},
                "text": f"{nom_fichier}\n\n"
            }
        })

        # Infos générales (brutes, ordonnées)
        for key, val in infos_generales.items():
            requests.append({
                "insertText": {
                    "location": {"index": 1},
                    "text": f"{key} : {val.strip()}\n"
                }
            })

        requests.append({
            "insertText": {
                "location": {"index": 1},
                "text": "\n"
            }
        })

        # Statut de la Checklist
        requests.append({
            "insertText": {
                "location": {"index": 1},
                "text": "### Statut de la Checklist\n"
            }
        })

        # Ajouter chaque item + indentation des sous-lignes
        for bloc in checklist_items_reversed:
            for line in bloc:
                text = f"{line.strip()}\n" if line.startswith("   - ") else f"{line.strip()}\n"
                requests.append({
                    "insertText": {
                        "location": {"index": 1},
                        "text": text
                    }
                })

        # 4. Exécuter les requêtes
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": list(reversed(requests))}
        ).execute()

        # 5. Déplacer dans le bon dossier
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
        st.error(f"Erreur API Google : {error}")
        return ""
    except Exception as e:
        st.error(f"Erreur inattendue : {e}")
        return ""
