{
    "name": "Caritas Fleet Management",
    "version": "18.0.1.5.0",
    "category": "Operations/Fleet",
    "summary": "Vehicle request and fleet management system",
    "description": """
Vehicle request and fleet management system for Caritas Ukraine.

Main features:
- Vehicle request submission and approval workflow
- Centralized fleet management
- Department-based access and visibility
- Calendar-based vehicle availability control
- Internal communication via Odoo chatter
- External notifications integration (Signal API)
    """,
    "author": "Caritas Ukraine",
    "website": "https://caritas.ua",
    "license": "LGPL-3",
    "depends": [
        'base',
        "fleet",
        "mail",
        "calendar",
    ],
    "external_dependencies": {
        "python": []
    },
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/vehicle_request_sequence.xml",
        "data/vehicle_trip_sequence.xml",
        "views/menus.xml",
        "views/vehicle_trip_views.xml",
        "views/vehicle_department_views.xml",
        "views/fleet_vehicle_views.xml",
        "views/vehicle_request_reject_wizard.xml",
        "views/vehicle_request_views.xml",
        "views/vehicle_request_menu.xml",
    ],
    "demo": [
        # Demo data will be added in later steps
    ],
    'installable': True,
    'auto_install': False,
    'images': [
        'static/description/icon.png',
    ],
    'application': True,
}