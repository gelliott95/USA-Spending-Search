from flask import Flask, request, jsonify, send_file
import pandas as pd
import requests
import os

app = Flask(__name__)

def fetch_award_data(recipient_name, award_type_codes, amount_field):
    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
    payload = {
        "filters": {"recipient_search_text": [recipient_name], "award_type_codes": award_type_codes},
        "fields": ["Award ID", "Recipient Name", amount_field, "Description"],
        "sort": amount_field, "order": "desc", "limit": 100, "page": 1
    }
    headers = {"Content-Type": "application/json"}

    all_results = []
    while True:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            results = response.json().get("results", [])
            if not results: break
            all_results.extend(results)
            payload["page"] += 1
        else: break
    return pd.DataFrame(all_results)

@app.route("/fetch", methods=["GET"])
def fetch_data():
    recipient_name = request.args.get("recipient_name")
    award_type = request.args.get("award_type")

    if not recipient_name or not award_type:
        return jsonify({"error": "Missing parameters: recipient_name and award_type are required"}), 400

    award_type_codes = ["A", "B", "C", "D"] if award_type == "Contracts" else ["07", "08"]
    amount_field = "Award Amount" if award_type == "Contracts" else "Loan Value"

    df = fetch_award_data(recipient_name, award_type_codes, amount_field)
    if not df.empty:
        file_path = "temp_output.csv"
        df.to_csv(file_path, index=False)
        return send_file(file_path, as_attachment=True, download_name="data.csv")
    else:
        return jsonify({"message": "No data found."})

if __name__ == "__main__":
    app.run(debug=True)
