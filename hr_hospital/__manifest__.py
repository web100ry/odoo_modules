{
    'name': 'Hospital Caritas Ukraine',
    'summary': '',
    'author': 'Valerii Ivaniuk',
    'website': 'https://www.vivaniuk.pp.ua/',
    'category': 'Customizations',
    'license': 'LGPL-3',
    'version': '18.0.3.1.1',
    'depends': [
        'base',
    ],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/hr_hospital_hospital_views.xml',
        'views/hr_hospital_doctor_views.xml',
        'views/hr_hospital_patient_views.xml',
        'views/hr_hospital_disease_views.xml',
        'views/hr_hospital_visit_views.xml',
        'views/hr_hospital_menu.xml',
        'data/hr_hospital_disease_data.xml',
    ],
    'demo': [
        'demo/hr_hospital_hospital_demo.xml',
        'demo/hr_hospital_doctor_demo.xml',
        'demo/hr_hospital_patient_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'images': [
        'static/description/icon.png',
    ],
    'application': False,
}
