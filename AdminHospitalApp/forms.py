from django import forms
from .models import InventoryItem, FinancialRecord

# Inventory form
class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['name', 'description', 'quantity', 'reorder_level', 'price']

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity < 0:
            raise forms.ValidationError("Quantity cannot be negative.")
        return quantity

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError("Price must be positive.")
        return price

from django import forms

class InventoryFilterForm(forms.Form):
    name = forms.CharField(required=False, label='Item Name')
    min_quantity = forms.IntegerField(required=False, min_value=0, label='Minimum Quantity')
    max_quantity = forms.IntegerField(required=False, min_value=0, label='Maximum Quantity')
    price_min = forms.DecimalField(required=False, min_value=0, decimal_places=2, label='Minimum Price')
    price_max = forms.DecimalField(required=False, min_value=0, decimal_places=2, label='Maximum Price')

# Financial form
from django import forms
from .models import FinancialRecord

class FinancialRecordForm(forms.ModelForm):
    class Meta:
        model = FinancialRecord
        fields = ['transaction_type', 'amount', 'description']
        widgets = {
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be positive.")
        return amount

class FinancialRecordFilterForm(forms.Form):
    TRANSACTION_TYPE_CHOICES = [
        ('', 'All'),
        ('Income', 'Income'),
        ('Expense', 'Expense'),
    ]
    transaction_type = forms.ChoiceField(
        choices=TRANSACTION_TYPE_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-control'})
    )
    start_date = forms.DateField(
        required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

from django import forms
from django.contrib.auth.models import User
from HospitalApp.models import PatientAccount, DoctorAccount
from django.contrib.auth.forms import UserCreationForm

class UserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
        return user

class PatientAccountForm(forms.ModelForm):
    class Meta:
        model = PatientAccount
        fields = ['phone_number', 'address', 'profile_photo', 'medical_records_photo', 'verification_status']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'profile_photo': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            'medical_records_photo': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }

class DoctorAccountForm(forms.ModelForm):
    class Meta:
        model = DoctorAccount
        fields = ['specialty', 'qualification', 'years_of_experience', 'is_doctor']
        widgets = {
            'qualification': forms.Textarea(attrs={'rows': 3}),
        }

class SearchForm(forms.Form):
    query = forms.CharField(max_length=100, required=False, label='Search')
    ROLE_CHOICES = [
        ('', 'All'),
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=False)