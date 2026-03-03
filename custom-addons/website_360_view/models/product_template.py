# =============================================================================
# product_template.py — Extend the Product Template model
# =============================================================================
# We INHERIT the existing 'product.template' model to add new fields.
#
# KEY CONCEPTS:
#   _inherit = "product.template"
#       → Adds our fields/methods to the EXISTING model (no new table).
#       → This is called "classical inheritance" in Odoo.
#
#   Binary field vs URL field:
#       → Binary stores the image inside Odoo's filestore (simple, self-contained)
#       → Char (URL) lets you point to an externally-hosted panorama
#       → We provide BOTH so the user can choose.
#
#   We do NOT use hardcoded IDs anywhere — only XML IDs for references.
# =============================================================================

from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # -------------------------------------------------------------------------
    # Fields
    # -------------------------------------------------------------------------

    # Master toggle — lets the admin enable/disable 360 view per product
    x_360_enabled = fields.Boolean(
        string="Enable 360° View",
        default=False,
        help="Check this box to display a 360° panoramic viewer on the "
             "product page instead of the standard image carousel.",
    )

    # Option A: Upload the panorama image directly
    x_360_image = fields.Binary(
        string="360° Image",
        attachment=True,  # stored as ir.attachment (efficient, streamable)
        help="Upload an equirectangular panoramic image (JPEG/PNG). "
             "Recommended resolution: 4096×2048 or higher for quality.",
    )

    # Option B: External URL to a hosted panorama
    x_360_image_url = fields.Char(
        string="360° Image URL",
        help="Alternatively, provide a direct URL to an equirectangular "
             "panoramic image hosted externally (e.g., CDN or cloud storage).",
    )

    # Computed field to check if we have any 360 content available
    x_360_has_content = fields.Boolean(
        string="Has 360° Content",
        compute="_compute_360_has_content",
        store=False,  # no need to persist — it's fast to compute
    )

    # -------------------------------------------------------------------------
    # Configuration fields for the viewer
    # -------------------------------------------------------------------------
    x_360_auto_rotate = fields.Boolean(
        string="Auto-Rotate",
        default=True,
        help="Automatically rotate the panorama when the viewer loads.",
    )

    x_360_default_fov = fields.Integer(
        string="Default Field of View",
        default=100,
        help="Initial zoom level in degrees (1-120). Lower = more zoomed in.",
    )

    # -------------------------------------------------------------------------
    # Advanced: Multiple scenes (stored as JSON text for simplicity)
    # -------------------------------------------------------------------------
    x_360_scenes_json = fields.Text(
        string="360° Scenes (JSON)",
        help="Advanced: Define multiple panorama scenes with hotspots in JSON "
             "format. See module documentation for the schema.",
    )

    # -------------------------------------------------------------------------
    # Computed methods
    # -------------------------------------------------------------------------
    @api.depends("x_360_enabled", "x_360_image", "x_360_image_url", "x_360_scenes_json")
    def _compute_360_has_content(self):
        """
        Returns True if 360 is enabled AND we have an image, URL, or scenes JSON.
        Used in website templates to decide which viewer to show.
        """
        for record in self:
            record.x_360_has_content = (
                record.x_360_enabled
                and (record.x_360_image or record.x_360_image_url or record.x_360_scenes_json)
            )
