import streamlit as st
import time
from datetime import datetime
from PIL import Image


def create_landing_animation():
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)

    # Load and display the image
    # logo = Image.open("S:\Work (Souhail)\Archive\Exhibitor Version\expo-app//assets\logo.png")
    logo = Image.open("v0 Exhibitor app/assets/logo.png")
    st.image(logo, use_column_width="auto")

    # Welcome message with animation
    st.markdown("""
<br>
<div style="font-size: 1.5rem; color: #3498db; animation: fadeIn 2s;">
    Welcome to Your Exhibitor Portal
</div>
<br>

<style>
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
</style>
""", unsafe_allow_html=True)



    # """Create a welcoming animation for the landing page"""
    # st.markdown("""
    # <div style="text-align: center; margin-bottom: 2rem;">
    #     <img src="S:\Work (Souhail)\Archive\Exhibitor Version\expo-app//assets\logo.PNG" 
    #          alt="Expo Convention Contractors Logo" 
    #          style="width: 80%; max-width: 400px; margin-bottom: 1rem;">
        
    #     <div style="font-size: 1.5rem; color: #3498db; animation: fadeIn 2s;">
    #         Welcome to Your Exhibitor Portal
    #     </div>
    # </div>
    
    # <style>
    # @keyframes fadeIn {
    #     from { opacity: 0; }
    #     to { opacity: 1; }
    # }
    # </style>
    # """, unsafe_allow_html=True)

def create_card_layout(order):
    """
    Create a card layout for a single order
    
    Args:
        order (pd.Series): A row from the orders dataframe
    """
    # Get the order details with fallbacks for missing data
    order_id = order.get('Hour', 'unknown')
    item = order.get('Item', 'Unknown Item')
    quantity = order.get('Quantity', '1')
    status = order.get('Status', 'In Process')
    date = order.get('Date', datetime.now().strftime('%Y-%m-%d'))
    
    # Map status to emoji and CSS class
    status_mapping = {
        'Delivered': ('🟢', 'status-delivered'),
        'In route from warehouse': ('🟠', 'status-in-progress'),
        'In Process': ('🟠', 'status-in-progress'),
        'Out for delivery': ('🟠', 'status-in-progress'),
        'Received': ('🟢', 'status-delivered'),
        'Not started': ('🔴', 'status-not-started'),
        'cancelled': ('⚫', 'status-not-started')
    }
    
    status_emoji, status_class = status_mapping.get(status, ('⚪', ''))
    
    # Create the card with HTML/CSS
    st.markdown(f"""
    <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <h3 style="margin: 0;">{item}</h3>
            <span class="{status_class}">{status_emoji} {status}</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <div><strong>Quantity:</strong> {quantity}</div>
            <div><strong>Date:</strong> {date}</div>
        </div>
        
    </div>
    """, unsafe_allow_html=True)
    
    # Add buttons for order actions
    col1 = st.columns(1)[0]
    
    # with col1:
    #     if st.button("View Details", key=f"details_{order_id}", use_container_width=True):
    #         # In a real application, this would display more order details
    #         st.info("Order details functionality would be implemented here.")

    with col1:
        # Check if this is a "delivered" type of status
        delivered_statuses = ['Delivered', 'Received']
        is_delivered = status in delivered_statuses

        # Only show animation button for orders that are not delivered
        if not is_delivered:
            if st.button("View Details", key=f"anim_{order_id}", use_container_width=True):
                # Store the order in session state and show the confirmation screen
                st.session_state.last_order = order
                st.session_state.show_confirmation = True
                st.rerun()
        else:
            # Show a disabled button or alternative for delivered orders
            st.markdown("""
            <div style="width: 100%; text-align: center;">
                <button style="width: 100%; background-color: #e2e8f0; color: #718096; 
                              border-radius: 10px; padding: 0.5rem; cursor: not-allowed;">
                    Order Complete
                </button>
            </div>
            """, unsafe_allow_html=True)

    
    # with col2:
    #     # Check if this is a "delivered" type of status
    #     delivered_statuses = ['Delivered', 'Received']
    #     is_delivered = status in delivered_statuses

    #     # Only show animation button for orders that are not delivered
    #     if not is_delivered:
    #         if st.button("View Progress", key=f"anim_{order_id}", use_container_width=True):
    #             # Store the order in session state and show the confirmation screen
    #             st.session_state.last_order = order
    #             st.session_state.show_confirmation = True
    #             st.rerun()
    #     else:
    #         # Show a disabled button or alternative for delivered orders
    #         st.markdown("""
    #         <div style="width: 100%; text-align: center;">
    #             <button style="width: 100%; background-color: #e2e8f0; color: #718096; 
    #                           border-radius: 10px; padding: 0.5rem; cursor: not-allowed;">
    #                 Order Complete
    #             </button>
    #         </div>
    #         """, unsafe_allow_html=True)


    # """
    # Create a card layout for a single order
    
    # Args:
    #     order (pd.Series): A row from the orders dataframe
    # """
    # # Get the order details with fallbacks for missing data
    # item = order.get('Item', 'Unknown Item')
    # quantity = order.get('Quantity', '1')
    # status = order.get('Status', 'In Process')
    # date = order.get('Date', datetime.now().strftime('%Y-%m-%d'))
    
    # # Map status to emoji and CSS class
    # status_mapping = {
    #     'Delivered': ('🟢', 'status-delivered'),
    #     'In route from warehouse': ('🟠', 'status-in-progress'),
    #     'In Process': ('🟠', 'status-in-progress'),
    #     'Out for delivery': ('🟠', 'status-in-progress'),
    #     'Received': ('🟢', 'status-delivered'),
    #     'Not started': ('🔴', 'status-not-started'),
    #     'cancelled': ('⚫', 'status-not-started')
    # }
    
    # status_emoji, status_class = status_mapping.get(status, ('⚪', ''))
    
    # # Create the card with HTML/CSS
    # st.markdown(f"""
    # <div class="card">
    #     <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
    #         <h3 style="margin: 0;">{item}</h3>
    #         <span class="{status_class}">{status_emoji} {status}</span>
    #     </div>
    #     <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
    #         <div><strong>Quantity:</strong> {quantity}</div>
    #         <div><strong>Date:</strong> {date}</div>
    #     </div>
        
    #     {f'<div><strong>Comments:</strong> {order.get("Comments", "")}</div>' if order.get('Comments') else ''}
        
    #     {f'<div><strong>Color:</strong> {order.get("Color", "")}</div>' if order.get('Color') else ''}
    # </div>
    # """, unsafe_allow_html=True)

def create_confirmation_animation(container):
    """
    Create an animated confirmation screen with rotating messages
    
    Args:
        container: streamlit container to render the animation
    """
    messages = [
        "We've got everything covered ✅",
        "Your order is on its way to you 🚚",
        "Your order is excited to meet you 😊"
    ]
    
    # Track the current message index in session state
    if "message_index" not in st.session_state:
        st.session_state.message_index = 0
    
    # Get the current message
    current_message = messages[st.session_state.message_index]
    
    # Display the message with animation
    container.markdown(f"""
    <div style="text-align: center; padding: 2rem; background-color: #f0f8ff; 
                border-radius: 15px; margin: 2rem 0; animation: fadeIn 1s ease-in-out;">
        <div style="font-size: 1.8rem; font-weight: bold; color: #3498db; margin-bottom: 1rem;">
            {current_message}
        </div>
    </div>
    
    <style>
    @keyframes fadeIn {{
        0% {{ opacity: 0; transform: translateY(10px); }}
        100% {{ opacity: 1; transform: translateY(0); }}
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Update message index for next iteration
    st.session_state.message_index = (st.session_state.message_index + 1) % len(messages)

def create_status_badge(status):
    """
    Create a colored badge for order status
    
    Args:
        status (str): The order status
    
    Returns:
        str: HTML string for the status badge
    """
    color_map = {
        'Delivered': '#27ae60',  # Green
        'In route from warehouse': '#f39c12',  # Orange
        'In Process': '#3498db',  # Blue
        'Out for delivery': '#9b59b6',  # Purple
        'Received': '#2ecc71',  # Light Green
        'Not started': '#e74c3c',  # Red
        'cancelled': '#95a5a6'   # Gray
    }
    
    color = color_map.get(status, '#95a5a6')  # Default to gray
    
    return f"""
    <div style="background-color: {color}; color: white; padding: 0.25rem 0.5rem; 
                border-radius: 10px; font-size: 0.8rem; display: inline-block;">
        {status}
    </div>
    """

def create_animated_confirmation_page():
    """
    Create a full page animated confirmation screen
    
    This function creates a rotating animation between three messages,
    with fade-in/fade-out transitions.
    """
    # Container for the animation
    animation_container = st.empty()
    
    # Messages to rotate through
    messages = [
        "We've got everything covered",
        "Your order is on its way to you",
        "Your order is excited to meet you"
    ]
    
    # Only animate if the session is recent
    if "animation_start_time" not in st.session_state:
        st.session_state.animation_start_time = time.time()
        st.session_state.animation_message_index = 0
    
    # Only show animation for a maximum of 2 minutes
    elapsed_time = time.time() - st.session_state.animation_start_time
    
    if elapsed_time < 120:  # 2 minutes in seconds
        # Get current message
        message = messages[st.session_state.animation_message_index]
        
        # Display with animation
        animation_container.markdown(f"""
        <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; 
                    min-height: 50vh; text-align: center; animation: fadeIn 2s ease-in-out;">
            <div style="font-size: 2.2rem; font-weight: bold; color: #3498db; margin-bottom: 1rem;">
                {message}
            </div>
            <div style="font-size: 3rem; margin: 1rem 0;">
                {'✅' if st.session_state.animation_message_index == 0 else '🚚' if st.session_state.animation_message_index == 1 else '😊'}
            </div>
        </div>
        
        <style>
        @keyframes fadeIn {{
            0% {{ opacity: 0; }}
            20% {{ opacity: 1; }}
            80% {{ opacity: 1; }}
            100% {{ opacity: 0; }}
        }}
        </style>
        """, unsafe_allow_html=True)
        
        # Update message index
        st.session_state.animation_message_index = (st.session_state.animation_message_index + 1) % len(messages)
        
        # Sleep briefly to control animation timing
        time.sleep(2.5)
        
        # Update the UI
        st.rerun()
    else:
        # Show static message after time limit
        animation_container.markdown(f"""
        <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; 
                    min-height: 50vh; text-align: center;">
            <div style="font-size: 2.2rem; font-weight: bold; color: #3498db; margin-bottom: 1rem;">
                We've got everything covered
            </div>
            <div style="font-size: 3rem; margin: 1rem 0;">
                ✅
            </div>
        </div>
        """, unsafe_allow_html=True)