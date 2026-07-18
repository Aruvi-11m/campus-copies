# Campus Copies System

A complete management system for a university printing shop.

## 1. Folder Structure

```
campus_copies/
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── ...
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── vite.config.js
│   ├── ...
├── print_agent/
│   ├── agent.py
│   ├── requirements.txt
├── render.yaml
├── README.md
```

## 2. Backend Start Command

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
The backend will start at `http://localhost:8000`. Default admin credentials: `admin` / `admin123`.

## 3. Frontend Start Command

```bash
cd frontend
npm install
npm run dev
```
The frontend will be available at `http://localhost:5173`. Make sure to set `VITE_API_URL` to your production backend URL in your `.env` file when deploying.

## 4. Render Deployment Steps (Backend)

1. Push this repository to GitHub.
2. Go to Render.com -> New -> Web Service.
3. Connect your repository.
4. Render will automatically detect `render.yaml` and configure the service.
5. (Optional) For persistent data, configure a "Disk" mount in Render dashboard mounted to `/opt/render/project/src/backend/uploads` and `/opt/render/project/src/backend/campus_copies.db` (update SQLAlchemy URL accordingly).

## 5. Netlify Deployment Steps (Frontend)

1. Go to Netlify -> Add New Site -> Import an existing project.
2. Connect your GitHub repository.
3. Set the "Base directory" to `frontend/`.
4. Netlify will use the `netlify.toml` file to run `npm run build` and publish the `dist` directory.
5. Go to Site Settings -> Environment Variables and add `VITE_API_URL` pointing to your Render backend URL.

## 6. Mac Mini Print Agent Setup Steps

1. Install Python 3 on the Mac Mini.
2. Open terminal and run:
```bash
cd print_agent
pip install -r requirements.txt
```
3. Open `agent.py` and modify `API_BASE_URL` to point to your deployed Render backend (or `http://localhost:8000` if testing locally).
4. Run the agent:
```bash
python3 agent.py
```
5. Ensure your Epson M1170 is set as the default printer in macOS System Preferences > Printers & Scanners.

*Note: Color jobs will remain pending in "Payment Received" status so they can be processed manually through the Admin portal.*
