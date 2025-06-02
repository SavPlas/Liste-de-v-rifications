import streamlit as st
from checklist_personnalisee import app_generer_liste_verification
from export_to_drive import export_resume_to_google_doc

# Appel de la checklist
app_generer_liste_verification()

# Bouton d'export après affichage du résumé
if "resultats_checklist" in st.session_state:
    resume_lines = []
    for item, data in st.session_state.resultats_checklist.items():
        if not data:
            resume_lines.append(f"{item} : n/a")
        else:
            actifs = [k for k, v in data.items() if v]
            if actifs:
                resume_lines.append(f"{item} : {', '.join(actifs)}")
            else:
                resume_lines.append(f"{item} : n/a")
    resume_text = "\n".join(resume_lines)


    nom_fichier = st.text_input("Nom du fichier (sans extension) :", value="Résumé Voyage")
    if nom_fichier:
        lien_doc = export_resume_to_google_doc(resume_text, nom_fichier)
        if lien_doc:
            st.success(f"Document exporté : [Ouvrir dans Google Docs]({lien_doc})")
