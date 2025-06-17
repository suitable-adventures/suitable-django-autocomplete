from django import forms
from django.urls import reverse_lazy


class AutocompleteWidget(forms.TextInput):
    """Modern autocomplete widget for Django forms."""
    
    template_name = 'suitable_django_autocomplete/autocomplete.html'
    
    def __init__(self, url=None, attrs=None):
        self.url = url
        super().__init__(attrs)
    
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget'].update({
            'url': self.url or reverse_lazy('autocomplete'),
        })
        return context
    
    class Media:
        css = {
            'all': ('suitable_django_autocomplete/autocomplete.css',)
        }
        js = ('suitable_django_autocomplete/autocomplete.js',)