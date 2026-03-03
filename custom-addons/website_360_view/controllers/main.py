# =============================================================================
# main.py — HTTP Controllers (optional, for API endpoints)
# =============================================================================
# Controllers handle HTTP routes. We include one example route that returns
# the 360° image data as a JSON response — useful if you later want to build
# an API or fetch image data asynchronously via AJAX.
#
# For now this is mostly a placeholder. The actual product page is served
# by website_sale's built-in controller; we just extend the template.
# =============================================================================

import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class Website360Controller(http.Controller):

    @http.route(
        "/shop/product/<int:product_id>/360-config",
        type="json",
        auth="public",
        website=True,
    )
    def get_360_config(self, product_id, **kwargs):
        """
        JSON API endpoint to fetch 360° configuration for a product.
        Useful for dynamic/AJAX loading scenarios.

        Returns:
            dict with image_url, auto_rotate, fov, scenes_json
        """
        product = request.env["product.template"].sudo().browse(product_id)
        if not product.exists() or not product.x_360_has_content:
            return {"error": "No 360° content available"}

        image_url = product.x_360_image_url or (
            "/web/image/product.template/%s/x_360_image" % product.id
        )

        return {
            "image_url": image_url,
            "auto_rotate": product.x_360_auto_rotate,
            "default_fov": product.x_360_default_fov,
            "scenes_json": product.x_360_scenes_json or "",
        }
