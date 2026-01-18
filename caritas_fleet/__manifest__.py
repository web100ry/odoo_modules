{
    'name': 'Caritas Fleet',
    'version': '18.0.1.0.1',
    'category': 'Fleet',
    'summary': 'Manage Caritas fleet operations',
    'description': """
        Custom module for Caritas fleet management.
    """,
    'author': 'Caritas',
    'website': 'https://www.caritas.org',
    'depends': [
        'fleet',
        'mail',
        'calendar',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/caritas_fleet_views.xml',
    ],
    'demo': [
        'demo/caritas_fleet_demo.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
    'images': [
        'static/description/icon.png',
    ],
}
