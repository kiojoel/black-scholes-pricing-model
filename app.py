import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from main import run_calculations, get_live_market_data
from analysis import scenario_analysis, implied_volatility
from pricer import BlackScholesPricer
from datetime import date, timedelta

# Set up the page
st.set_page_config(
    page_title="Black-Scholes Calculator",
    page_icon="📈",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
    .greek-positive {
        color: #00C851;
        font-weight: bold;
    }
    .greek-negative {
        color: #ff4444;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("📈 Black-Scholes Option Pricing Calculator")
st.markdown("""
**Professional options pricing tool** using the Black-Scholes model with real-time market data.
Calculate theoretical prices, Greeks, and perform scenario analysis.
""")

# Single Option Pricer (Main Content)
# Main single option pricer
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 Market Data")
    ticker_input = st.text_input("Stock Ticker", value="AAPL", help="Enter stock symbol (e.g., AAPL, GOOGL, TSLA)")

    # Fetch market data
    if ticker_input:
        try:
            with st.spinner(f'Fetching live data for {ticker_input}...'):
                market_data = get_live_market_data(ticker_input)

            col_price, col_vol = st.columns(2)
            with col_price:
                s_input = st.number_input(
                    "Current Stock Price ($)",
                    value=float(market_data['price']),
                    min_value=0.01,
                    format="%.2f"
                )
            with col_vol:
                sigma_input = st.number_input(
                    "Volatility (σ)",
                    value=float(market_data['volatility']),
                    min_value=0.001,
                    max_value=3.0,
                    format="%.4f",
                    help="Historical volatility calculated from 1-year data"
                )

            # Show market data summary
            st.info(f"📈 Live data for **{ticker_input}**: ${market_data['price']:.2f} | Vol: {market_data['volatility']:.1%}")

        except Exception as e:
            st.error(f"❌ Could not fetch data for {ticker_input}. Using default values.")
            s_input = st.number_input("Current Stock Price ($)", value=100.0, min_value=0.01, format="%.2f")
            sigma_input = st.number_input("Volatility (σ)", value=0.20, min_value=0.001, max_value=3.0, format="%.4f")

    # Fetch live risk-free rate
    try:
        from main import get_risk_free_rate
        with st.spinner('Fetching live risk-free rate...'):
            live_rate = get_risk_free_rate(maturity_days=365)  # Default to 1 year
    except Exception as e:
        st.warning(f"⚠️ Could not fetch live risk-free rate. Using default 5%. Error: {str(e)}")
        live_rate = 0.05

    r_input = st.number_input(
        "Risk-Free Rate (%)",
        value=live_rate * 100,  # Convert to percentage for display
        min_value=0.0,
        max_value=20.0,
        format="%.3f",
        help="Annual risk-free interest rate (fetched from US Treasury data)"
    ) / 100  # Convert back to decimal

with col2:
    st.subheader("⚙️ Option Parameters")
    k_input = st.number_input(
        "Strike Price ($)",
        value=100.0,
        min_value=0.01,
        format="%.2f"
    )

    # Date picker with better default
    today = date.today()
    default_exp = today + timedelta(days=30)  # 30 days from now
    t_input_date = st.date_input(
        "Expiration Date",
        value=default_exp,
        min_value=today + timedelta(days=1),
        help="Option expiration date"
    )

    option_type_input = st.selectbox(
        "Option Type",
        ["Call", "Put"],
        help="Call = right to buy, Put = right to sell"
    )

    # Show time to expiration
    days_to_exp = (t_input_date - today).days
    st.info(f"⏱️ Time to expiration: **{days_to_exp} days** ({days_to_exp/365:.3f} years)")

    with st.expander("🧮 Calculate Implied Volatility from Market Price"):
        # Input for the market price
        market_price_input = st.number_input(
            "Enter the Option's Current Market Price ($)",
            value=10.0,
            min_value=0.01,
            format="%.2f",
            help="The price you see on your brokerage platform."
        )

        # A button within the expander to trigger the calculation
        if st.button("Calculate IV"):
            try:
                # We use all the other inputs from the main UI (s_input, k_input, etc.)
                T = days_to_exp / 365.25

                with st.spinner("Calculating Implied Volatility..."):
                    iv = implied_volatility(
                        market_price=market_price_input,
                        S=s_input,
                        K=k_input,
                        T=max(T, 1e-8),
                        r=r_input,
                        option_type=option_type_input.lower()
                    )

                st.metric("Calculated Implied Volatility (IV)", f"{iv:.2%}")

                # Provide valuable context by comparing IV to Historical Volatility
                hist_vol = sigma_input # sigma_input holds the calculated historical volatility
                vol_premium = iv - hist_vol

                st.info(f"Historical Volatility is **{hist_vol:.2%}**. The market is implying a volatility that is **{abs(vol_premium):.2%}** {'higher' if vol_premium > 0 else 'lower'} than the stock's historical average.")

            except Exception as e:
                st.error(f"Could not calculate Implied Volatility. Error: {e}")

        st.divider() # Another horizontal line

# Calculate button
st.markdown("---")
if st.button("🧮 Calculate Option Price", type="primary", use_container_width=True):
    # Validation
    if s_input <= 0 or k_input <= 0 or sigma_input <= 0:
        st.error("❌ All inputs must be positive values!")
    elif days_to_exp <= 0:
        st.error("❌ Expiration date must be in the future!")
    else:
        # Perform calculation
        T = days_to_exp / 365.25
        T = max(T, 1e-8)  # Prevent division by zero

        pricer = BlackScholesPricer(
            S=s_input, K=k_input, T=T, r=r_input,
            sigma=sigma_input, option_type=option_type_input.lower()
        )

        price = pricer.price()
        greeks = pricer.get_all_greeks()

        # Results section
        st.markdown("## 🎯 Results")

        # Main price display
        col_result1, col_result2, col_result3 = st.columns(3)

        with col_result1:
            st.metric(
                "💰 Option Price",
                f"${price:.2f}",
                help="Theoretical fair value using Black-Scholes model"
            )

        with col_result2:
            intrinsic = max(s_input - k_input, 0) if option_type_input.lower() == 'call' else max(k_input - s_input, 0)
            time_value = price - intrinsic
            st.metric(
                "⏰ Time Value",
                f"${time_value:.2f}",
                help="Premium above intrinsic value"
            )

        with col_result3:
            moneyness = s_input / k_input
            if moneyness > 1.05:
                money_status = "ITM" if option_type_input.lower() == 'call' else "OTM"
            elif moneyness < 0.95:
                money_status = "OTM" if option_type_input.lower() == 'call' else "ITM"
            else:
                money_status = "ATM"

            st.metric(
                "📊 Moneyness",
                money_status,
                f"{moneyness:.2f}",
                help="In-the-Money (ITM), At-the-Money (ATM), or Out-of-the-Money (OTM)"
            )

        # Greeks display - Better formatting
        st.markdown("### 📈 The Greeks (Risk Sensitivities)")

        greeks_col1, greeks_col2, greeks_col3 = st.columns(3)

        with greeks_col1:
            delta_val = greeks['delta']
            delta_color = "greek-positive" if delta_val > 0 else "greek-negative"
            st.markdown(f"""
            **Delta (Δ)**: <span class="{delta_color}">{delta_val:.4f}</span>
            *Price sensitivity to $1 stock move*
            """, unsafe_allow_html=True)

            gamma_val = greeks['gamma']
            st.markdown(f"""
            **Gamma (Γ)**: <span class="greek-positive">{gamma_val:.4f}</span>
            *Delta sensitivity to $1 stock move*
            """, unsafe_allow_html=True)

        with greeks_col2:
            vega_val = greeks['vega'] / 100
            st.markdown(f"""
            **Vega (ν)**: <span class="greek-positive">{vega_val:.4f}</span>
            *Price sensitivity to 1% volatility change*
            """, unsafe_allow_html=True)

            theta_val = greeks['theta'] / 365
            theta_color = "greek-negative" if theta_val < 0 else "greek-positive"
            st.markdown(f"""
            **Theta (Θ)**: <span class="{theta_color}">{theta_val:.4f}</span>
            *Daily time decay*
            """, unsafe_allow_html=True)

        with greeks_col3:
            rho_val = greeks['rho'] / 100
            rho_color = "greek-positive" if rho_val > 0 else "greek-negative"
            st.markdown(f"""
            **Rho (ρ)**: <span class="{rho_color}">{rho_val:.4f}</span>
            *Sensitivity to 1% rate change*
            """, unsafe_allow_html=True)

        # --- SCENARIO ANALYSIS ---
        st.markdown("---")
        st.subheader("🔎 Scenario Analysis")

        # Create a range of stock prices around the current price
    current_price = s_input
    price_range = np.linspace(current_price * 0.75, current_price * 1.25, 50) # -25% to +25%

    # Run the analysis
    scenario_df = scenario_analysis(pricer, price_range)

    # Create an interactive Plotly chart
    fig = px.line(
        scenario_df,
        x='Stock Price',
        y='P&L',
        title='Option P&L vs. Underlying Stock Price',
        labels={'Stock Price': 'Underlying Stock Price ($)', 'P&L': 'Profit / Loss ($)'}
    )

    # Add a horizontal line at P&L = 0 (breakeven point relative to initial price)
    fig.add_hline(y=0, line_dash="dash", line_color="gray")

    # Add a vertical line at the current stock price
    fig.add_vline(x=current_price, line_dash="dash", line_color="red", annotation_text="Current Price")

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("View Scenario Data Table"):
        st.dataframe(scenario_df)



# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.8em;'>
📊 Built with Streamlit | 🧮 Powered by Black-Scholes Model | 📈 Real-time data via Yahoo Finance
</div>
""", unsafe_allow_html=True)