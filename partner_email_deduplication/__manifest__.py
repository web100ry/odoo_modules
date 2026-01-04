{
    'name': 'Partner Email Deduplication',
    'version': '1.0.0',
    'category': 'Sales/CRM',
    'summary': 'Prevents duplicate emails for partners',
    'description': """
Partner Email Deduplication
===========================
This module ensures that no two partners in the system have the same email address.
It adds a constraint to the Partner model that checks for duplicate emails upon creation or update.
    """,
    'author': 'web100ry',
    'website': 'https://github.com/web100ry',
    'depends': ['base'],
    'data': [],
    'assets': {},
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
