{
    'name': 'Caritas Fleet',
    'version': '18.0.1.5.3',
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
        'security/caritas_fleet_security.xml',
        'security/ir.model.access.csv',
        'data/vehicle_request_data.xml',
        'views/caritas_fleet_views.xml',
        'report/vehicle_usage_report.xml',
        'report/vehicle_usage_report_templates.xml',
        'security/caritas_fleet_rules.xml',
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
