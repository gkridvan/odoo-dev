from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    x_marzipano_enabled = fields.Boolean(
        string="Activer la visite 360°",
        default=False,
    )
    x_marzipano_tour_id = fields.Many2one(
        "website.360.tour",
        string="Tour Marzipano",
        help="Sélectionnez le tour 360° à afficher sur la page produit.",
        ondelete="set null",
    )