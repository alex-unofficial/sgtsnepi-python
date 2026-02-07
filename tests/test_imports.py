#!/usr/bin/env python3
"""Simple smoke test to verify sgtsnepi package imports correctly."""

def test_import_module():
    """Test that the module can be imported."""
    import sgtsnepi
    assert sgtsnepi is not None

def test_import_function():
    """Test that the main function can be imported directly."""
    from sgtsnepi import sgtsnepi
    assert sgtsnepi is not None
    assert callable(sgtsnepi)

if __name__ == "__main__":
    test_import_module()
    test_import_function()
    print("✓ All import tests passed")
