from django.contrib import admin


from .models import Record

class SalesModelAdmin(admin.ModelAdmin):
    list_display = ["date","gross_sale","cash_recieved","eft_added"]
    # list_display_links = ["date"]
    date_hierarchy = 'date'
    list_per_page = 20
    list_filter = ['date','sold_by']
    search_fields = ['sold_by']
    list_editable = ['gross_sale','cash_recieved','eft_added']

    class Meta:
        model = Record


admin.site.register(Record,SalesModelAdmin)
