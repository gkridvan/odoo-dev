# =============================================================================
# Module Manifest — __manifest__.py
# =============================================================================
# This is the "ID card" of your module. Odoo reads it to know:
#   - What this module does (name, summary, description)
#   - What other modules it depends on
#   - What data/views/templates/assets to load
#   - Its version & license
#
# IMPORTANT RULES:
#   - 'depends' must list ALL modules whose models/views you inherit
#   - 'data' files are loaded in ORDER — security first, then views
#   - 'assets' replaces the old 'template' approach for JS/CSS in Odoo 17
#   - 'license' must be LGPL-3 for Odoo Community modules
#   - 'version' follows: odoo_major.odoo_minor.module_version
# =============================================================================
{
    "name": "Website 360° View",
    "summary": "Add interactive 360° panoramic image viewer to product pages",
    "description": """
        This module extends the Website product page to display a 360° panoramic
        image viewer (powered by Pannellum) when a 360° image is uploaded.

        Features:
        - Upload equirectangular panorama images per product template
        - Or provide URL to hosted panorama
        - Interactive pan/zoom viewer on the product page
        - Falls back to normal product images when no 360 image is set
        - Admin toggle to enable/disable the 360 viewer per product
        - Support for multiple scenes with hotspots (advanced)
        - Fully responsive, theme-safe
    """,
    "author": "Your Company Name",
    "website": "https://yourcompany.com",
    "category": "Website/Website",
    "version": "17.0.1.0.0",
    "license": "LGPL-3",

    # -------------------------------------------------------------------------
    # Dependencies
    # -------------------------------------------------------------------------
    # 'website_sale' gives us the product page on the website
    # 'website' gives us the website builder framework
    # Both are required because we inherit their models and templates.
    "depends": [
        "website_sale",
    ],

    # -------------------------------------------------------------------------
    # Data files — loaded IN ORDER at install/upgrade
    # -------------------------------------------------------------------------
    # RULE: security files FIRST, then views, then data.
    # Why? Views may reference record rules; record rules need the model
    # registered first (which happens via Python auto-discovery).
    "data": [
        "security/ir.model.access.csv",
        "views/product_template_views.xml",
        "views/website_360_templates.xml",
    ],

    # -------------------------------------------------------------------------
    # Assets — JS, CSS, and external libraries
    # -------------------------------------------------------------------------
    # 'web.assets_frontend' is the bundle loaded on public website pages.
    # We add Pannellum (open-source panorama viewer) and our custom JS/CSS.
    "assets": {
        "web.assets_frontend": [
            # Our custom code only — Pannellum is loaded via <script> tag
            # in the template to ensure window.pannellum global is available.
            "website_360_view/static/src/css/website_360_view.css",
            "website_360_view/static/src/js/website_360_viewer.js",
        ],
    },

    # -------------------------------------------------------------------------
    # Module flags
    # -------------------------------------------------------------------------
    "installable": True,
    "application": False,     # It's an extension, not a standalone app
    "auto_install": False,    # User must explicitly install it
}
