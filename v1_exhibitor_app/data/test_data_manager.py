import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from datetime import datetime

class GoogleSheetsManager:
    """Gestionnaire pour interagir avec les fichiers Google Sheets."""
    
    def __init__(self):
        # Définir les scopes nécessaires pour l'API
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Se connecter à l'API Google Sheets
        # self._connect()
        self.client = self._connect()
        
    @st.cache_resource(ttl=3600)
    def _connect(_self):
        """Établit la connexion à l'API Google Sheets."""
        try:
            # Récupérer les identifiants depuis les secrets Streamlit
            credentials = Credentials.from_service_account_info(
                st.secrets["gcp_service_account"],
                scopes=_self.scopes
            )
            
            # Créer le client gspread
            _self.client = gspread.authorize(credentials)
            return _self.client
        except Exception as e:
            st.error(f"Erreur de connexion à Google Sheets: {e}")
            return None
    
    def get_worksheets(self, sheet_id):
        """Récupère la liste des feuilles d'un classeur Google Sheets."""
        try:
            spreadsheet = self.client.open_by_key(sheet_id)
            return [worksheet.title for worksheet in spreadsheet.worksheets()]
        except Exception as e:
            st.error(f"Erreur lors de la récupération des feuilles: {e}")
            return []
            
    # @st.cache_data(ttl=60)
    # def get_data(_self, sheet_id, worksheet_name):
    #     """Récupère les données d'une feuille Google Sheets."""
    #     try:
    #         # Ouvrir le classeur et accéder à la feuille
    #         spreadsheet = _self.client.open_by_key(sheet_id)
    #         worksheet = spreadsheet.worksheet(worksheet_name)
            
    #         # Récupérer les données sous forme de DataFrame
    #         data = get_as_dataframe(worksheet, evaluate_formulas=True, skipinitialspace=True)
            
    #         # Nettoyer le DataFrame (supprimer les lignes vides)
    #         data = data.dropna(how='all').reset_index(drop=True)
            
    #         return data
    #     except Exception as e:
    #         st.error(f"Erreur lors de la récupération des données: {e}")
    #         return pd.DataFrame()

    def get_data(self, sheet_id, worksheet_name):
        """Récupère les données d'une feuille Google Sheets."""
        try:
            # Utiliser la même approche de connexion que dans add_order
            scope = ["https://www.googleapis.com/auth/spreadsheets", 
                    "https://www.googleapis.com/auth/drive"]
            creds = Credentials.from_service_account_file(
                # "S:\\Work (Souhail)\\Archive\\Dashboard Web\\gestion-exposants-eb6f7767a2ad.json",
                "S:\\Work (Souhail)\\Archive\\Dashboard Web\\gestion-exposants-eb6f7767a2ad.json",
                scopes=scope
            )
            gc = gspread.authorize(creds)
            
            # Ouvrir le classeur et accéder à la feuille
            spreadsheet = gc.open_by_key(sheet_id)
            worksheet = spreadsheet.worksheet(worksheet_name)
            
            # Récupérer les données sous forme de DataFrame
            data = get_as_dataframe(worksheet, evaluate_formulas=True, skipinitialspace=True)
            
            # Nettoyer le DataFrame (supprimer les lignes vides)
            data = data.dropna(how='all').reset_index(drop=True)
            
            return data
        except Exception as e:
            # st.error(f"Erreur lors de la récupération des données: {e}")
            return pd.DataFrame()
    
    def update_order_status(self, sheet_id, worksheet, booth_num, item_name, color, status, user):
        """Met à jour le statut d'une commande dans le classeur Order Tracking."""
        try:
            # Ouvrir le classeur et accéder à la feuille
            spreadsheet = self.client.open_by_key(sheet_id)
            worksheet = spreadsheet.worksheet(worksheet)
            
            # Obtenir toutes les valeurs
            data = worksheet.get_all_records()
            
            # Trouver la ligne à mettre à jour
            for idx, row in enumerate(data):
                if (str(row.get('Booth #')) == str(booth_num) and 
                    row.get('Item') == item_name and 
                    row.get('Color') == color):
                    
                    # Index de ligne dans la feuille (ajouter 2 pour tenir compte de l'en-tête et de l'indexation à 0)
                    row_index = idx + 2
                    
                    # Mettre à jour le statut
                    worksheet.update_cell(row_index, worksheet.find('Status').col, status)
                    
                    # Mettre à jour l'utilisateur
                    worksheet.update_cell(row_index, worksheet.find('User').col, user)
                    
                    # Mettre à jour la date et l'heure
                    now = datetime.now()
                    worksheet.update_cell(row_index, worksheet.find('Date').col, now.strftime("%m/%d/%Y"))
                    worksheet.update_cell(row_index, worksheet.find('Hour').col, now.strftime("%I:%M:%S %p"))
                    
                    return True
            
            return False
        except Exception as e:
            st.error(f"Erreur lors de la mise à jour du statut: {e}")
            return False
    
    def update_checklist_item(self, sheet_id, worksheet, booth_num, item_name, data):
        """Met à jour un élément de checklist dans le classeur Booth Checklist."""
        try:
            # Ouvrir le classeur et accéder à la feuille
            spreadsheet = self.client.open_by_key(sheet_id)
            worksheet = spreadsheet.worksheet(worksheet)
            
            # Obtenir toutes les valeurs
            worksheet_data = worksheet.get_all_records()
            
            # Trouver la ligne à mettre à jour
            for idx, row in enumerate(worksheet_data):
                if (str(row.get('Booth #')) == str(booth_num) and 
                    row.get('Item Name') == item_name):
                    
                    # Index de ligne dans la feuille (ajouter 2 pour tenir compte de l'en-tête et de l'indexation à 0)
                    row_index = idx + 2
                    
                    # Mettre à jour le statut
                    if 'Status' in data:
                        status_col = worksheet.find('Status').col
                        worksheet.update_cell(row_index, status_col, data['Status'])
                    
                    # Mettre à jour la date
                    if 'Date' in data:
                        date_col = worksheet.find('Date').col
                        worksheet.update_cell(row_index, date_col, data['Date'])
                    
                    # Mettre à jour l'heure
                    if 'Hour' in data:
                        hour_col = worksheet.find('Hour').col
                        worksheet.update_cell(row_index, hour_col, data['Hour'])
                    
                    return True
            
            return False
        except Exception as e:
            st.error(f"Erreur lors de la mise à jour de l'élément de checklist: {e}")
            return False
    
    def add_order(self, sheet_id, order_data):
        """Ajoute une nouvelle commande en utilisant la méthode directe qui fonctionne."""
        try:
            # Utiliser directement l'approche qui fonctionne
            scope = ["https://www.googleapis.com/auth/spreadsheets"]
            creds = Credentials.from_service_account_file(
                "S:\\Work (Souhail)\\Archive\\Dashboard Web\\gestion-exposants-eb6f7767a2ad.json", 
                scopes=scope
            )
            gc = gspread.authorize(creds)
            sh = gc.open_by_key(sheet_id)
            orders_sheet = sh.worksheet("Orders")
            
            # Préparer les données à insérer
            now = datetime.now()
            
            # Créer une liste de valeurs pour la nouvelle ligne
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
            
            # Mettre à jour également la feuille de section correspondante
            section = order_data.get('Section', '')
            if section:
                try:
                    section_sheet = sh.worksheet(section)
                    section_sheet.append_row(row_data)
                except Exception as section_error:
                    # La feuille de section n'existe pas ou erreur
                    pass
            
            return True
        except Exception as e:
            st.error(f"Erreur lors de l'ajout de la commande: {e}")
            return False

    # First, add a function to GoogleSheetsManager in data/test_data_manager.py
    # Add this method to your GoogleSheetsManager class:

    def delete_order(self, sheet_id, worksheet, booth_num, item_name, color):
        """
        Delete an order from Google Sheets
        
        Args:
            sheet_id (str): The ID of the Google Sheet
            worksheet (str): The name of the worksheet
            booth_num (str): The booth number of the order to delete
            item_name (str): The item name of the order to delete
            color (str): The color of the item to delete
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Open the specified worksheet
            sheet = self.client.open_by_key(sheet_id).worksheet(worksheet)
            
            # Get all data
            data = sheet.get_all_values()
            if not data:
                return False
            
            # Find the row with matching booth number, item name, and color
            header_row = data[0]
            booth_col = header_row.index('Booth #') if 'Booth #' in header_row else None
            item_col = header_row.index('Item') if 'Item' in header_row else None
            color_col = header_row.index('Color') if 'Color' in header_row else None
            
            if booth_col is None or item_col is None or color_col is None:
                return False
            
            row_to_delete = None
            for i in range(1, len(data)):
                if (str(data[i][booth_col]) == str(booth_num) and 
                    data[i][item_col] == str(item_name) and 
                    data[i][color_col] == str(color)):
                    row_to_delete = i + 1  # +1 because Google Sheets is 1-indexed
                    break
            
            if row_to_delete:
                sheet.delete_rows(row_to_delete)
                return True
            return False
        
        except Exception as e:
            print(f"Error deleting order: {e}")
            return False

    # Next, add a direct deletion function in data/direct_sheets_operations.py
    # Add this function:

    def direct_delete_order(sheet_id, booth_num, item_name, color, section):
        """
        Direct function to delete an order from Google Sheets
        
        Args:
            sheet_id (str): The ID of the Google Sheet
            booth_num (str): The booth number of the order to delete
            item_name (str): The item name of the order to delete
            color (str): The color of the item to delete
            section (str): The section where the order is located
        
        Returns:
            bool: True if successful, False otherwise
        """
        from data.test_data_manager import GoogleSheetsManager
        
        gs_manager = GoogleSheetsManager()
        
        # Try to delete from the section worksheet first
        success = gs_manager.delete_order(
            sheet_id=sheet_id,
            worksheet=section,
            booth_num=booth_num,
            item_name=item_name,
            color=color
        )
        
        # If not successful or if we're not sure where it is, try the main Orders sheet
        if not success:
            success = gs_manager.delete_order(
                sheet_id=sheet_id,
                worksheet="Orders",
                booth_num=booth_num,
                item_name=item_name,
                color=color
            )
        
        return success