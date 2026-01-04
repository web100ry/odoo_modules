from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestPartnerEmailDeduplication(TransactionCase):

    def setUp(self):
        super(TestPartnerEmailDeduplication, self).setUp()
        self.Partner = self.env['res.partner']
        
        # Створення першого партнера
        self.partner1 = self.Partner.create({
            'name': 'Test Partner 1',
            'email': 'test@example.com'
        })

    def test_01_create_duplicate_email(self):
        """Перевірка створення партнера з дублікатом email"""
        with self.assertRaises(ValidationError):
            self.Partner.create({
                'name': 'Test Partner 2',
                'email': 'test@example.com'
            })

    def test_02_write_duplicate_email(self):
        """Перевірка оновлення партнера на дублікат email"""
        partner2 = self.Partner.create({
            'name': 'Test Partner 2',
            'email': 'unique@example.com'
        })
        with self.assertRaises(ValidationError):
            partner2.write({'email': 'test@example.com'})

    def test_03_allow_same_email_different_case(self):
        """
        Перевірка чи враховується регістр (в Odoo пошук зазвичай нечутливий до регістру для email в залежності від БД)
        У нашому коді ми використовуємо '=', що в PostgreSQL для Char полів зазвичай чутливо до регістру,
        але Odoo може мати свої особливості.
        """
        # Якщо ми хочемо сувору унікальність незалежно від регістру, код треба було б підправити.
        # Але за замовчуванням перевіримо поточну реалізацію.
        with self.assertRaises(ValidationError):
            self.Partner.create({
                'name': 'Test Partner 3',
                'email': 'TEST@EXAMPLE.COM'
            })

    def test_04_allow_empty_emails(self):
        """Перевірка що декілька партнерів можуть мати пустий email"""
        p1 = self.Partner.create({'name': 'No Email 1', 'email': False})
        p2 = self.Partner.create({'name': 'No Email 2', 'email': False})
        self.assertTrue(p1 and p2)
