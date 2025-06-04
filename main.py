import streamlit as st
from checklist_personnalisee import app_generer_liste_verification
from export_to_drive_function import export_resume_to_google_doc

st.set_page_config(layout="centered")
st.title("Générateur de Liste de Vérification pour Activité Scolaire")

# Initialisation sécurisée de la session_state
if "checklist_items" not in st.session_state:
    st.session_state["checklist_items"] = [
        "F1",
        "Demande d'activité scolaire",
        "Demande de résa TRAIN",
        "CEC 5",
        "CEC6bis",
        "Accord CFWB",
        "Office des étrangers : des étudiants de nationalité non-européenne ?",
        "Assurance provinciale"
    ]

if "infos_generales" not in st.session_state:
    st.session_state["infos_generales"] = {
        "Intitulé du voyage": "",
        "Code régie": "",
        "Professeur-organisateur": ""
    }

# ➕ Ajouter un nouvel item
st.markdown("---")
st.subheader("Checklist Personnalisée")

new_item = st.text_input("Ajouter un nouvel item à la checklist :", "")
if st.button("Ajouter à la checklist") and new_item.strip():
    if new_item not in st.session_state["checklist_items"]:
        st.session_state["checklist_items"].append(new_item.strip())
    else:
        st.warning("Cet item existe déjà.")

# ➖ Supprimer un ou plusieurs items
items_to_remove = st.multiselect("Supprimer des items de la checklist :", st.session_state["checklist_items"])
if st.button("Supprimer les items sélectionnés"):
    for item in items_to_remove:
        st.session_state["checklist_items"].remove(item)
        if item in st.session_state.get("resultats_checklist", {}):
            del st.session_state["resultats_checklist"][item]
    st.success("Items supprimés.")

# 1. Informations générales
st.markdown("---")
st.subheader("1. Informations Générales du Voyage")

infos = st.session_state["infos_generales"]
infos["Intitulé du voyage"] = st.text_input("Intitulé du voyage", value=infos["Intitulé du voyage"], key="intitule_voyage_input")
infos["Code régie"] = st.text_input("Code régie", value=infos["Code régie"], key="code_regie_input")
infos["Professeur-organisateur"] = st.text_input("Professeur-organisateur", value=infos["Professeur-organisateur"], key="prof_org_input")

# 2. Checklist dynamique
st.markdown("---")
app_generer_liste_verification(infos, st.session_state["checklist_items"])
# Génération automatique du résumé après la checklist
resume_lines = []
resume_lines.append("### Informations Générales")
for key, val in infos.items():
    resume_lines.append(f"- **{key}** : {val if val else 'Non renseigné'}")

resume_lines.append("\n### Statut de la Checklist")
for item in st.session_state["checklist_items"]:
    etat = st.session_state.get("resultats_checklist", {}).get(item, {})
    statut = "N/A" if etat.get("n_a") else "Oui" if etat.get("oui") else "Non" if etat.get("non") else "Non renseigné"
    resume_lines.append(f"- {item} : {statut}")
    if "dates" in etat:
        for label, date in etat["dates"].items():
            resume_lines.append(f"   - {label} : {date}")

# Stocker le résumé dans la session
st.session_state["resume_checklist"] = "\n".join(resume_lines)



# 3. Résumé + export
if "resume_checklist" in st.session_state:
    resume_text = st.session_state["resume_checklist"]
    st.markdown("---")
    st.subheader("Résumé de la Liste de Vérification")
    st.text_area("Contenu du résumé :", resume_text, height=300)

    from datetime import datetime
import pytz

nom_fichier_base = st.text_input("Nom du fichier (base) à exporter :", value="", key="nom_fichier_input")

if nom_fichier_base and st.button("Exporter vers Google Docs"):
    # Ajout de l'horodatage belge
    tz = pytz.timezone("Europe/Brussels")
    horodatage = datetime.now(tz).strftime("%Y-%m-%d_%Hh%M")
    nom_fichier_complet = f"{nom_fichier_base}_{horodatage}"

    lien_doc = export_resume_to_google_doc(resume_text, nom_fichier_complet, infos)
    if lien_doc:
        st.success(f"✅ Document exporté : [Ouvrir dans Google Docs]({lien_doc})")

