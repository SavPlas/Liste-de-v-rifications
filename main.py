import streamlit as st
st.set_page_config(layout="centered")

from checklist_personnalisee import app_generer_liste_verification
from export_to_drive_function import export_resume_to_google_doc  # ✅ correction ici

# Infos générales
infos_generales = {
    "Intitulé du voyage": st.text_input("Intitulé du voyage", "Savery"),
    "Code régie": st.text_input("Code régie", "6P"),
    "Professeur-organisateur": st.text_input("Professeur-organisateur", "CUISAL")
}

# Appel de la checklist
app_generer_liste_verification()

# Affichage et export
if "resultats_checklist" in st.session_state:
    resume_lines = []
    for item, data in st.session_state.resultats_checklist.items():
        if not data:
            resume_lines.append(f"{item} : N/A")
        else:
            actifs = [k for k, v in data.items() if v and k != "dates"]
            dates = data.get("dates", {})
            lignes_item = []
            if not actifs:
                lignes_item.append("N/A")
            else:
                for statut in actifs:
                    ligne = statut.replace("_", " ").capitalize()
                    if statut in dates:
                        ligne += f" (le {dates[statut]})"
                    lignes_item.append(ligne)
            resume_lines.append(f"{item} : {', '.join(lignes_item)}")

    resume_text = "\n".join(resume_lines)

    nom_fichier = st.text_input("Nom du fichier (sans extension) :", value="")
    if nom_fichier and st.button("Exporter vers Google Docs"):
        lien_doc = export_resume_to_google_doc(resume_text, nom_fichier, infos_generales)  # ✅ infos_generales ajoutées
        if lien_doc:
            st.success(f"Document exporté : [Ouvrir dans Google Docs]({lien_doc})")
