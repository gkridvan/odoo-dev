from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # ── Profil patrimonial ────────────────────────────────────────────────────

    x_patrimoine_type = fields.Selection(
        selection=[
            ('retraite', 'Retraite'),
            ('assurance_vie', 'Assurance Vie'),
            ('immobilier', 'Investissement Immobilier'),
            ('fiscalite', 'Optimisation Fiscale'),
            ('transmission', 'Transmission / Succession'),
            ('protection', 'Prévoyance / Protection'),
            ('autre', 'Autre'),
        ],
        string='Type de besoin patrimoine',
        index=True,
    )
    x_situation_familiale = fields.Selection(
        selection=[
            ('celibataire', 'Célibataire'),
            ('marie', 'Marié(e)'),
            ('pacs', 'Pacsé(e)'),
            ('divorce', 'Divorcé(e)'),
            ('veuf', 'Veuf / Veuve'),
        ],
        string='Situation familiale',
    )
    x_situation_professionnelle = fields.Selection(
        selection=[
            ('salarie', 'Salarié'),
            ('independant', 'Indépendant / Libéral'),
            ('dirigeant', "Dirigeant d'entreprise"),
            ('retraite', 'Retraité'),
            ('autre', 'Autre'),
        ],
        string='Situation professionnelle',
    )

    # ── Données financières ───────────────────────────────────────────────────

    x_revenu_annuel_brut = fields.Float(
        string='Revenu annuel brut (€)',
        digits=(12, 0),
    )
    x_actifs_estimes = fields.Float(
        string='Actifs estimés (€)',
        digits=(12, 0),
    )

    # ── Objectifs & horizon ───────────────────────────────────────────────────

    x_objectif_principal = fields.Char(string='Objectif principal')
    x_horizon_investissement = fields.Selection(
        selection=[
            ('court', '< 3 ans'),
            ('moyen', '3 – 8 ans'),
            ('long', '> 8 ans'),
        ],
        string="Horizon d'investissement",
    )
    x_niveau_risque = fields.Selection(
        selection=[
            ('prudent', 'Prudent'),
            ('equilibre', 'Équilibré'),
            ('dynamique', 'Dynamique'),
            ('agressif', 'Agressif'),
        ],
        string='Profil de risque',
    )

    # ── Suivi commercial ──────────────────────────────────────────────────────

    x_segment = fields.Selection(
        selection=[
            ('vip', '⭐ VIP'),
            ('prioritaire', '🔶 Prioritaire'),
            ('standard', '🔷 Standard'),
            ('froid', '❄️ Froid'),
        ],
        string='Segment prospect',
        default='standard',
        index=True,
    )
    x_premier_contact = fields.Selection(
        selection=[
            ('site_web', 'Site Web'),
            ('recommandation', 'Recommandation'),
            ('salon', 'Salon / Événement'),
            ('cold', 'Démarchage'),
            ('autre', 'Autre'),
        ],
        string='Canal de premier contact',
    )
    x_date_premier_rdv = fields.Date(string='Date 1er RDV')
    x_notes_analyse = fields.Text(string="Notes d'analyse patrimoniale")

    # ── Vue 360° — compteurs liés au contact ─────────────────────────────────

    x_count_devis = fields.Integer(
        string='Devis', compute='_compute_360', store=True, compute_sudo=True,
    )
    x_count_factures = fields.Integer(
        string='Factures', compute='_compute_360', store=True, compute_sudo=True,
    )
    x_montant_facture = fields.Float(
        string='CA facturé (€)', compute='_compute_360', store=True, compute_sudo=True,
        digits=(12, 0),
    )
    x_montant_devis = fields.Float(
        string='Devis en cours (€)', compute='_compute_360', store=True, compute_sudo=True,
        digits=(12, 0),
    )

    @api.depends('partner_id')
    def _compute_360(self):
        for lead in self:
            partner = lead.partner_id
            if not partner:
                lead.x_count_devis = 0
                lead.x_count_factures = 0
                lead.x_montant_facture = 0.0
                lead.x_montant_devis = 0.0
                continue
            orders = self.env['sale.order'].search(
                [('partner_id', '=', partner.id)]
            )
            invoices = self.env['account.move'].search(
                [('partner_id', '=', partner.id),
                 ('move_type', '=', 'out_invoice'),
                 ('state', '=', 'posted')]
            )
            lead.x_count_devis = len(orders)
            lead.x_count_factures = len(invoices)
            lead.x_montant_devis = sum(orders.mapped('amount_total'))
            lead.x_montant_facture = sum(invoices.mapped('amount_total'))

    def action_view_devis_360(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Devis — {self.partner_id.name}',
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.partner_id.id)],
            'context': {'default_partner_id': self.partner_id.id},
        }

    def action_view_factures_360(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Factures — {self.partner_id.name}',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.partner_id.id),
                       ('move_type', '=', 'out_invoice')],
            'context': {'default_partner_id': self.partner_id.id,
                        'default_move_type': 'out_invoice'},
        }
