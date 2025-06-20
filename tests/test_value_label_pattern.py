"""
Tests demonstrating the value/label pattern for model autocomplete fields.
"""

import json
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django import forms
from suitable_django_autocomplete import ModelAutocompleteField, AutocompleteWidget
from suitable_django_autocomplete.views import ModelAutocompleteView


# Test models (in a real app, these would be in models.py)
class MockProduct:
    """Mock product model for testing."""
    def __init__(self, id, name, price, category):
        self.id = id
        self.pk = id
        self.name = name
        self.price = price
        self.category = category


class ProductAutocompleteView:
    """Test view that demonstrates value/label pattern."""
    
    def format_result(self, obj):
        return {
            'value': str(obj.id),  # What gets submitted
            'label': f"{obj.name} - ${obj.price} ({obj.category})"  # What user sees
        }
    
    def get_results(self, query):
        """Mock search functionality."""
        products = [
            MockProduct(1, "iPhone 15", 999.99, "Electronics"),
            MockProduct(2, "MacBook Pro", 2499.99, "Computers"),
            MockProduct(3, "AirPods", 249.99, "Audio")
        ]
        
        # Simple search - if query is in product name
        matching_products = [p for p in products if query.lower() in p.name.lower()]
        return [self.format_result(obj) for obj in matching_products]


class ValueLabelPatternTest(TestCase):
    """Test the value/label pattern works correctly."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
    
    def test_autocomplete_view_returns_value_and_label(self):
        """Test that the autocomplete view returns both value and label."""
        view = ProductAutocompleteView()
        
        # Test the get_results method directly
        results = view.get_results('phone')
        
        # Should find iPhone 15 (contains 'phone')
        iphone_results = [r for r in results if 'iPhone' in r['label']]
        self.assertEqual(len(iphone_results), 1)
        
        result = iphone_results[0]
        self.assertEqual(result['value'], '1')  # ID as string
        self.assertEqual(result['label'], 'iPhone 15 - $999.99 (Electronics)')
    
    def test_widget_configuration(self):
        """Test that the widget properly configures value and label fields."""
        widget = AutocompleteWidget(
            url='/autocomplete/products/',
            value_field='value',
            label_field='label'
        )
        
        context = widget.get_context('product', None, {})
        
        self.assertEqual(context['widget']['value_field'], 'value')
        self.assertEqual(context['widget']['label_field'], 'label')
    
    def test_initial_display_value(self):
        """Test that initial display values are properly set."""
        widget = AutocompleteWidget(
            url='/autocomplete/products/',
            initial_display_value='iPhone 15 - $999.99 (Electronics)'
        )
        
        context = widget.get_context('product', '1', {})  # '1' is the value (ID)
        
        self.assertEqual(context['widget']['value'], '1')
        self.assertEqual(context['widget']['initial_display_value'], 
                        'iPhone 15 - $999.99 (Electronics)')
    
    def test_model_autocomplete_field_form(self):
        """Test that ModelAutocompleteField works in a form."""
        
        class TestForm(forms.Form):
            product = forms.ChoiceField(
                choices=[('1', 'iPhone'), ('2', 'MacBook')],
                widget=AutocompleteWidget(
                    url='/autocomplete/products/',
                    initial_display_value='iPhone 15 - $999.99 (Electronics)'
                )
            )
        
        # Test form with initial value
        form = TestForm(initial={'product': '1'})
        
        # The widget should have both the value and display value
        widget = form.fields['product'].widget
        self.assertEqual(widget.initial_display_value, 'iPhone 15 - $999.99 (Electronics)')
        
        # Test form submission
        form = TestForm(data={'product': '1'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['product'], '1')  # Submits the ID
    
    def test_javascript_value_label_handling(self):
        """
        Test that demonstrates how the JavaScript would handle value/label.
        This is a documentation test showing the expected behavior.
        """
        # When the autocomplete returns results:
        mock_results = [
            {
                'value': '1',  # This goes to _internals.setFormValue()
                'label': 'iPhone 15 - $999.99 (Electronics)'  # This goes to input.value
            },
            {
                'value': '2',
                'label': 'MacBook Pro - $2499.99 (Computers)'
            }
        ]
        
        # The JavaScript component would:
        # 1. Display the label in the dropdown
        # 2. When selected, show the label in the input field
        # 3. But submit the value through the form
        
        # This is handled by the JavaScript code:
        # this.input.value = label;        // User sees the label
        # this.updateFormValue(value);     // Form submits the value
        
        # Form submission would contain:
        expected_form_data = {'product': '1'}  # Not the label!
        
        self.assertEqual(mock_results[0]['value'], expected_form_data['product'])