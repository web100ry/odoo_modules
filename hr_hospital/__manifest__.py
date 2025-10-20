{
    'name': 'Hospital Caritas Ukraine',
    'summary': '',
    'author': 'Valerii Ivaniuk',
    'website': 'https://www.vivaniuk.pp.ua/',
    'category': 'Customizations',
    'license': 'LGPL-3',
    'version': '18.0.2.1.4',
    'description': "Даний модуль створено в рамках уроків ODOO Shool",
    'depends': [
        'base',
    ],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        'security/ir.model.access.csv',
        # load actions first (views define actions)
        'views/hr_hospital_hospital_views.xml',
        'views/hr_hospital_doctor_views.xml',
        'views/hr_hospital_patient_views.xml',
        'views/hr_hospital_visit_views.xml',
        # load menus last (menus reference actions)
        'views/hr_hospital_menu.xml',
    ],
    'demo': [
        'demo/hr_hospital_hospital_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'images': [
        'static/description/icon.png',
    ],
    'application': False,
}