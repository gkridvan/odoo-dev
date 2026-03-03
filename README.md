# Odoo 17 — Website 360° View Module

## Project Structure

```
Odoo/
├── docker-compose.yml          # Docker stack (Odoo 17 + PostgreSQL 15)
├── config/
│   └── odoo.conf               # Odoo server configuration
├── custom-addons/
│   └── website_360_view/       # ← OUR CUSTOM MODULE
│       ├── __init__.py          # Module entry point
│       ├── __manifest__.py      # Module metadata & dependencies
│       ├── models/
│       │   ├── __init__.py
│       │   └── product_template.py   # Extended product model
│       ├── controllers/
│       │   ├── __init__.py
│       │   └── main.py               # HTTP controller (API endpoint)
│       ├── security/
│       │   └── ir.model.access.csv   # Access control rules
│       ├── views/
│       │   ├── product_template_views.xml   # Backend form extension
│       │   └── website_360_templates.xml    # Website product page extension
│       └── static/
│           ├── description/
│           │   ├── icon.png          # Module icon (128x128)
│           │   └── index.html        # Module description page
│           └── src/
│               ├── css/
│               │   └── website_360_view.css   # Frontend styles
│               ├── js/
│               │   └── website_360_viewer.js  # Pannellum integration
│               └── lib/
│                   └── pannellum/
│                       ├── pannellum.js       # Pannellum library
│                       └── pannellum.css      # Pannellum styles
├── .gitignore
└── README.md                   # This file
```

## Quick Start

### Prerequisites
- Docker Desktop installed and running
- Git

### 1. Download Pannellum Library

```bash
# Download Pannellum 2.5.6 (or latest)
cd custom-addons/website_360_view/static/src/lib/pannellum/

# Option A: Using curl (Git Bash / WSL)
curl -L -o pannellum.js "https://cdn.jsdelivr.net/npm/pannellum@2.5.6/build/pannellum.js"
curl -L -o pannellum.css "https://cdn.jsdelivr.net/npm/pannellum@2.5.6/build/pannellum.css"

# Option B: Using PowerShell
Invoke-WebRequest -Uri "https://cdn.jsdelivr.net/npm/pannellum@2.5.6/build/pannellum.js" -OutFile pannellum.js
Invoke-WebRequest -Uri "https://cdn.jsdelivr.net/npm/pannellum@2.5.6/build/pannellum.css" -OutFile pannellum.css
```

### 2. Start the Stack

```bash
cd /path/to/Odoo
docker compose up -d
```

Wait ~30 seconds for initialization, then visit: **http://localhost:8069**

### 3. Initial Setup

1. Create a new database (first visit will prompt you):
   - Master Password: `MySuperSecretAdminPassword` (from odoo.conf)
   - Database Name: `odoo_dev`
   - Email: your admin email
   - Password: your admin password
   - Check "Demo data" if you want sample products

2. Enable Developer Mode:
   - Go to **Settings** → scroll to bottom → click **Activate the developer mode**
   - Or add `?debug=1` to the URL

3. Install the Module:
   - Go to **Apps** → Remove the "Apps" filter → Search for "360"
   - Click **Install** on "Website 360° View"

### 4. Configure a Product

1. Go to **Website** → **Products** → pick any product
2. Click the **360° View** tab
3. Enable the toggle
4. Upload an equirectangular panorama image (or enter a URL)
5. Save
6. Visit the product on the website → you should see the 360° viewer!

### Testing Panorama Images

You can use free test panoramas from:
- https://pannellum.org/documentation/examples/simple-example/
- https://commons.wikimedia.org/wiki/Category:360°_panorama_photographs

## Development Commands

```bash
# Start the stack
docker compose up -d

# View Odoo logs (very useful for debugging!)
docker logs -f odoo_web

# Restart Odoo (after Python changes)
docker compose restart web

# Update the module (after XML/Python changes)
docker compose exec web odoo -u website_360_view -d odoo_dev --stop-after-init

# Open a shell inside the Odoo container
docker compose exec web bash

# Open Odoo shell (Python REPL with Odoo environment)
docker compose exec web odoo shell -d odoo_dev

# Stop everything
docker compose down

# Stop + remove data volumes (FULL RESET)
docker compose down -v
```

## Updating the Module

After making changes to your module:

| Changed | Action |
|---------|--------|
| Python files (.py) | `docker compose restart web` |
| XML views/templates | `docker compose exec web odoo -u website_360_view -d odoo_dev --stop-after-init` then restart |
| JS/CSS assets | Clear browser cache + restart Odoo. In dev mode: `?debug=assets` |
| __manifest__.py | Full update: `-u website_360_view` |

## Odoo.sh Deployment

This module is designed to be Odoo.sh compatible:

1. **No absolute paths** — all paths are relative
2. **No external CDN dependencies** — Pannellum is bundled locally
3. **Standard module structure** — follows Odoo conventions
4. **LGPL-3 license** — compatible with Odoo Community

### Deploy to Odoo.sh:

1. Push your `website_360_view` folder to a Git repository
2. In Odoo.sh, link your repository
3. Place the module in the root or a subfolder
4. Odoo.sh will auto-detect and make it available for installation

### Repository Structure for Odoo.sh:

```
your-repo/
└── website_360_view/
    ├── __init__.py
    ├── __manifest__.py
    └── ... (all module files)
```

**Important**: Odoo.sh expects the module folder directly in the repo root (or in a configured subfolder), NOT inside `custom-addons/`.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Module not visible in Apps | Remove "Apps" filter, or run update: `-u base` |
| 360 viewer not loading | Check browser console (F12) for Pannellum errors |
| Image not displaying | Ensure the image is equirectangular format |
| CSS/JS not updating | Add `?debug=assets` to URL, or clear cache |
| Database connection error | Check docker-compose.yml credentials match odoo.conf |

## License

LGPL-3.0 — See [LICENSE](https://www.gnu.org/licenses/lgpl-3.0.html)
