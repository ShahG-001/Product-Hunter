# Product Hunter

A beginner-friendly e-commerce product screening app built with **Streamlit + CrewAI + Groq**.

## Agent team

For every category you enter, the app creates one Category Scout. It then adds five shared specialists: Competitor Analyst, Pricing Analyst, Sourcing and Feasibility Analyst, Evidence Reviewer, and Product Recommendation Analyst. A run with two categories therefore uses seven agents. CrewAI runs their tasks as one sequential process so analysts can review earlier outputs. To stay within Groq's free-tier token rate, each run accepts up to two categories and 2,500 characters of notes; research other categories in separate runs.

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

**Streamlit deployment setting:** select Python **3.13** in Advanced settings. The pinned CrewAI release supports Python 3.10–3.13, not 3.14. If an app is already deployed on Python 3.14, Streamlit requires deleting and redeploying it to change Python versions; preserve your URL and re-enter your secrets during redeployment.

## Groq connection

CrewAI's native OpenAI-compatible connection talks to Groq at `https://api.groq.com/openai/v1` using the `GROQ_API_KEY` secret. CrewAI removes its leading `openai/` routing prefix, so the code uses `openai/openai/gpt-oss-120b` to send Groq the exact model ID `openai/gpt-oss-120b`. This configuration uses `custom_openai=True` and does not need CrewAI's optional LiteLLM adapter or a direct Groq SDK call.

Keep the API key out of source code and GitHub. In Streamlit Community Cloud, save it under **App settings → Secrets** as:

```toml
GROQ_API_KEY = "your-groq-key-here"
SERPER_API_KEY = "your-serper-key-here"
```

`SERPER_API_KEY` is optional when live search is turned off. Never commit real keys.
