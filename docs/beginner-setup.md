# Beginner guide: browser → GitHub → Streamlit

This project can be edited and deployed without installing Python or libraries on your laptop. GitHub Codespaces provides the browser-based coding environment, and Streamlit Community Cloud installs the app dependencies when it deploys.

## Step 1: Create your free accounts

1. Create or sign in to a GitHub account at [github.com](https://github.com).
2. Create/sign in to a Streamlit Community Cloud account at [share.streamlit.io](https://share.streamlit.io) and connect it to GitHub.
3. Create/sign in to a Groq account at [console.groq.com](https://console.groq.com) and create an API key.
4. For live web search, create a Serper account at [serper.dev](https://serper.dev) and copy its API key. Serper advertises a 2,500-query free trial; usage beyond included credits is paid.

GitHub Codespaces includes a monthly free quota on eligible personal accounts, and Streamlit describes Community Cloud as free. Quotas and service terms can change. Groq's API has model-specific rate limits, and its pricing page may list paid per-token rates; verify your account's current plan/model charges before running it. This is a free-to-start stack, not a promise of unlimited free AI calls.

## Step 2: Put this project on GitHub

The project files are ready in this folder. To connect this local workspace to your own GitHub repository, create an **empty private or public repository** on GitHub, then use GitHub Desktop (if already available) or the browser's upload flow to upload the project files. Do not upload `.git`, `.env`, or any secret file. The source folder contains a `.gitignore` to help exclude local keys and caches.

For a first-time user, the browser upload route:

1. On GitHub, open your new repository and choose **Add file → Upload files**.
2. Drag in the project files and folders (`app.py`, `product_hunter`, `requirements.txt`, `.gitignore`, `README.md`, and `docs`).
3. Enter a commit message such as `Add Product Hunter starter app` and click **Commit changes**.

Later edits can be made in Codespaces or with GitHub's web editor and committed to the same repository. Each commit updates the repository. After deployment, Community Cloud detects repository updates and redeploys the app.

## Step 3: Add your API key as a secret

Do not put either key in Python code, README files, or a GitHub commit. Add them privately in Streamlit settings in Step 5. The app reads `GROQ_API_KEY`; `SERPER_API_KEY` enables the optional live-search checkbox. If you skip Serper, turn live search off and paste your own research notes.

## Step 4: Start a browser Codespace (optional development check)

1. Open your GitHub repository.
2. Click **Code → Codespaces → Create codespace on main**.
3. In the Codespaces terminal, run:

   ```bash
   pip install -r requirements.txt
   ```

   This installs libraries inside the temporary cloud Codespace, not on your laptop. Add a key to the Codespaces environment only if you want to run the app there; for simple deployment, you can skip this step and let Community Cloud handle the install.
4. To preview the app from Codespaces, set the environment secret `GROQ_API_KEY` in the Codespace and run `streamlit run app.py`. Use the forwarded port link Codespaces displays.
5. Stop or delete the Codespace when done so it stops using its included compute/storage quota.

If you do not want to run a development preview, you can skip Step 4 and deploy directly from GitHub.

## Step 5: Deploy to Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. Click **Create app** and choose your repository, branch (`main`), and entrypoint file (`app.py`).
3. Open **Advanced settings → Secrets** and paste:

   ```toml
   GROQ_API_KEY = "paste-your-real-key-here"
   SERPER_API_KEY = "paste-your-serper-key-here"
   ```

   If you are not using live web search, omit the `SERPER_API_KEY` line.

4. Click **Deploy**. Streamlit installs `requirements.txt` on its server and gives you a `streamlit.app` URL.
5. Open the URL, enter a target market, keep or change the sample categories, leave live search on (if you added the Serper key), paste any supplier/research notes, and click **Run product research**.

If deployment fails, open the app's logs in Streamlit. Common causes are a typo in the secret, an unavailable model, a dependency build issue, or a Groq rate limit.

## Step 6: Make changes and update the live app

Edit the source files in GitHub/Codespaces, commit the change to the connected branch, and push it. Community Cloud watches the connected repository and deploys committed changes automatically. The secret remains in Streamlit settings and should never be added to GitHub.

## Current version boundaries

- Live search returns result snippets and URLs through Serper; the app does not crawl every marketplace listing or automatically open pasted URLs.
- The evidence reviewer checks agent output for gaps, but snippets do not independently verify final checkout prices, sales volume, supplier terms, or compliance.
- API usage has limits and may incur charges depending on Groq's current plan and model pricing.
- Validate supplier terms, marketplace fees, legal/compliance rules, and real demand before buying inventory or spending on ads.
