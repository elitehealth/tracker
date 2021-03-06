from django.contrib import admin


from .models import appointment

class AppointmentModelAdmin(admin.ModelAdmin):
    list_display = ["date","consultations_scheduled"]
    # list_display_links = ["date"]
    date_hierarchy = 'date'
    list_per_page = 20
    list_filter = ['date']

    class Meta:
        model = appointment


admin.site.register(appointment,AppointmentModelAdmin)
