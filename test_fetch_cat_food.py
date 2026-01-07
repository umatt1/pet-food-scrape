#!/usr/bin/env python3
"""
Tests for the cat food scraper script.

This test file validates the core functionality of the scraper,
including database operations and data parsing.
"""

import sqlite3
import os
import sys
import json

# Import functions from the main script
sys.path.insert(0, os.path.dirname(__file__))
from fetch_cat_food import (
    create_database,
    parse_product_data,
    insert_product,
    DB_NAME
)


def test_database_creation():
    """Test that the database and table are created correctly."""
    # Clean up any existing test database
    test_db = "test_pet_food.db"
    if os.path.exists(test_db):
        os.remove(test_db)
    
    # Temporarily override DB_NAME
    import fetch_cat_food
    original_db = fetch_cat_food.DB_NAME
    fetch_cat_food.DB_NAME = test_db
    
    try:
        create_database()
        
        # Verify database exists
        assert os.path.exists(test_db), "Database file was not created"
        
        # Verify table schema
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
        result = cursor.fetchone()
        assert result is not None, "Products table was not created"
        
        # Verify columns
        cursor.execute("PRAGMA table_info(products)")
        columns = {row[1] for row in cursor.fetchall()}
        expected_columns = {
            'id', 'barcode', 'name', 'brand', 'ingredients',
            'protein_100g', 'fat_100g', 'fiber_100g',
            'carbohydrates_100g', 'energy_kcal_100g', 'created_at'
        }
        assert expected_columns.issubset(columns), f"Missing columns. Expected: {expected_columns}, Got: {columns}"
        
        conn.close()
        print("✓ Database creation test passed")
        
    finally:
        # Restore original DB_NAME and clean up
        fetch_cat_food.DB_NAME = original_db
        if os.path.exists(test_db):
            os.remove(test_db)


def test_parse_product_data():
    """Test that product data is parsed correctly."""
    # Sample product data similar to API response
    sample_product = {
        'product_name': 'Test Cat Food',
        'brands': 'Test Brand',
        'ingredients_text': 'Chicken, Rice, Vegetables',
        'nutriments': {
            'proteins_100g': 10.5,
            'fat_100g': 5.2,
            'fiber_100g': 1.8,
            'carbohydrates_100g': 3.5,
            'energy-kcal_100g': 95.0
        }
    }
    
    barcode = '1234567890123'
    parsed = parse_product_data(sample_product, barcode)
    
    # Verify parsed data
    assert parsed['barcode'] == barcode, "Barcode not parsed correctly"
    assert parsed['name'] == 'Test Cat Food', "Name not parsed correctly"
    assert parsed['brand'] == 'Test Brand', "Brand not parsed correctly"
    assert parsed['ingredients'] == 'Chicken, Rice, Vegetables', "Ingredients not parsed correctly"
    assert parsed['protein_100g'] == 10.5, "Protein not parsed correctly"
    assert parsed['fat_100g'] == 5.2, "Fat not parsed correctly"
    assert parsed['fiber_100g'] == 1.8, "Fiber not parsed correctly"
    assert parsed['carbohydrates_100g'] == 3.5, "Carbohydrates not parsed correctly"
    assert parsed['energy_kcal_100g'] == 95.0, "Energy not parsed correctly"
    
    print("✓ Parse product data test passed")


def test_insert_product():
    """Test that product data can be inserted into the database."""
    test_db = "test_pet_food.db"
    if os.path.exists(test_db):
        os.remove(test_db)
    
    # Temporarily override DB_NAME
    import fetch_cat_food
    original_db = fetch_cat_food.DB_NAME
    fetch_cat_food.DB_NAME = test_db
    
    try:
        create_database()
        
        # Test data
        product_data = {
            'barcode': '9876543210987',
            'name': 'Premium Cat Food',
            'brand': 'Premium Brand',
            'ingredients': 'Salmon, Tuna, Brown Rice',
            'protein_100g': 12.0,
            'fat_100g': 6.5,
            'fiber_100g': 2.0,
            'carbohydrates_100g': 4.0,
            'energy_kcal_100g': 105.0
        }
        
        insert_product(product_data)
        
        # Verify data was inserted
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE barcode = ?", (product_data['barcode'],))
        row = cursor.fetchone()
        
        assert row is not None, "Product was not inserted"
        assert row[1] == product_data['barcode'], "Barcode mismatch"
        assert row[2] == product_data['name'], "Name mismatch"
        assert row[3] == product_data['brand'], "Brand mismatch"
        assert row[4] == product_data['ingredients'], "Ingredients mismatch"
        
        conn.close()
        print("✓ Insert product test passed")
        
    finally:
        # Restore original DB_NAME and clean up
        fetch_cat_food.DB_NAME = original_db
        if os.path.exists(test_db):
            os.remove(test_db)


def test_parse_missing_data():
    """Test that parser handles missing data gracefully."""
    # Product with missing fields
    sparse_product = {
        'product_name': 'Minimal Cat Food',
        # Missing brands, ingredients, and most nutrients
        'nutriments': {
            'proteins_100g': 8.0
            # Missing other nutrients
        }
    }
    
    barcode = '1111111111111'
    parsed = parse_product_data(sparse_product, barcode)
    
    # Should handle missing data without errors
    assert parsed['barcode'] == barcode
    assert parsed['name'] == 'Minimal Cat Food'
    assert parsed['brand'] == ''
    assert parsed['ingredients'] == ''
    assert parsed['protein_100g'] == 8.0
    assert parsed['fat_100g'] is None
    assert parsed['fiber_100g'] is None
    
    print("✓ Parse missing data test passed")


def run_all_tests():
    """Run all tests."""
    print("Running tests for cat food scraper...\n")
    
    tests = [
        test_database_creation,
        test_parse_product_data,
        test_insert_product,
        test_parse_missing_data
    ]
    
    failed = 0
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Tests completed: {len(tests) - failed}/{len(tests)} passed")
    print(f"{'='*60}")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
