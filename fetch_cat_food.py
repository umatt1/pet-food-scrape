#!/usr/bin/env python3
"""
Cat Food Data Scraper

This script fetches cat food product data from the OpenPetFoodFacts API
and stores it in a SQLite database.
"""

import sqlite3
import json
import time
from typing import Dict, List, Optional
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


# Example cat food barcodes (from OpenPetFoodFacts database)
EXAMPLE_BARCODES = [
    "3564700266403",  # Whiskas
    "5900951251573",  # Felix
    "8410136016905",  # Gourmet
    "5900951251566",  # Felix
    "3222473780505",  # Purina
]

API_BASE_URL = "https://world.openpetfoodfacts.org/api/v0/product/{barcode}.json"
DB_NAME = "pet_food.db"


def create_database():
    """Create the SQLite database and products table if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT UNIQUE NOT NULL,
            name TEXT,
            brand TEXT,
            ingredients TEXT,
            protein_100g REAL,
            fat_100g REAL,
            fiber_100g REAL,
            carbohydrates_100g REAL,
            energy_kcal_100g REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"Database '{DB_NAME}' initialized successfully.")


def fetch_product_data(barcode: str) -> Optional[Dict]:
    """
    Fetch product data from OpenPetFoodFacts API for a given barcode.
    
    Args:
        barcode: The product barcode
        
    Returns:
        Dictionary containing product data, or None if product not found
    """
    url = API_BASE_URL.format(barcode=barcode)
    
    try:
        # Add User-Agent header as required by OpenFoodFacts API
        req = Request(url, headers={'User-Agent': 'PetFoodScraper/1.0'})
        with urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if data.get('status') == 1 and 'product' in data:
                return data['product']
            else:
                print(f"Product not found for barcode: {barcode}")
                return None
                
    except HTTPError as e:
        print(f"HTTP Error fetching barcode {barcode}: {e.code} - {e.reason}")
        return None
    except URLError as e:
        print(f"URL Error fetching barcode {barcode}: {e.reason}")
        return None
    except Exception as e:
        print(f"Error fetching barcode {barcode}: {str(e)}")
        return None


def parse_product_data(product: Dict, barcode: str) -> Dict:
    """
    Parse product data and extract relevant fields.
    
    Args:
        product: Raw product data from API
        barcode: The product barcode
        
    Returns:
        Dictionary with parsed product information
    """
    # Extract basic information
    name = product.get('product_name', '') or product.get('product_name_en', '')
    brand = product.get('brands', '')
    
    # Extract ingredients
    ingredients = product.get('ingredients_text', '') or product.get('ingredients_text_en', '')
    
    # Extract nutrition information (per 100g)
    nutriments = product.get('nutriments', {})
    
    parsed_data = {
        'barcode': barcode,
        'name': name,
        'brand': brand,
        'ingredients': ingredients,
        'protein_100g': nutriments.get('proteins_100g'),
        'fat_100g': nutriments.get('fat_100g'),
        'fiber_100g': nutriments.get('fiber_100g'),
        'carbohydrates_100g': nutriments.get('carbohydrates_100g'),
        'energy_kcal_100g': nutriments.get('energy-kcal_100g'),
    }
    
    return parsed_data


def insert_product(product_data: Dict):
    """
    Insert or update product data in the SQLite database.
    
    Args:
        product_data: Parsed product information
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO products 
            (barcode, name, brand, ingredients, protein_100g, fat_100g, 
             fiber_100g, carbohydrates_100g, energy_kcal_100g)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product_data['barcode'],
            product_data['name'],
            product_data['brand'],
            product_data['ingredients'],
            product_data['protein_100g'],
            product_data['fat_100g'],
            product_data['fiber_100g'],
            product_data['carbohydrates_100g'],
            product_data['energy_kcal_100g'],
        ))
        
        conn.commit()
        print(f"Successfully inserted product: {product_data['name']} (Barcode: {product_data['barcode']})")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


def main():
    """Main function to fetch and store cat food product data."""
    print("Starting Cat Food Data Scraper...")
    print(f"API Base URL: {API_BASE_URL.replace('{barcode}', '<barcode>')}")
    print(f"Database: {DB_NAME}\n")
    
    # Initialize database
    create_database()
    
    # Process each barcode
    print(f"\nProcessing {len(EXAMPLE_BARCODES)} barcodes...\n")
    
    successful = 0
    failed = 0
    
    for i, barcode in enumerate(EXAMPLE_BARCODES, 1):
        print(f"[{i}/{len(EXAMPLE_BARCODES)}] Fetching barcode: {barcode}")
        
        # Fetch product data
        product = fetch_product_data(barcode)
        
        if product:
            # Parse and insert into database
            parsed_data = parse_product_data(product, barcode)
            insert_product(parsed_data)
            successful += 1
        else:
            failed += 1
        
        # Be nice to the API - add a small delay between requests
        if i < len(EXAMPLE_BARCODES):
            time.sleep(1)
        
        print()
    
    # Summary
    print("="*60)
    print(f"Scraping completed!")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total: {len(EXAMPLE_BARCODES)}")
    print(f"\nData stored in: {DB_NAME}")
    print("="*60)
    
    # Display sample data
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT barcode, name, brand FROM products LIMIT 5")
    rows = cursor.fetchall()
    
    if rows:
        print("\nSample data from database:")
        print("-" * 60)
        for row in rows:
            print(f"Barcode: {row[0]}")
            print(f"Name: {row[1]}")
            print(f"Brand: {row[2]}")
            print("-" * 60)
    
    conn.close()


if __name__ == "__main__":
    main()
