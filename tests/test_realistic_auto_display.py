"""
Test realistic scenarios for automatic initial_display_value setting.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django import forms
from suitable_django_autocomplete import ModelAutocompleteField


class RealisticAutoDisplayTest(TestCase):
    """Test realistic usage scenarios."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='john_doe',
            email='john@example.com',
            first_name='John',
            last_name='Doe'
        )
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            is_staff=True
        )
    
    def test_edit_form_scenario(self):
        """Test the common scenario of editing a model with ForeignKey."""
        
        # Simulate a model form for editing an order
        class OrderEditForm(forms.Form):
            customer = ModelAutocompleteField(
                queryset=User.objects.all(),
                url='/autocomplete/customers/',
                search_fields=['username', 'email', 'first_name']
            )
            assigned_to = ModelAutocompleteField(
                queryset=User.objects.filter(is_staff=True),
                url='/autocomplete/staff/',
                search_fields=['first_name', 'last_name', 'username']
            )
        
        # Create form with existing model data (what Django ModelForm does)
        form = OrderEditForm(initial={
            'customer': self.user,      # Model instance
            'assigned_to': self.admin   # Model instance
        })
        
        # When the form is rendered, prepare_value is called for each field
        customer_value = form.fields['customer'].prepare_value(self.user)
        assigned_value = form.fields['assigned_to'].prepare_value(self.admin)
        
        # Should return the IDs as strings
        self.assertEqual(customer_value, str(self.user.pk))
        self.assertEqual(assigned_value, str(self.admin.pk))
        
        # The widgets should have the display values set based on search_fields
        self.assertEqual(
            form.fields['customer'].widget.initial_display_value,
            'john_doe'  # First search field: username
        )
        self.assertEqual(
            form.fields['assigned_to'].widget.initial_display_value,
            'Admin'  # First search field: first_name
        )
    
    def test_form_with_initial_ids(self):
        """Test when form is initialized with IDs (common in views)."""
        
        class TaskForm(forms.Form):
            assignee = ModelAutocompleteField(
                queryset=User.objects.all(),
                url='/autocomplete/users/',
                search_fields=['email', 'username']  # Email first
            )
        
        # Simulate a view that passes ID as initial value
        form = TaskForm(initial={'assignee': str(self.user.pk)})
        
        # Render the field (calls prepare_value)
        value = form.fields['assignee'].prepare_value(str(self.user.pk))
        
        self.assertEqual(value, str(self.user.pk))
        self.assertEqual(
            form.fields['assignee'].widget.initial_display_value,
            'john@example.com'  # First search field: email
        )
    
    def test_no_search_fields_fallback(self):
        """Test fallback behavior when no search_fields specified."""
        
        class SimpleForm(forms.Form):
            user = ModelAutocompleteField(
                queryset=User.objects.all(),
                url='/autocomplete/users/',
                search_fields=[]  # No search fields
            )
        
        form = SimpleForm(initial={'user': self.user})
        form.fields['user'].prepare_value(self.user)
        
        # Should fall back to str(user) which is username for User model
        self.assertEqual(
            form.fields['user'].widget.initial_display_value,
            str(self.user)  # 'john_doe'
        )
    
    def test_template_rendering_scenario(self):
        """Test that the widget context includes the display value."""
        
        class ProfileForm(forms.Form):
            manager = ModelAutocompleteField(
                queryset=User.objects.filter(is_staff=True),
                url='/autocomplete/managers/',
                search_fields=['first_name', 'last_name']
            )
        
        form = ProfileForm(initial={'manager': self.admin})
        field = form.fields['manager']
        
        # Prepare the value (happens during rendering)
        field.prepare_value(self.admin)
        
        # Get the widget context (what the template sees)
        context = field.widget.get_context('manager', str(self.admin.pk), {})
        
        # The context should include the initial_display_value
        self.assertEqual(context['widget']['value'], str(self.admin.pk))
        self.assertEqual(context['widget']['initial_display_value'], 'Admin')
    
    def test_manual_override_not_touched(self):
        """Test that manually set initial_display_value is not overridden."""
        
        from suitable_django_autocomplete import AutocompleteWidget
        
        class CustomForm(forms.Form):
            user = ModelAutocompleteField(
                queryset=User.objects.all(),
                url='/autocomplete/users/',
                search_fields=['username'],
                widget=AutocompleteWidget(
                    url='/autocomplete/users/',
                    initial_display_value='Custom Display Value'
                )
            )
        
        form = CustomForm(initial={'user': self.user})
        form.fields['user'].prepare_value(self.user)
        
        # Manual value should be preserved
        self.assertEqual(
            form.fields['user'].widget.initial_display_value,
            'Custom Display Value'
        )
    
    def test_complex_search_fields(self):
        """Test with related field search patterns."""
        
        # Create some users with different data
        manager = User.objects.create_user(
            username='manager1',
            email='mgr@company.com',
            first_name='Jane',
            last_name='Manager'
        )
        
        class StaffForm(forms.Form):
            supervisor = ModelAutocompleteField(
                queryset=User.objects.all(),
                url='/autocomplete/supervisors/',
                search_fields=['last_name', 'first_name', 'email']  # Last name first
            )
        
        form = StaffForm(initial={'supervisor': manager})
        form.fields['supervisor'].prepare_value(manager)
        
        # Should use last_name (first search field)
        self.assertEqual(
            form.fields['supervisor'].widget.initial_display_value,
            'Manager'
        )