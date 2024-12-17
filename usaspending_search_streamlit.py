import streamlit as st
import requests
import pandas as pd

# Define your function to fetch data
def fetch_award_data(recipient_name, award_type):
    # Your API fetching code goes here (no Flask needed)
    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
    payload = {
        "filters": {"recipient_search_text": [recipient_name]},
        "award_type_codes": ["A", "B", "C", "D"] if award_type == "Contracts" else ["07", "08"],
        "fields": ["Award ID", "Recipient Name", "Award Amount", "Description"],
        "limit": 100
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return pd.DataFrame(response.json().get("results", []))
    else:
        return pd.DataFrame()  # Return empty DataFrame in case of error

# Streamlit UI
recipient_name = st.text_input("Recipient Name:")
award_type = st.radio("Award Type", ["Contracts", "Loans"])

if st.button("Fetch Data"):
    data = fetch_award_data(recipient_name, award_type)
    if not data.empty:
        st.write(data)
    else:
        st.write("No data found or an error occurred.")


if __name__ == "__main__":
    app.run(debug=True)
