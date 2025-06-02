import streamlit as st
from checklist_personnalisee import app_generer_liste_verification
from export_to_drive import export_resume_to_google_doc

# Appel de la checklist
app_generer_liste_verification()

# Bouton d'export après affichage du résumé
if "resultats_checklist" in st.session_state and st.button("Exporter le Résumé vers Google Docs"):
    resume_lines = []
    for item, data in st.session_state.resultats_checklist.items():
        resume_lines.append(f"{item} : {', '.join(k for k, v in data.items() if v is True)}")
    resume_text = "\n".join(resume_lines)

    nom_fichier = st.text_input("Nom du fichier (sans extension) :", value="")
    if nom_fichier:
        lien_doc = export_resume_to_google_doc(resume_text, nom_fichier)
        if lien_doc:
            st.success(f"Document exporté : [Ouvrir dans Google Docs]({lien_doc})")
