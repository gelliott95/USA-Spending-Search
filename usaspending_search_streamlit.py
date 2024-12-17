import requests
import pandas as pd
import tempfile
import streamlit as st

# Function to fetch award data
def fetch_award_data(recipient_name, award_type_codes, amount_field):
    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
    payload = {
        "filters": {
            "recipient_search_text": [recipient_name],
            "award_type_codes": award_type_codes
        },
        "fields": ["Award ID", "Recipient Name", amount_field, "Description", "generated_internal_id"],  # Removed action_date here
        "sort": amount_field,
        "order": "desc",
        "limit": 100,
        "page": 1
    }
    headers = {"Content-Type": "application/json"}

    all_results = []

    while True:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            results = response.json().get("results", [])
            if not results:
                break
            all_results.extend(results)
            payload["page"] += 1
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            break

    if all_results:
        df = pd.DataFrame(all_results)
        
        # Remove 'generated_internal_id' if it exists
        if 'generated_internal_id' in df.columns:
            df = df.drop(columns=['generated_internal_id'])

        # Reorder columns
        df = df[["Recipient Name", amount_field, "Description", "generated_internal_id", "Award ID"]]
        
        return df
    else:
        st.info("No data found for the given input.")
        return None

# Streamlit UI for the app
def start_streamlit_app():
    st.title("USA Spending Data Fetch Tool")

    # Recipient Name
    recipient_name = st.text_input("Recipient Name:")

    # Award Type
    award_type = st.radio("Select Award Type:", ["Contracts", "Loans"])

    if recipient_name and award_type:
        # Dynamically set award type codes and amount field
        if award_type == "Contracts":
            award_type_codes = ["A", "B", "C", "D"]
            amount_field = "Award Amount"
        else:
            award_type_codes = ["07", "08"]
            amount_field = "Loan Value"

        # Fetch award data
        df = fetch_award_data(recipient_name, award_type_codes, amount_field)
        
        if df is not None:
            # Display data in Streamlit app
            st.subheader(f"Data for {recipient_name} ({award_type}):")
            st.dataframe(df)

            # Option to download the data as CSV
            csv = df.to_csv(index=False)
            st.download_button("Download Data as CSV", csv, file_name="usaspending_data.csv")
            
        else:
            st.info("No data found for the given recipient.")

if __name__ == "__main__":
    start_streamlit_app()
