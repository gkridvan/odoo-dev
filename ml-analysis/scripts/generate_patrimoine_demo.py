"""
Conseil Patrimoine  Génération de données de démonstration
============================================================
Workflow complet Gillet Patrimoine dans Odoo :
  res.partner  ->  crm.lead  ->  sale.order (devis)  ->  account.move (facture)

Segmentation :
  VIP (7)          -> lead + devis confirmé + facture posted
  Prioritaire (10) -> lead + devis envoyé (en attente)
  Standard (6)     -> lead + devis brouillon
  Froid (2)        -> lead uniquement

Usage:  python generate_patrimoine_demo.py
"""

import xmlrpc.client
import random
import sys
from datetime import date, timedelta

ODOO_URL  = 'http://localhost:8069'
ODOO_DB   = 'odoo_dev'
ODOO_USER = 'ridooo333@gmail.com'
ODOO_PASS = 'admin123'

random.seed(42)

PRENOMS = [
    'Jean-Pierre', 'Marie-Claire', 'Francois', 'Isabelle', 'Philippe',
    'Catherine', 'Michel', 'Nathalie', 'Alain', 'Sylvie',
    'Nicolas', 'Veronique', 'Laurent', 'Martine', 'Stephane',
    'Christophe', 'Valerie', 'Thierry', 'Anne', 'Bruno',
    'Olivier', 'Celine', 'Eric', 'Julie', 'Thomas',
]
NOMS = [
    'Martin', 'Bernard', 'Thomas', 'Petit', 'Robert',
    'Durand', 'Dubois', 'Moreau', 'Laurent', 'Simon',
    'Lefebvre', 'Leroy', 'Roux', 'David', 'Bertrand',
    'Morel', 'Fournier', 'Girard', 'Bonnet', 'Dupont',
    'Lambert', 'Fontaine', 'Rousseau', 'Vincent', 'Muller',
]
VILLES = [
    'Paris', 'Lyon', 'Bordeaux', 'Toulouse', 'Nantes',
    'Strasbourg', 'Lille', 'Nice', 'Rennes', 'Montpellier',
    'Grenoble', 'Tours', 'Dijon', 'Angers', 'Reims',
    'Metz', 'Clermont-Ferrand', 'Aix-en-Provence', 'Rouen', 'Brest',
]

# Accented display names (parallel list)
PRENOMS_FR = [
    'Jean-Pierre', 'Marie-Claire', 'François', 'Isabelle', 'Philippe',
    'Catherine', 'Michel', 'Nathalie', 'Alain', 'Sylvie',
    'Nicolas', 'Véronique', 'Laurent', 'Martine', 'Stéphane',
    'Christophe', 'Valérie', 'Thierry', 'Anne', 'Bruno',
    'Olivier', 'Céline', 'Éric', 'Julie', 'Thomas',
]


def identite(i):
    prenom_slug = PRENOMS[i % len(PRENOMS)]
    prenom_fr   = PRENOMS_FR[i % len(PRENOMS_FR)]
    nom         = NOMS[(i * 7 + 3) % len(NOMS)]
    ville       = VILLES[i % len(VILLES)]
    slug        = prenom_slug.lower().replace(' ', '').replace('-', '').replace("'", '')
    email       = f'{slug}.{nom.lower()}@example.fr'
    phone       = f'+33 6 {10+(i%90):02d} {10+((i*3)%90):02d} {10+((i*7)%90):02d} {10+((i*13)%90):02d}'
    return prenom_fr, nom, ville, email, phone


# Services du cabinet (name, price, index)
SERVICES = [
    ('Mission de conseil patrimonial',   1500.0),   # 0
    ('Analyse financiere complete',       800.0),   # 1
    ('Accompagnement assurance vie',      500.0),   # 2
    ('Optimisation fiscale',             1200.0),   # 3
    ('Ingenierie de transmission',       2500.0),   # 4
    ('Bilan retraite',                    700.0),   # 5
    ('Strategie immobiliere locative',    950.0),   # 6
    ('Bilan prevoyance',                  450.0),   # 7
]

# (type_besoin, sit_pro, sit_fam, revenu, actifs, horizon, risque,
#  segment, objectif, canal, notes, [svc_idx1, svc_idx2])
ARCHETYPES = [
    ('transmission','dirigeant','marie',180000,850000,'long','dynamique','vip',
     "Transmission de l'entreprise familiale avec optimisation fiscale",
     'recommandation',"Dirigeant 18 ans. Holding patrimoniale + pacte Dutreil.",[4,0]),

    ('fiscalite','dirigeant','pacs',210000,1200000,'moyen','dynamique','vip',
     "Reduire la pression fiscale, diversifier hors entreprise",
     'recommandation',"SARL BTP. IR + IFI optimises. Excess tresorerie a investir.",[3,0]),

    ('transmission','dirigeant','marie',150000,600000,'long','equilibre','prioritaire',
     "Retraite dirigeant + perennite du capital",
     'salon',"PME de negoce. Pas de strategie successorale. OBO envisage.",[4,1]),

    ('fiscalite','dirigeant','divorce',95000,320000,'moyen','equilibre','prioritaire',
     "Optimisation fiscale post-divorce, restructuration patrimoniale",
     'site_web',"Regime separatiste. Reprendre en main son patrimoine.",[3,1]),

    ('transmission','dirigeant','marie',230000,2000000,'long','dynamique','vip',
     "Family office simplifie pour la famille",
     'recommandation',"Groupe familial multisite. Heritiers multiples.",[4,0]),

    ('assurance_vie','independant','marie',130000,280000,'long','equilibre','prioritaire',
     "Capital retraite + protection familiale",
     'recommandation',"Medecin generaliste 45 ans. AV multisupport + madelin.",[2,7]),

    ('retraite','independant','marie',160000,550000,'long','equilibre','vip',
     "Securiser la retraite hors CARMF",
     'recommandation',"Chirurgien 52 ans. Capital constitue peu structure.",[5,2]),

    ('assurance_vie','independant','celibataire',115000,180000,'moyen','dynamique','standard',
     "Epargne de precaution + projection retraite",
     'site_web',"Medecin specialiste 38 ans. Solution cle en main.",[2,0]),

    ('protection','independant','pacs',98000,120000,'court','prudent','standard',
     "Prevoyance arret de travail",
     'cold',"Kinesitherapeute liberal. Pas de prevoyance individuelle.",[7,0]),

    ('retraite','independant','marie',140000,400000,'long','equilibre','prioritaire',
     "Diversifier epargne retraite fonds euro + UC",
     'recommandation',"Veterinaire 48 ans. Contrats a optimiser.",[5,2]),

    ('immobilier','salarie','marie',85000,150000,'moyen','equilibre','standard',
     "Immobilier locatif avec effet de levier",
     'site_web',"Directeur marketing 42 ans. Primo-investisseur.",[6,0]),

    ('immobilier','salarie','marie',72000,90000,'moyen','equilibre','standard',
     "Defiscalisation immobiliere TMI 41%",
     'salon',"Ingenieur R&D. SCPI en demembrement.",[6,3]),

    ('assurance_vie','salarie','celibataire',65000,80000,'long','dynamique','standard',
     "Capital long terme via unites de compte",
     'site_web',"Cadre finance 35 ans. Exposition actions monde.",[2,0]),

    ('fiscalite','salarie','marie',110000,300000,'moyen','equilibre','prioritaire',
     "Optimisation TMI 45% : PER + investissement",
     'recommandation',"DRH groupe cote. Prime exceptionnelle.",[3,1]),

    ('immobilier','salarie','divorce',58000,60000,'court','prudent','froid',
     "Reinvestir soulte de divorce",
     'cold',"Cadre 47 ans. Hesitant, a convaincre.",[6,0]),

    ('transmission','retraite','veuf',42000,750000,'court','prudent','vip',
     "Succession + protection des enfants",
     'recommandation',"Veuve 68 ans. Capital vente bien. Urgence donation.",[4,1]),

    ('retraite','retraite','marie',55000,480000,'moyen','prudent','prioritaire',
     "Optimiser revenus complementaires retraite",
     'site_web',"Cadre retraite 66 ans. Revenus fonciers a optimiser.",[5,3]),

    ('transmission','retraite','marie',38000,290000,'court','prudent','standard',
     "Transmission aux enfants et petits-enfants",
     'cold',"Retraite artisan 71 ans. Premier conseiller.",[4,0]),

    ('protection','retraite','celibataire',28000,110000,'court','prudent','froid',
     "Complementaire sante + dependance",
     'cold',"Retraite 74 ans. Besoin protection avant tout.",[7,0]),

    ('transmission','retraite','marie',67000,1100000,'moyen','equilibre','vip',
     "Transmission via SCI familiale",
     'recommandation',"Ancienne dirigeante 64 ans. SCI + donation-partage.",[4,1]),

    ('fiscalite','dirigeant','celibataire',160000,400000,'long','agressif','vip',
     "Defiscalisation revenus exceptionnels FCPI/FCPR/IR-PME",
     'site_web',"Fondateur SaaS 34 ans. Dividende 200k euros.",[3,0]),

    ('assurance_vie','dirigeant','pacs',95000,250000,'long','dynamique','prioritaire',
     "Sortir tresorerie excedentaire de facon optimisee",
     'recommandation',"Co-fondateur ESN 39 ans. Holding existante.",[2,0]),

    ('immobilier','dirigeant','marie',120000,320000,'moyen','dynamique','prioritaire',
     "Investissement immobilier via SCI a l'IS",
     'site_web',"CTO startup 40 ans. SCI IS pour levier.",[6,1]),

    ('immobilier','independant','celibataire',75000,90000,'long','dynamique','standard',
     "Batir patrimoine immobilier avec peu d apport",
     'site_web',"Freelance dev 31 ans. Investissement locatif fort rendement.",[6,0]),

    ('fiscalite','independant','marie',88000,170000,'moyen','equilibre','prioritaire',
     "Optimiser remuneration salaire/dividendes/retraite",
     'recommandation',"Consultant independant 43 ans SASU. Arbitrage PER/dividendes.",[3,0]),
]

STAGES = [
    ('Nouveau', 10), ('Qualifie', 20), ('Analyse patrimoniale', 30),
    ('Proposition commerciale', 40), ('Negociation', 50), ('Gagne', 60), ('Perdu', 70),
]
SEGMENT_STAGE = {
    'vip': 'Proposition commerciale', 'prioritaire': 'Analyse patrimoniale',
    'standard': 'Qualifie', 'froid': 'Nouveau',
}


def connect():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
    if not uid:
        print('ERREUR auth Odoo.'); sys.exit(1)
    return uid, xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object',
                                          allow_none=True)


def rpc(m, uid, model, method, args, kw=None):
    return m.execute_kw(ODOO_DB, uid, ODOO_PASS, model, method, args, kw or {})


def purge(uid, m):
    print('\n  Nettoyage...')
    # Factures
    ids = rpc(m, uid, 'account.move', 'search', [[['move_type','=','out_invoice']]])
    if ids:
        posted = rpc(m, uid, 'account.move', 'search',
                     [[['id','in',ids],['state','=','posted']]])
        if posted: rpc(m, uid, 'account.move', 'button_draft', [posted])
        rpc(m, uid, 'account.move', 'unlink', [ids])
        print(f'    {len(ids)} factures supprimees.')
    # Commandes
    ids = rpc(m, uid, 'sale.order', 'search', [[]])
    if ids:
        for oid in ids:
            try: rpc(m, uid, 'sale.order', 'action_cancel', [[oid]])
            except: pass
        # Only unlink orders that are now in 'cancel' state
        cancel_ids = rpc(m, uid, 'sale.order', 'search',
                         [[['id','in',ids],['state','=','cancel']]])
        if cancel_ids:
            rpc(m, uid, 'sale.order', 'unlink', [cancel_ids])
        # Force-delete remaining (draft) ones
        remaining = rpc(m, uid, 'sale.order', 'search',
                        [[['id','in',ids],['state','=','draft']]])
        if remaining:
            rpc(m, uid, 'sale.order', 'unlink', [remaining])
        print(f'    {len(ids)} commandes supprimees.')
    # Leads
    ids = rpc(m, uid, 'crm.lead', 'search', [[]])
    if ids:
        rpc(m, uid, 'crm.lead', 'unlink', [ids])
        print(f'    {len(ids)} leads supprimes.')
    # Contacts
    admin_p = rpc(m, uid, 'res.users', 'read', [[uid]], {'fields':['partner_id']})[0]['partner_id'][0]
    user_ps = {u['partner_id'][0] for u in rpc(m, uid, 'res.users', 'search_read',
               [[['active','in',[True,False]]]], {'fields':['partner_id']}) if u.get('partner_id')}
    cids = rpc(m, uid, 'res.partner', 'search',
               [[['is_company','=',False],['type','=','contact'],['id','!=',admin_p]]])
    d = a = 0
    for pid in [p for p in cids if p not in user_ps]:
        try:    rpc(m, uid, 'res.partner', 'unlink', [[pid]]); d += 1
        except:
            try: rpc(m, uid, 'res.partner', 'write', [[pid],{'active':False}]); a += 1
            except: pass
    print(f'    {d} contacts supprimes, {a} archives.')


def ensure_services(uid, m):
    svc = {}
    for name, price in SERVICES:
        ids = rpc(m, uid, 'product.product', 'search', [[['name', '=', name]]])
        if ids:
            # Update invoice_policy on existing product
            tmpl_ids = rpc(m, uid, 'product.product', 'read', [ids[:1]],
                           {'fields': ['product_tmpl_id']})[0]['product_tmpl_id']
            rpc(m, uid, 'product.template', 'write', [[tmpl_ids[0]],
                {'invoice_policy': 'order', 'taxes_id': []}])
            svc[name] = ids[0]
        else:
            tid = rpc(m, uid, 'product.template', 'create', [{
                'name': name, 'type': 'service',
                'list_price': price, 'invoice_policy': 'order', 'taxes_id': [],
            }])
            svc[name] = rpc(m, uid, 'product.product', 'search',
                            [[['product_tmpl_id', '=', tid]]])[0]
    return svc


def ensure_stages(uid, m):
    sm = {}
    for name, seq in STAGES:
        ids = rpc(m, uid, 'crm.stage', 'search', [[['name','=',name]]])
        sm[name] = ids[0] if ids else rpc(m, uid, 'crm.stage', 'create',
                                          [{'name':name,'sequence':seq}])
    return sm


def configure_company(uid, m):
    rpc(m, uid, 'res.company', 'write', [[1], {
        'name': 'Cabinet Conseil Patrimoine', 'city': 'Paris',
        'zip': '75008', 'country_id': 75,
        'phone': '+33 1 23 45 67 89',
        'email': 'contact@cabinet-conseil-patrimoine.fr',
        'website': 'https://www.cabinet-conseil-patrimoine.fr',
    }])
    print('    Societe mise a jour.')


def main():
    print('=' * 62)
    print('  Conseil Patrimoine  —  Workflow : Lead > Devis > Facture')
    print('=' * 62)

    uid, m = connect()
    print(f'  Connecte (uid={uid})')

    print('\n  Societe...')
    configure_company(uid, m)

    purge(uid, m)

    print('\n  Services...')
    svc = ensure_services(uid, m)
    print(f'    {len(svc)} services.')

    print('\n  Etapes CRM...')
    stages = ensure_stages(uid, m)
    print(f'    {len(stages)} etapes.')

    print(f'\n  {"#":>3}  {"Nom":<28} {"Segment":<12} {"Besoin":<16} {"Devis":>7} {"Facture":>8}')
    print(f'  {"---":<3}  {"-"*28} {"-"*12} {"-"*16} {"-"*7} {"-"*8}')

    stats = {'leads': 0, 'orders': 0, 'invoices': 0}
    prio = {'vip':'2','prioritaire':'1','standard':'0','froid':'0'}

    for i, arc in enumerate(ARCHETYPES):
        (tb, sp, sf, rev, act, hor, ris, seg, obj, can, notes, svc_idx) = arc
        prenom, nom, ville, email, phone = identite(i)

        # Contact
        pid = rpc(m, uid, 'res.partner', 'create', [{
            'name': f'{prenom} {nom}', 'email': email,
            'phone': phone, 'city': ville,
            'country_id': 75, 'is_company': False,
        }])

        # CRM Lead
        stage_id = stages.get(SEGMENT_STAGE[seg], stages['Nouveau'])
        rpc(m, uid, 'crm.lead', 'create', [{
            'name': f'Dossier patrimoine  {prenom} {nom}',
            'partner_id': pid, 'stage_id': stage_id, 'priority': prio[seg],
            'expected_revenue': round(act * 0.015, 0),
            'x_patrimoine_type': tb, 'x_situation_professionnelle': sp,
            'x_situation_familiale': sf, 'x_revenu_annuel_brut': float(rev),
            'x_actifs_estimes': float(act), 'x_horizon_investissement': hor,
            'x_niveau_risque': ris, 'x_segment': seg,
            'x_objectif_principal': obj, 'x_premier_contact': can,
            'x_notes_analyse': notes,
            'x_date_premier_rdv': str(date.today() - timedelta(days=i*3)),
        }])
        stats['leads'] += 1

        order_id = inv_id = None

        # Devis (tous sauf froid)
        if seg != 'froid':
            lines = [(0, 0, {
                'product_id': svc[SERVICES[idx][0]],
                'name': SERVICES[idx][0],
                'product_uom_qty': 1,
                'price_unit': SERVICES[idx][1],
            }) for idx in svc_idx]

            order_id = rpc(m, uid, 'sale.order', 'create', [{
                'partner_id': pid, 'order_line': lines,
                'note': f'Proposition  {tb.replace("_"," ").title()}',
            }])
            stats['orders'] += 1

            if seg == 'vip':
                rpc(m, uid, 'sale.order', 'action_confirm', [[order_id]])
            elif seg == 'prioritaire':
                rpc(m, uid, 'sale.order', 'action_quotation_send', [[order_id]])

        # Facture (VIP uniquement)
        if seg == 'vip' and order_id:
            try:
                ctx = {'active_ids': [order_id], 'active_model': 'sale.order',
                       'active_id': order_id}
                wiz_id = rpc(m, uid, 'sale.advance.payment.inv', 'create',
                             [{'advance_payment_method': 'delivered'}],
                             {'context': ctx})
                try:
                    rpc(m, uid, 'sale.advance.payment.inv', 'create_invoices',
                        [[wiz_id]], {'context': ctx})
                except xmlrpc.client.Fault as fe:
                    # Odoo returns action dict with None values — invoice still created
                    if 'cannot marshal None' not in str(fe):
                        raise
                # Find the invoice (created despite potential serialization error)
                order_name = rpc(m, uid, 'sale.order', 'read',
                                 [[order_id]], {'fields': ['name']})[0]['name']
                move_ids = rpc(m, uid, 'account.move', 'search',
                               [[['invoice_origin', '=', order_name],
                                 ['move_type', '=', 'out_invoice'],
                                 ['state', '=', 'draft']]])
                if move_ids:
                    rpc(m, uid, 'account.move', 'action_post', [move_ids])
                    inv_id = move_ids[0]
                    stats['invoices'] += 1
            except Exception as e:
                print(f'    [WARN invoice {order_id}]: {e}')
                inv_id = None

        d_str = f'SO{order_id}' if order_id else ''
        f_str = f'INV{inv_id}'  if inv_id   else ''
        print(f'  [{i+1:02d}]  {prenom+" "+nom:<28} {seg:<12} {tb:<16} {d_str:>7} {f_str:>8}')

    print(f'\n{"=" * 62}')
    print(f'  {stats["leads"]:>3} leads    {stats["orders"]:>3} devis    {stats["invoices"]:>3} factures')
    print(f'  CRM         -> http://localhost:8069/odoo/crm')
    print(f'  Ventes      -> http://localhost:8069/odoo/sales')
    print(f'  Facturation -> http://localhost:8069/odoo/accounting')
    print(f'{"=" * 62}\n')


if __name__ == '__main__':
    main()
