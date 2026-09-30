"""Streamlit entry point for Product Hunter."""

import os

import streamlit as st

from product_hunter.crew import run_product_hunt

st.set_page_config(page_title="Product Hunter", page_icon="🔎", layout="wide")
st.title("🔎 Product Hunter")
st.caption("A CrewAI research team to help you screen e-commerce product ideas.")

with st.sidebar:
    st.header("Research brief")
    market = st.text_input("Target market", placeholder="United States")
    currency = st.text_input("Currency", value="USD")
    channel = st.selectbox("Sales channel", ["Amazon", "Shopify / own store", "Etsy", "eBay", "Other / undecided"])
    categories_text = st.text_area("Categories to investigate (one per line)", value="Kitchen & home\nPet supplies\nTravel accessories", height=110)
    sourcing_model = st.selectbox("Sourcing model", ["Private label", "Wholesale", "Local production", "Dropshipping", "Undecided"])
    target_margin = st.slider("Target gross margin (%)", 10, 80, 40, 5)

st.subheader("Your research inputs")
st.info(
    "Turn on live web search in the sidebar to let the CrewAI agents search for candidates and competitor/pricing evidence. "
    "Search results are snippets and links, not a complete audit of a marketplace. Paste supplier quotes or your own research below "
    "for better feasibility and unit-economics analysis. A URL pasted here is not fetched automatically."
)
research_notes = st.text_area(
    "Paste notes or data (optional, but improves accuracy)",
    placeholder="Example: product title, price, review count, source URL, observed date; supplier quote, MOQ, shipping estimate; customer pain points...",
    height=190,
)

with st.expander("What the agents do"):
    st.markdown(
        """
        - **Category scouts:** one CrewAI agent for each category you enter; searches when live search is enabled.
        - **Competitor analyst:** looks for competing offers and compares positioning.
        - **Pricing analyst:** looks for displayed prices and considers costs, channel, and target margin.
        - **Feasibility analyst:** checks sourcing, operations, and risk assumptions.
        - **Evidence reviewer:** separates sourced facts from estimates and flags gaps.
        - **Recommendation analyst:** produces a ranked, cautious shortlist.

        A run uses **the number of categories you enter, plus five specialist agents**.
        """
    )

groq_api_key = os.environ.get("GROQ_API_KEY")
if not groq_api_key:
    try:
        groq_api_key = st.secrets.get("GROQ_API_KEY")
    except (FileNotFoundError, KeyError):
        groq_api_key = None

serper_api_key = os.environ.get("SERPER_API_KEY")
if not serper_api_key:
    try:
        serper_api_key = st.secrets.get("SERPER_API_KEY")
    except (FileNotFoundError, KeyError):
        serper_api_key = None

use_web_search = st.checkbox(
    "Use live web search (requires Serper API key)",
    value=bool(serper_api_key),
    help="Search uses CrewAI's Serper tool. It searches the web and returns results/snippets; it does not guarantee marketplace data is complete.",
)

if not groq_api_key:
    st.warning("Add GROQ_API_KEY in Streamlit Community Cloud → App settings → Secrets to run the agents.")
if use_web_search and not serper_api_key:
    st.warning("Live search needs SERPER_API_KEY. Add it in Streamlit Secrets, or turn off live search to analyze pasted notes only.")

run_clicked = st.button("Run product research", type="primary", disabled=not groq_api_key or (use_web_search and not serper_api_key))
if run_clicked:
    categories = [line.strip() for line in categories_text.splitlines() if line.strip()]
    if not market.strip():
        st.error("Enter a target market first.")
    elif not categories:
        st.error("Enter at least one category.")
    elif len(categories) > 6:
        st.error("Use six categories or fewer per run to keep the research focused and within API limits.")
    else:
        brief = {
            "market": market.strip(),
            "currency": currency.strip() or "USD",
            "channel": channel,
            "categories": categories,
            "sourcing_model": sourcing_model,
            "target_margin": target_margin,
            "research_notes": research_notes.strip() or "No external research notes were supplied.",
        }
        try:
            with st.spinner("CrewAI is coordinating the product research team…"):
                result = run_product_hunt(brief, groq_api_key, serper_api_key if use_web_search else None)
            st.success("Research complete")
            st.markdown(result)
            st.download_button("Download this report", data=str(result), file_name="product_hunter_report.md", mime="text/markdown")
        except Exception as exc:
            st.error("The research run did not finish. Check the app logs and confirm your Groq key and model access.")
            st.exception(exc)

st.divider()
st.caption("Research output is decision support, not a verified market study. Validate prices, demand, supplier terms, compliance, and fees before investing.")
