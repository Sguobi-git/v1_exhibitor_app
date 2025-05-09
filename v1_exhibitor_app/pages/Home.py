import streamlit as st
import pandas as pd
import time
from datetime import datetime
from PIL import Image
import sys
import os
# Import custom components
from components import create_landing_animation, create_card_layout

# # from data.test_data_manager import GoogleSheetsManager
# from v1_exhibitor_app.test_data_manager import GoogleSheetsManager

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from test_data_manager import GoogleSheetsManager


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







