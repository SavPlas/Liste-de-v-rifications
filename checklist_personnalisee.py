import streamlit as st
import datetime

def get_initial_item_state():
    """Retourne la structure d'état initiale complète pour un nouvel élément."""
    return {
        "oui": False,
        "non": False,
        "a_completer": False,
        "complete": False,
        "envoye_regie": False,
        "signe_lpeth": False,
        "envoye_cfwb": False,
        "n_a": False,
        # Ajout de toutes les clés spécifiques pour les différents types d'éléments
        "doc_envoye_cfwb": False,      # Pour Office des Étrangers
        "document_a_completer": False, # Pour Office des Étrangers
        "doc_envoye_assu": False,      # Pour Assurance provinciale
        "doc_a_envoyer": False,        # Pour Assurance provinciale
        "dates": {}
    }

def app_generer_liste_verification():
    """Génère une liste de vérification interactive pour une activité scolaire avec Streamlit."""

    
    st.title("Générateur de Liste de Vérification pour Activité Scolaire")
    st.markdown("---")

    # Informations générales du voyage
    st.header("1. Informations Générales du Voyage")
    intitule_voyage = st.text_input("Intitulé du voyage :", key="intitule_voyage")
    code_regie = st.text_input("Code régie :", key="code_regie")
    prof_org = st.text_input("Professeur-organisateur :", key="prof_org")
    
    # Définir les éléments de la liste de vérification
    elements_checklist = [
        "F1",
        "Demande d'activité scolaire",
        "Demande de résa TRAIN",
        "CEC 5",
        "CEC6bis",
        "Accord CFWB",
        "Office des étrangers : des étudiants de nationalité non-européenne ?",
        "Assurance provinciale"
    ]

    # Utiliser st.session_state pour persister les résultats entre les rafraîchissements
    if 'resultats_checklist' not in st.session_state:
        st.session_state.resultats_checklist = {item: get_initial_item_state() for item in elements_checklist}

    st.header("2. Statut des Éléments de la Checklist")

    # --- Fonctions pour gérer chaque type d'élément ---

    def get_date_input(item_key, status_label, date_key_in_data):
        """Helper pour afficher un date_input et gérer sa valeur.
           Le champ est vide si aucune date n'est déjà enregistrée."""
        current_date_val = None
        if date_key_in_data in st.session_state.resultats_checklist[item_key]["dates"]:
            try:
                current_date_val = datetime.datetime.strptime(st.session_state.resultats_checklist[item_key]["dates"][date_key_in_data], "%d-%m-%Y").date()
            except ValueError:
                current_date_val = None # Ensure it's None if parsing fails
        
        date_val = st.date_input(
            f"Date de {status_label} :",
            value=current_date_val, # MODIFIED LINE: Removed 'if current_date_val else datetime.date.today()'
            key=f"date_{date_key_in_data.replace(' ', '_').replace('/', '_')}_{item_key}"
        )
        # Return empty string if date_val is None (field was empty), otherwise format the date
        return date_val.strftime("%d-%m-%Y") if date_val else ""


    # Fonction utilitaire pour gérer les checkboxes et leur persistance
    def handle_checkbox_with_rerun(item_key, checkbox_label, state_key, current_item_data, col_idx=None, exclusivity_key=None, force_rerun=False):
        """Gère une checkbox, sa persistance, l'exclusivité et le rerun."""
        widget_key = f"checkbox_{state_key}_{item_key}"
        
        if col_idx is not None:
            # Place la checkbox dans une colonne spécifique
            with st.columns(3)[col_idx] if col_idx < 3 else st.columns(2)[col_idx - 3]: # Simple pour Oui/Non/NA
                checked = st.checkbox(
                    checkbox_label,
                    value=current_item_data[state_key],
                    key=widget_key
                )
        else: # Si pas de colonne spécifiée
            checked = st.checkbox(
                checkbox_label,
                value=current_item_data[state_key],
                key=widget_key
            )
        
        # Détection du changement de l'état de la checkbox
        if checked != current_item_data[state_key]:
            current_item_data[state_key] = checked
            
            # Gestion de l'exclusivité (par exemple, Oui/Non)
            if exclusivity_key and checked:
                current_item_data[exclusivity_key] = False # Décocher l'autre
            
            # Si la checkbox est décochée, supprimer la date associée si elle existe
            if not checked and state_key in current_item_data["dates"]:
                del current_item_data["dates"][state_key]

            st.rerun() # Toujours reréunir pour la mise à jour immédiate de l'UI
        
        return checked

    def render_common_n_a_oui_non_checkboxes(item_key, item_data):
        """Affiche les checkboxes Oui/Non/N/A communes à plusieurs éléments."""
        cols = st.columns(3)

        # Case N/A
        with cols[0]:
            n_a_checked = st.checkbox(
                "N/A (Non Applicable)",
                value=item_data["n_a"],
                key=f"checkbox_na_{item_key}"
            )
            # Logique de réinitialisation si N/A vient d'être coché
            if n_a_checked and not item_data["n_a"]: # Si N/A vient d'être coché
                st.session_state.resultats_checklist[item_key] = get_initial_item_state()
                st.session_state.resultats_checklist[item_key]["n_a"] = True # Réactiver N/A
                st.rerun()
            elif not n_a_checked and item_data["n_a"]: # Si N/A vient d'être décoché
                st.session_state.resultats_checklist[item_key] = get_initial_item_state() # Réinitialiser à un état vide
                st.rerun()

            item_data["n_a"] = n_a_checked # Mettre à jour l'état dans item_data

        # Affiche Oui/Non seulement si N/A n'est pas coché
        if not item_data["n_a"]:
            with cols[1]:
                oui_checked = st.checkbox(
                    "Oui (Complété/Réalisé)",
                    value=item_data["oui"],
                    key=f"checkbox_oui_{item_key}"
                )
                if oui_checked != item_data["oui"]:
                    item_data["oui"] = oui_checked
                    if oui_checked: item_data["non"] = False
                    st.rerun()

            with cols[2]:
                non_checked = st.checkbox(
                    "Non (Non Complété)",
                    value=item_data["non"],
                    key=f"checkbox_non_{item_key}"
                )
                if non_checked != item_data["non"]:
                    item_data["non"] = non_checked
                    if non_checked: item_data["oui"] = False
                    st.rerun()
        return item_data


    def handle_f1_demande_ecole_resa_train_cec5_cec6bis(item_key, item_data):
        """Logique pour F1, Demande d'activité scolaire, Demande de résa TRAIN, CEC 5, CEC6bis."""
        item_data = render_common_n_a_oui_non_checkboxes(item_key, item_data)

        if not item_data["n_a"]:
            if item_data["oui"]:
                st.subheader("Détails de complétion :")
                
                # Signé direction LPETH
                col_lpeth, col_date_lpeth = st.columns([0.4, 0.6])
                with col_lpeth:
                    signe_lpeth_checked = st.checkbox(
                        "Signé direction LPETH",
                        value=item_data["signe_lpeth"],
                        key=f"checkbox_signe_lpeth_{item_key}"
                    )
                    if signe_lpeth_checked != item_data["signe_lpeth"]:
                        item_data["signe_lpeth"] = signe_lpeth_checked
                        if not signe_lpeth_checked and "Signé direction LPETH" in item_data["dates"]:
                            del item_data["dates"]["Signé direction LPETH"]
                        st.rerun()
                with col_date_lpeth:
                    if item_data["signe_lpeth"]:
                        item_data["dates"]["Signé direction LPETH"] = get_date_input(item_key, "signature LPETH", "Signé direction LPETH")

                # Envoyé à la Régie
                col_regie, col_date_regie = st.columns([0.4, 0.6])
                with col_regie:
                    envoye_regie_checked = st.checkbox(
                        "Envoyé à la Régie",
                        value=item_data["envoye_regie"],
                        key=f"checkbox_envoye_regie_{item_key}"
                    )
                    if envoye_regie_checked != item_data["envoye_regie"]:
                        item_data["envoye_regie"] = envoye_regie_checked
                        if not envoye_regie_checked and "Envoyé à la Régie" in item_data["dates"]:
                            del item_data["dates"]["Envoyé à la Régie"]
                        st.rerun()
                with col_date_regie:
                    if item_data["envoye_regie"]:
                        item_data["dates"]["Envoyé à la Régie"] = get_date_input(item_key, "envoi Régie", "Envoyé à la Régie")
            
            elif item_data["non"]:
                st.subheader("Actions requises :")
                st.markdown("- À envoyer à la Régie")
                st.markdown("- À faire signer par la direction du LPETH")
        
        return item_data

    def handle_accord_cfwb(item_key, item_data):
        """Logique pour Accord CFWB."""
        item_data = render_common_n_a_oui_non_checkboxes(item_key, item_data)

        if not item_data["n_a"]:
            if item_data["oui"]:
                st.subheader("Détails de complétion :")
                col_cfwb, col_date_cfwb = st.columns([0.6, 0.4])
                with col_cfwb:
                    envoye_cfwb_checked = st.checkbox(
                        "Envoyé à la CFWB",
                        value=item_data["envoye_cfwb"],
                        key=f"checkbox_envoye_cfwb_{item_key}"
                    )
                    if envoye_cfwb_checked != item_data["envoye_cfwb"]:
                        item_data["envoye_cfwb"] = envoye_cfwb_checked
                        if not envoye_cfwb_checked and "Envoyé à la CFWB" in item_data["dates"]:
                            del item_data["dates"]["Envoyé à la CFWB"]
                        st.rerun()
                with col_date_cfwb:
                    if item_data["envoye_cfwb"]:
                        item_data["dates"]["Envoyé à la CFWB"] = get_date_input(item_key, "envoi CFWB", "Envoyé à la CFWB")
            
            elif item_data["non"]:
                st.subheader("Actions requises :")
                st.markdown("- À compléter et envoyer à la CFWB")
        
        return item_data

    def handle_office_etrangers(item_key, item_data):
        """Logique pour Office des étrangers."""
        # Correction : 2 colonnes pour Oui/Non, car pas de N/A ici
        cols = st.columns(2) 

        with cols[0]:
            oui_checked = st.checkbox(
                "Oui (des étudiants de nationalité non-européenne)",
                value=item_data["oui"],
                key=f"checkbox_oui_{item_key}"
            )
            if oui_checked != item_data["oui"]:
                item_data["oui"] = oui_checked
                if oui_checked: item_data["non"] = False
                # Si 'Oui' est coché, s'assurer que les clés de sous-statuts existent
                if not item_data.get("doc_envoye_cfwb"): item_data["doc_envoye_cfwb"] = False
                if not item_data.get("document_a_completer"): item_data["document_a_completer"] = False
                st.rerun()

        with cols[1]:
            non_checked = st.checkbox(
                "Non (aucun étudiant non-européen)",
                value=item_data["non"],
                key=f"checkbox_non_{item_key}"
            )
            if non_checked != item_data["non"]:
                item_data["non"] = non_checked
                if non_checked: item_data["oui"] = False
                # Si 'Non' est coché, réinitialiser les sous-statuts et dates de 'Oui'
                item_data["doc_envoye_cfwb"] = False
                item_data["document_a_completer"] = False
                if "Document envoyé à la CFWB" in item_data["dates"]: del item_data["dates"]["Document envoyé à la CFWB"]
                st.rerun()

        if item_data["oui"]:
            st.subheader("Documents Office des Étrangers :")
            # Document envoyé à la CFWB
            col_doc_cfwb, col_date_doc_cfwb = st.columns([0.6, 0.4])
            with col_doc_cfwb:
                doc_envoye_cfwb_checked = st.checkbox(
                    "Document envoyé à la CFWB",
                    value=item_data["doc_envoye_cfwb"], # Utilise la clé directement
                    key=f"checkbox_doc_envoye_cfwb_{item_key}"
                )
                if doc_envoye_cfwb_checked != item_data["doc_envoye_cfwb"]:
                    item_data["doc_envoye_cfwb"] = doc_envoye_cfwb_checked
                    if not doc_envoye_cfwb_checked and "Document envoyé à la CFWB" in item_data["dates"]:
                        del item_data["dates"]["Document envoyé à la CFWB"]
                    st.rerun()
            with col_date_doc_cfwb:
                if item_data["doc_envoye_cfwb"]:
                    item_data["dates"]["Document envoyé à la CFWB"] = get_date_input(item_key, "envoi document CFWB", "Document envoyé à la CFWB")

            # Document encore à compléter
            document_a_completer_checked = st.checkbox(
                "Document encore à compléter",
                value=item_data["document_a_completer"], # Utilise la clé directement
                key=f"checkbox_doc_a_completer_{item_key}"
            )
            item_data["document_a_completer"] = document_a_completer_checked # Pas besoin de rerun ici, pas de date associée
            
        elif item_data["non"]:
            st.markdown("Aucune action requise pour l'Office des Étrangers.")
        
        return item_data

    def handle_assurance_provinciale(item_key, item_data):
        """Logique pour Assurance provinciale."""
        item_data = render_common_n_a_oui_non_checkboxes(item_key, item_data) # Inclut N/A

        if not item_data["n_a"]:
            if item_data["oui"]:
                st.subheader("Détails de l'assurance :")
                # Document envoyé au service assurances
                col_assu, col_date_assu = st.columns([0.6, 0.4])
                with col_assu:
                    doc_envoye_assu_checked = st.checkbox(
                        "Document envoyé au service assurances de la Province",
                        value=item_data["doc_envoye_assu"], # Utilise la clé directement
                        key=f"checkbox_doc_envoye_assu_{item_key}"
                    )
                    if doc_envoye_assu_checked != item_data["doc_envoye_assu"]:
                        item_data["doc_envoye_assu"] = doc_envoye_assu_checked
                        if not doc_envoye_assu_checked and "Document envoyé au service assurances" in item_data["dates"]:
                            del item_data["dates"]["Document envoyé au service assurances"]
                        st.rerun()
                with col_date_assu:
                    if item_data["doc_envoye_assu"]:
                        item_data["dates"]["Document envoyé au service assurances"] = get_date_input(item_key, "envoi service assurances", "Document envoyé au service assurances")
                
                # Document encore à envoyer
                doc_a_envoyer_checked = st.checkbox(
                    "Document encore à envoyer",
                    value=item_data["doc_a_envoyer"], # Utilise la clé directement
                    key=f"checkbox_doc_a_envoyer_{item_key}"
                )
                item_data["doc_a_envoyer"] = doc_a_envoyer_checked # Pas besoin de rerun ici, pas de date associée
        
        return item_data

    # --- Boucle principale pour afficher les éléments ---
    for item in elements_checklist:
        st.markdown("---") # Séparateur visuel entre chaque élément
        st.subheader(f"**{item}**")
        
        # Récupérer l'état actuel de l'élément
        current_item_data = st.session_state.resultats_checklist[item]

        # Appeler la fonction de gestion spécifique pour chaque élément
        if item in ["F1", "Demande d'activité scolaire", "Demande de résa TRAIN", "CEC 5", "CEC6bis"]:
            updated_item_data = handle_f1_demande_ecole_resa_train_cec5_cec6bis(item, current_item_data)
        elif item == "Accord CFWB":
            updated_item_data = handle_accord_cfwb(item, current_item_data)
        elif item == "Office des étrangers : des étudiants de nationalité non-européenne ?":
            updated_item_data = handle_office_etrangers(item, current_item_data)
        elif item == "Assurance provinciale":
            updated_item_data = handle_assurance_provinciale(item, current_item_data)
        else:
            st.warning(f"Logique non définie pour l'élément : {item}")
            # Fallback si un nouvel élément est ajouté sans logique dédiée
            updated_item_data = render_common_n_a_oui_non_checkboxes(item, current_item_data) 

        # L'état est déjà mis à jour directement via item_data qui est une référence à st.session_state

    st.markdown("---")
    st.header("3. Résumé de la Liste de Vérification")

    if st.button("Afficher le Résumé", key="show_summary_button"):
        if not intitule_voyage or not code_regie:
            st.warning("Veuillez remplir l'intitulé du voyage et le code régie pour le résumé.")
        else:
            st.write(f"**Intitulé du voyage :** {intitule_voyage}")
            st.write(f"**Code régie :** {code_regie}")
            st.write(f"**Professeur-organisateur :** {prof_org if prof_org else 'À compléter'}")
            st.write("---")

            for item, data in st.session_state.resultats_checklist.items():
                statuts_affichage_liste = []
                
                # Logique pour Office des Étrangers
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

                # Logique pour Assurance Provinciale
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
                        statuts_affichage_liste.append("Non (Non Complété)")
                    else:
                        statuts_affichage_liste.append("Statut indéfini")

                # Logique pour les autres items communs (F1, Demande, CEC, Accord CFWB)
                else: 
                    if data["n_a"]: # Si N/A est coché, seul N/A est affiché comme statut
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
                    else: # Si ni Oui ni Non ni N/A n'est coché
                        statuts_affichage_liste.append("Statut indéfini")
                
                # Joindre tous les statuts pour l'affichage
                statuts_affiches = ", ".join(statuts_affichage_liste) if statuts_affichage_liste else "Aucun statut sélectionné"
                
                st.markdown(f"- **{item}** : {statuts_affiches}")
            st.success("Résumé généré avec succès !")
    
# Exécuter l'application Streamlit
if __name__ == "__main__":
    app_generer_liste_verification()
