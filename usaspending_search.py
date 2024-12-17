import requests
import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import tempfile

def fetch_award_data(recipient_name, award_type_codes, amount_field):
    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
    payload = {
        "filters": {
            "recipient_search_text": [recipient_name],
            "award_type_codes": award_type_codes
        },
        "fields": ["Award ID", "Recipient Name", amount_field, "Description"],
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
            print(f"Fetched page {payload['page']} with {len(results)} records.")
            payload["page"] += 1
        else:
            print("Error:", response.status_code, response.text)
            break

    if all_results:
        df = pd.DataFrame(all_results)
        
        # Remove 'generated_internal_id' if it exists
        if 'generated_internal_id' in df.columns:
            df = df.drop(columns=['generated_internal_id'])

        return df  # Return the DataFrame for further processing (view or save)
    else:
        messagebox.showinfo("No Data", "No data found for the given input.")
        return None

def start_gui():
    def on_submit():
        recipient_name = entry_recipient.get().strip()
        award_type = award_type_var.get()

        if not recipient_name or not award_type:
            messagebox.showerror("Input Error", "All fields must be filled.")
            return

        # Dynamically set award type codes and amount field
        if award_type == "Contracts":
            award_type_codes = ["A", "B", "C", "D"]
            amount_field = "Award Amount"
        else:
            award_type_codes = ["07", "08"]
            amount_field = "Loan Value"

        # Fetch award data
        df = fetch_award_data(recipient_name, award_type_codes, amount_field)
        
        # Check if data is returned
        if df is not None:
            # Save data to a temporary file automatically
            temp_csv_file = tempfile.mktemp(suffix=".csv")
            df.to_csv(temp_csv_file, index=False)

            # Ask the user if they want to view or download
            view_or_download = messagebox.askyesno("View or Download", 
                "Data fetched successfully. Do you want to view it instead of downloading?")

            if view_or_download:
                # Display data in a new window
                view_data_window(df)
                
                # After viewing, delete the temporary CSV file
                if os.path.exists(temp_csv_file):
                    os.remove(temp_csv_file)
                print(f"Deleted the temporary file {temp_csv_file}")
            else:
                # Ask for the final save location
                output_file = filedialog.asksaveasfilename(defaultextension=".csv", 
                                                           filetypes=[("CSV files", "*.csv")])

                if output_file:
                    # Save the data to the specified location
                    df.to_csv(output_file, index=False)
                    messagebox.showinfo("Success", f"Data saved to {output_file} with {len(df)} records.")
                else:
                    messagebox.showinfo("No Save Location", "No file was selected for saving.")
        else:
            messagebox.showinfo("No Data", "No data found for the given input.")

    def view_data_window(df):
        # Create a new window to display the data
        view_window = tk.Toplevel(window)
        view_window.title("View Data")
        view_window.geometry("800x400")

        # Create a Treeview widget with vertical and horizontal scrollbars
        tree_frame = tk.Frame(view_window)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        tree_scroll_y = tk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        tree_scroll_x = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        tree = ttk.Treeview(tree_frame, columns=df.columns.tolist(), show="headings",
                            yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        # Configure the scrollbars
        tree_scroll_y.config(command=tree.yview)
        tree_scroll_x.config(command=tree.xview)

        # Define columns
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor="w")

        # Insert rows into the treeview
        for index, row in df.iterrows():
            tree.insert("", "end", values=row.tolist())

        tree.pack(fill=tk.BOTH, expand=True)

        # Make the treeview columns resizable
        for col in df.columns:
            tree.column(col, width=200, minwidth=100, stretch=tk.YES)

    # Create the main GUI window
    window = tk.Tk()
    window.title("USA Spending Data Fetch Tool")
    window.geometry("400x200")

    # Recipient Name
    tk.Label(window, text="Recipient Name:").pack(pady=(10, 0))
    entry_recipient = tk.Entry(window, width=40)
    entry_recipient.pack()

    # Award Type
    tk.Label(window, text="Select Award Type:").pack(pady=(10, 0))
    award_type_var = tk.StringVar(value="Contracts")
    tk.Radiobutton(window, text="Contracts", variable=award_type_var, value="Contracts").pack()
    tk.Radiobutton(window, text="Loans", variable=award_type_var, value="Loans").pack()

    # Submit Button
    tk.Button(window, text="Fetch Data", command=on_submit).pack(pady=20)

    # Run the GUI
    window.mainloop()

if __name__ == "__main__":
    start_gui()
