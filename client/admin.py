from django.contrib import admin


from .models import Client, Program, Lead, Trainer

class ClientModelAdmin(admin.ModelAdmin):
    list_display = ["client_name","date_sign_up","gross_sale","cash_recieved","eft_added"]
    list_display_links = ["client_name"]
    date_hierarchy = 'date_sign_up'
    list_per_page = 20
    list_filter = ['date_sign_up','date_input']
    search_fields = ['client_name']
    list_editable = ['cash_recieved','eft_added']

    class Meta:
        model = Client


admin.site.register(Client,ClientModelAdmin)
admin.site.register(Program)
admin.site.register(Lead)
admin.site.register(Trainer)
