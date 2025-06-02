import streamlit as st
from checklist_personnalisee import app_generer_liste_verification
from export_to_drive import export_resume_to_google_doc

# Génère la checklist
app_generer_liste_verification()

# Vérifie s'il y a un résumé à exporter
if "resultats_checklist" in st.session_state:

    # Affiche le résumé sous forme de texte
    resume_lines = []
    for item, data in st.session_state.resultats_checklist.items():
        ligne = f"- **{item}** : {', '.join(k for k, v in data.items() if v)}"
        resume_lines.append(ligne)
    
    resume_text = "\n".join(resume_lines)
    st.markdown("### Résumé à exporter")
    st.markdown(resume_text)

    # Champ pour nommer le fichier
    nom_fichier = st.text_input("📝 Nom du fichier Google Docs :", value="Résumé Voyage")

    # Bouton pour exporter une fois le nom défini
    if st.button("📤 Exporter vers Google Docs") and nom_fichier:
        lien_doc = export_resume_to_google_doc(resume_text, nom_fichier)
        if lien_doc:
            st.success("✅ Document exporté avec succès !")
            st.markdown(f"[🔗 Ouvrir dans Google Docs]({lien_doc})")
