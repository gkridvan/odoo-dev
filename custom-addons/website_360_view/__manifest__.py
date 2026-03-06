{
    "name": "Website 360 View",
    "summary": "Marzipano multi-scene 360 tour on product pages (iframe)",
    "author": "Your Company Name",
    "category": "Website/Website",
    "version": "17.0.3.0.0",
    "license": "LGPL-3",
    "depends": ["website_sale"],
    "data": [
        "security/ir.model.access.csv",
        "views/website_360_tour_views.xml",
        "views/product_template_views.xml",
        "views/website_360_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_360_view/static/src/css/website_360_view.css",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}