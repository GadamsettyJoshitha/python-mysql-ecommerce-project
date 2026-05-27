# Deploy & Environment Setup (Vercel + GitHub)

Follow these steps to finish deployment and enable the pipeline trigger.

1) Required environment variables

- Vercel (Project → Settings → Environment Variables or `vercel env add`):
  - `GITHUB_REPO` = GadamsettyJoshitha/python-mysql-ecommerce-project
  - `VERCEL_TRIGGER_SECRET` = <choose-a-secret>
  - `GITHUB_TOKEN` = <your-personal-access-token-with-repo+workflow-scopes> (required for `/api/trigger` dispatch)

- GitHub (Repository → Settings → Secrets):
  - `SMTP_HOST`, `SMTP_PORT`, `SMTP_TIMEOUT`, `EMAIL_SENDER`, `EMAIL_APP_PASSWORD`
  - `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`

2) Add Vercel environment variables (interactive CLI)

Install Vercel CLI if you don't have it:

```powershell
npm install -g vercel
vercel login
```

Add the three required Vercel env vars interactively:

```powershell
vercel env add GITHUB_REPO production
vercel env add VERCEL_TRIGGER_SECRET production
vercel env add GITHUB_TOKEN production
```

For each command you'll be prompted to enter the value. Use the same commands for `preview` or `development` if you need those scopes.

3) Add GitHub repository secrets (using `gh` GitHub CLI)

Install `gh` and authenticate if needed:

```powershell
# install (if missing)
winget install --id GitHub.cli
gh auth login
```

Set secrets (examples — you'll be prompted for the value or use `--body`):

```powershell
# example: set SMTP creds
gh secret set SMTP_HOST --body "smtp.gmail.com" --repo GadamsettyJoshitha/python-mysql-ecommerce-project
gh secret set SMTP_PORT --body "587" --repo GadamsettyJoshitha/python-mysql-ecommerce-project
gh secret set EMAIL_SENDER --body "you@example.com" --repo GadamsettyJoshitha/python-mysql-ecommerce-project
gh secret set EMAIL_APP_PASSWORD --body "<app-password>" --repo GadamsettyJoshitha/python-mysql-ecommerce-project

# MySQL
gh secret set MYSQL_HOST --body "localhost" --repo GadamsettyJoshitha/python-mysql-ecommerce-project
gh secret set MYSQL_USER --body "root" --repo GadamsettyJoshitha/python-mysql-ecommerce-project
gh secret set MYSQL_PASSWORD --body "<mysql-password>" --repo GadamsettyJoshitha/python-mysql-ecommerce-project
gh secret set MYSQL_DATABASE --body "ecommerce_project" --repo GadamsettyJoshitha/python-mysql-ecommerce-project
```

4) Test the Vercel trigger endpoint

Use curl to call the function (replace values):

```bash
curl -i -X POST https://<your-deploy-url>/api/trigger -H "x-trigger-secret: <your-secret>"
```

- 200 OK: workflow dispatch sent. Check GitHub Actions.  
- 403: secret mismatch — re-enter `VERCEL_TRIGGER_SECRET`.  
- 500: function missing `GITHUB_TOKEN` or `GITHUB_REPO` — add those env vars in Vercel.

5) Verify GitHub Actions

- Open: https://github.com/GadamsettyJoshitha/python-mysql-ecommerce-project/actions
- Choose the `Run pipeline (manual)` workflow. Inspect the latest run logs.

6) Optional: Redeploy or redeploy with new envs

After adding Vercel env vars, redeploy from Vercel dashboard (Project → Deployments → Redeploy) or push a new commit.

If you want, run these commands to push and deploy from your machine (one-liner):

```powershell
# push branch and deploy public/ directly
git checkout -B vercel-deploy
git add -A; git commit -m "Deploy: add Vercel frontend and trigger endpoint" || echo 'nothing to commit'
git push -u origin vercel-deploy
vercel --prod public
```

If you get stuck, paste the console output or the Vercel/GitHub logs here and I'll help fix it.
