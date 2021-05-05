from django.contrib import admin
from .models import User, Lead, UserProfile, Category, FollowUp


class LeadAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'age', 'email')
    list_filter = ('category',)
    search_fields = ('first_name', 'last_name', 'email')


admin.site.register(Lead, LeadAdmin)

admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(Category)
admin.site.register(FollowUp)
