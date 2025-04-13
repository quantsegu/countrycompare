import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Define currency conversion rates
CURRENCY_RATES = {
    "EUR_TO_CHF": 0.95,  # 1 EUR = 0.95 CHF
    "EUR_TO_AED": 3.98,  # 1 EUR = 3.98 AED
}

# Currency formatting function
def format_currency(amount, currency):
    """Format amount with appropriate currency symbol and thousands separator"""
    if currency == "EUR":
        return f"€{amount:,.0f}"
    elif currency == "CHF":
        return f"CHF {amount:,.0f}"
    else:  # AED
        return f"AED {amount:,.0f}"

# Cost of living index (Netherlands as base 100)
COST_OF_LIVING = {
    "NL": 100,  # Base index
    "UAE": 85,  # Dubai is about 15% cheaper overall
    "CH-ZG": 145,  # Zug is about 45% more expensive
}

# Add social security benefits information after cost of living definitions
SOCIAL_SECURITY_BENEFITS = {
    "NL": {
        "rate": "Up to 27.65% total (employer + employee)",
        "unemployment": {
            "contribution": "2.7% (WW-premie)",
            "benefit": "Up to 75% of last salary for 2 months, then 70% for up to 24 months",
            "conditions": "26 weeks of work history, involuntary unemployment"
        },
        "disability": {
            "contribution": "6.75% (WIA)",
            "benefit": "Up to 75% of last salary for long-term disability",
            "conditions": "Minimum 35% work incapacity"
        },
        "healthcare": {
            "contribution": "Basic insurance mandatory (€120-150/month)",
            "benefit": "Universal healthcare coverage",
            "conditions": "Must have basic insurance, can add supplementary"
        },
        "pension": {
            "contribution": "17.9% (AOW)",
            "benefit": "State pension ~€1,300/month (single) after retirement age",
            "conditions": "Based on years of residence in NL"
        }
    },
    "UAE": {
        "rate": "No mandatory social security for expats",
        "unemployment": {
            "contribution": "None",
            "benefit": "No unemployment benefits for expats",
            "conditions": "End of service gratuity only"
        },
        "disability": {
            "contribution": "Covered by mandatory health insurance",
            "benefit": "Depends on private insurance coverage",
            "conditions": "Based on insurance policy terms"
        },
        "healthcare": {
            "contribution": "Employer must provide basic coverage",
            "benefit": "Private healthcare coverage",
            "conditions": "Coverage level depends on insurance plan"
        },
        "pension": {
            "contribution": "None for expats",
            "benefit": "End of service gratuity: 21 days salary per year for first 5 years, 30 days per year after",
            "conditions": "Minimum 1 year of service"
        }
    },
    "CH-ZG": {
        "rate": "Up to 13.8% total (employer + employee)",
        "unemployment": {
            "contribution": "2.2% (ALV)",
            "benefit": "70-80% of last salary for up to 18 months",
            "conditions": "12 months contributions in last 2 years"
        },
        "disability": {
            "contribution": "1.4% (IV)",
            "benefit": "Up to 100% pension based on degree of disability",
            "conditions": "Minimum 40% work incapacity"
        },
        "healthcare": {
            "contribution": "Basic insurance mandatory (300-400 CHF/month)",
            "benefit": "High-quality healthcare coverage",
            "conditions": "Must have basic insurance, can add supplementary"
        },
        "pension": {
            "contribution": "10.2% (AHV/AVS)",
            "benefit": "Up to 2,390 CHF/month maximum state pension",
            "conditions": "Based on years of contributions"
        }
    }
}

def adjust_for_cost_of_living(amount, country):
    """Adjust amount based on cost of living index (higher index = more expensive)"""
    nl_equivalent = (amount * 100) / COST_OF_LIVING[country]
    return nl_equivalent

# Add currency conversion functions after the CURRENCY_RATES definition
def convert_to_eur(amount, from_currency):
    if from_currency == "EUR":
        return amount
    elif from_currency == "CHF":
        return amount / CURRENCY_RATES["EUR_TO_CHF"]
    elif from_currency == "AED":
        return amount / CURRENCY_RATES["EUR_TO_AED"]
    return amount

st.set_page_config(page_title="NL vs CH & Dubai Comparison", layout="wide")

st.title("Netherlands vs Switzerland (Zug) & Dubai Comparison")
st.write("Compare income scenarios and lifestyle factors between locations")

# Create main tabs
tab_income, tab_factors = st.tabs(["💰 Income Scenarios", "🌟 Lifestyle Factors"])

with tab_income:
    # Add master inputs at the top
    st.subheader("Master Income Parameters")
    col1, col2 = st.columns(2)
    
    with col1:
        master_daily_rate = st.number_input(
            "Daily Rate (EUR)",
            min_value=200,
            max_value=2000,
            value=800,
            step=50,
            help="Base daily rate in EUR for all calculations"
        )
        
    with col2:
        working_days = st.number_input(
            "Working Days per Year",
            min_value=100,
            max_value=240,
            value=220,
            step=5,
            help="Number of working days per year"
        )

    # Calculate master annual income
    master_annual_income = master_daily_rate * working_days
    
    # Display equivalent annual incomes in different currencies
    st.write("### Equivalent Annual Income")
    curr_col1, curr_col2, curr_col3 = st.columns(3)
    with curr_col1:
        st.metric("EUR", f"€{master_annual_income:,.0f}")
    with curr_col2:
        st.metric("CHF", f"CHF {master_annual_income * CURRENCY_RATES['EUR_TO_CHF']:,.0f}")
    with curr_col3:
        st.metric("AED", f"AED {master_annual_income * CURRENCY_RATES['EUR_TO_AED']:,.0f}")

    # Define the scenarios with their respective tax rates
    base_scenarios = [
        # Netherlands scenarios
        {
            "scenario": "NL: Regular Salary",
            "country": "NL",
            "currency": "EUR",
            "income_tax_rate": 0.3961,
            "social_security_rate": 0.0669,
            "needs_hourly": False,
            "description": "Standard Dutch employment"
        },
        {
            "scenario": "NL: BV Retention",
            "country": "NL",
            "currency": "EUR",
            "income_tax_rate": 0.3961,
            "corporate_tax_rate": 0.25,
            "dividend_tax_rate": 0.25,
            "social_security_rate": 0.0669,
            "min_salary": 60000,
            "needs_hourly": True,
            "description": "Dutch BV with minimum salary and maximum retention"
        },
        # Dubai scenarios
        {
            "scenario": "Dubai: Regular Salary",
            "country": "UAE",
            "currency": "AED",
            "income_tax_rate": 0.0,
            "social_security_rate": 0.0,
            "pension_rate": 0.0,
            "needs_hourly": False,
            "description": "UAE employment in Dubai"
        },
        {
            "scenario": "Dubai: FZ Company",
            "country": "UAE",
            "currency": "AED",
            "income_tax_rate": 0.0,
            "social_security_rate": 0.0,
            "pension_rate": 0.0,
            "corporate_tax_rate": 0.09,
            "dividend_tax_rate": 0.0,
            "min_salary": 60000 * CURRENCY_RATES['EUR_TO_AED'],  # Convert EUR to AED
            "needs_hourly": True,
            "description": "Dubai Free Zone Company with minimum salary and maximum retention"
        },
        # Zug scenarios
        {
            "scenario": "Zug: Regular Salary",
            "country": "CH-ZG",
            "currency": "CHF",
            "income_tax_rate": 0.05,
            "social_security_rate": 0.0515,
            "pension_rate": 0.0865,
            "needs_hourly": False,
            "description": "Swiss employment in Zug"
        },
        {
            "scenario": "Zug: AG Retention",
            "country": "CH-ZG",
            "currency": "CHF",
            "income_tax_rate": 0.05,
            "social_security_rate": 0.0515,
            "pension_rate": 0.0865,
            "corporate_tax_rate": 0.1152,
            "dividend_tax_rate": 0.0,
            "min_salary": 60000 * CURRENCY_RATES['EUR_TO_CHF'],  # Convert EUR to CHF
            "needs_hourly": True,
            "description": "Swiss AG in Zug with minimum salary and maximum retention"
        }
    ]

    # Add tax information in the sidebar
    with st.sidebar:
        st.header("Tax Information")
        st.markdown("""
        ### Netherlands (BV)
        - Corporate tax: 19% (up to €395k), 25.8% (over €395k)
        - Dividend tax: 25%
        - VAT (BTW): 21%
        - Income tax: up to 49.5%
        - Minimum director salary: €60,000
        
        ### Dubai (Free Zone)
        - Corporate tax: 9% (as of 2023)
        - No personal income tax
        - No dividend tax
        - VAT: 5%
        - No social security for expats
        - Minimum salary requirement: AED 238,800 (€60,000 equivalent)
        
        ### Zug (AG)
        - Corporate tax: 11.52% (Federal 8.5% + Cantonal 3.02%)
        - No dividend tax for residents
        - VAT (MwSt): 7.7%
        - Income tax: ~5% (combined)
        - Minimum salary requirement: CHF 57,000 (€60,000 equivalent)
        """)

    # Create sections for expense inputs
    st.subheader("Company Expenses")
    expense_cols = st.columns(len(base_scenarios))
    scenarios = []

    # Initialize session state for storing values if not already initialized
    if 'scenario_values' not in st.session_state:
        st.session_state.scenario_values = {
            idx: {
                'company_expenses': 0
            } for idx in range(len(base_scenarios))
        }

    for idx, (col, base_scenario) in enumerate(zip(expense_cols, base_scenarios)):
        with col:
            st.markdown(f"**{base_scenario['scenario']}**")
            st.caption(base_scenario['description'])
            
            # Convert master annual income to scenario currency
            if base_scenario['currency'] == 'EUR':
                gross_income = master_annual_income
                currency_symbol = '€'
            elif base_scenario['currency'] == 'CHF':
                gross_income = master_annual_income * CURRENCY_RATES['EUR_TO_CHF']
                currency_symbol = 'CHF'
            else:  # AED
                gross_income = master_annual_income * CURRENCY_RATES['EUR_TO_AED']
                currency_symbol = 'AED'

            company_expenses = st.number_input(
                f"Additional Expenses ({currency_symbol})",
                min_value=0,
                max_value=int(gross_income * 0.5),  # Max 50% of gross income
                value=st.session_state.scenario_values[idx]['company_expenses'],
                step=1000,
                key=f"expense_{idx}"
            )
            
            # Update session state
            st.session_state.scenario_values[idx]['company_expenses'] = company_expenses
            
            # Create complete scenario with all parameters
            scenario = base_scenario.copy()
            scenario["gross_income"] = gross_income
            scenario["company_expenses"] = company_expenses
            scenarios.append(scenario)

    # Calculate net retention and its percentage for each scenario
    results = []
    for scenario in scenarios:
        scenario_type = scenario["scenario"]
        gross_income = scenario["gross_income"]
        company_expenses = scenario["company_expenses"]
        currency = scenario["currency"]
        country = scenario["country"]
        
        # Initialize tax components
        personal_tax = 0
        corporate_tax = 0
        dividend_tax = 0
        social_security = 0
        pension = 0
        
        if "Self-employed" in scenario_type:
            # Apply deductions before tax
            if "NL" in scenario_type:
                taxable_income = gross_income - scenario["self_employment_deduction"] - company_expenses
            else:
                taxable_income = gross_income - company_expenses
                
            personal_tax = taxable_income * scenario["income_tax_rate"]
            social_security = taxable_income * scenario.get("social_security_rate", 0)
            net_income = taxable_income - personal_tax - social_security
        
        elif "AG" in scenario_type or "BV" in scenario_type:
            # Use minimum salary for all BV/AG scenarios
            salary = scenario["min_salary"]
            personal_tax = salary * scenario["income_tax_rate"]
            social_security = salary * scenario.get("social_security_rate", 0)
            pension = salary * scenario.get("pension_rate", 0)
            
            # Calculate corporate portion (everything above minimum salary)
            corporate_income = gross_income - salary - company_expenses
            if corporate_income > 0:
                corporate_tax = corporate_income * scenario["corporate_tax_rate"]
                # No immediate dividend distribution, keep as retained earnings
                retained_earnings = corporate_income - corporate_tax
                net_income = (salary - personal_tax - social_security - pension) + retained_earnings
            else:
                net_income = salary - personal_tax - social_security - pension
        
        else:
            # Regular salary scenarios
            taxable_income = gross_income - company_expenses
            personal_tax = taxable_income * scenario["income_tax_rate"]
            social_security = taxable_income * scenario.get("social_security_rate", 0)
            pension = taxable_income * scenario.get("pension_rate", 0)
            net_income = taxable_income - personal_tax - social_security - pension
        
        # After calculating net_income, add cost of living adjustment
        net_income_adjusted = adjust_for_cost_of_living(net_income, country)
        
        # Store results with tax breakdown
        results.append({
            "Scenario": scenario_type,
            "Country": country,
            "Currency": currency,
            "Gross Income": gross_income,
            "Company Expenses": company_expenses,
            "Net Income": net_income,
            "Net Income (CoL Adjusted)": net_income_adjusted,
            "Personal Tax": personal_tax,
            "Corporate Tax": corporate_tax,
            "Dividend Tax": dividend_tax,
            "Social Security": social_security,
            "Pension": pension,
            "Retention %": (net_income / gross_income) * 100,
            "Cost of Living Index": COST_OF_LIVING[country]
        })

    # Convert results to DataFrame
    df = pd.DataFrame(results)

    # Create EUR version for charts
    df_eur = df.copy()
    currency_cols = ["Gross Income", "Company Expenses", "Net Income", "Net Income (CoL Adjusted)",
                    "Personal Tax", "Corporate Tax", "Dividend Tax", "Social Security", "Pension"]

    # Convert all monetary values to EUR for the chart DataFrame
    for col in currency_cols:
        df_eur[col] = df_eur.apply(lambda x: convert_to_eur(x[col], x['Currency']), axis=1)

    # Create two columns for displaying results
    col1, col2 = st.columns([2, 3])

    with col1:
        st.subheader("Results Table")
        display_df = df.copy()
        currency_cols = ["Gross Income", "Company Expenses", "Net Income", "Net Income (CoL Adjusted)",
                        "Personal Tax", "Corporate Tax", "Dividend Tax", "Social Security", "Pension"]
        
        # Update currency formatting
        for col in currency_cols:
            display_df[col] = display_df.apply(
                lambda x: format_currency(x[col], x['Currency']), 
                axis=1
            )
        display_df["Retention %"] = display_df["Retention %"].apply(lambda x: f"{x:.1f}%")
        display_df["Cost of Living Index"] = display_df["Cost of Living Index"].apply(lambda x: f"{x:.0f}")
        
        # Create simplified view
        simple_df = display_df[["Scenario", "Net Income", "Net Income (CoL Adjusted)", "Cost of Living Index", "Retention %"]]
        st.table(simple_df)
        
        with st.expander("Show Full Breakdown"):
            display_cols = [col for col in display_df.columns if col not in ['Country', 'Currency']]
            st.table(display_df[display_cols])

    with col2:
        # Create tabs for different visualizations
        tab1, tab2 = st.tabs(["Income Breakdown", "Net Income Comparison"])
        
        with tab1:
            st.subheader("Full Income Breakdown (in EUR)")
            # Create stacked bar chart using plotly
            fig1 = go.Figure()
            
            # Add bars for each component using df_eur
            components = [
                ("Net Income", "rgb(53, 167, 137)"),
                ("Personal Tax", "rgb(251, 133, 0)"),
                ("Corporate Tax", "rgb(255, 65, 54)"),
                ("Dividend Tax", "rgb(128, 0, 128)"),
                ("Social Security", "rgb(55, 83, 109)"),
                ("Pension", "rgb(0, 128, 128)"),
                ("Company Expenses", "rgb(169, 169, 169)")
            ]
            
            for component, color in components:
                fig1.add_trace(go.Bar(
                    name=component,
                    x=df_eur["Scenario"],
                    y=df_eur[component],  # Use df_eur for EUR values
                    marker_color=color,
                    text=df_eur[component].apply(lambda x: f"€{x:,.0f}"),
                    textposition="inside"
                ))
            
            fig1.update_layout(
                barmode='stack',
                height=600,
                yaxis_title="Amount in EUR",
                xaxis_title="Scenario",
                legend_title="Components",
                font=dict(size=12),
                xaxis_tickangle=-75,
                margin=dict(b=150)
            )
            
            st.plotly_chart(fig1, use_container_width=True)
        
        with tab2:
            st.subheader("Net Income & Cost of Living Comparison (in EUR)")
            fig2 = go.Figure()
            
            # Add nominal net income bars
            fig2.add_trace(go.Bar(
                name="Net Income",
                x=df_eur["Scenario"],
                y=df_eur["Net Income"],
                marker_color="rgb(53, 167, 137)",
                text=df_eur["Net Income"].apply(lambda x: f"€{x:,.0f}"),
                textposition="inside"
            ))
            
            # Add CoL adjusted net income line
            fig2.add_trace(go.Scatter(
                name="Net Income (CoL Adjusted)",
                x=df_eur["Scenario"],
                y=df_eur["Net Income (CoL Adjusted)"],
                line=dict(color="rgb(255, 165, 0)", width=3),  # Orange line
                mode="lines+markers+text",
                text=df_eur["Net Income (CoL Adjusted)"].apply(lambda x: f"€{x:,.0f}"),
                textposition="top center"
            ))
            
            # Add retention percentage line
            fig2.add_trace(go.Scatter(
                name="Retention %",
                x=df_eur["Scenario"],
                y=df_eur["Retention %"],
                yaxis="y2",
                line=dict(color="rgb(255, 65, 54)", width=3),
                mode="lines+markers+text",
                text=df_eur["Retention %"].apply(lambda x: f"{x:.1f}%"),
                textposition="top center"
            ))
            
            fig2.update_layout(
                height=600,
                yaxis=dict(
                    title="Amount in EUR",
                    tickfont=dict(color="rgb(53, 167, 137)")
                ),
                yaxis2=dict(
                    title="Retention %",
                    tickfont=dict(color="rgb(255, 65, 54)"),
                    overlaying="y",
                    side="right",
                    range=[0, 100]
                ),
                xaxis_title="Scenario",
                legend_title="Metrics",
                font=dict(size=12),
                xaxis_tickangle=-75,
                margin=dict(b=150),
                showlegend=True
            )
            
            st.plotly_chart(fig2, use_container_width=True)

            # Add explanatory note about cost of living adjustment
            st.markdown("""
            ### Notes:
            - Cost of Living Index: Netherlands = 100 (base)
            - Dubai: 85 (15% cheaper than NL)
            - Zug: 145 (45% more expensive than NL)
            - Adjusted values show the equivalent purchasing power in Netherlands
            - All chart values are in EUR
            - Table values are in local currencies
            """)

    # Add explanatory notes
    st.markdown("""
    ### Notes:
    - All chart values are converted to EUR for easy comparison
    - Table values remain in local currencies (EUR, CHF, AED)
    - Tax rates based on 2023/2024 rates
    - Netherlands (NL):
      - BV scenarios assume minimum salary of €60,000
      - Corporate tax: 19% up to €395k, 25.8% above
      - Dividend tax: 25%

    - Dubai (UAE):
      - No personal income tax
      - 9% corporate tax (as of 2023)
      - Minimum salary requirement in AED
      - No social security for expats

    - Zug (CH):
      - Personal tax ~5%
      - Combined federal (8.5%) and cantonal (3.02%) corporate tax
      - Minimum salary requirement in CHF
    """)

    # Add social security benefits section after the charts
    st.header("Social Security Benefits by Location")
    st.write("Compare social security contributions and benefits across locations")

    # Create tabs for each location
    nl_tab, dubai_tab, zug_tab = st.tabs(["🇳🇱 Netherlands", "🇦🇪 Dubai", "🇨🇭 Zug"])

    def format_benefit_section(location_data):
        st.write(f"**Overall Rate:** {location_data['rate']}")
        
        # Unemployment Benefits
        st.subheader("🏢 Unemployment Protection")
        cols = st.columns([1, 2])
        with cols[0]:
            st.write("Contribution:")
            st.write("Benefit:")
            st.write("Conditions:")
        with cols[1]:
            st.write(f"{location_data['unemployment']['contribution']}")
            st.write(f"{location_data['unemployment']['benefit']}")
            st.write(f"{location_data['unemployment']['conditions']}")
        
        # Disability Benefits
        st.subheader("🏥 Disability Coverage")
        cols = st.columns([1, 2])
        with cols[0]:
            st.write("Contribution:")
            st.write("Benefit:")
            st.write("Conditions:")
        with cols[1]:
            st.write(f"{location_data['disability']['contribution']}")
            st.write(f"{location_data['disability']['benefit']}")
            st.write(f"{location_data['disability']['conditions']}")
        
        # Healthcare
        st.subheader("⚕️ Healthcare System")
        cols = st.columns([1, 2])
        with cols[0]:
            st.write("Contribution:")
            st.write("Benefit:")
            st.write("Conditions:")
        with cols[1]:
            st.write(f"{location_data['healthcare']['contribution']}")
            st.write(f"{location_data['healthcare']['benefit']}")
            st.write(f"{location_data['healthcare']['conditions']}")
        
        # Pension
        st.subheader("👴 Pension System")
        cols = st.columns([1, 2])
        with cols[0]:
            st.write("Contribution:")
            st.write("Benefit:")
            st.write("Conditions:")
        with cols[1]:
            st.write(f"{location_data['pension']['contribution']}")
            st.write(f"{location_data['pension']['benefit']}")
            st.write(f"{location_data['pension']['conditions']}")

    with nl_tab:
        st.subheader("Netherlands Social Security System")
        st.write("""
        The Dutch social security system is comprehensive and provides extensive coverage.
        It's based on residency and employment, with both employers and employees contributing.
        """)
        format_benefit_section(SOCIAL_SECURITY_BENEFITS["NL"])
        
    with dubai_tab:
        st.subheader("Dubai Social Security System")
        st.write("""
        Dubai's system for expats is primarily private insurance-based with minimal state benefits.
        Employers are required to provide certain basic coverages and end-of-service benefits.
        """)
        format_benefit_section(SOCIAL_SECURITY_BENEFITS["UAE"])
        
    with zug_tab:
        st.subheader("Zug Social Security System")
        st.write("""
        The Swiss social security system is well-structured and provides good coverage,
        though with higher out-of-pocket costs than the Netherlands. It combines state and
        private elements.
        """)
        format_benefit_section(SOCIAL_SECURITY_BENEFITS["CH-ZG"])

    # Add summary comparison
    st.subheader("Quick Comparison")
    comparison_df = pd.DataFrame({
        "Location": ["Netherlands", "Dubai", "Zug"],
        "Social Security Rate": [
            SOCIAL_SECURITY_BENEFITS["NL"]["rate"],
            SOCIAL_SECURITY_BENEFITS["UAE"]["rate"],
            SOCIAL_SECURITY_BENEFITS["CH-ZG"]["rate"]
        ],
        "Unemployment Max": [
            "24 months, 70-75%",
            "None (end of service only)",
            "18 months, 70-80%"
        ],
        "Healthcare System": [
            "Universal + Private",
            "Private Only",
            "Universal + Private"
        ],
        "State Pension": [
            "€1,300/month",
            "End of service gratuity",
            "Up to CHF 2,390/month"
        ]
    })

    st.table(comparison_df)

    st.markdown("""
    ### Additional Notes:
    - **Netherlands**: Most comprehensive system with highest contributions but also highest benefits
    - **Dubai**: Lowest contributions but relies heavily on private insurance and company benefits
    - **Zug**: Balance between contributions and benefits, with high-quality healthcare but higher out-of-pocket costs

    ### Important Considerations:
    1. **Netherlands**:
       - Most secure system for unemployment and disability
       - Healthcare has low out-of-pocket costs
       - Pension system includes state, employer, and private pillars

    2. **Dubai**:
       - No unemployment benefits for expats
       - Healthcare quality depends on insurance plan
       - End of service benefits instead of pension
       - Need private planning for long-term security

    3. **Zug**:
       - Strong unemployment protection
       - High-quality but expensive healthcare
       - Good pension system with three pillars
       - Lower contributions than Netherlands
    """)

with tab_factors:
    st.subheader("Location Factor Comparison")
    st.write("Compare quality of life factors between locations")
    
    # Define factors and their scores
    factors = {
        "Cost of Living": {"NL": 7, "Dubai": 6, "Zug": 3},
        "Quality of Life": {"NL": 8, "Dubai": 8, "Zug": 9},
        "Tax Burden": {"NL": 6, "Dubai": 10, "Zug": 9},
        "Education": {"NL": 8, "Dubai": 7, "Zug": 8},
        "Political Stability": {"NL": 9, "Dubai": 8, "Zug": 9},
        "Safety": {"NL": 8, "Dubai": 9, "Zug": 9},
        "Healthcare": {"NL": 8, "Dubai": 7, "Zug": 8},
        "Banking & Privacy": {"NL": 7, "Dubai": 8, "Zug": 9},
        "International Community": {"NL": 9, "Dubai": 9, "Zug": 8},
        "Public Transport": {"NL": 9, "Dubai": 7, "Zug": 8},
        "Nature & Recreation": {"NL": 7, "Dubai": 6, "Zug": 9}
    }
    
    # Create columns for factor weights
    st.write("Adjust importance of different factors (0-10)")
    weights = {}
    factor_cols = st.columns(4)
    for i, (factor, scores) in enumerate(factors.items()):
        with factor_cols[i % 4]:
            weights[factor] = st.slider(
                factor,
                min_value=0,
                max_value=10,
                value=5,
                key=f"weight_{factor.lower().replace(' ', '_')}",  # Add unique keys
                help=f"NL: {scores['NL']}/10, Dubai: {scores['Dubai']}/10, Zug: {scores['Zug']}/10"
            )
    
    # Ensure we don't divide by zero
    total_weight = sum(weights.values())
    if total_weight > 0:
        # Calculate weighted scores
        nl_score = sum(weights[f] * factors[f]["NL"] for f in factors) / total_weight
        dubai_score = sum(weights[f] * factors[f]["Dubai"] for f in factors) / total_weight
        zg_score = sum(weights[f] * factors[f]["Zug"] for f in factors) / total_weight
        
        # Create radar chart
        categories = list(factors.keys())
        nl_values = [factors[f]["NL"] for f in categories]
        dubai_values = [factors[f]["Dubai"] for f in categories]
        zg_values = [factors[f]["Zug"] for f in categories]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=nl_values,
            theta=categories,
            fill='toself',
            name='Netherlands',
            line=dict(color='#FF9999')  # Light red
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=dubai_values,
            theta=categories,
            fill='toself',
            name='Dubai',
            line=dict(color='#FFD700')  # Gold
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=zg_values,
            theta=categories,
            fill='toself',
            name='Zug',
            line=dict(color='#99FF99')  # Light green
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10]
                )),
            showlegend=True,
            title="Location Comparison by Factors",
            height=700,
            template="plotly_white"  # Use a white template for better visibility
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display final scores
        st.subheader("Overall Weighted Scores")
        score_data = pd.DataFrame({
            "Location": ["Netherlands", "Dubai", "Zug"],
            "Score": [f"{nl_score:.1f}/10", f"{dubai_score:.1f}/10", f"{zg_score:.1f}/10"],
            "Raw Score": [nl_score, dubai_score, zg_score]  # Add raw scores for sorting
        }).sort_values(by="Raw Score", ascending=False).drop("Raw Score", axis=1)  # Sort and drop raw scores
        
        st.table(score_data)
    else:
        st.warning("Please adjust at least one factor weight above zero to see the comparison.")
    
    # Add explanatory notes for factors
    with st.expander("See Detailed Factor Explanations"):
        st.markdown("""
        ### Factor Explanations
        
        #### Cost of Living
        - 🇳🇱 NL: High housing costs in major cities, moderate daily expenses
        - 🇦🇪 Dubai: High housing costs, tax-free shopping but expensive lifestyle
        - 🇨🇭 Zug: Extremely high housing costs, highest daily expenses
        
        #### Quality of Life
        - 🇳🇱 NL: Excellent work-life balance, cycling culture
        - 🇦🇪 Dubai: Modern amenities, luxury lifestyle, but very hot climate
        - 🇨🇭 Zug: High standard of living, clean environment, outdoor activities
        
        #### Tax Structure
        - 🇳🇱 NL: Higher tax burden, complex system
        - 🇦🇪 Dubai: No personal income tax, 9% corporate tax, very favorable
        - 🇨🇭 Zug: Very low personal tax, competitive corporate tax
        
        #### International Community
        - 🇳🇱 NL: Very international, especially in major cities
        - 🇦🇪 Dubai: Highly international, expat-dominated society
        - 🇨🇭 Zug: Growing international community, many global companies
        
        #### Healthcare
        - 🇳🇱 NL: Universal healthcare, lower costs
        - 🇦🇪 Dubai: High-quality private healthcare, insurance required
        - 🇨🇭 Zug: High-quality but expensive healthcare
        
        #### Education
        - 🇳🇱 NL: Good public schools, many international schools
        - 🇦🇪 Dubai: Mainly private international schools, high quality but expensive
        - 🇨🇭 Zug: Excellent public schools, some international options
        
        #### Public Transport
        - 🇳🇱 NL: Extensive network, frequent service
        - 🇦🇪 Dubai: Modern metro and bus system, car-dependent culture
        - 🇨🇭 Zug: Very reliable but more expensive
        
        #### Nature & Recreation
        - 🇳🇱 NL: Flat landscape, water activities
        - 🇦🇪 Dubai: Desert activities, beaches, indoor attractions
        - 🇨🇭 Zug: Mountains, lakes, skiing, hiking
        """)

