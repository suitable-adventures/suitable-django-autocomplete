"""
Tests for automatic initial_display_value setting in ModelAutocompleteField.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django import forms
from suitable_django_autocomplete import ModelAutocompleteField, AutocompleteWidget


class AutoInitialDisplayValueTest(TestCase):
    """Test automatic setting of initial_display_value for model fields."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
    
    def test_automatic_display_value_with_search_fields(self):
        """Test that display value is automatically set based on search fields."""
        
        class TestForm(forms.Form):
            user = ModelAutocompleteField(
                queryset=User.objects.all(),
                url='/autocomplete/users/',
                search_fields=['username', 'email']  # First field should be used
            )
        
        # Create form with initial value (model instance)
        form = TestForm(initial={'user': self.user})
        
        # Force prepare_value to be called (this happens during form rendering)
        form.fields['user'].prepare_value(self.user)
        
        # The widget should automatically have the display value set
        self.assertEqual(form.fields['user'].widget.initial_display_value, 'testuser')
    
    def test_automatic_display_value_with_id_initial(self):
        """Test that display value works when initial value is an ID."""
        
        class TestForm(forms.Form):
            user = ModelAutocompleteField(
                queryset=User.objects.all(),
                url='/autocomplete/users/',
                search_fields=['first_name', 'username']
            )
        
        # Create form with initial value (ID)
        form = TestForm(initial={'user': str(self.user.pk)})
        
        # Force prepare_value to be called (this happens during form rendering)
        form.fields['user'].prepare_value(str(self.user.pk))
        
        # The widget should automatically have the display value set
        # Should use first_name since it's the first search field
        self.assertEqual(form.fields['user'].widget.initial_display_value, 'Test')
    
    def test_get_display_value_method(self):
        """Test the get_display_value method directly."""
        
        field = ModelAutocompleteField(
            queryset=User.objects.all(),
            url='/autocomplete/users/',
            search_fields=['username', 'email']
        )
        
        # Should use the first search field
        display_value = field.get_display_value(self.user)
        self.assertEqual(display_value, 'testuser')
        
        # Test with different search fields
        field.search_fields = ['first_name', 'last_name']
        display_value = field.get_display_value(self.user)
        self.assertEqual(display_value, 'Test')
    
    def test_get_display_value_with_related_fields(self):
        """Test get_display_value with related field notation."""
        
        # Create a simple related model scenario using User's auth_permissions
        field = ModelAutocompleteField(
            queryset=User.objects.all(),
            url='/autocomplete/users/',
            search_fields=['username']  # Simple field
        )
        
        display_value = field.get_display_value(self.user)
        self.assertEqual(display_value, 'testuser')
    
    def test_get_display_value_fallback_to_str(self):
        """Test that it falls back to str(obj) when no search_fields."""
        
        field = ModelAutocompleteField(
            queryset=User.objects.all(),
            url='/autocomplete/users/',
            search_fields=[]  # No search fields
        )
        
        display_value = field.get_display_value(self.user)
        self.assertEqual(display_value, str(self.user))  # Should be 'testuser'
    
    def test_get_display_value_with_none(self):
        """Test get_display_value with None input."""
        
        field = ModelAutocompleteField(
            queryset=User.objects.all(),
            url='/autocomplete/users/',
            search_fields=['username']
        )
        
        display_value = field.get_display_value(None)
        self.assertEqual(display_value, '')
    
    def test_manual_initial_display_value_not_overridden(self):
        """Test that manually set initial_display_value is not overridden."""
        
        class TestForm(forms.Form):
            user = ModelAutocompleteField(
                queryset=User.objects.all(),
                url='/autocomplete/users/',
                search_fields=['username'],
                widget=AutocompleteWidget(
                    url='/autocomplete/users/',
                    initial_display_value='Manually Set Value'
                )
            )
        
        # Create form with initial value
        form = TestForm(initial={'user': self.user})
        
        # The manually set value should not be overridden
        self.assertEqual(form.fields['user'].widget.initial_display_value, 'Manually Set Value')
    
    def test_modelform_integration(self):
        """Test that this works with ModelForm scenarios."""
        
        # This would typically be in a ModelForm scenario where Django
        # automatically sets initial values from model instances
        field = ModelAutocompleteField(
            queryset=User.objects.all(),
            url='/autocomplete/users/',
            search_fields=['email', 'username']
        )
        
        # Simulate what Django does in ModelForm
        prepared_value = field.prepare_value(self.user)
        
        # Should return the ID as a string
        self.assertEqual(prepared_value, str(self.user.pk))
        
        # And the widget should have the display value set
        self.assertEqual(field.widget.initial_display_value, 'test@example.com')
    
    def test_prepare_value_with_invalid_id(self):
        """Test prepare_value handles invalid IDs gracefully."""
        
        field = ModelAutocompleteField(
            queryset=User.objects.all(),
            url='/autocomplete/users/',
            search_fields=['username']
        )
        
        # This should not raise an exception
        prepared_value = field.prepare_value('999999')  # Non-existent ID
        self.assertEqual(prepared_value, '999999')
        
        # Widget should not have initial_display_value set
        self.assertIsNone(field.widget.initial_display_value)