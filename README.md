# Product Hunter

A beginner-friendly e-commerce product screening app built with **Streamlit + CrewAI + Groq**.

## Agent team

For every category you enter, the app creates one Category Scout. It then adds five shared specialists: Competitor Analyst, Pricing Analyst, Sourcing and Feasibility Analyst, Evidence Reviewer, and Product Recommendation Analyst. A run with three categories therefore uses eight agents. CrewAI runs their tasks as one sequential process so analysts can review earlier outputs.

## Research behavior and limits

Turn on optional live search to give scouts and analysts CrewAI's Serper web-search tool. You need a `SERPER_API_KEY`; Serper offers a limited free trial. Search snippets and links are useful leads, not comprehensive marketplace facts, and pasted URLs are not automatically fetched. Without live search or user-supplied research, demand, price, and competitor claims remain hypotheses.

## Files

- `app.py`: Streamlit interface and user inputs
- `product_hunter/crew.py`: CrewAI roles, tasks, Groq model configuration, and workflow
- `requirements.txt`: dependencies Streamlit Community Cloud installs remotely
- `docs/system-blueprint.md`: architecture, evidence policy, and scoring plan
- `docs/beginner-setup.md`: browser-only GitHub → Streamlit Cloud steps

## Run without installing anything on your laptop

Use GitHub Codespaces in your browser to edit and run the app. When deployed, Streamlit Community Cloud installs packages on its server from `requirements.txt`. You need a Groq API key. Live search additionally needs a Serper API key. Free usage is limited, and Groq model pricing/availability can change. Check current provider limits and pricing before use.

Follow [the browser-only guide](docs/beginner-setup.md).

## Groq connection

CrewAI's `LLM` wrapper talks to Groq using the `GROQ_API_KEY` environment variable. The configured model is `openai/gpt-oss-120b`, served by Groq. This matches the model in the Groq example you supplied, while CrewAI remains responsible for agent orchestration. The Groq Python SDK is not called directly in this CrewAI app.

Keep the API key out of source code and GitHub. In Streamlit Community Cloud, save it under **App settings → Secrets** as:

```toml
GROQ_API_KEY = "your-groq-key-here"
SERPER_API_KEY = "your-serper-key-here"
```

`SERPER_API_KEY` is optional when live search is turned off. Never commit real keys.
