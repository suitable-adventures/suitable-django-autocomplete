# Security Considerations

This document outlines security considerations when using suitable-django-autocomplete.

## XSS Protection

All user-generated content displayed in autocomplete results is automatically HTML-escaped to prevent Cross-Site Scripting (XSS) attacks:

- The `ModelAutocompleteView.format_result()` method escapes both values and labels
- The JavaScript component uses `textContent` instead of `innerHTML` for displaying results
- Custom implementations should follow the same pattern

## CSRF Protection

When implementing autocomplete endpoints:

1. **Read-only endpoints** (GET requests):
   - CSRF protection is not required for read-only autocomplete searches
   - Ensure endpoints only perform read operations

2. **Write operations** (if any):
   - Apply Django's `@csrf_protect` decorator if the endpoint performs any write operations
   - Include CSRF token in AJAX requests

## Input Validation

### Server-side:
- Query parameters are automatically validated by Django's request handling
- Implement query length limits in your views:
  ```python
  def get(self, request):
      query = request.GET.get('q', '')[:100]  # Limit query length
  ```

### Client-side:
- The widget enforces a minimum query length (`min_length` parameter)
- Network requests include a 10-second timeout to prevent hanging requests

## Rate Limiting

Consider implementing rate limiting for autocomplete endpoints to prevent abuse:

```python
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

@method_decorator(cache_page(60), name='get')  # Cache for 1 minute
class MyAutocompleteView(ModelAutocompleteView):
    ...
```

Or use Django's rate limiting middleware/decorators.

## Database Query Protection

The built-in `ModelAutocompleteView`:
- Uses Django's ORM which provides SQL injection protection
- Limits results to prevent large data transfers (`limit` parameter)
- Uses `icontains` lookups which are safe from injection

## Access Control

Implement proper access control in your autocomplete views:

```python
from django.contrib.auth.mixins import LoginRequiredMixin

class SecureAutocompleteView(LoginRequiredMixin, ModelAutocompleteView):
    model = MyModel
    search_fields = ['name']
    
    def get_queryset(self):
        # Filter by user permissions
        return super().get_queryset().filter(owner=self.request.user)
```

## Content Security Policy (CSP)

The widget uses:
- Inline styles within Shadow DOM (safe and isolated)
- No inline scripts
- No external resource loading

Compatible with strict CSP policies.

## Best Practices

1. **Validate and sanitize all inputs** on the server side
2. **Implement appropriate access controls** for sensitive data
3. **Use HTTPS** in production to protect data in transit
4. **Monitor and log** autocomplete usage for suspicious patterns
5. **Keep dependencies updated** for security patches

## Reporting Security Issues

If you discover a security vulnerability, please email security@suitable-adventures.com with:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

Please do not open public issues for security vulnerabilities.