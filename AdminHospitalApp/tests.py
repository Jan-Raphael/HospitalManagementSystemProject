# AdminHospitalApp/tests.py

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import InventoryItem, AdminProfile


class InventoryTests(TestCase):
    def setUp(self):
        # Create an admin user
        self.user = User.objects.create_user(username='admin', password='adminpass')
        self.admin_profile = AdminProfile.objects.create(user=self.user, is_admin=True)
        self.client.login(username='admin', password='adminpass')

        # Create sample inventory items
        InventoryItem.objects.create(name='Syringe', description='Disposable syringe', quantity=50, reorder_level=10,
                                     price=0.50)
        InventoryItem.objects.create(name='Bandage', description='Medical bandage', quantity=20, reorder_level=5,
                                     price=1.00)

    def test_inventory_list_view(self):
        response = self.client.get(reverse('inventory_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Syringe')
        self.assertContains(response, 'Bandage')

    def test_add_inventory_item(self):
        response = self.client.post(reverse('add_inventory_item'), {
            'name': 'Gloves',
            'description': 'Latex gloves',
            'quantity': 100,
            'reorder_level': 20,
            'price': 0.10
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(InventoryItem.objects.filter(name='Gloves').exists())

    def test_edit_inventory_item(self):
        item = InventoryItem.objects.get(name='Syringe')
        response = self.client.post(reverse('edit_inventory_item', args=[item.pk]), {
            'name': 'Syringe',
            'description': 'Disposable syringe - updated',
            'quantity': 60,
            'reorder_level': 15,
            'price': 0.55
        })
        self.assertEqual(response.status_code, 302)
        item.refresh_from_db()
        self.assertEqual(item.description, 'Disposable syringe - updated')
        self.assertEqual(item.quantity, 60)
        self.assertEqual(item.reorder_level, 15)
        self.assertEqual(item.price, 0.55)

    def test_delete_inventory_item(self):
        item = InventoryItem.objects.get(name='Bandage')
        response = self.client.post(reverse('delete_inventory_item', args=[item.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(InventoryItem.objects.filter(name='Bandage').exists())

    def test_export_inventory_csv(self):
        response = self.client.get(reverse('export_inventory_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        content = response.content.decode()
        self.assertIn('Syringe', content)
        self.assertIn('Bandage', content)


# AdminHospitalApp/tests.py

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import FinancialRecord, AdminProfile


class FinancialRecordTests(TestCase):
    def setUp(self):
        # Create an admin user
        self.user = User.objects.create_user(username='admin', password='adminpass')
        self.admin_profile = AdminProfile.objects.create(user=self.user, is_admin=True)
        self.client.login(username='admin', password='adminpass')

        # Create a financial record
        FinancialRecord.objects.create(transaction_type='Income', amount=1000, description='Test Income')

    def test_financial_records_view(self):
        response = self.client.get(reverse('financial_records'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Income')

    def test_add_financial_record(self):
        response = self.client.post(reverse('add_financial_record'), {
            'transaction_type': 'Expense',
            'amount': 500,
            'description': 'Test Expense'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(FinancialRecord.objects.filter(description='Test Expense').exists())

    def test_edit_financial_record(self):
        record = FinancialRecord.objects.get(description='Test Income')
        response = self.client.post(reverse('edit_financial_record', args=[record.pk]), {
            'transaction_type': 'Income',
            'amount': 1500,
            'description': 'Updated Income'
        })
        self.assertEqual(response.status_code, 302)
        record.refresh_from_db()
        self.assertEqual(record.amount, 1500)
        self.assertEqual(record.description, 'Updated Income')

    def test_delete_financial_record(self):
        record = FinancialRecord.objects.get(description='Test Income')
        response = self.client.post(reverse('delete_financial_record', args=[record.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(FinancialRecord.objects.filter(pk=record.pk).exists())

    def test_export_financial_records_csv(self):
        response = self.client.get(reverse('export_financial_records_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('Test Income', response.content.decode())

