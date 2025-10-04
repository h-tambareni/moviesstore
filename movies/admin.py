from django.contrib import admin
from django import forms
from .models import Movie, Review, Petition, Vote

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

class VoteInline(admin.TabularInline):
    model = Vote
    extra = 0
    readonly_fields = ['created_at']

class PetitionAdmin(admin.ModelAdmin):
    list_display = ['movie_title', 'created_by', 'created_at', 'get_yes_votes_count', 'get_no_votes_count', 'is_processed']
    list_filter = ['created_at', 'is_processed']
    search_fields = ['movie_title', 'movie_description', 'created_by__username']
    readonly_fields = ['created_at']
    inlines = [VoteInline]
    
    def get_yes_votes_count(self, obj):
        return obj.get_yes_votes_count()
    get_yes_votes_count.short_description = 'Yes Votes'
    
    def get_no_votes_count(self, obj):
        return obj.get_no_votes_count()
    get_no_votes_count.short_description = 'No Votes'

class VoteAdmin(admin.ModelAdmin):
    list_display = ['petition', 'user', 'vote_type', 'created_at']
    list_filter = ['vote_type', 'created_at']
    search_fields = ['petition__movie_title', 'user__username']
    readonly_fields = ['created_at']

admin.site.register(Movie, MovieAdmin)
admin.site.register(Review)
admin.site.register(Petition, PetitionAdmin)
admin.site.register(Vote, VoteAdmin)
