from django.contrib import admin


from .models import Target_type, Goal

class GoalModelAdmin(admin.ModelAdmin):
    list_display = ["date","sold_by","goal_type","goal"]
    list_display_links = ["date"]
    date_hierarchy = 'date'
    list_per_page = 20
    list_filter = ['date','goal_type']
    search_fields = ['sold_by']
    list_editable = ['goal']

    class Meta:
        model = Goal


admin.site.register(Goal,GoalModelAdmin)
admin.site.register(Target_type)
