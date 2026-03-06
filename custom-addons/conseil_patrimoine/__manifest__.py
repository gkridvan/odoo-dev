{
    'name': 'Conseil Patrimoine — Gestion des Prospects',
    'version': '17.0.1.0.0',
    'category': 'CRM',
    'summary': 'Gestion et suivi des prospects patrimoniaux — profil financier, objectifs et cycle de vie client',
    'author': 'Cabinet Conseil Patrimoine',
    'depends': ['crm', 'sale', 'account', 'mass_mailing', 'hr', 'website'],
    'data': [
        'views/crm_lead_views.xml',
        'views/crm_scoring_dashboard.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
