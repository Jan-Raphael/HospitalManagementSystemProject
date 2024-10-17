from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import DoctorAccount


@admin.register(DoctorAccount)
class DoctorAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialty', 'years_of_experience', 'is_approved')
    list_filter = ('is_approved', 'specialty')
    search_fields = ('user__username', 'specialty')
    actions = ['approve_doctors', 'reject_doctors']

    def approve_doctors(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, "Selected doctor accounts have been approved.")

    approve_doctors.short_description = "Approve selected doctors"

    def reject_doctors(self, request, queryset):
        for doctor in queryset:
            doctor.user.delete()  # Optionally delete the user
        self.message_user(request, "Selected doctor accounts have been rejected and deleted.")

    reject_doctors.short_description = "Reject selected doctors"