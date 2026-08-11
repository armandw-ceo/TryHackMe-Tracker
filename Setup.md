This guide will help you configure the automated pipeline that fetches your completed TryHackMe labs from your private Notion tracker and injects them directly into your public GitHub Profile layout.

## 📋 Prerequisites
Before starting, ensure you have:
* A public GitHub repository named exactly after your GitHub username.
* A free Notion account.

---

## 🏗️ Step-by-Step Instructions

### Step 1: Configure Your Notion Database
1. Create a new **Table View** database in Notion.
2. Ensure your columns use these **exact case-sensitive names and data types**:
   * **`Name`** (Title) ➡️ *The name of your room*
   * **`Category`** (Select) ➡️ *Options: `Red Team`, `Blue Team`, `Purple Team`*
   * **`Difficulty`** (Select) ➡️ *Options: `Info`, `Easy`, `Medium`, `Hard`, `Insane`*
   * **`Completed`** (Date) ➡️ *The date you finished the lab*
   * **`Url`** (Url) ➡️ *Direct link to the TryHackMe room*

### Step 2: Create a Notion Internal Integration
1. Go to the web browser portal: [Notion Developers Hub](https://notion.so).
2. Click **+ New integration**.
3. Name your integration (e.g., `THM Profile Sync`), select your correct workspace, and click **Submit**.
4. Click **Show** under your secrets field and copy the token starting with **`ntn_`**. Keep this private.

### Step 3: Link Your Database to the Integration
1. Open your custom TryHackMe Tracker database page inside your Notion workspace.
2. Click the **three dots (`...`)** located in the very top-right corner of the Notion app interface window.
3. Scroll down, click **Connect to**, search for your integration name, and click it to grant authorization.

### Step 4: Add Your Encrypted Repository Secrets
To keep your public profile secure, your private keys are hidden in your repository settings:
1. Navigate to your GitHub Profile repository page on **GitHub.com**.
2. Click the **Settings** gear icon tab at the top.
3. Expand **Secrets and variables** in the left sidebar and select **Actions**.
4. Click **New repository secret** and add your integration token:
   * **Name:** `NOTION_TOKEN`
   * **Secret:** *(Paste your clean token string starting with `ntn_`)*
5. Click **New repository secret** again to save your database tracker ID:
   * **Name:** `NOTION_DATABASE_ID`
   * **Secret:** *(Paste only the 32-character alpha-numeric ID block from your Notion database URL. Strip away any slashes, workspace names, or text after a question mark `?`)*

### Step 5: Put Placeholder Anchors in Your Profile
Open your profile's main **`README.md`** file on GitHub and insert these exact hidden comment line blocks wherever you want your live statistics table to render:

```markdown
## 📊 My Cyber Security Lab Dashboard

<!-- THM-ROOMS:START -->
<!-- THM-ROOMS:END -->
```

---

## 🏃 Running Your Dashboard
* **Automatic Schedule:** Your tracking script uses GitHub Actions and is pre-configured to wake up and execute automatically every single day at **midnight**.
* **Forced Manual Run:** To update it immediately, click your repository's **Actions** tab, highlight **Track TryHackMe Labs** on the left menu, select the **Run workflow** dropdown bar on the right side of the screen, and hit the green button.
