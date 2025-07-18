import streamlit as st
import TNB_Non_Domestric as tnb_non_domestic
import TNB_Domestric as tnb_domestic
import pandas as pd # Import pandas
import base64

st.set_page_config(layout="wided")

# --- Custom CSS for DataFrame Output ---
st.markdown(
    """
    <style>
    /* Target the table cells within Streamlit dataframes */
    [data-testid="stDataFrame"] table td {
        font-size: 16px !important; /* Adjust font size as needed */
        font-weight: bold !important; /* Make text bold */
    }
    /* Target the table headers within Streamlit dataframes */
    [data-testid="stDataFrame"] table th {
        font-size: 16px !important; /* Adjust font size as needed */
        font-weight: bold !important; /* Make text bold */
    }
    </style>
    """,
    unsafe_allow_html=True
)
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

add_bg_from_local("backgroud_picture.png") 

st.title("TNB Electricity Bill Calculator and Reverser")

# --- Sidebar for mode and tariff selection (remains largely the same) ---
st.sidebar.header("Select Mode")
mode = st.sidebar.radio("Choose operation:", ["Calculate Bill from Usage", "Estimate Usage from Bill"])

st.sidebar.header("Select Tariff Type")
tariff_type = st.sidebar.radio("Choose Tariff Type:", ["Domestic", "Non-Domestic"])

# --- Conditional logic for Non-Domestic Tariff ---
if tariff_type == "Non-Domestic":
    st.sidebar.header("Select Non-Domestic Tariff Category")
    tariff_category = st.sidebar.selectbox("Choose a category:", 
                                           ['low_General', 'low_TOU', 
                                            'medium_General', 'medium_TOU', 
                                            'high_General', 'high_TOU'])

    if mode == "Calculate Bill from Usage":
        st.header("Calculate Non-Domestic Electricity Bill from Usage")

        # Input Section (can use st.container to group visually)
        with st.container(border=True): # New container for inputs
            st.markdown("### Input Details") # Subheader for inputs
            if tariff_category == 'low_General':
                total_usage = st.number_input("Enter Total Usage (kWh):", min_value=1)
            elif tariff_category == 'low_TOU':
                total_usage = st.number_input("Enter Total Usage (kWh):", min_value=1)
                peak_percent = st.slider("Peak Usage Percentage (%) :", 0, 100, 50)
            elif tariff_category in ['medium_General', 'high_General']:
                total_usage = st.number_input("Enter Total Usage (kWh):", min_value=1)
                maximum_demand = st.number_input("Enter Maximum Demand (kW):", min_value=0.0, format="%.2f")
            elif tariff_category in ['medium_TOU', 'high_TOU']:
                total_usage = st.number_input("Enter Total Usage (kWh):", min_value=1)
                maximum_demand = st.number_input("Enter Maximum Demand (kW):", min_value=0.0, format="%.2f")
                peak_percent = st.slider("Peak Usage Percentage (%) :", 0, 100, 50)
            
            calculate_button = st.button("Calculate Bill")

        if calculate_button:
            result = {}
            if tariff_category == 'low_General':
                if total_usage is not None:
                    result = tnb_non_domestic.calculate_bill_from_usage_nd_low_general(total_usage)
                else: st.warning("Please enter a total usage.")
            elif tariff_category == 'low_TOU':
                if total_usage is not None:
                    result = tnb_non_domestic.calculate_bill_from_usage_nd_TOU(total_usage, peak_percent)
                else: st.warning("Please enter a total usage.")
            elif tariff_category == 'medium_General':
                if total_usage is not None and maximum_demand is not None:
                    result = tnb_non_domestic.calculate_bill_from_usage_nd_medium_general(total_usage, maximum_demand)
                else: st.warning("Please enter total usage and maximum demand.")
            elif tariff_category == 'medium_TOU':
                if total_usage is not None and maximum_demand is not None:
                    result = tnb_non_domestic.calculate_bill_from_usage_nd_medium_TOU(total_usage, maximum_demand, peak_percent)
                else: st.warning("Please enter total usage, maximum demand, and peak percentage.")
            elif tariff_category == 'high_General':
                if total_usage is not None and maximum_demand is not None:
                    result = tnb_non_domestic.calculate_bill_from_usage_nd_high_general(total_usage, maximum_demand)
                else: st.warning("Please enter total usage and maximum demand.")
            elif tariff_category == 'high_TOU':
                if total_usage is not None and maximum_demand is not None:
                    result = tnb_non_domestic.calculate_bill_from_usage_nd_high_TOU(total_usage, maximum_demand, peak_percent)
                else: st.warning("Please enter total usage, maximum demand, and peak percentage.")

            if result:
                st.subheader("Calculation Results:")
                # Convert dictionary to a DataFrame for tabular display
                df_result = pd.DataFrame(result.items(), columns=['Metric', 'Value'])
                df_result['Value'] = df_result['Value'].apply(lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x) # Format numbers
                st.dataframe(df_result, hide_index=True, use_container_width=True) # Display as a table


    elif mode == "Estimate Usage from Bill":
        st.header("Estimate Non-Domestic Usage from Total Bill")
        with st.container(border=True): # New container for inputs
            st.markdown("### Input Details")
            if tariff_category == 'low_General':
                total_bill_input = st.number_input("Enter Total Bill (RM):", min_value=0.0, format="%.2f")
            elif tariff_category == 'low_TOU':
                total_bill_input = st.number_input("Enter Total Bill (RM):", min_value=0.0, format="%.2f")
                peak_percent = st.slider("Assumed Peak Usage Percentage (%):", 0, 100, 50)
            elif tariff_category in ['medium_General', 'high_General']:
                total_bill_input = st.number_input("Enter Total Bill (RM):", min_value=0.0, format="%.2f")
                maximum_demand = st.number_input("Enter Maximum Demand (kW):", min_value=0.0, format="%.2f")
            elif tariff_category in ['medium_TOU', 'high_TOU']:
                total_bill_input = st.number_input("Enter Total Bill (RM):", min_value=0.0, format="%.2f")
                maximum_demand = st.number_input("Enter Maximum Demand (kW):", min_value=0.0, format="%.2f")
                peak_percent = st.slider("Assumed Peak Usage Percentage (%):", 0, 100, 50)
            
            estimate_button = st.button("Estimate Usage")

        if estimate_button:
            result = {}
            if tariff_category == 'low_General':
                if total_bill_input is not None:
                    result = tnb_non_domestic.reverse_tnb_nd_general_bill(total_bill_input)
                else: st.warning("Please enter the total bill amount.")
            elif tariff_category == 'low_TOU':
                if total_bill_input is not None:
                    result = tnb_non_domestic.reverse_tnb_nd_tou_bill(total_bill_input, peak_percent)
                else: st.warning("Please enter the total bill amount and assumed peak percentage.")
            elif tariff_category == 'medium_General':
                if total_bill_input is not None and maximum_demand is not None:
                    result = tnb_non_domestic.reverse_tnb_nd_medium_general_bill(total_bill_input, maximum_demand)
                else: st.warning("Please enter the total bill amount and maximum demand.")
            elif tariff_category == 'medium_TOU':
                if total_bill_input is not None and maximum_demand is not None:
                    result = tnb_non_domestic.reverse_tnb_nd_medium_tou_bill(total_bill_input, maximum_demand, peak_percent)
                else: st.warning("Please enter the total bill amount, maximum demand, and assumed peak percentage.")
            elif tariff_category == 'high_General':
                if total_bill_input is not None and maximum_demand is not None:
                    result = tnb_non_domestic.reverse_tnb_nd_high_general_bill(total_bill_input, maximum_demand)
                else: st.warning("Please enter the total bill amount and maximum demand.")
            elif tariff_category == 'high_TOU':
                if total_bill_input is not None and maximum_demand is not None:
                    result = tnb_non_domestic.reverse_tnb_nd_high_tou_bill(total_bill_input, maximum_demand, peak_percent)
                else: st.warning("Please enter the total bill amount, maximum demand, and assumed peak percentage.")

            if result:
                st.subheader("Estimation Results:")
                if 'error' in result:
                    st.error(result['error'])
                    df_error = pd.DataFrame(result.items(), columns=['Metric', 'Value'])
                    df_error['Value'] = df_error['Value'].apply(lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x)
                    st.dataframe(df_error, hide_index=True, use_container_width=True)
                else:
                    df_result = pd.DataFrame(result.items(), columns=['Metric', 'Value'])
                    df_result['Value'] = df_result['Value'].apply(lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x)
                    st.dataframe(df_result, hide_index=True, use_container_width=True)

# --- Conditional logic for Domestic Tariff ---
elif tariff_type == "Domestic":
    st.sidebar.header("Select Domestic Tariff Category")
    tariff_category = st.sidebar.selectbox("Choose a category:", 
                                           ['general', 'TOU'])

    if mode == "Calculate Bill from Usage":
        st.header("Calculate Domestic Electricity Bill from Usage")
        with st.container(border=True): # New container for inputs
            st.markdown("### Input Details")
            total_usage = st.number_input("Enter Total Usage (kWh):", min_value=1)

            if tariff_category == 'TOU':
                peak_percent = st.slider("Peak Usage Percentage (%) :", 0, 100, 25)
            
            calculate_button = st.button("Calculate Bill")

        if calculate_button:
            result = {}
            if total_usage is not None:
                if tariff_category == 'general':
                    result = tnb_domestic.calculate_bill_from_usage_general(total_usage)
                elif tariff_category == 'TOU':
                    result = tnb_domestic.calculate_bill_from_usage(total_usage, peak_percent)
            else:
                st.warning("Please enter a total usage.")

            if result:
                st.subheader("Calculation Results:")
                df_result = pd.DataFrame(result.items(), columns=['Metric', 'Value'])
                df_result['Value'] = df_result['Value'].apply(lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x)
                st.dataframe(df_result, hide_index=True, use_container_width=True)

    elif mode == "Estimate Usage from Bill":
        st.header("Estimate Domestic Usage from Total Bill")
        with st.container(border=True): # New container for inputs
            st.markdown("### Input Details")
            total_bill_input = st.number_input("Enter Total Bill (RM):", min_value=0.0, format="%.2f")

            if tariff_category == 'TOU':
                peak_percent = st.slider("Assumed Peak Usage Percentage (%):", 0, 100, 25)
            
            estimate_button = st.button("Estimate Usage")

        if estimate_button:
            result = {}
            if total_bill_input is not None:
                if tariff_category == 'general':
                    result = tnb_domestic.reverse_tnb_general_bill(total_bill_input)
                elif tariff_category == 'TOU':
                    result = tnb_domestic.reverse_tnb_tou_bill(total_bill_input, peak_percent)
            else:
                st.warning("Please enter the total bill amount.")

            if result:
                st.subheader("Estimation Results:")
                if 'error' in result:
                    st.error(result['error'])
                    df_error = pd.DataFrame(result.items(), columns=['Metric', 'Value'])
                    df_error['Value'] = df_error['Value'].apply(lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x)
                    st.dataframe(df_error, hide_index=True, use_container_width=True)
                else:
                    df_result = pd.DataFrame(result.items(), columns=['Metric', 'Value'])
                    df_result['Value'] = df_result['Value'].apply(lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x)
                    st.dataframe(df_result, hide_index=True, use_container_width=True)
