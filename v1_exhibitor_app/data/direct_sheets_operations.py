import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import streamlit as st

def direct_add_order(sheet_id, order_data):
    """
    Fonction indépendante qui utilise directement l'approche fonctionnelle 
    pour ajouter une commande à Google Sheets.
    """
    try:
        # Approche directe qui fonctionne
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file(
            "S:\\Work (Souhail)\\Archive\\Dashboard Web\\gestion-exposants-eb6f7767a2ad.json", 
            scopes=scope
        )
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(sheet_id)
        orders_sheet = sh.worksheet("Orders")
        
        # Préparer les données
        now = datetime.now()
        
        # Créer la ligne de données
        row_data = [
            order_data.get('Booth #', ''),
            order_data.get('Section', ''),
            order_data.get('Exhibitor Name', ''),
            order_data.get('Item', ''),
            order_data.get('Color', ''),
            order_data.get('Quantity', ''),
            now.strftime("%m/%d/%Y"),  # Date
            now.strftime("%I:%M:%S %p"),  # Heure
            order_data.get('Status', 'New'),
            order_data.get('Type', 'New Order'),
            order_data.get('Boomers Quantity', ''),
            order_data.get('Comments', ''),
            order_data.get('User', '')
        ]
        
        # Insérer la nouvelle ligne
        orders_sheet.append_row(row_data)
        st.success("Commande ajoutée avec succès!")
        
        # Mettre à jour la feuille de section si elle existe
        section = order_data.get('Section', '')
        if section:
            try:
                section_sheet = sh.worksheet(section)
                section_sheet.append_row(row_data)
            except Exception:
                # La feuille n'existe pas ou autre erreur - on ignore
                pass
        
        return True
    except Exception as e:
        st.error(f"Erreur lors de l'ajout de la commande: {e}")
        print(f"Détails de l'erreur: {e}")  # Pour le débogage
        return False


def direct_delete_order(sheet_id, booth_num, item_name, color, section):
    """
    Fonction pour supprimer une commande de Google Sheets basée sur le numéro de stand, 
    l'article et la couleur. Gère les feuilles avec des cellules vides dans l'en-tête.
    
    Args:
        sheet_id (str): ID du classeur Google Sheets
        booth_num (str): Numéro de stand
        item_name (str): Nom de l'article
        color (str): Couleur de l'article
        section (str): Section de l'exposant
        
    Returns:
        bool: True si la suppression a réussi, False sinon
    """
    try:
        # Configurer l'accès à l'API
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file(
            "S:\\Work (Souhail)\\Archive\\Dashboard Web\\gestion-exposants-eb6f7767a2ad.json", 
            scopes=scope
        )
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(sheet_id)
        
        # Supprimer de la feuille principale "Orders"
        orders_sheet = sh.worksheet("Orders")
        
        # Obtenir toutes les valeurs (y compris l'en-tête)
        all_values = orders_sheet.get_all_values()
        if not all_values:
            return False
        
        # Extraire l'en-tête
        headers = all_values[0]
        
        # Trouver les index des colonnes nécessaires
        try:
            booth_idx = headers.index('Booth #')
            item_idx = headers.index('Item')
            color_idx = headers.index('Color')
        except ValueError:
            # Essayer une approche plus générique si les en-têtes exacts ne sont pas trouvés
            booth_idx = next((i for i, h in enumerate(headers) if 'booth' in h.lower()), 0)
            item_idx = next((i for i, h in enumerate(headers) if 'item' in h.lower()), 3)
            color_idx = next((i for i, h in enumerate(headers) if 'color' in h.lower()), 4)
        
        # Trouver la ligne à supprimer
        row_to_delete = None
        for i, row in enumerate(all_values[1:], 2):  # Start from row 2 (1-indexed)
            if (len(row) > max(booth_idx, item_idx, color_idx) and
                str(row[booth_idx]).strip() == str(booth_num).strip() and
                row[item_idx].strip() == item_name.strip() and
                row[color_idx].strip() == color.strip()):
                row_to_delete = i
                break
        
        # Supprimer la ligne si trouvée
        if row_to_delete:
            orders_sheet.delete_rows(row_to_delete)
            
            # Tenter de supprimer également de la feuille de section si elle existe
            if section:
                try:
                    section_sheet = sh.worksheet(section)
                    section_values = section_sheet.get_all_values()
                    
                    if section_values:
                        section_headers = section_values[0]
                        
                        # Trouver les index dans la feuille de section
                        try:
                            s_booth_idx = section_headers.index('Booth #')
                            s_item_idx = section_headers.index('Item')
                            s_color_idx = section_headers.index('Color')
                        except ValueError:
                            s_booth_idx = booth_idx
                            s_item_idx = item_idx
                            s_color_idx = color_idx
                        
                        # Trouver la ligne à supprimer dans la section
                        section_row_to_delete = None
                        for s_i, s_row in enumerate(section_values[1:], 2):  # Start from row 2 (1-indexed)
                            if (len(s_row) > max(s_booth_idx, s_item_idx, s_color_idx) and
                                str(s_row[s_booth_idx]).strip() == str(booth_num).strip() and
                                s_row[s_item_idx].strip() == item_name.strip() and
                                s_row[s_color_idx].strip() == color.strip()):
                                section_row_to_delete = s_i
                                break
                        
                        if section_row_to_delete:
                            section_sheet.delete_rows(section_row_to_delete)
                
                except Exception as section_error:
                    print(f"Erreur lors de la suppression dans la section: {section_error}")
            
            return True
        
        return False  # Ligne non trouvée
    
    except Exception as e:
        st.error(f"Erreur lors de la suppression de la commande: {e}")
        print(f"Détails de l'erreur: {e}")  # Pour le débogage
        return False