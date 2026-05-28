import streamlit as st
import requests
import pandas as pd

server_loc = st.secrets["server_url"].rstrip("/")
st.title("Expense Tracker")

opt = st.sidebar.selectbox(
    "Choose Operation",
    ["Add expenses","View expenses","Update expense","Delete expense",
     "Search expenses","Sort expenses","Filter expenses",
     "Generate reports","Analyze Spending"]
)

if opt == "Add expenses":

    st.header("Add New Expense")
    date = st.date_input("Date")
    category = st.selectbox("Category",
        ["Food","Travel","Shopping","Bills","Entertainment","Health","Education","Other"])
    amount = st.number_input("Amount", min_value=0.0, step=0.01)

    payment_method = st.selectbox("Payment Method",
        ["Cash","Credit Card","Debit Card","Online Payment","Other"])
    description = st.text_area("Description")
    if st.button("Add Expense"):
        data = {
            "date": str(date),
            "category": category,
            "amount": amount,
            "payment_method": payment_method,
            "description": description
        }
        response = requests.post(
            f"{server_loc}/add_expense",data=data   # IMPORTANT (matches your FastAPI)
        )
        st.success("Expense added successfully!")

            
elif opt == "View expenses":
    st.header("View Expenses")
    response = requests.get(f"{server_loc}/view_expenses")
    if response.status_code == 200:
        expenses = response.json()
        df = pd.DataFrame(expenses)
        st.dataframe(df)
    else:
        st.error("Failed to retrieve expenses.")
        
elif opt == "Update expense":

    st.header("Update Expense")

    expense_id = st.number_input(
        "Expense ID",
        min_value=1,
        step=1
    )

    date = st.date_input("Date")

    category = st.selectbox(
        "Category",
        [
            "Food",
            "Travel",
            "Shopping",
            "Bills",
            "Entertainment",
            "Health",
            "Education",
            "Other"
        ]
    )

    amount = st.number_input(
        "Amount",
        min_value=0.0,
        step=0.01
    )

    payment_method = st.selectbox(
        "Payment Method",
        [
            "Cash",
            "Credit Card",
            "Debit Card",
            "Online Payment",
            "Other"
        ]
    )

    description = st.text_area("Description")
    if st.button("Update Expense"):

        data = {
            "date": str(date),
            "category": category,
            "amount": amount,
            "payment_method": payment_method,
            "description": description        }

        response = requests.put(
        f"{server_loc}/update_expense/{expense_id}",data=data)

        st.success("Expense updated successfully!")

        
elif opt == "Delete expense":

    st.header("Delete Expense")
    expense_id = st.number_input("Enter Expense ID",min_value=1,step=1)
    if st.button("Delete Expense"):
        response = requests.delete(f"{server_loc}/delete_expense/{expense_id}")
        if response.status_code == 200:
            st.success("Expense deleted successfully!")
        else:
            st.error("Failed to delete expense.")

# ---------------- SEARCH EXPENSES ----------------

elif opt == "Search expenses":
    st.header("Search Expenses")
    category = st.selectbox(
        "Select Category",
        [
            "Food",
            "Travel",
            "Shopping",
            "Bills",
            "Entertainment",
            "Health",
            "Education",
            "Other"
        ]
    )
    if st.button("Search"):
        response = requests.get(f"{server_loc}/search_expenses", params={"category": category})
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            st.dataframe(df)
        else:
            st.error("Failed to search expenses.")

elif opt == "Sort expenses":    
    st.header("Sort Expenses")
    sort_by = st.selectbox("Sort By", ["date", "amount", "category"])
    order = st.selectbox("Order", ["asc", "desc"])

    if st.button("Sort"):
        params = {"sort_by": sort_by, "order": order}
        response = requests.get(f"{server_loc}/sort_expenses", params=params)
        if response.status_code == 200:
            expenses = response.json()
            df = pd.DataFrame(expenses)
            st.dataframe(df)
        else:
            st.error("Failed to sort expenses.")
        
elif opt == "Filter expenses":
    st.header("Filter Expenses")
    category = st.selectbox(
        "Select Category",
        [
            "Food",
            "Travel",
            "Shopping",
            "Bills",
            "Entertainment",
            "Health",
            "Education",
            "Other"
        ]
    )
    min_amount = st.number_input("Minimum Amount",min_value=0.0,step=0.01)
    max_amount = st.number_input("Maximum Amount",min_value=0.0,step=0.01)
    if st.button("Filter Expenses"):
        params = {
            "category": category,
            "min_amount": min_amount,
            "max_amount": max_amount
        }
        response = requests.get(f"{server_loc}/filter_expenses", params=params)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            st.dataframe(df)
        else:
            st.error("Failed to filter expenses.")
            
# ---------------- GENERATE REPORT ----------------
elif opt == "Generate reports":

    st.header("Generate Reports")
    report_type = st.selectbox("Report Type",
        ["Monthly", "Yearly", "Category-wise"])

    if st.button("Generate Report"):

        response = requests.get(f"{server_loc}/generate_report",params={"report_type": report_type})
        if response.status_code == 200:
            report = response.json()
            st.subheader("Total Spending")
            st.write(report["total_amount"])
            df = pd.DataFrame(report["expenses"])
            st.dataframe(df)
        else:
            st.error("Failed to generate report.")
elif opt == "Analyze Spending":
    st.header("Analyze Spending")

    response = requests.get(f"{server_loc}/analyze_spending")

    if response.status_code != 200:
        st.error("Backend not responding")
        st.stop()

    analysis = response.json()

    # ---------------- CATEGORY ANALYSIS ----------------
    st.subheader("Category-wise Spending")
    category_df = pd.DataFrame(
        analysis["category_analysis"],
        columns=["Category", "Total Amount"])
    st.dataframe(category_df)
    st.bar_chart(category_df.set_index("Category"))

    # ---------------- PAYMENT ANALYSIS ----------------
    st.subheader("Payment Method Analysis")
    payment_df = pd.DataFrame(analysis["payment_analysis"],
        columns=["Payment Method", "Total Amount"])
    st.dataframe(payment_df)
    st.line_chart(payment_df.set_index("Payment Method"))

    # ---------------- PIE CHART ----------------
    st.subheader("Spending Distribution")
    pie_df = pd.DataFrame(analysis["category_analysis"])
# ensure correct column names
    pie_df.columns = ["Category", "Total Amount"]
    st.dataframe(pie_df)
    st.bar_chart(pie_df.set_index("Category"))