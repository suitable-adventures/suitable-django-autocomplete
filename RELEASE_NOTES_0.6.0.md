# Release Notes - v0.6.0

## 🚀 Security and Reliability Release

This release focuses on improving security, code quality, and error handling throughout the library.

### 🔒 Security Enhancements

- **XSS Protection**: All user-generated content in autocomplete results is now automatically HTML-escaped
- **Request Security**: Added proper request headers and timeout protection
- **Security Documentation**: New SECURITY.md file with comprehensive security guidelines

### 🛡️ Error Handling Improvements

- **Network Timeouts**: Autocomplete requests now timeout after 10 seconds
- **Better Error Messages**: Users see specific, helpful error messages for different failure scenarios
- **Response Validation**: Added validation for server responses to handle malformed data gracefully

### 📝 Code Quality

- **Type Hints**: Added comprehensive type annotations to Python code for better IDE support
- **Version Consistency**: Fixed version mismatch between package files
- **Project Organization**: Improved test file structure

### 📋 Full Changelog

#### Added
- XSS protection via HTML escaping in `ModelAutocompleteView.format_result()`
- Network request timeout handling (10 seconds)
- Comprehensive error handling in JavaScript with user-friendly messages
- Type hints for all public methods in views.py and widgets.py
- SECURITY.md documentation file
- Request headers for better server-side handling

#### Changed
- Moved test HTML files to `tests/fixtures/` directory
- Enhanced error messages for network failures, timeouts, and server errors

#### Fixed
- Version mismatch between pyproject.toml and __init__.py
- Potential XSS vulnerability in autocomplete results

#### Security
- All user-generated content is now HTML-escaped before display
- Added timeout protection to prevent hanging requests
- Documented security best practices in SECURITY.md

### 💡 Upgrade Notes

This release is fully backward compatible. No code changes are required when upgrading from 0.5.x.

The security improvements are applied automatically - your autocomplete results will now be HTML-escaped by default. If you have custom `format_result()` implementations, consider adding escaping to those as well:

```python
from django.utils.html import escape

def format_result(self, obj):
    return {
        'value': escape(str(obj.id)),
        'label': escape(str(obj.name)),
    }
```

### 🙏 Thanks

Thanks to all contributors who helped identify and fix these security and reliability issues!