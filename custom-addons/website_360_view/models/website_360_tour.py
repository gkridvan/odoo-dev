from odoo import fields, models


class Website360Tour(models.Model):
    _name = "website.360.tour"
    _description = "Tour Marzipano 360"
    _order = "name"

    name = fields.Char(
        string="Nom du dossier",
        required=True,
        help="Nom exact du dossier dans static/src/tours/ (ex: project-title)",
    )
    display_name_custom = fields.Char(
        string="Libellé affiché",
        help="Nom lisible affiché dans les menus (ex: Cabinet Client 1)",
    )
    product_ids = fields.One2many(
        "product.template", "x_marzipano_tour_id",
        string="Produits utilisant ce tour",
    )

    def name_get(self):
        result = []
        for rec in self:
            label = rec.display_name_custom or rec.name
            result.append((rec.id, label))
        return result