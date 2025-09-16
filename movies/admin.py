from django.contrib import admin
from django import forms
from .models import Movie, Review

class MovieAdminForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = '__all__'
    
    def clean_amount_left(self):
        amount_left = self.cleaned_data.get('amount_left')
        if self.instance.pk:  # Editing existing movie
            if self.instance.amount_left == 0 and amount_left != 0:
                raise forms.ValidationError("Cannot change amount_left when it equals 0.")
        return amount_left

class MovieAdmin(admin.ModelAdmin):
    form = MovieAdminForm
    ordering = ['name']
    search_fields = ['name']
    list_display = ['name', 'price', 'amount_left']
    fields = ['name', 'price', 'description', 'image', 'amount_left']
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.amount_left == 0:
            return ['amount_left']
        return []

admin.site.register(Movie, MovieAdmin)
admin.site.register(Review)
