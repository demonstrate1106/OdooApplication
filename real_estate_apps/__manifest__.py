# -*- coding: utf-8 -*-
{
    'name': "Real Estate Management",
    'description': """
        An Application for managing Real Estate Property!
    """,
    'version': '1.0',
    'summary': 'Real Estate - Odoo App',
    'author': 'Awadhesh Giri , iTech Classes',
    'website': "www.demonstrate.com",
    'sequence': -100,
    'licence': 'LGPL-3',
    'maintainer': 'Awadhesh Giri ',
    'category': 'Real Estate/Brokerage',
    'depends': ['mail', 'board'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'demo/mail_template.xml',
        'security/security.xml',
        'demo/demo.xml',
        'demo/demo_data.xml',
        'demo/property_demo.xml',
        'views/dashboard.xml',
        'views/estate_views.xml',
        'views/view_property_type.xml',
        'views/view_property_type_tags.xml',
        'views/estate_offer_view.xml',
        'reports/estate_property_templates.xml',
        'reports/estate_offer.xml',
        'views/estate_menu_view.xml',
        'views/res_user_view.xml',
        'wizard/wizard_validation_form.xml',
        'views/agent_view.xml',
        'views/agent_language.xml',
    ],

    'demo': [],
    'images': ['static/description/image.png'],
    'installable': True,
    'application': True,
    'auto-install': False,
    
}
