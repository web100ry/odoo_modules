from odoo.tests.common import TransactionCase
from odoo.fields import Datetime
from datetime import timedelta

class TestCaritasFleet(TransactionCase):

    def setUp(self):
        super(TestCaritasFleet, self).setUp()
        self.department = self.env['vehicle.department'].create({'name': 'Test Department'})
        self.vehicle_model = self.env['fleet.vehicle.model'].create({
            'name': 'Model X',
            'brand_id': self.env['fleet.vehicle.model.brand'].create({'name': 'Brand X'}).id,
        })
        self.vehicle = self.env['fleet.vehicle'].create({
            'model_id': self.vehicle_model.id,
            'license_plate': 'TEST-001',
            'vehicle_department_id': self.department.id,
        })
        self.user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'test_user',
            'vehicle_department_id': self.department.id,
            'groups_id': [(4, self.env.ref('caritas_fleet.group_caritas_fleet_user').id)]
        })

    def test_01_create_request(self):
        """Test creating a vehicle request"""
        request = self.env['vehicle.request'].with_user(self.user).create({
            'request_type': 'with_driver',
            'vehicle_id': self.vehicle.id,
            'start_datetime': Datetime.now() + timedelta(days=1),
            'end_datetime': Datetime.now() + timedelta(days=1, hours=2),
        })
        self.assertTrue(request.name != 'New', "Reference should be generated")
        self.assertEqual(request.state, 'draft')

    def test_02_approve_request(self):
        """Test approving a request and automatic trip creation logic (if applicable)"""
        request = self.env['vehicle.request'].create({
            'requester_id': self.user.id,
            'request_type': 'with_driver',
            'vehicle_id': self.vehicle.id,
            'start_datetime': Datetime.now() + timedelta(days=1),
            'end_datetime': Datetime.now() + timedelta(days=1, hours=2),
        })
        request.action_approve()
        self.assertEqual(request.state, 'approved')

    def test_03_create_trip_and_event(self):
        """Test that creating a trip creates a calendar event"""
        request = self.env['vehicle.request'].create({
            'requester_id': self.user.id,
            'request_type': 'with_driver',
            'vehicle_id': self.vehicle.id,
            'start_datetime': Datetime.now() + timedelta(days=1),
            'end_datetime': Datetime.now() + timedelta(days=1, hours=2),
        })
        trip = self.env['vehicle.trip'].create({
            'request_id': request.id,
            'route': 'A to B',
        })
        self.assertTrue(trip.calendar_event_id, "Calendar event should be created automatically")
