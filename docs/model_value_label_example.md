# Using Autocomplete with Django Models: Value/Label Pattern

This guide demonstrates how to use the suitable-django-autocomplete widget with Django models, ensuring that user-friendly labels are displayed while the correct model IDs are submitted.

## The Challenge

When working with Django ForeignKey or ModelChoiceField, you typically want to:
- Display a user-friendly label (e.g., "iPhone 15 Pro - $999")
- Submit the actual model ID (e.g., "42")
- Convert the submitted ID back to a model instance

## How It Works

The suitable-django-autocomplete widget handles this automatically through:

1. **Separate Display and Submit Values**: The JavaScript component maintains two values:
   - What the user sees in the input field (label)
   - What gets submitted with the form (value)

2. **Web Components Form Integration**: Uses the `ElementInternals` API to properly set form values

3. **ModelChoiceField Integration**: The `ModelAutocompleteField` extends Django's `ModelChoiceField` to handle ID-to-instance conversion

## Complete Example

### 1. Models (models.py)

```python
from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    in_stock = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### 2. Autocomplete Views (views.py)

```python
from suitable_django_autocomplete.views import ModelAutocompleteView
from django.contrib.auth.models import User
from .models import Product

class ProductAutocompleteView(ModelAutocompleteView):
    model = Product
    search_fields = ['name', 'sku', 'category']
    
    def get_queryset(self):
        # Only show in-stock products
        qs = super().get_queryset()
        return qs.filter(in_stock=True)
    
    def format_result(self, obj):
        """
        Return a dictionary with separate value and label.
        The value is what gets submitted, the label is what's displayed.
        """
        return {
            'value': str(obj.id),  # Submit the ID
            'label': f"{obj.name} - ${obj.price} ({obj.category})",  # Display friendly text
            # Include extra data if needed for client-side logic
            'price': float(obj.price),
            'sku': obj.sku,
            'category': obj.category
        }

class CustomerAutocompleteView(ModelAutocompleteView):
    model = User
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    def format_result(self, obj):
        # Build a descriptive label
        parts = [obj.username]
        if obj.get_full_name():
            parts.append(f"({obj.get_full_name()})")
        if obj.email:
            parts.append(f"- {obj.email}")
        
        return {
            'value': str(obj.id),
            'label': ' '.join(parts)
        }
```

### 3. Forms (forms.py)

```python
from django import forms
from suitable_django_autocomplete import ModelAutocompleteField, AutocompleteWidget
from .models import Order, Product

class OrderForm(forms.ModelForm):
    # Override the default fields with autocomplete versions
    customer = ModelAutocompleteField(
        queryset=User.objects.all(),
        url='/autocomplete/customers/',
        widget=AutocompleteWidget(
            attrs={'placeholder': 'Start typing customer name...'},
            min_length=2,
            debounce_delay=300,
            # These are the defaults, shown for clarity
            value_field='value',  # Which field contains the submit value
            label_field='label'   # Which field contains the display text
        ),
        help_text='Search by username, name, or email'
    )
    
    product = ModelAutocompleteField(
        queryset=Product.objects.filter(in_stock=True),
        url='/autocomplete/products/',
        widget=AutocompleteWidget(
            attrs={'placeholder': 'Search products...'}
        ),
        help_text='Search by product name, SKU, or category'
    )
    
    class Meta:
        model = Order
        fields = ['customer', 'product', 'quantity', 'notes']

class OrderEditForm(OrderForm):
    """Form for editing existing orders with pre-populated autocomplete fields."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # When editing, set initial display values for autocomplete fields
        if self.instance and self.instance.pk:
            # Set initial display value for customer
            if self.instance.customer:
                customer = self.instance.customer
                label_parts = [customer.username]
                if customer.get_full_name():
                    label_parts.append(f"({customer.get_full_name()})")
                if customer.email:
                    label_parts.append(f"- {customer.email}")
                
                self.fields['customer'].widget.initial_display_value = ' '.join(label_parts)
            
            # Set initial display value for product
            if self.instance.product:
                product = self.instance.product
                self.fields['product'].widget.initial_display_value = (
                    f"{product.name} - ${product.price} ({product.category})"
                )
```

### 4. URL Configuration (urls.py)

```python
from django.urls import path
from .views import ProductAutocompleteView, CustomerAutocompleteView

urlpatterns = [
    # ... other patterns ...
    path('autocomplete/products/', ProductAutocompleteView.as_view(), name='autocomplete-products'),
    path('autocomplete/customers/', CustomerAutocompleteView.as_view(), name='autocomplete-customers'),
]
```

### 5. Template Usage

The form renders normally:

```django
{% load crispy_forms_tags %}

<form method="post">
    {% csrf_token %}
    {{ form|crispy }}
    <button type="submit" class="btn btn-primary">Save Order</button>
</form>
```

Or manually:

```django
<form method="post">
    {% csrf_token %}
    <div class="form-group">
        {{ form.customer.label_tag }}
        {{ form.customer }}
        {{ form.customer.help_text }}
        {{ form.customer.errors }}
    </div>
    <div class="form-group">
        {{ form.product.label_tag }}
        {{ form.product }}
        {{ form.product.help_text }}
        {{ form.product.errors }}
    </div>
    <!-- other fields ... -->
</form>
```

## Automatic Initial Display Values

**New in v0.4+**: The `ModelAutocompleteField` now automatically sets appropriate `initial_display_value` when editing existing records, so you don't need to manually set this in most cases!

### How It Works

When you specify `search_fields` in your `ModelAutocompleteField`, the widget automatically uses the **first search field** to generate a display value for initial/existing data:

```python
class OrderForm(forms.ModelForm):
    customer = ModelAutocompleteField(
        queryset=User.objects.all(),
        url='/autocomplete/customers/',
        search_fields=['first_name', 'last_name', 'email']  # Will use 'first_name'
    )
    
    class Meta:
        model = Order
        fields = ['customer', 'product', 'quantity']

# When editing an existing order, this "just works"
order = Order.objects.get(pk=1)
form = OrderForm(instance=order)  # Customer field will show the first_name automatically
```

### Fallback Behavior

If no `search_fields` are specified, it falls back to `str(model_instance)`:

```python
# Without search_fields
user_field = ModelAutocompleteField(
    queryset=User.objects.all(),
    url='/autocomplete/users/'
)
# Will display: "john_doe" (User.__str__ returns username)
```

### Manual Override

You can still manually set the display value if needed:

```python
form = OrderForm(instance=order)
# Override the automatic value
form.fields['customer'].widget.initial_display_value = "Custom Display Text"
```

## How the Value/Label Magic Works

### 1. User Types and Sees Results
When the user types, they see the formatted labels:
- "iPhone 15 Pro - $999 (Electronics)"
- "MacBook Air - $1299 (Computers)"

### 2. Selection Updates Both Values
When they select an item:
```javascript
// In autocomplete.js
this.input.value = label;        // User sees: "iPhone 15 Pro - $999 (Electronics)"
this.updateFormValue(value);     // Form submits: "42"
```

### 3. Form Submission
The form submits the ID value (e.g., "42"), not the display text.

### 4. Django Converts ID to Model Instance
The `ModelAutocompleteField.to_python()` method converts the submitted ID back to a model instance:
```python
# This happens automatically in ModelAutocompleteField
value = "42"  # What was submitted
instance = Product.objects.get(pk=value)  # Converted to model instance
```

## Advanced Patterns

### Custom Value Fields

If your model uses a different field as the identifier:

```python
class ProductAutocompleteView(ModelAutocompleteView):
    model = Product
    
    def format_result(self, obj):
        return {
            'value': obj.sku,  # Use SKU instead of ID
            'label': f"{obj.name} (SKU: {obj.sku})"
        }

# In the form
product = ModelAutocompleteField(
    queryset=Product.objects.all(),
    to_field_name='sku',  # Tell Django to lookup by SKU
    url='/autocomplete/products/'
)
```

### Multiple Display Formats

Provide different information density:

```python
def format_result(self, obj):
    return {
        'value': str(obj.id),
        'label': obj.name,  # Simple display in dropdown
        'display': f"{obj.name} - ${obj.price}",  # Richer display when selected
        'description': obj.description[:100]  # For tooltips
    }
```

### Conditional Formatting

Format based on object state:

```python
def format_result(self, obj):
    label = obj.name
    if obj.on_sale:
        label = f"🏷️ {label} (SALE: ${obj.sale_price})"
    elif obj.quantity < 10:
        label = f"⚠️ {label} (Low Stock)"
    
    return {
        'value': str(obj.id),
        'label': label
    }
```

## Troubleshooting

### Issue: Wrong value is submitted
**Solution**: Ensure your `format_result` returns a dict with 'value' key containing the ID.

### Issue: Initial values don't show labels
**Solution**: Set `initial_display_value` on the widget when initializing the form.

### Issue: Validation fails with "Select a valid choice"
**Solution**: Ensure the submitted value exists in the queryset and matches the `to_field_name`.

## Best Practices

1. **Always return consistent value types**: If using IDs, always return strings
2. **Include meaningful labels**: Help users identify the correct option
3. **Filter querysets appropriately**: Don't expose options users shouldn't select
4. **Set initial display values**: For edit forms, always set the display label
5. **Use descriptive search fields**: Enable searching by multiple attributes

## Summary

The suitable-django-autocomplete widget seamlessly handles the complexity of displaying user-friendly labels while submitting proper model identifiers. This pattern works perfectly with Django's ModelChoiceField and ForeignKey relationships, providing an excellent user experience without sacrificing data integrity.