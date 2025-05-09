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

# Define your sheet ID as a constant to use throughout the app
SHEET_ID = "1dYeok-Dy_7a03AhPDLV2NNmGbRNoCD3q0zaAHPwxxCE"

class GoogleSheetsManager:
    """Manager for interacting with Google Sheets files."""
    
    def __init__(self):
        # Define necessary scopes for the API
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Connect to the Google Sheets API
        self.client = self._connect()
        
    @st.cache_resource(ttl=3600)
    def _connect(_self):
        """Establishes connection to the Google Sheets API."""
        try:
            # Create credentials dictionary from the data provided
            
            # Get credentials from the service account info
            credentials = Credentials.from_service_account_info(
                st.secrets["gcp_service_account"],
                scopes=_self.scopes
            )
            
            # Create and return gspread client
            # client = gspread.authorize(credentials)
            # return client
            _self.client = gspread.authorize(credentials)
            return _self.client
        except Exception as e:
            st.error(f"Error connecting to Google Sheets: {e}")
            return None
    
    def get_worksheets(self, sheet_id):
        """Get the list of worksheets in a Google Sheets file."""
        try:
            spreadsheet = self.client.open_by_key(sheet_id)
            return [worksheet.title for worksheet in spreadsheet.worksheets()]
        except Exception as e:
            st.error(f"Error retrieving worksheets: {e}")
            return []
            
    def get_data(self, sheet_id, worksheet_name):
        """Get data from a Google Sheets worksheet."""
        try:
            # Open the spreadsheet and access the worksheet
            spreadsheet = self.client.open_by_key(sheet_id)
            worksheet = spreadsheet.worksheet(worksheet_name)
            
            # Get data as DataFrame
            data = get_as_dataframe(worksheet, evaluate_formulas=True, skipinitialspace=True)
            
            # Clean the DataFrame (remove empty rows)
            data = data.dropna(how='all').reset_index(drop=True)
            
            return data
        except Exception as e:
            # st.error(f"Error retrieving data: {e}")
            return pd.DataFrame()
    
    def update_order_status(self, sheet_id, worksheet, booth_num, item_name, color, status, user):
        """Update the status of an order in the Order Tracking sheet."""
        try:
            # Open the spreadsheet and access the worksheet
            spreadsheet = self.client.open_by_key(sheet_id)
            worksheet = spreadsheet.worksheet(worksheet)
            
            # Get all values
            data = worksheet.get_all_records()
            
            # Find the row to update
            for idx, row in enumerate(data):
                if (str(row.get('Booth #')) == str(booth_num) and 
                    row.get('Item') == item_name and 
                    row.get('Color') == color):
                    
                    # Row index in the sheet (add 2 to account for header and 0-indexing)
                    row_index = idx + 2
                    
                    # Update the status
                    worksheet.update_cell(row_index, worksheet.find('Status').col, status)
                    
                    # Update the user
                    worksheet.update_cell(row_index, worksheet.find('User').col, user)
                    
                    # Update date and time
                    now = datetime.now()
                    worksheet.update_cell(row_index, worksheet.find('Date').col, now.strftime("%m/%d/%Y"))
                    worksheet.update_cell(row_index, worksheet.find('Hour').col, now.strftime("%I:%M:%S %p"))
                    
                    return True
            
            return False
        except Exception as e:
            st.error(f"Error updating status: {e}")
            return False
    
    def update_checklist_item(self, sheet_id, worksheet, booth_num, item_name, data):
        """Update a checklist item in the Booth Checklist sheet."""
        try:
            # Open the spreadsheet and access the worksheet
            spreadsheet = self.client.open_by_key(sheet_id)
            worksheet = spreadsheet.worksheet(worksheet)
            
            # Get all values
            worksheet_data = worksheet.get_all_records()
            
            # Find the row to update
            for idx, row in enumerate(worksheet_data):
                if (str(row.get('Booth #')) == str(booth_num) and 
                    row.get('Item Name') == item_name):
                    
                    # Row index in the sheet (add 2 to account for header and 0-indexing)
                    row_index = idx + 2
                    
                    # Update the status
                    if 'Status' in data:
                        status_col = worksheet.find('Status').col
                        worksheet.update_cell(row_index, status_col, data['Status'])
                    
                    # Update the date
                    if 'Date' in data:
                        date_col = worksheet.find('Date').col
                        worksheet.update_cell(row_index, date_col, data['Date'])
                    
                    # Update the hour
                    if 'Hour' in data:
                        hour_col = worksheet.find('Hour').col
                        worksheet.update_cell(row_index, hour_col, data['Hour'])
                    
                    return True
            
            return False
        except Exception as e:
            st.error(f"Error updating checklist item: {e}")
            return False
    
    def add_order(self, sheet_id, order_data):
        """Add a new order using the client already established."""
        try:
            # Use the existing client
            spreadsheet = self.client.open_by_key(sheet_id)
            orders_sheet = spreadsheet.worksheet("Orders")
            
            # Prepare data to insert
            now = datetime.now()
            
            # Create a list of values for the new row
            row_data = [
                order_data.get('Booth #', ''),
                order_data.get('Section', ''),
                order_data.get('Exhibitor Name', ''),
                order_data.get('Item', ''),
                order_data.get('Color', ''),
                order_data.get('Quantity', ''),
                now.strftime("%m/%d/%Y"),  # Date
                now.strftime("%I:%M:%S %p"),  # Hour
                order_data.get('Status', 'New'),
                order_data.get('Type', 'New Order'),
                order_data.get('Boomers Quantity', ''),
                order_data.get('Comments', ''),
                order_data.get('User', '')
            ]
            
            # Insert the new row
            orders_sheet.append_row(row_data)
            
            # Also update the corresponding section sheet
            section = order_data.get('Section', '')
            if section:
                try:
                    section_sheet = spreadsheet.worksheet(section)
                    section_sheet.append_row(row_data)
                except Exception as section_error:
                    # Section sheet doesn't exist or error
                    pass
            
            return True
        except Exception as e:
            st.error(f"Error adding order: {e}")
            return False

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

# Initialize the Google Sheets manager
gs_manager = GoogleSheetsManager()

# Function to delete an order directly - can be called independently
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

# Function to add an order directly - can be called independently
def direct_add_order(sheet_id, order_data):
    """
    Direct function to add an order to Google Sheets
    
    Args:
        sheet_id (str): The ID of the Google Sheet
        order_data (dict): Dictionary containing order information
    
    Returns:
        bool: True if successful, False otherwise
    """
    gs_manager = GoogleSheetsManager()
    return gs_manager.add_order(sheet_id, order_data)

# Function to load available shows
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_shows():
    try:
        # Use the global sheet ID constant
        shows_df = gs_manager.get_data(SHEET_ID, "Shows")
        
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
        # Use the global sheet ID constant
        orders_df = gs_manager.get_data(SHEET_ID, "Orders")
        
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
        # Use the global sheet ID constant
        inventory_df = gs_manager.get_data(SHEET_ID, "Show Inventory")
        
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
                    
                    # Add new order using the direct function with sheet ID
                    success = direct_add_order(SHEET_ID, order_data)
                    
                    if success:
                        # Store the order data in session state for confirmation screen
                        st.session_state.last_order = order_data
                        st.session_state.show_confirmation = True
                        st.session_state.reload_data = True
                        
                        # Redirect to confirmation screen
                        st.rerun()
                    else:
                        st.error("There was an error submitting your order. Please try again.")

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
    # Show
    show_dashboard()









