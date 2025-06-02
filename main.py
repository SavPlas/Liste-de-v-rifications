import streamlit as st
from checklist_personnalisee import app_generer_liste_verification
from export_to_drive import export_resume_to_google_doc

st.set_page_config(layout="centered")

# Zone de saisie : Infos générales (modifiables)
st.title("Liste de Vérification - Voyage scolaire")

infos_generales = {
    "Intitulé du voyage": st.text_input("Intitulé du voyage", value=""),
    "Code régie": st.text_input("Code régie", value=""),
    "Professeur-organisateur": st.text_input("Professeur-organisateur", value="")
}

# 1. Génération de la checklist (interactive)
app_generer_liste_verification()

# 2. Génération du résumé et export
if "resultats_checklist" in st.session_state:
    resume_lines = []

    # Ajouter en haut les infos générales
    resume_lines.append(f"Intitulé du voyage : {infos_generales['Intitulé du voyage']}")
    resume_lines.append(f"Code régie : {infos_generales['Code régie']}")
    resume_lines.append(f"Professeur-organisateur : {infos_generales['Professeur-organisateur']}")
    resume_lines.append("")  # Ligne vide

    # Puis, les items de la checklist
    for item, data in st.session_state.resultats_checklist.items():
        statuts_affichage_liste = []

        # Logique spéciale Office des Étrangers
        if item == "Office des étrangers : des étudiants de nationalité non-européenne ?":
            if data["oui"]:
                statuts_affichage_liste.append("Oui (étudiants non-européens)")
                if data["doc_envoye_cfwb"]:
                    date_str = data["dates"].get("Document envoyé à la CFWB", "date non saisie")
                    statuts_affichage_liste.append(f"Document envoyé à la CFWB (le {date_str})")
                if data["document_a_completer"]:
                    statuts_affichage_liste.append("Document encore à compléter")
            elif data["non"]:
                statuts_affichage_liste.append("Non (aucun étudiant non-européen)")
                statuts_affichage_liste.append("(Aucune action requise)")
            else:
                statuts_affichage_liste.append("Statut indéfini")

        elif item == "Assurance provinciale":
            if data["n_a"]:
                statuts_affichage_liste.append("N/A")
            elif data["oui"]:
                statuts_affichage_liste.append("Oui")
                if data["doc_envoye_assu"]:
                    date_str = data["dates"].get("Document envoyé au service assurances", "date non saisie")
                    statuts_affichage_liste.append(f"Document envoyé au service assurances (le {date_str})")
                if data["doc_a_envoyer"]:
                    statuts_affichage_liste.append("Document encore à envoyer")
            elif data["non"]:
                statuts_affichage_liste.append("Non")
            else:
                statuts_affichage_liste.append("Statut indéfini")

        else:
            if data["n_a"]:
                statuts_affichage_liste.append("N/A")
            elif data["oui"]:
                statuts_affichage_liste.append("Oui")
                if data["signe_lpeth"]:
                    date_str = data["dates"].get("Signé direction LPETH", "date non saisie")
                    statuts_affichage_liste.append(f"Signé LPETH (le {date_str})")
                if data["envoye_regie"]:
                    date_str = data["dates"].get("Envoyé à la Régie", "date non saisie")
                    statuts_affichage_liste.append(f"Envoyé Régie (le {date_str})")
                if data["envoye_cfwb"]:
                    date_str = data["dates"].get("Envoyé à la CFWB", "date non saisie")
                    statuts_affichage_liste.append(f"Envoyé CFWB (le {date_str})")
            elif data["non"]:
                statuts_affichage_liste.append("Non")
                if item in ["F1", "Demande d'activité scolaire", "Demande de résa TRAIN", "CEC 5", "CEC6bis"]:
                    statuts_affichage_liste.append("(À envoyer Régie, À faire signer LPETH)")
                elif item == "Accord CFWB":
                    statuts_affichage_liste.append("(À compléter et envoyer CFWB)")
            else:
                statuts_affichage_liste.append("Statut indéfini")

        resume_lines.append(f"{item} : {', '.join(statuts_affichage_liste)}")

    resume_text = "\n".join(resume_lines)

    st.markdown("---")
    st.subheader("Résumé généré")
    st.text_area("Contenu du résumé :", resume_text, height=350)

    nom_fichier = st.text_input("Nom du fichier à exporter (sans extension) :", value="")
    if nom_fichier and st.button("Exporter vers Google Docs"):
        lien = export_resume_to_google_doc(resume_text, nom_fichier, infos_generales)
        if lien:
            st.success(f"Document exporté avec succès : [Voir le document]({lien})")
