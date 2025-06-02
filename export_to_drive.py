import streamlit as st

# Cette commande doit être en tout premier
st.set_page_config(layout="centered")

from checklist_personnalisee import app_generer_liste_verification
from export_to_drive import export_resume_to_google_doc

# Informations générales (modifiable par l'utilisateur)
infos_generales = {
    "Intitulé du voyage": st.text_input("Intitulé du voyage", "Savery"),
    "Code régie": st.text_input("Code régie", "6P"),
    "Professeur-organisateur": st.text_input("Professeur-organisateur", "CUISAL")
}

# Appel de la checklist
app_generer_liste_verification()

# Interface pour ajouter dynamiquement des items
st.markdown("---")
st.subheader("Ajouter un nouvel item à la checklist")

if "items_additionnels" not in st.session_state:
    st.session_state["items_additionnels"] = []

nouvel_item = st.text_input("Nom du nouvel item")
details_item = st.text_input("Détails de l'item (ex: Oui, Envoyé Régie (le 19-06-2025))")

if st.button("Ajouter l'item") and nouvel_item and details_item:
    st.session_state.items_additionnels.append((nouvel_item, details_item))
    st.success(f"Item '{nouvel_item}' ajouté !")

# Affichage du résumé et export
if "resultats_checklist" in st.session_state:
    resume_lines = []
    for item, data in st.session_state.resultats_checklist.items():
        if not data:
            resume_lines.append(f"{item} : N/A")
        else:
            actifs = [k for k, v in data.items() if v]
            if actifs:
                resume_lines.append(f"{item} : {', '.join(actifs)}")
            else:
                resume_lines.append(f"{item} : N/A")

    # Ajout des items dynamiques
    for item_nom, item_details in st.session_state.items_additionnels:
        resume_lines.append(f"{item_nom} : {item_details}")

    resume_text = "\n".join(resume_lines)

    st.markdown("---")
    st.subheader("Résumé généré")
    st.text_area("Contenu du résumé :", resume_text, height=300)

    nom_fichier = st.text_input("Nom du fichier à exporter (sans extension) :", value="Résumé Voyage")
    if nom_fichier and st.button("Exporter vers Google Docs"):
        lien_doc = export_resume_to_google_doc(resume_text, nom_fichier, infos_generales)
        if lien_doc:
            st.success(f"Document exporté : [Ouvrir dans Google Docs]({lien_doc})")
