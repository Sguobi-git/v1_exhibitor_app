import streamlit as st
import pandas as pd
import time
from datetime import datetime
from PIL import Image
import sys
import os
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from datetime import datetime
# Import custom components
from components import create_landing_animation, create_card_layout

# # from data.test_data_manager import GoogleSheetsManager
# from v1_exhibitor_app.test_data_manager import GoogleSheetsManager


# Page configuration with friendly title and wide layout
st.set_page_config(
    page_title="Exhibitor Portal - Expo Convention Contractors",
    page_icon="🎪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS for a more vibrant, friendly UI
st.markdown("""
<style>
    /* More friendly colors and styles */
    .main { 
        background-color: #f8f9fa;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    .stButton button {
        background-color: #3498db;
        color: white;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        background-color: #2980b9;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    /* Card styling */
    .card {
        border-radius: 15px;
        padding: 1.5rem;
        background: white;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    .card:hover {
        box-shadow: 0 6px 14px rgba(0,0,0,0.1);
        transform: translateY(-3px);
    }
    /* Status indicators */
    .status-delivered {
        color: #27ae60;
        font-weight: bold;
    }
    .status-in-progress {
        color: #f39c12;
        font-weight: bold;
    }
    .status-not-started {
        color: #e74c3c;
        font-weight: bold;
    }
    /* Enhancing selection dropdowns */
    .stSelectbox label, .stTextInput label {
        color: #3498db;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)




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
        """Establishes connection to the Google Sheets API."""
        try:
            # Create credentials dictionary from the data provided
            credentials_dict = {
                "type": "service_account",
                "project_id": "gestion-exposants",
                "private_key_id": "eb6f7767a2ad35276d46b965a19492def00c8fdd",
                "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCx3xF1TxOwMdfE\n+XjLj3j8AOQKjHbgwcR8isxjs2Bg5hf0GXyHT6nUqzKa1DI1xMyweOerevEQgc86\nYIZh5Z/dnlSRC/mpZwkNMZ5jd1hpRJ1UIkDHUeGwtn4yFOmKWq5RTLQgnAYG2T02\n5VUMLZ+jqA5gejy/IOz8M3RlqkP1Laaeyft+tW9lY5Rw2NHsopxrS9QCOg3UXoVl\nXtp3sKzChI+mejpa/fnA2wwJ5UWMYMsCv49qH3NrJCk7OyLTf/Al4w0TdSn92htI\nhp9tB1+Hd0Xq5H2QpPAIAsPCj/61VJh7PVdzkTZLxrNgnxY2qTbFh1DgSO4dFPLC\naZEty/fPAgMBAAECggEABtsQMzNPEPV62Y68ByyKfzwRjg6H7nXJevtmkVkyl8mG\nltP8psJ9S0Ml+i2/ma7yLMMcOtHMRNScBiX+R/uvw7z8iXKqtsrP4IBPGIpbEAOj\nBMElOgl/523BQ3Dm53xDR8LrFm6tFMp+v4TrWELR6l7p3vIXMU61k6rwC5Mad3Kw\njAUefY2n3Uw4c9OsTlZOMa7tEyvnrUuvJ4JfZBqtZgCHeenpSso9z3RuWEtdn/iP\nLYqthcvYfTkMUkS6EhDm2/cYqC3ZvsCgpdcCZZ5XbAmfuuPn+pWV4V4HFuidg2uj\nIpq9JXCA2JwYNhWbfFgKROVYxsC3hgqTKiFyk2wMUQKBgQDXwT5iVCl1N1RdpLbl\nPDE7NTUxkHuYPECoJDScpuXVODFyQiEwRXVgT/XNplsHI8Tllz6vrUnb3kscFBRi\nW50hpNxf6sV5w4NVE6bDvstYO3tnhlC7EiPWGgUjLzOCQYkelLxQizT65GCMTPJm\n8P+yC7ON0sHECFcwdzmL2tZY3QKBgQDTDM5vV+9a+FZiXxJNxxUZ3WYDUjo32qoU\n37fU+bqtT8EG2SkU9VpTIz1vXeTa9D6+fiprWCkSedd53XfLVVRsUC6LLhuHORXF\nWTDpMoR8nffWo3LV5yM1Mk6oYr6/vhDxdtVfQ2eNyWgYquayuQq/nUlbQ7K3E+ul\n2Gbg9D0ymwKBgQC/0jx/uan+YAnvE9HUL1bp+B1qCrYIHJGzrDTmjfBLSKGVnzvY\nqfh4f77fbycBSwj0wyplkKDZDWMj/Ko+5IrobaXM1XNrFau/STB8WjZ6JLBL03wV\nRkR8RzgIFyApj9C0UrK2vX2GDuPT+VmOsnfzOToTPq0td+jk2ytbr13hNQKBgA0f\nb7qWoihq5pwpQy8Y4OQB0zUDqOEONKMlof2ZJZVfLyZo3FgURXCD8W76TJ+crkYT\n/Dk+exdOAirurWM0RBKUDcDTthx7XTIvMI5feMNy4xUyhpJsU9Eb9q4brbaob89D\nz1KkE01Kp7FY9w1H2jY95nDJTdR6ZZ2jTgpQxXlfAoGAEW5dZgA4JmAmL7EWtswO\noqw7u9pxo4IQz/Ihy9rGs4W281RO1J2bhodBJO05VslNdSL2duxOWLsYJJAMJE1V\n10qAXbIRfEURw//ANgI56pZthLTBjakCT8wPr2jrXW1udz7fVoxFK6vnAcfkAGEp\n0M9wlC4tCU7z5Wwdhu454EM=\n-----END PRIVATE KEY-----\n",
                "client_email": "souhail@gestion-exposants.iam.gserviceaccount.com",
                "client_id": "110261957473866409903",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/souhail%40gestion-exposants.iam.gserviceaccount.com"
            }
            
            # Get credentials from the service account info
            credentials = Credentials.from_service_account_info(
                credentials_dict,
                scopes=_self.scopes
            )
            
            # Create gspread client
            client = gspread.authorize(credentials)
            return client
        except Exception as e:
            st.error(f"Error connecting to Google Sheets: {e}")
            return None
    # def _connect(_self):
    #     """Établit la connexion à l'API Google Sheets."""
    #     try:
    #         # Récupérer les identifiants depuis les secrets Streamlit
    #         credentials = Credentials.from_service_account_info(
    #             st.secrets["gcp_service_account"],
    #             scopes=_self.scopes
    #         )
            
    #         # Créer le client gspread
    #         _self.client = gspread.authorize(credentials)
    #         return _self.client
    #     except Exception as e:
    #         st.error(f"Erreur de connexion à Google Sheets: {e}")
    #         return None
    
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
        # from data.test_data_manager import GoogleSheetsManager
        
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






# Initialize the Google Sheets manager
gs_manager = GoogleSheetsManager()

# Function to load available shows
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_shows():
    try:
        # Replace with actual sheet ID from your secrets when deploying
        sheet_id = "1dYeok-Dy_7a03AhPDLV2NNmGbRNoCD3q0zaAHPwxxCE"
        shows_df = gs_manager.get_data(sheet_id, "Shows")
        
        # Process the data: assume first row contains headers
        shows_df.columns = shows_df.iloc[0].str.strip()
        shows_df = shows_df[1:].reset_index(drop=True)
        
        # Extract show names from the data
        show_list = shows_df["Show Name"].dropna().tolist() if "Show Name" in shows_df.columns else []
        
        # If no shows are found, provide some sample data
        if not show_list:
            show_list = ["Miami Home Design and Remodeling Show", "Florida International Boat Show", "South Florida Business Expo"]
            
        return show_list
    except Exception as e:
        # st.error(f"Error loading shows: {e}")
        return ["Miami Home Design and Remodeling Show", "Florida International Boat Show", "South Florida Business Expo"]

# Initialize session state for storing booth and show information
if "booth_number" not in st.session_state:
    st.session_state.booth_number = None

if "selected_show" not in st.session_state:
    st.session_state.selected_show = None

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "reload_data" not in st.session_state:
    st.session_state.reload_data = False

# Landing page for selecting show and booth
def show_landing_page():
    # Create columns for better layout
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Add logo or welcome animation
        create_landing_animation()
        
        # st.title("Welcome to Expo Convention Contractors")
        # st.markdown(
        #     """
        #     <h1 style='text-align: center; color: black;'>
        #         Welcome to Expo Convention Contractors
        #     </h1>
        #     """,
        #     unsafe_allow_html=True
        # )

        # st.subheader("Your Exhibitor Portal")
        
        # Show selection
        shows = load_shows()
        selected_show = st.selectbox("Select Your Show:", shows)
        
        # Booth number input
        booth_number = st.text_input("Enter Your Booth Number:", 
                                    placeholder="e.g., 108",
                                    help="Please enter your assigned booth number")
        
        # Login button
        login_col1, login_col2 = st.columns([3, 1])
        with login_col2:
            if st.button("Continue →", use_container_width=True):
                if booth_number and selected_show:
                    # Store in session state
                    st.session_state.booth_number = booth_number
                    st.session_state.selected_show = selected_show
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Please enter both your show and booth number to continue.")
        
        # Add some friendly help text
        st.caption("Need help? Contact our support team at support@expocontractors.com")

# Function to load orders for a specific booth
@st.cache_data(ttl=120)  # Cache for 2 minutes to simulate real-time updates
def load_booth_orders(booth_number, show_name):
    try:
        # Replace with actual sheet ID from your secrets when deploying
        sheet_id = "1dYeok-Dy_7a03AhPDLV2NNmGbRNoCD3q0zaAHPwxxCE" 
        
        # Load orders data
        orders_df = gs_manager.get_data(sheet_id, "Orders")
        
        # Process the dataframe: assume first row contains headers
        if not orders_df.empty:
            orders_df.columns = orders_df.iloc[0].str.strip()
            orders_df = orders_df[1:].reset_index(drop=True)
            
            # Filter for the booth number
            if "Booth #" in orders_df.columns:
                # Convert booth numbers to string for comparison
                orders_df["Booth #"] = orders_df["Booth #"].astype(str)
                booth_orders = orders_df[orders_df["Booth #"] == str(booth_number)]
                return booth_orders
            else:
                st.warning("Data format issue: 'Booth #' column not found")
                return pd.DataFrame()
        else:
            st.warning("No orders data found")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading orders: {e}")
        return pd.DataFrame()

# Function to load available items for ordering
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_inventory():
    try:
        # Replace with actual sheet ID from your secrets when deploying
        sheet_id = "1dYeok-Dy_7a03AhPDLV2NNmGbRNoCD3q0zaAHPwxxCE"
        
        # Load inventory data
        inventory_df = gs_manager.get_data(sheet_id, "Show Inventory")
        
        # Process the dataframe: assume first row contains headers
        if not inventory_df.empty:
            inventory_df.columns = inventory_df.iloc[0].str.strip()
            inventory_df = inventory_df[1:].reset_index(drop=True)
            
            # Extract available items
            available_items = inventory_df["Items"].dropna().tolist() if "Items" in inventory_df.columns else []
            return available_items
        else:
            # Return sample items if no data found
            return ["Chair", "Table", "Booth Carpet", "Lighting", "Display Shelf", "Counter"]
    except Exception as e:
        st.error(f"Error loading inventory: {e}")
        # Return sample items in case of error
        return ["Chair", "Table", "Booth Carpet", "Lighting", "Display Shelf", "Counter"]

# Main dashboard for logged-in exhibitors
def show_dashboard():
    # Add a welcome header with booth number
    st.title(f"Welcome Booth #{st.session_state.booth_number}! 🎪")
    st.caption(f"Show: {st.session_state.selected_show}")
    
    # Create tabs for different sections
    tab1, tab2 = st.tabs(["Your Orders", "Place New Order"])
    
    # Check if we need to reload data
    if st.session_state.get('reload_data', False):
        load_booth_orders.clear()
        st.session_state.reload_data = False
    
    # Tab 1: Orders Overview
    with tab1:
        # Get booth's orders
        booth_orders = load_booth_orders(st.session_state.booth_number, st.session_state.selected_show)
        
        if not booth_orders.empty:
            st.subheader(f"Your Current Orders ({len(booth_orders)})")
            
            # Create a grid layout for cards
            col1, col2 = st.columns(2)
            
            # Display each order in a card layout
            for i, (_, order) in enumerate(booth_orders.iterrows()):
                # Alternate between columns for a balanced layout
                with col1 if i % 2 == 0 else col2:
                    create_card_layout(order)
        else:
            st.info("You don't have any orders yet. Use the 'Place New Order' tab to get started!")
            
            # Add a hint for first-time users
            with st.expander("How to place your first order"):
                st.write("""
                1. Click on the 'Place New Order' tab above
                2. Select the item you need from the dropdown
                3. Enter the quantity
                4. Add any special requests in the comments
                5. Click 'Place Order' to submit your request
                
                Our team will process your order as soon as possible!
                """)
    
    # Tab 2: New Order
    with tab2:
        # Get available items
        available_items = load_inventory()
        
        st.subheader("Place a New Order")
        
        with st.form("new_order_form"):
            # Create a cleaner layout with columns
            col1, col2 = st.columns(2)
            
            with col1:
                # Item selection with a friendly dropdown
                item = st.selectbox(
                    "What item do you need?",
                    options=[""] + available_items,
                    format_func=lambda x: f"🔹 {x}" if x else "Select an item...",
                    help="Select the item you wish to order"
                )
                
                # Quantity selection
                quantity = st.number_input(
                    "How many do you need?",
                    min_value=1,
                    max_value=100,
                    value=1,
                    help="Enter the quantity needed"
                )
            
            with col2:
                # Add color selection if applicable
                color_options = ["White", "Black", "Blue", "Red", "Green", "Burgundy", "Teal", "Other"]
                color = st.selectbox("Color (if applicable):", color_options)
                
                # Comments or special requests
                comments = st.text_area(
                    "Any special requests?",
                    max_chars=500,
                    placeholder="Enter any special requirements or requests here...",
                    help="Add any additional information about your order"
                )
            
            # Submit button with better styling
            submit_col1, submit_col2, submit_col3 = st.columns([1, 2, 1])
            with submit_col2:
                submitted = st.form_submit_button("Place Order", use_container_width=True)
            
            if submitted:
                if not item:
                    st.error("Please select an item to order.")
                else:
                    # Prepare the order data
                    order_data = {
                        'Booth #': st.session_state.booth_number,
                        'Exhibitor Name': f"Booth {st.session_state.booth_number}",  # Can be updated if we collect exhibitor name
                        'Section': "Main Floor",  # Default section
                        'Item': item,
                        'Color': color,
                        'Quantity': quantity,
                        'Status': "In Process",  # Default status for new orders
                        'Type': "New Order",
                        'Comments': comments,
                        'User': f"Exhibitor-{st.session_state.booth_number}"  # Track that this came from an exhibitor
                    }
                    
                    # Add new order to Google Sheets
                    try:
                        from data.direct_sheets_operations import direct_add_order
                        success = direct_add_order("1dYeok-Dy_7a03AhPDLV2NNmGbRNoCD3q0zaAHPwxxCE", order_data)
                        
                        if success:
                            # Store the order data in session state for confirmation screen
                            st.session_state.last_order = order_data
                            st.session_state.show_confirmation = True
                            st.session_state.reload_data = True
                            
                            # Redirect to confirmation screen
                            st.rerun()
                        else:
                            st.error("There was an error submitting your order. Please try again.")
                    except Exception as e:
                        st.error(f"Error: {e}")
                        st.info("For testing purposes, we'll simulate a successful order.")
                        
                        # For demo without actual Google Sheets
                        st.session_state.last_order = order_data
                        st.session_state.show_confirmation = True
                        st.rerun()

# Confirmation screen with animation
def show_confirmation():
    st.title("🎉 Order Confirmed!")

    # Get the last order details
    order = st.session_state.last_order

    # Create a nice confirmation box
    with st.container():
        st.markdown("""
        <div style="padding: 2rem; background-color: #f0f9ff; border-radius: 15px; 
                    border-left: 5px solid #3498db; margin-bottom: 1rem;">
            <h2 style="color: #2980b9;">Order Summary</h2>
            <p style="font-size: 1.1rem;">
                <strong>Item:</strong> {item}<br>
                <strong>Quantity:</strong> {quantity}<br>
                <strong>Color:</strong> {color}<br>
                <strong>Comments:</strong> {comments}
            </p>
        </div>
        """.format(
            item=order.get('Item', 'N/A'),
            quantity=order.get('Quantity', 'N/A'),
            color=order.get('Color', 'N/A'),
            comments=order.get('Comments', 'None')
        ), unsafe_allow_html=True)

    from streamlit.components.v1 import html
    from datetime import datetime

    component_key = f"confirmation_{datetime.now().timestamp()}"

    html("""
    <link href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react/17.0.2/umd/react.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/17.0.2/umd/react-dom.production.min.js"></script>

    <div id="confirmation-animation-root" style="margin: 2rem 0;"></div>

    <script>
    function ConfirmationAnimation() {
        const [currentMessage, setCurrentMessage] = React.useState(0);
        const [fade, setFade] = React.useState(true);

        const messages = [
            "We've got everything covered ✅",
            "Your order is on its way to you 🚚",
            "Your order is excited to meet you 😊"
        ];

        React.useEffect(() => {
            const fadeOutTimer = setTimeout(() => {
                setFade(false);
            }, 3500);
            const changeMessageTimer = setTimeout(() => {
                setCurrentMessage((prev) => (prev + 1) % messages.length);
                setFade(true);
            }, 4000);

            return () => {
                clearTimeout(fadeOutTimer);
                clearTimeout(changeMessageTimer);
            };
        }, [currentMessage]);

        return React.createElement(
            'div', 
            { className: 'flex flex-col items-center justify-center w-full py-8' },
            React.createElement(
                'div', 
                { 
                    className: `text-5xl font-bold text-blue-500 transition-opacity duration-1000 ${fade ? 'opacity-100' : 'opacity-0'}`,
                    style: { transition: 'opacity 1s ease' }
                },
                messages[currentMessage]
            )
        );
    }

    const domContainer = document.querySelector('#confirmation-animation-root');
    ReactDOM.render(React.createElement(ConfirmationAnimation), domContainer);
    </script>
    """, height=200)

#         st.title("🎉 Order Confirmed!")
    
#         # Get the last order details
#         order = st.session_state.last_order
        
#         # Create a nice confirmation box
#         with st.container():
#             st.markdown("""
#             <div style="padding: 2rem; background-color: #f0f9ff; border-radius: 15px; 
#                         border-left: 5px solid #3498db; margin-bottom: 1rem;">
#                 <h2 style="color: #2980b9;">Order Summary</h2>
#                 <p style="font-size: 1.1rem;">
#                     <strong>Item:</strong> {item}<br>
#                     <strong>Quantity:</strong> {quantity}<br>
#                     <strong>Color:</strong> {color}<br>
#                     <strong>Comments:</strong> {comments}
#                 </p>
#             </div>
#             """.format(
#                 item=order.get('Item', 'N/A'),
#                 quantity=order.get('Quantity', 'N/A'),
#                 color=order.get('Color', 'N/A'),
#                 comments=order.get('Comments', 'None')
#             ), unsafe_allow_html=True)
        
#         # Use streamlit-component-lib to render the React component
#         from streamlit.components.v1 import html
        
#         # Generate a unique key based on timestamp to prevent component caching issues
#         component_key = f"confirmation_{datetime.now().timestamp()}"
        
#         # Render the React animation component
#         html("""
#         <link href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css" rel="stylesheet">
#         <script src="https://cdnjs.cloudflare.com/ajax/libs/react/17.0.2/umd/react.production.min.js"></script>
#         <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/17.0.2/umd/react-dom.production.min.js"></script>
        
#         <div id="confirmation-animation-root" style="margin: 2rem 0;"></div>
        
#         <script>
#         // Animation component
#         function ConfirmationAnimation() {
#             const [currentMessage, setCurrentMessage] = React.useState(0);
#             const [fade, setFade] = React.useState(true);
            
#             const messages = [
#                 "We've got everything covered ✅",
#                 "Your order is on its way to you 🚚",
#                 "Your order is excited to meet you 😊"
#             ];
            
#             React.useEffect(() => {
#                 // Fade out effect
#                 const fadeOutTimer = setTimeout(() => {
#                     setFade(false);
#                 }, 3500);
                
#                 // Change message and fade back in
#                 const changeMessageTimer = setTimeout(() => {
#                     setCurrentMessage((prev) => (prev + 1) % messages.length);
#                     setFade(true);
#                 }, 4000);
                
#                 return () => {
#                     clearTimeout(fadeOutTimer);
#                     clearTimeout(changeMessageTimer);
#                 };
#             }, [currentMessage]);
            
#             return React.createElement(
#                 'div', 
#                 { className: 'flex flex-col items-center justify-center w-full py-8' },
#                 [
#                     React.createElement(
#                         'div', 
#                         { 
#                             key: 'message',
#                             className: `text-2xl font-bold text-blue-500 transition-opacity duration-1000 ${fade ? 'opacity-100' : 'opacity-0'}`,
#                             style: { transition: 'opacity 1s ease' }
#                         },
#                         messages[currentMessage]
#                     ),
#                     React.createElement(
#                         'div',
#                         {
#                             key: 'progress',
#                             className: 'mt-8 w-full max-w-md'
#                         },
#                         React.createElement(
#                             'div',
#                             { className: 'relative pt-1' },
#                             [
#                                 React.createElement(
#                                     'div',
#                                     { key: 'header', className: 'flex mb-2 items-center justify-between' },
#                                     [
#                                         React.createElement(
#                                             'div',
#                                             { key: 'label' },
#                                             React.createElement(
#                                                 'span',
#                                                 { className: 'text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-blue-600 bg-blue-200' },
#                                                 'Order Progress'
#                                             )
#                                         ),
#                                         React.createElement(
#                                             'div',
#                                             { key: 'status', className: 'text-right' },
#                                             React.createElement(
#                                                 'span',
#                                                 { className: 'text-xs font-semibold inline-block text-blue-600' },
#                                                 'Processing'
#                                             )
#                                         )
#                                     ]
#                                 ),
#                                 React.createElement(
#                                     'div',
#                                     { key: 'bar', className: 'overflow-hidden h-2 mb-4 text-xs flex rounded bg-blue-200' },
#                                     React.createElement(
#                                         'div',
#                                         { 
#                                             className: 'shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-blue-500',
#                                             style: { width: '45%' }
#                                         }
#                                     )
#                                 )
#                             ]
#                         )
#                     )
#                 ]
#             );
#         }
        
#         // Render the React component
#         const domContainer = document.querySelector('#confirmation-animation-root');
#         ReactDOM.render(React.createElement(ConfirmationAnimation), domContainer);
#         </script>
#         """, height=300)
        
    # Navigation buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("View Your Orders", use_container_width=True):
            st.session_state.show_confirmation = False
            st.rerun()
    
    with col2:
        if st.button("Place Another Order", use_container_width=True):
            st.session_state.show_confirmation = False
            st.rerun()
    # st.title("🎉 Order Confirmed!")
    
    # # Get the last order details
    # order = st.session_state.last_order
    
    # # Create a nice confirmation box
    # with st.container():
    #     st.markdown("""
    #     <div style="padding: 2rem; background-color: #f0f9ff; border-radius: 15px; 
    #                 border-left: 5px solid #3498db; margin-bottom: 1rem;">
    #         <h2 style="color: #2980b9;">Order Summary</h2>
    #         <p style="font-size: 1.1rem;">
    #             <strong>Item:</strong> {item}<br>
    #             <strong>Quantity:</strong> {quantity}<br>
    #             <strong>Color:</strong> {color}<br>
    #             <strong>Comments:</strong> {comments}
    #         </p>
    #     </div>
    #     """.format(
    #         item=order.get('Item', 'N/A'),
    #         quantity=order.get('Quantity', 'N/A'),
    #         color=order.get('Color', 'N/A'),
    #         comments=order.get('Comments', 'None')
    #     ), unsafe_allow_html=True)
    
    # # Create animated messages
    # animation_container = st.empty()
    
    # # Messages to animate through
    # messages = [
    #     "We've got everything covered ✅",
    #     "Your order is on its way to you 🚚",
    #     "Your order is excited to meet you 😊"
    # ]
    
    # # Create JavaScript for the animation
    # st.markdown("""
    # <script>
    # // Animation function
    # function fadeAnimation() {
    #     const messages = ["We've got everything covered ✅", 
    #                      "Your order is on its way to you 🚚", 
    #                      "Your order is excited to meet you 😊"];
    #     let currentIndex = 0;
        
    #     const messageElement = document.getElementById('animation-message');
        
    #     setInterval(() => {
    #         // Fade out
    #         messageElement.style.opacity = 0;
            
    #         // Change content after fade out
    #         setTimeout(() => {
    #             currentIndex = (currentIndex + 1) % messages.length;
    #             messageElement.textContent = messages[currentIndex];
                
    #             // Fade in
    #             messageElement.style.opacity = 1;
    #         }, 1000);
    #     }, 4000);
    # }
    
    # // Run animation when document is loaded
    # document.addEventListener('DOMContentLoaded', fadeAnimation);
    # </script>
    
    # <div style="text-align: center; margin: 2rem 0;">
    #     <div id="animation-message" style="font-size: 1.5rem; font-weight: bold; 
    #                                   color: #3498db; transition: opacity 1s ease;">
    #         We've got everything covered ✅
    #     </div>
    # </div>
    # """, unsafe_allow_html=True)
    
    # # Fallback animation for when JavaScript doesn't work
    # import time
    
    # # Only animate for a short time during the session
    # if "animation_started" not in st.session_state:
    #     st.session_state.animation_started = time.time()
    #     st.session_state.message_index = 0
    
    # # Show static message if animation has been running for too long
    # current_time = time.time()
    # elapsed_time = current_time - st.session_state.animation_started
    
    # if elapsed_time < 30:  # Only animate for 30 seconds
    #     # Animate through messages
    #     message = messages[st.session_state.message_index]
    #     animation_container.markdown(f"""
    #     <div style="text-align: center; margin: 2rem 0;">
    #         <div style="font-size: 1.5rem; font-weight: bold; color: #3498db;">
    #             {message}
    #         </div>
    #     </div>
    #     """, unsafe_allow_html=True)
        
    #     # Increment message index for next iteration
    #     st.session_state.message_index = (st.session_state.message_index + 1) % len(messages)
        
    #     # Auto-refresh for animation
    #     time.sleep(0.1)  # Small pause to avoid using too much CPU
    #     st.rerun()
    # else:
    #     # Show static message after animation period
    #     animation_container.markdown(f"""
    #     <div style="text-align: center; margin: 2rem 0;">
    #         <div style="font-size: 1.5rem; font-weight: bold; color: #3498db;">
    #             {messages[0]}
    #         </div>
    #     </div>
    #     """, unsafe_allow_html=True)
    
    # # Navigation buttons
    # col1, col2 = st.columns(2)
    
    # with col1:
    #     if st.button("View Your Orders", use_container_width=True):
    #         st.session_state.show_confirmation = False
    #         st.rerun()
    
    # with col2:
    #     if st.button("Place Another Order", use_container_width=True):
    #         st.session_state.show_confirmation = False
    #         st.rerun()

# Sidebar with helpful information
with st.sidebar:
    # Show booth information if logged in
    if st.session_state.get("logged_in", False):
        st.header(f"Booth #{st.session_state.booth_number}")
        st.subheader(st.session_state.selected_show)
        
        # Add a divider
        st.divider()
        
        # Refresh data button
        if st.button("🔄 Refresh Data", use_container_width=True):
            load_booth_orders.clear()
            load_inventory.clear()
            st.session_state.reload_data = True
            st.rerun()
        
        # Logout button
        if st.button("📤 Log Out", use_container_width=True):
            # Reset session state
            st.session_state.logged_in = False
            st.session_state.booth_number = None
            st.session_state.selected_show = None
            st.session_state.show_confirmation = False
            # Reload the page
            st.rerun()
    
    # Always show contact information
    st.divider()
    st.subheader("Need Assistance?")
    st.markdown("""
    📞 Call: (305) 555-1234  
    📱 Text: (305) 555-5678  
    📧 Email: support@expocontractors.com
    """)
    
    st.caption("On-site support is available at the Exhibitor Service Desk")

# Main app flow
if not st.session_state.get("logged_in", False):
    # Show landing page for non-logged in users
    show_landing_page()
elif st.session_state.get("show_confirmation", False):
    # Show confirmation screen after order is placed
    show_confirmation()
else:
    # Show main dashboard for logged-in users
    show_dashboard()











