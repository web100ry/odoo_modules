from odoo.tests.common import TransactionCase
from odoo.fields import Datetime


class TestHrHospitalModels(TransactionCase):

    def setUp(self):
        super(TestHrHospitalModels, self).setUp()
        self.Patient = self.env['hr.hospital.patient']
        self.Doctor = self.env['hr.hospital.doctor']
        self.Visit = self.env['hr.hospital.visit']
        self.Country = self.env['res.country']
        self.Lang = self.env['res.lang']

        # Create test data
        self.country_ua = self.Country.create({
            'name': 'Ukraine',
            'code': 'UA'
        })
        self.lang_ua = self.Lang.search(
            [('code', '=', 'uk_UA')],
            limit=1
        )
        if not self.lang_ua:
            self.lang_ua = self.Lang.create({
                'name': 'Ukrainian',
                'code': 'uk_UA'
            })

        self.doctor = self.Doctor.create({
            'first_name': 'Ivan',
            'last_name': 'Ivanov',
            'license_number': '12345',
            'gender': 'male',
        })

        self.patient = self.Patient.create({
            'first_name': 'Petro',
            'last_name': 'Petrov',
            'gender': 'male',
            'country_id': self.country_ua.id,
            'lang_id': self.lang_ua.id,
        })

    def test_01_search_patients_by_language(self):
        """Test search_patients_by_language method"""
        patients = self.Patient.search_patients_by_language('uk_UA')
        self.assertIn(self.patient, patients, "Patient should be "
                                              "found by language")

    def test_02_search_patients_by_country(self):
        """Test search_patients_by_country method"""
        patients = self.Patient.search_patients_by_country('UA')
        self.assertIn(self.patient, patients, "Patient should be "
                                              "found by country")

    def test_03_patient_doctor_history(self):
        """Test if history is created when personal
        doctor is assigned or changed"""
        # Test creation history
        new_patient = self.Patient.create({
            'first_name': 'Sidor',
            'last_name': 'Sidorov',
            'gender': 'male',
            'personal_doctor_id': self.doctor.id,
        })
        history = self.env['hr.hospital.patient.doctor.history'].search([
            ('patient_id', '=', new_patient.id)
        ])
        self.assertEqual(len(history), 1, "One history record should be "
                                          "created on creation")
        self.assertEqual(history.doctor_id, self.doctor)

        # Test change history
        doctor2 = self.Doctor.create({
            'first_name': 'Stepan',
            'last_name': 'Stepanov',
            'license_number': '67890',
            'gender': 'male',
        })
        new_patient.write({'personal_doctor_id': doctor2.id})
        history = self.env['hr.hospital.patient.doctor.history'].search([
            ('patient_id', '=', new_patient.id)
        ], order='change_date desc')
        self.assertEqual(len(history), 2, "Two history records should exist")
        self.assertEqual(history[0].doctor_id, doctor2)

    def test_04_visit_display_name(self):
        """Test _compute_display_name of hr.hospital.visit"""
        visit = self.Visit.create({
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id,
            'planned_datetime': Datetime.now(),
            'visit_type': 'primary',
        })
        # Doctor: Ivanov I., Patient: Petrov P.
        expected_name = "Dr.Ivanov I. / Petrov P."
        self.assertEqual(visit.display_name, expected_name)
