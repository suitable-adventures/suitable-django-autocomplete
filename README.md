# Suitable Django Autocomplete

A modern, accessible autocomplete widget for Django 4.2+ built with web components. No jQuery or other JavaScript framework dependencies required.

[![PyPI version](https://badge.fury.io/py/suitable-django-autocomplete.svg)](https://badge.fury.io/py/suitable-django-autocomplete)
[![Python versions](https://img.shields.io/pypi/pyversions/suitable-django-autocomplete)](https://pypi.org/project/suitable-django-autocomplete/)
[![Django versions](https://img.shields.io/badge/Django-4.2%2B-blue)](https://www.djangoproject.com/)

## Features

- 🎯 **Zero dependencies** - No jQuery, no framework lock-in
- ♿ **Fully accessible** - ARIA compliant with keyboard navigation
- 🚀 **Web components** - Uses native browser APIs
- 🔍 **Smart search** - Debounced search with loading states
- 🎨 **Customizable** - Easy to style and extend
- 📱 **Mobile friendly** - Works great on touch devices
- 🔧 **Django integration** - Seamless form field integration

## Installation

```bash
pip install suitable-django-autocomplete
```

Or with uv:

```bash
uv add suitable-django-autocomplete
```

## Quick Start

### 1. Add to your Django settings

```python
INSTALLED_APPS = [
    ...
    'suitable_django_autocomplete',
]
```

### 2. Create an autocomplete view

```python
# views.py
from suitable_django_autocomplete import SimpleAutocompleteView

class FruitAutocompleteView(SimpleAutocompleteView):
    choices = [
        'Apple', 'Apricot', 'Banana', 'Blackberry', 'Blueberry',
        'Cherry', 'Date', 'Elderberry', 'Fig', 'Grape'
    ]
```

### 3. Add URL pattern

```python
# urls.py
from django.urls import path
from .views import FruitAutocompleteView

urlpatterns = [
    path('autocomplete/fruits/', FruitAutocompleteView.as_view(), name='fruits-autocomplete'),
]
```

### 4. Use in your forms

```python
# forms.py
from django import forms
from suitable_django_autocomplete import AutocompleteField

class OrderForm(forms.Form):
    favorite_fruit = AutocompleteField(
        url='/autocomplete/fruits/',
        attrs={'placeholder': 'Start typing a fruit name...'}
    )
```

### 5. Include in your templates

```html
<!-- your_template.html -->
<form method="post">
  {% csrf_token %} {{ form.as_p }}
  <!-- This loads the required CSS and JavaScript -->
  {{ form.media }}
  <button type="submit">Submit</button>
</form>
```

## Model-Based Autocomplete

For database-backed autocomplete, use `ModelAutocompleteView`:

```python
# views.py
from django.contrib.auth.models import User
from suitable_django_autocomplete import ModelAutocompleteView

class UserAutocompleteView(ModelAutocompleteView):
    model = User
    search_fields = ['username', 'first_name', 'last_name', 'email']

    def get_queryset(self):
        # Optional: add custom filtering
        return super().get_queryset().filter(is_active=True)

# forms.py
from suitable_django_autocomplete import ModelAutocompleteField

class TaskForm(forms.ModelForm):
    assigned_to = ModelAutocompleteField(
        queryset=User.objects.filter(is_active=True),
        url='/autocomplete/users/',
        attrs={'placeholder': 'Search for a user...'}
    )

    class Meta:
        model = Task
        fields = ['title', 'assigned_to']
```

## Value/Label Pattern for Model Fields

When working with Django model relationships (ForeignKey, OneToOneField), you often need to display user-friendly labels while submitting the actual model ID. The autocomplete widget handles this seamlessly:

```python
# views.py
class ProductAutocompleteView(ModelAutocompleteView):
    model = Product
    search_fields = ['name', 'sku', 'category']
    
    def format_result(self, obj):
        """Return both the value (ID) and display label."""
        return {
            'value': str(obj.id),  # What gets submitted
            'label': f"{obj.name} - ${obj.price} ({obj.category})"  # What user sees
        }

# forms.py
class OrderForm(forms.ModelForm):
    product = ModelAutocompleteField(
        queryset=Product.objects.filter(in_stock=True),
        url='/autocomplete/products/',
        widget=AutocompleteWidget(
            # These are the defaults:
            value_field='value',  # Which field contains the submit value
            label_field='label'   # Which field contains the display text
        )
    )
    
    class Meta:
        model = Order
        fields = ['product', 'quantity']
```

### Automatic Initial Display Values ✨

**New Feature**: When you specify `search_fields`, the widget automatically sets user-friendly display values for existing records:

```python
class OrderForm(forms.ModelForm):
    customer = ModelAutocompleteField(
        queryset=User.objects.all(),
        url='/autocomplete/customers/',
        search_fields=['first_name', 'last_name', 'email']  # Uses first_name for display
    )
    
    class Meta:
        model = Order
        fields = ['customer', 'quantity']

# When editing existing orders, this just works!
order = Order.objects.get(pk=1)
form = OrderForm(instance=order)  # Shows customer's first_name automatically
```

For custom display values, you can still override manually:

```python
# Custom display value
form.fields['customer'].widget.initial_display_value = "Custom Label"
```

The widget automatically:
- Shows the label text in the input field
- Submits the ID value with the form
- Converts the submitted ID back to a model instance

See the [detailed example](docs/model_value_label_example.md) for more complex use cases.

## Advanced Usage

### Custom Search Logic

```python
class ProductAutocompleteView(ModelAutocompleteView):
    model = Product
    search_fields = ['name', 'sku', 'category__name']

    def get_queryset(self):
        qs = super().get_queryset()
        # Only show products in stock
        return qs.filter(stock__gt=0)

    def get_result_label(self, obj):
        # Customize how results are displayed
        return f"{obj.name} (SKU: {obj.sku})"
```

### Styling

The widget uses semantic HTML and can be styled with CSS:

```css
/* Custom styling example */
.autocomplete-container {
  position: relative;
  width: 100%;
}

.autocomplete-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.autocomplete-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #ddd;
  border-top: none;
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
}

.autocomplete-result {
  padding: 8px 12px;
  cursor: pointer;
}

.autocomplete-result:hover,
.autocomplete-result[aria-selected="true"] {
  background-color: #f0f0f0;
}
```

## Browser Support

- Chrome 61+
- Firefox 63+
- Safari 10.1+
- Edge 79+

## Requirements

- Python 3.9+
- Django 4.2+

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Releasing New Versions

For maintainers: See [RELEASE.md](RELEASE.md) for the release process. New versions are automatically published to PyPI when a version tag is pushed.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
