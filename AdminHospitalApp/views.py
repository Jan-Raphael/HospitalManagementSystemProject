from .forms import InventoryItemForm, FinancialRecordForm
from .models import InventoryItem, FinancialRecord
from django.db.models import F, FloatField
from .forms import InventoryFilterForm
from django.db.models import F, FloatField
from .forms import InventoryFilterForm
from .forms import InventoryItemForm, FinancialRecordForm
from .models import InventoryItem, FinancialRecord


# Inventory Management
def admin_dashboard(request):
    return render(request, 'admin/admin_dashboard.html')




def inventory_reports(request):
    total_items = InventoryItem.objects.aggregate(total=Sum('quantity'))['total'] or 0
    total_inventory_value = InventoryItem.objects.aggregate(
        total=Sum(F('quantity') * F('price'), output_field=FloatField())
    )['total'] or 0
    low_stock_items = InventoryItem.objects.filter(quantity__lte=F('reorder_level'))

    context = {
        'total_items': total_items,
        'total_inventory_value': total_inventory_value,
        'low_stock_items': low_stock_items,
    }
    return render(request, 'admin/inventory_reports.html', context)


def inventory_list(request):
    form = InventoryFilterForm(request.GET or None)
    items = InventoryItem.objects.all()

    if form.is_valid():
        name = form.cleaned_data.get('name')
        min_quantity = form.cleaned_data.get('min_quantity')
        max_quantity = form.cleaned_data.get('max_quantity')
        price_min = form.cleaned_data.get('price_min')
        price_max = form.cleaned_data.get('price_max')

        if name:
            items = items.filter(name__icontains=name)
        if min_quantity is not None:
            items = items.filter(quantity__gte=min_quantity)
        if max_quantity is not None:
            items = items.filter(quantity__lte=max_quantity)
        if price_min is not None:
            items = items.filter(price__gte=price_min)
        if price_max is not None:
            items = items.filter(price__lte=price_max)

    paginator = Paginator(items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin/inventory_list.html', {'items': page_obj, 'form': form})


def export_inventory_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inventory_items.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Description', 'Quantity', 'Reorder Level', 'Price'])

    items = InventoryItem.objects.all()
    for item in items:
        writer.writerow([item.name, item.description, item.quantity, item.reorder_level, item.price])

    return response


def add_inventory_item(request):
    if request.method == 'POST':
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventory_list')
    else:
        form = InventoryItemForm()
    return render(request, 'admin/add_inventory_item.html', {'form': form})


def edit_inventory_item(request, pk):
    item = InventoryItem.objects.get(pk=pk)
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('inventory_list')
    else:
        form = InventoryItemForm(instance=item)
    return render(request, 'admin/edit_inventory_item.html', {'form': form})

def delete_inventory_item(request, pk):
    item = InventoryItem.objects.get(pk=pk)
    item.delete()
    return redirect('inventory_list')


def add_financial_record(request):
    if request.method == 'POST':
        form = FinancialRecordForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('financial_records')
    else:
        form = FinancialRecordForm()
    return render(request, 'admin/add_financial_record.html', {'form': form})


def edit_financial_record(request, pk):
    record = get_object_or_404(FinancialRecord, pk=pk)
    if request.method == 'POST':
        form = FinancialRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect('financial_records')
    else:
        form = FinancialRecordForm(instance=record)
    return render(request, 'admin/edit_financial_record.html', {'form': form})


def delete_financial_record(request, pk):
    record = get_object_or_404(FinancialRecord, pk=pk)
    if request.method == 'POST':
        record.delete()
        return redirect('financial_records')
    return render(request, 'admin/delete_financial_record.html', {'record': record})


from .forms import FinancialRecordFilterForm



def financial_records(request):
    form = FinancialRecordFilterForm(request.GET or None)
    records = FinancialRecord.objects.all()

    if form.is_valid():
        transaction_type = form.cleaned_data.get('transaction_type')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')

        if transaction_type:
            records = records.filter(transaction_type=transaction_type)
        if start_date:
            records = records.filter(date__gte=start_date)
        if end_date:
            records = records.filter(date__lte=end_date)

    return render(request, 'admin/financial_records.html', {'records': records, 'form': form})

from django.db.models import Sum


def financial_reports(request):
    income_total = FinancialRecord.objects.filter(transaction_type='Income').aggregate(Sum('amount'))['amount__sum'] or 0
    expense_total = FinancialRecord.objects.filter(transaction_type='Expense').aggregate(Sum('amount'))['amount__sum'] or 0
    net_profit = income_total - expense_total
    context = {
        'income_total': income_total,
        'expense_total': expense_total,
        'net_profit': net_profit,
    }
    return render(request, 'admin/financial_reports.html', context)


def export_financial_records_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="financial_records.csv"'

    writer = csv.writer(response)
    writer.writerow(['Transaction Type', 'Amount', 'Description', 'Date'])

    records = FinancialRecord.objects.all()
    for record in records:
        writer.writerow([record.transaction_type, record.amount, record.description, record.date])

    return response

def is_admin(user):
    return user.is_authenticated and hasattr(user, 'adminprofile') and user.adminprofile.is_admin


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from HospitalApp.models import PatientAccount, DoctorAccount
from .forms import UserForm, PatientAccountForm, DoctorAccountForm, SearchForm
from django.core.paginator import Paginator
import csv
from django.http import HttpResponse

def account_list(request):
    search_form = SearchForm(request.GET or None)
    users = User.objects.all().order_by('-date_joined')

    if search_form.is_valid():
        query = search_form.cleaned_data.get('query')
        role = search_form.cleaned_data.get('role')

        if query:
            users = users.filter(username__icontains=query) | users.filter(email__icontains=query)

        if role == 'patient':
            users = users.filter(patientaccount__isnull=False)
        elif role == 'doctor':
            users = users.filter(doctoraccount__isnull=False)

    paginator = Paginator(users, 10)  # Show 10 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'users': page_obj,
        'search_form': search_form,
    }
    return render(request, 'admin/account_list.html', context)


def add_account(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        role = request.POST.get('role')

        if user_form.is_valid():
            user = user_form.save()
            if role == 'patient':
                patient_form = PatientAccountForm(request.POST, request.FILES)
                if patient_form.is_valid():
                    patient = patient_form.save(commit=False)
                    patient.user = user
                    patient.save()
            elif role == 'doctor':
                doctor_form = DoctorAccountForm(request.POST)
                if doctor_form.is_valid():
                    doctor = doctor_form.save(commit=False)
                    doctor.user = user
                    doctor.save()
            return redirect('account_list')
    else:
        user_form = UserForm()
        patient_form = PatientAccountForm()
        doctor_form = DoctorAccountForm()

    context = {
        'user_form': user_form,
        'patient_form': PatientAccountForm(),
        'doctor_form': DoctorAccountForm(),
    }
    return render(request, 'admin/add_account.html', context)


def edit_account(request, pk):
    user = get_object_or_404(User, pk=pk)
    try:
        patient_profile = user.patientaccount
        profile_type = 'patient'
    except PatientAccount.DoesNotExist:
        patient_profile = None
        try:
            doctor_profile = user.doctoraccount
            profile_type = 'doctor'
        except DoctorAccount.DoesNotExist:
            doctor_profile = None
            profile_type = 'unknown'

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        if profile_type == 'patient':
            profile_form = PatientAccountForm(request.POST, request.FILES, instance=patient_profile)
        elif profile_type == 'doctor':
            profile_form = DoctorAccountForm(request.POST, instance=doctor_profile)
        else:
            profile_form = None

        if user_form.is_valid() and (profile_form.is_valid() if profile_form else True):
            user_form.save()
            if profile_form:
                profile_form.save()
            return redirect('account_list')
    else:
        user_form = UserForm(instance=user)
        if profile_type == 'patient':
            profile_form = PatientAccountForm(instance=patient_profile)
        elif profile_type == 'doctor':
            profile_form = DoctorAccountForm(instance=doctor_profile)
        else:
            profile_form = None

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile_type': profile_type,
    }
    return render(request, 'admin/edit_account.html', context)



def delete_account(request, pk):
    user = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        user.delete()
        return redirect('account_list')

    return render(request, 'admin/delete_account.html', {'user': user})

def view_account(request, pk):
    user = get_object_or_404(User, pk=pk)
    try:
        patient_profile = user.patientaccount
        profile_type = 'patient'
    except PatientAccount.DoesNotExist:
        patient_profile = None
        try:
            doctor_profile = user.doctoraccount
            profile_type = 'doctor'
        except DoctorAccount.DoesNotExist:
            doctor_profile = None
            profile_type = 'unknown'

    context = {
        'user': user,
        'profile_type': profile_type,
        'patient_profile': patient_profile,
        'doctor_profile': doctor_profile,
    }
    return render(request, 'admin/view_account.html', context)

def export_accounts_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="accounts.csv"'

    writer = csv.writer(response)
    writer.writerow(['Username', 'Email', 'First Name', 'Last Name', 'Role', 'Phone Number', 'Address', 'Specialty',
                     'Years of Experience'])

    users = User.objects.all().order_by('-date_joined')
    for user in users:
        try:
            patient = user.patientaccount
            role = 'Patient'
            phone_number = patient.phone_number
            address = patient.address
            specialty = ''
            years_of_experience = ''
        except PatientAccount.DoesNotExist:
            try:
                doctor = user.doctoraccount
                role = 'Doctor'
                phone_number = ''
                address = ''
                specialty = doctor.specialty
                years_of_experience = doctor.years_of_experience
            except DoctorAccount.DoesNotExist:
                role = 'Unknown'
                phone_number = ''
                address = ''
                specialty = ''
                years_of_experience = ''

        writer.writerow([
            user.username,
            user.email,
            user.first_name,
            user.last_name,
            role,
            phone_number,
            address,
            specialty,
            years_of_experience
        ])

    return response