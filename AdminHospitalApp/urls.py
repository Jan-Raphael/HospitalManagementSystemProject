from django.urls import path
from . import views
from django.urls import path, include


urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/add/', views.add_inventory_item, name='add_inventory_item'),
    path('financial/', views.financial_records, name='financial_records'),
    path('financial/add/', views.add_financial_record, name='add_financial_record'),
    path('financial/edit/<int:pk>/', views.edit_financial_record, name='edit_financial_record'),
    path('financial/delete/<int:pk>/', views.delete_financial_record, name='delete_financial_record'),
    path('inventory/edit/<int:pk>/', views.edit_inventory_item, name='edit_inventory_item'),
    path('inventory/delete/<int:pk>/', views.delete_inventory_item, name='delete_inventory_item'),
path('financial/reports/', views.financial_reports, name='financial_reports'),
path('financial/export/csv/', views.export_financial_records_csv, name='export_financial_records_csv'),
path('inventory/reports/', views.inventory_reports, name='inventory_reports'),
    path('inventory/export/csv/', views.export_inventory_csv, name='export_inventory_csv'),
path('accounts/', views.account_list, name='account_list'),
    path('accounts/add/', views.add_account, name='add_account'),
    path('accounts/edit/<int:pk>/', views.edit_account, name='edit_account'),
    path('accounts/delete/<int:pk>/', views.delete_account, name='delete_account'),
    path('accounts/export/csv/', views.export_accounts_csv, name='export_accounts_csv'),
    path('accounts/view/<int:pk>/', views.view_account, name='view_account'),
]
