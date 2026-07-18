# Campus Copies Deployment Guide

This guide covers deploying the Campus Copies system.

## 1. Database (Neon)
- Sign up at Neon.tech for a free scale-to-zero Postgres database.
- Get the connection string (e.g. `postgres://...`). The backend will automatically convert this to `postgresql://` as required by SQLAlchemy.

## 2. Backend (Render Free Tier)
- Push the repository to GitHub.
- In Render, create a new "Blueprint" from the repository. It will automatically detect `render.yaml` and set up the `campus-copies-api` Web Service.
- In the Render dashboard, set the Environment Variables:
  - `DATABASE_URL`: Your Neon connection string.
  - `ADMIN_PASSWORD`: A strong password for the initial admin account.
- **Important Note on Storage**: Render's free tier has an ephemeral filesystem. Files saved to the `uploads/` directory will be lost if the server restarts. Before going live, you must either upgrade to a paid Render plan with a Persistent Disk or swap out the `app/storage.py` implementation with cloud storage (e.g., Supabase Storage, Cloudinary, AWS S3).
- **Seeding the Admin**: Once deployed, you can use Render's "Shell" tab to run `python seed_admin.py` to seed the initial admin account into the database. (If using sqlite locally, run this command in your terminal).

## 3. Frontend (Netlify Free Tier)
- In Netlify, create a new site by connecting your GitHub repository.
- **Build Settings**:
  - Base directory: `frontend`
  - Build command: `npm run build`
  - Publish directory: `frontend/dist`
- Set the `VITE_API_URL` environment variable to your deployed Render URL (e.g., `https://campus-copies-api.onrender.com`).
- The included `netlify.toml` will handle React Router redirects.

## 4. Print Agent (Mac Mini)
- Run the agent on a trusted local machine connected to the printers (e.g., a Mac Mini).
- Copy `print-agent/agent.py` and `print-agent/requirements.txt` to the machine.
- Install dependencies: `pip install -r requirements.txt`.
- Set Environment Variables:
  - `API_URL`: Your Render backend URL.
  - `AGENT_KEY`: Must match the `AGENT_API_KEY` set in Render.
- Run the agent: `python agent.py`.
- The agent will poll the backend every 10 seconds.
