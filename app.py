
import streamlit as st
import pandas as pd
import requests
import io

st.set_page_config(
    page_title="European Bank Customer Analytics",
    page_icon="🏦",
    layout="wide"
)

@st.cache_data
def load_data():
    token = st.secrets["GITHUB_TOKEN"]

    url = "https://api.github.com/repos/suhanisingh87566-design/european-bank-private-data/contents/European_Bank_Dashboard_Data.csv"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.raw"
    }
    repo_check = requests.get(
        "https://api.github.com/repos/suhanisingh87566-design/european-bank-private-data",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        },
        timeout=30
    )

    if repo_check.status_code != 200:
        st.error(f"Repository Access Error {repo_check.status_code}: {repo_check.text}")
        st.stop()
    response = requests.get(url, headers=headers, timeout=30)

    if response.status_code != 200:
        st.error(f"GitHub Error {response.status_code}: {response.text}")
        st.stop()

    return pd.read_csv(io.BytesIO(response.content))


df = load_data()
# SIDEBAR FILTERS

st.sidebar.title("Dashboard Filters")

countries = sorted(df["Geography"].dropna().unique().tolist())
ages = df["AgeGroup"].dropna().unique().tolist()
genders = sorted(df["Gender"].dropna().unique().tolist())
products = sorted(df["NumOfProducts"].dropna().unique().tolist())

selected_countries = st.sidebar.multiselect(
    "Select Country", countries, default=countries
)

selected_ages = st.sidebar.multiselect(
    "Select Age Group", ages, default=ages
)

selected_genders = st.sidebar.multiselect(
    "Select Gender", genders, default=genders
)

selected_products = st.sidebar.multiselect(
    "Select Number of Products", products, default=products
)

filtered_df = df[
    (df["Geography"].isin(selected_countries)) &
    (df["AgeGroup"].isin(selected_ages)) &
    (df["Gender"].isin(selected_genders)) &
    (df["NumOfProducts"].isin(selected_products))
].copy()

st.title("🏦 European Bank Customer Segmentation & Churn Analytics")
st.caption("Customer behaviour, segmentation and churn patterns")

if filtered_df.empty:
    st.warning("No customers match the selected filters.")
    st.stop()

# SECTION 1: OVERVIEW

st.header("1. Dashboard Overview")

total_customers = len(filtered_df)
exited_customers = int(filtered_df["Exited"].sum())
churn_rate = exited_customers / total_customers * 100
retention_rate = 100 - churn_rate

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Customers", f"{total_customers:,}")
col2.metric("Exited Customers", f"{exited_customers:,}")
col3.metric("Churn Rate", f"{churn_rate:.2f}%")
col4.metric("Retention Rate", f"{retention_rate:.2f}%")

st.divider()

# SECTION 2: GEOGRAPHY

st.header("2. Geography Analysis")

geo_summary = (
    filtered_df.groupby("Geography", observed=True)
    .agg(
        Total_Customers=("Exited", "count"),
        Exited_Customers=("Exited", "sum")
    )
    .reset_index()
)

geo_summary["Churn_Rate"] = (
    geo_summary["Exited_Customers"] /
    geo_summary["Total_Customers"] * 100
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Customer Distribution by Country")
    st.bar_chart(
        geo_summary.set_index("Geography")[["Total_Customers"]]
    )

with col2:
    st.subheader("Churn Rate by Country")
    st.bar_chart(
        geo_summary.set_index("Geography")[["Churn_Rate"]]
    )

st.subheader("Geography Summary")
st.dataframe(geo_summary.round(2), use_container_width=True)

st.divider()

# SECTION 3: DEMOGRAPHICS

st.header("3. Demographic Analysis")

age_summary = (
    filtered_df.groupby("AgeGroup", observed=True)
    .agg(
        Total_Customers=("Exited", "count"),
        Exited_Customers=("Exited", "sum")
    )
    .reset_index()
)

age_summary["Churn_Rate"] = (
    age_summary["Exited_Customers"] /
    age_summary["Total_Customers"] * 100
)

gender_summary = (
    filtered_df.groupby("Gender", observed=True)
    .agg(
        Total_Customers=("Exited", "count"),
        Exited_Customers=("Exited", "sum")
    )
    .reset_index()
)

gender_summary["Churn_Rate"] = (
    gender_summary["Exited_Customers"] /
    gender_summary["Total_Customers"] * 100
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Churn Rate by Age Group")
    st.bar_chart(
        age_summary.set_index("AgeGroup")[["Churn_Rate"]]
    )

with col2:
    st.subheader("Churn Rate by Gender")
    st.bar_chart(
        gender_summary.set_index("Gender")[["Churn_Rate"]]
    )

st.subheader("Age Group Summary")
st.dataframe(age_summary.round(2), use_container_width=True)

st.subheader("Gender Summary")
st.dataframe(gender_summary.round(2), use_container_width=True)

st.divider()

# SECTION 4: CUSTOMER SEGMENTATION

st.header("4. Customer Segmentation Analysis")

segment_options = {
    "Age Group": "AgeGroup",
    "Balance Group": "BalanceGroup",
    "Product Group": "ProductGroup",
    "Account Activity": "ActivityGroup",
    "Tenure Group": "TenureGroup",
    "Credit Score Group": "CreditScoreGroup"
}

selected_segment = st.selectbox(
    "Choose a Segmentation Dimension",
    list(segment_options.keys())
)

segment_column = segment_options[selected_segment]

segment_summary = (
    filtered_df.groupby(segment_column, observed=True)
    .agg(
        Total_Customers=("Exited", "count"),
        Exited_Customers=("Exited", "sum")
    )
    .reset_index()
)

segment_summary["Churn_Rate"] = (
    segment_summary["Exited_Customers"] /
    segment_summary["Total_Customers"] * 100
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Customer Distribution")
    st.bar_chart(
        segment_summary.set_index(segment_column)[["Total_Customers"]]
    )

with col2:
    st.subheader("Churn Rate by Segment")
    st.bar_chart(
        segment_summary.set_index(segment_column)[["Churn_Rate"]]
    )

st.subheader("Segmentation Summary")
st.dataframe(segment_summary.round(2), use_container_width=True)

st.caption(
    "Segmentation dimensions overlap. These patterns show associations, "
    "not causal relationships."
)

st.divider()

# SECTION 5: PRODUCT ANALYSIS

st.header("5. Product Analysis")

product_summary = (
    filtered_df.groupby("NumOfProducts", observed=True)
    .agg(
        Total_Customers=("Exited", "count"),
        Exited_Customers=("Exited", "sum")
    )
    .reset_index()
    .sort_values("NumOfProducts")
)

product_summary["Stayed_Customers"] = (
    product_summary["Total_Customers"] -
    product_summary["Exited_Customers"]
)

product_summary["Churn_Rate"] = (
    product_summary["Exited_Customers"] /
    product_summary["Total_Customers"] * 100
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Customer Count by Number of Products")
    st.bar_chart(
        product_summary.set_index("NumOfProducts")[["Total_Customers"]]
    )

with col2:
    st.subheader("Churn Rate by Number of Products")
    st.bar_chart(
        product_summary.set_index("NumOfProducts")[["Churn_Rate"]]
    )

st.subheader("Product Analysis Summary")
st.dataframe(product_summary.round(2), use_container_width=True)

st.subheader("Important Observations")

for _, row in product_summary.iterrows():
    product_count = int(row["NumOfProducts"])
    customer_count = int(row["Total_Customers"])
    rate = row["Churn_Rate"]

    if customer_count < 100:
        st.warning(
            f"{product_count} product(s): Only {customer_count} customers "
            f"are in this group. Its churn rate of {rate:.2f}% "
            "should be interpreted cautiously because the sample is small."
        )
    elif customer_count < 300:
        st.info(
            f"{product_count} product(s): {customer_count} customers; "
            f"churn rate {rate:.2f}%. Interpret this group with some caution."
        )

st.caption(
    "Product count and churn are observational patterns. "
    "A high churn rate in a small group does not establish a reliable "
    "general pattern or prove that product count causes churn."
)

st.divider()

# SECTION 6: ACTIVITY ANALYSIS

st.header("6. Activity Analysis")

activity_summary = (
    filtered_df.groupby("ActivityGroup", observed=True)
    .agg(
        Total_Customers=("Exited", "count"),
        Exited_Customers=("Exited", "sum")
    )
    .reset_index()
)

activity_summary["Stayed_Customers"] = (
    activity_summary["Total_Customers"] -
    activity_summary["Exited_Customers"]
)

activity_summary["Churn_Rate"] = (
    activity_summary["Exited_Customers"] /
    activity_summary["Total_Customers"] * 100
)

activity_summary["Customer_Percentage"] = (
    activity_summary["Total_Customers"] /
    activity_summary["Total_Customers"].sum() * 100
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Customer Distribution by Activity")
    st.bar_chart(
        activity_summary.set_index("ActivityGroup")[["Total_Customers"]]
    )

with col2:
    st.subheader("Churn Rate by Activity Status")
    st.bar_chart(
        activity_summary.set_index("ActivityGroup")[["Churn_Rate"]]
    )

st.subheader("Activity Analysis Summary")
st.dataframe(activity_summary.round(2), use_container_width=True)

st.subheader("Key Activity Insights")

if set(activity_summary["ActivityGroup"]) == {"Active", "Inactive"}:

    active_rate = activity_summary.loc[
        activity_summary["ActivityGroup"] == "Active",
        "Churn_Rate"
    ].iloc[0]

    inactive_rate = activity_summary.loc[
        activity_summary["ActivityGroup"] == "Inactive",
        "Churn_Rate"
    ].iloc[0]

    difference = inactive_rate - active_rate

    st.write(
        f"Inactive customers have a churn rate of {inactive_rate:.2f}%, "
        f"compared with {active_rate:.2f}% among active customers."
    )

    st.write(
        f"The observed difference is {difference:.2f} percentage points."
    )

    if difference > 0:
        st.info(
            "Inactive customers show a higher observed churn rate. "
            "The bank could investigate engagement patterns and consider "
            "targeted retention communication."
        )
    elif difference < 0:
        st.info(
            "Active customers show a higher observed churn rate in the "
            "currently filtered data. Further investigation is needed."
        )
    else:
        st.info("Both activity groups have the same observed churn rate.")

else:
    st.info("Select all relevant customer groups to compare activity status.")

st.caption(
    "Activity status and churn are associated patterns, "
    "not proof of causation."
)

st.divider()

# SECTION 7: FINANCIAL ANALYSIS

st.header("7. Financial Analysis")

st.write(
    "This section examines customer account balances and their relationship "
    "with observed churn. Balance is not a direct measure of profitability."
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Customer Balance Distribution")
    st.bar_chart(
        filtered_df["Balance"].value_counts(
            bins=10, sort=False
        ).rename("Customer_Count")
    )

with col2:
    st.subheader("Average Balance by Customer Status")
    average_balance = (
        filtered_df.groupby("Exited", observed=True)["Balance"]
        .mean()
        .rename(index={0: "Stayed", 1: "Exited"})
    )
    st.bar_chart(average_balance)

balance_summary = (
    filtered_df.groupby("BalanceGroup", observed=True)
    .agg(
        Total_Customers=("Exited", "count"),
        Exited_Customers=("Exited", "sum"),
        Average_Balance=("Balance", "mean")
    )
    .reset_index()
)

balance_summary["Churn_Rate"] = (
    balance_summary["Exited_Customers"] /
    balance_summary["Total_Customers"] * 100
)

st.subheader("Balance Group Analysis")

col1, col2 = st.columns(2)

with col1:
    st.write("Customer Distribution by Balance Group")
    st.bar_chart(
        balance_summary.set_index("BalanceGroup")[["Total_Customers"]]
    )

with col2:
    st.write("Churn Rate by Balance Group")
    st.bar_chart(
        balance_summary.set_index("BalanceGroup")[["Churn_Rate"]]
    )

st.dataframe(
    balance_summary.round(2),
    use_container_width=True,
    hide_index=True
)

st.caption(
    "The dataset does not specify the balance currency or unit. "
    "No currency symbol is used. These are descriptive comparisons only."
)

st.divider()

# SECTION 8: CHURN COMPARISON

st.header("8. Churn Comparison")

st.write(
    "This section compares customers who stayed with those who exited "
    "the bank across selected demographic and account characteristics."
)

comparison = (
    filtered_df.groupby("Exited", observed=True)
    .agg(
        Total_Customers=("Exited", "count"),
        Average_Age=("Age", "mean"),
        Average_Credit_Score=("CreditScore", "mean"),
        Average_Balance=("Balance", "mean"),
        Average_Tenure=("Tenure", "mean")
    )
    .reset_index()
)

comparison["Customer_Status"] = comparison["Exited"].map(
    {0: "Stayed", 1: "Exited"}
)

comparison = comparison[
    [
        "Customer_Status",
        "Total_Customers",
        "Average_Age",
        "Average_Credit_Score",
        "Average_Balance",
        "Average_Tenure"
    ]
]

st.subheader("Stayed vs Exited Customer Profile")

st.dataframe(
    comparison.round(2),
    use_container_width=True,
    hide_index=True
)

comparison_chart = comparison.set_index("Customer_Status")[
    [
        "Average_Age",
        "Average_Credit_Score",
        "Average_Balance",
        "Average_Tenure"
    ]
]

st.subheader("Average Customer Characteristics")
st.bar_chart(comparison_chart)

if set(filtered_df["Exited"].unique()) == {0, 1}:

    stayed = filtered_df[filtered_df["Exited"] == 0]
    exited = filtered_df[filtered_df["Exited"] == 1]

    st.subheader("Key Churn Comparison Insights")

    st.write(
        f"Average age: Stayed customers {stayed['Age'].mean():.2f}; "
        f"exited customers {exited['Age'].mean():.2f}."
    )

    st.write(
        f"Average credit score: Stayed customers "
        f"{stayed['CreditScore'].mean():.2f}; exited customers "
        f"{exited['CreditScore'].mean():.2f}."
    )

    st.write(
        f"Average balance: Stayed customers "
        f"{stayed['Balance'].mean():.2f}; exited customers "
        f"{exited['Balance'].mean():.2f}."
    )

    st.write(
        f"Average tenure: Stayed customers "
        f"{stayed['Tenure'].mean():.2f}; exited customers "
        f"{exited['Tenure'].mean():.2f}."
    )

else:
    st.info(
        "Both stayed and exited customers must be present "
        "in the selected filters for a comparison."
    )

st.caption(
    "These differences describe the available dataset. "
    "They do not establish why customers exited."
)

# --------------------------------------------------
# 9. BUSINESS INSIGHTS & RECOMMENDATIONS
# --------------------------------------------------

st.header("9. Business Insights & Recommendations")

st.markdown("""
This section translates the customer churn analysis into practical
recommendations for improving customer retention. These suggestions
are based on observed patterns in the available dataset.
""")

st.subheader("Key Business Findings")

st.markdown("""
**1. Germany has the highest customer churn**

- Germany's churn rate is **32.44%**, compared with 16.15% in France
  and 16.67% in Spain.
- Recommendation: Investigate customer feedback, service quality,
  pricing, and product suitability in Germany before designing
  targeted retention campaigns.

**2. Customers aged 46–55 and 56–65 show high churn**

- The churn rates are **50.57%** and **48.32%**, respectively.
- Recommendation: Study the needs and concerns of these age groups.
  Offer relevant financial guidance and review whether existing
  products meet their expectations.

**3. Inactive customers are more likely to leave**

- Inactive customers have a churn rate of **26.85%**, compared with
  **14.27%** among active customers.
- Recommendation: Test personalised engagement campaigns, useful
  account reminders, and relevant service updates to encourage
  meaningful account activity.

**4. Inactive single-product customers need attention**

- This segment contains 2,521 customers, with 924 exits.
- Its churn rate is **36.65%**.
- Recommendation: Review whether these customers understand the
  bank's available services. Offer relevant products only where
  they match the customer's actual needs.

**5. Customers with 3 or 4 products show very high churn**

- The observed churn rates are 82.71% for 3 products and 100% for
  4 products.
- However, these groups contain only 266 and 60 customers.
- Recommendation: Investigate these cases individually or through
  further research before making major business decisions.
""")

st.subheader("Recommended Retention Action Plan")

recommendation_data = pd.DataFrame({
    "Priority Area": [
        "Geography",
        "Age Group",
        "Account Activity",
        "Customer Engagement",
        "Product Usage",
        "Further Investigation"
    ],
    "Recommended Action": [
        "Investigate the reasons behind higher churn in Germany.",
        "Understand the needs of customers aged 46–65.",
        "Test engagement campaigns for inactive customers.",
        "Improve communication and collect customer feedback.",
        "Review product suitability, especially for inactive single-product customers.",
        "Study small high-churn product groups before drawing conclusions."
    ],
    "Purpose": [
        "Identify country-specific retention issues.",
        "Improve relevance of banking services.",
        "Encourage meaningful account activity.",
        "Identify dissatisfaction earlier.",
        "Improve customer-product fit.",
        "Avoid decisions based on small samples."
    ]
})

st.dataframe(recommendation_data, use_container_width=True)

st.subheader("Important Business Considerations")

st.markdown("""
- These findings show associations, not proven causes of customer churn.
- Retention campaigns should be tested and evaluated before large-scale
  implementation.
- The dataset does not provide revenue, profit, or customer lifetime value.
  Therefore, balance should not be treated as a direct measure of customer
  profitability.
- The currency or unit of the balance and salary fields is not documented.
- The dataset contains only the year 2025, so a time-based churn trend
  cannot be established.
""")

st.info(
    "These recommendations are analytical suggestions. "
    "The bank should validate them using customer feedback, operational "
    "data, and controlled retention experiments."
)
