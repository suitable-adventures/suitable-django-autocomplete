# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.1] - 2025-06-26

### Changed

- **CSS Variables**: Added `--autocomplete-input-height` (default: 40px)
- **Font Size**: Changed default from 14px to 16px for better mobile usability
- **Documentation**: Added RELEASE_NOTES_0.6.0.md to document the previous release

### Fixed

- **Development**: Updated .gitignore to handle example_project directory variations

## [0.6.0] - 2025-06-26

### Added

- **XSS Protection**: HTML escaping in `ModelAutocompleteView.format_result()` method
- **Network Security**: Timeout handling (10 seconds) for autocomplete requests
- **Error Handling**: Enhanced JavaScript error handling with specific error messages
- **Security Documentation**: Comprehensive SECURITY.md file with best practices
- **Type Hints**: Added to all public methods in views.py and widgets.py
- **Request Headers**: Added for better server-side handling
- **Response Validation**: Added to handle malformed server responses

### Changed

- **CSS Variables**: Added `--autocomplete-input-height` (default: 40px)
- **Font Size**: Changed default from 14px to 16px for better mobile usability
- **Project Organization**: Moved test HTML files to `tests/fixtures/` directory

### Fixed

- **Version Mismatch**: Fixed inconsistency between pyproject.toml and __init__.py
- **XSS Vulnerability**: All user-generated content now properly escaped

### Security

- All user-generated content is now HTML-escaped to prevent XSS attacks
- Added timeout protection to prevent hanging requests
- Documented security best practices in SECURITY.md

## [0.5.2] - 2025-06-26

### Fixed

- Safari form submission issue where both ID and display label were being submitted
- Fixed by preventing the `name` attribute from being copied to shadow DOM input

## [0.5.1] - 2025-06-26

### Added

- External styling support for autocomplete input field
- CSS custom properties for comprehensive theming

### Changed

- Input field styling can now be customized via CSS variables

## [0.5.0] - 2025-06-25

### Added

- Automatic initial display value for ModelAutocompleteField
- Uses first search field for user-friendly display

### Changed

- ModelAutocompleteField now automatically shows meaningful text for existing values
