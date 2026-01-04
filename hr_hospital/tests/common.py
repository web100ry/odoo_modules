from odoo.tests.common import TransactionCase


class HrHospitalTest(TransactionCase):
    def setUp(self):
        super(HrHospitalTest, self).setUp()
        self.Patient = self.env['hr.hospital.patient']
        self.Doctor = self.env['hr.hospital.doctor']

    def test_create_patient(self):
        """Test creating a new patient"""
        patient = self.Patient.create({
            'name': 'John Doe',
            'age': 35,
            'gender': 'male',
            'phone': '+380501234567',
        })
        self.assertTrue(patient)
        self.assertEqual(patient.name, 'John Doe')
        self.assertEqual(patient.age, 35)
        self.assertEqual(patient.gender, 'male')

    def test_create_doctor(self):
        """Test creating a new doctor"""
        doctor = self.Doctor.create({
            'name': 'Dr. Smith',
            'specialization': 'Cardiology',
            'phone': '+380509876543',
        })
        self.assertTrue(doctor)
        self.assertEqual(doctor.name, 'Dr. Smith')
        self.assertEqual(doctor.specialization, 'Cardiology')
