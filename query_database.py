#!/usr/bin/env python3
"""
Example script showing how to query the pet food database.

This demonstrates how to retrieve and analyze data stored by the scraper.
"""

import sqlite3
from fetch_cat_food import DB_NAME


def show_all_products():
    """Display all products in the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]
    
    print(f"Total products in database: {count}\n")
    
    if count > 0:
        cursor.execute("""
            SELECT barcode, name, brand, protein_100g, fat_100g, fiber_100g 
            FROM products 
            ORDER BY name
        """)
        
        print("=" * 100)
        print(f"{'Barcode':<15} {'Name':<30} {'Brand':<20} {'Protein':<10} {'Fat':<10} {'Fiber':<10}")
        print("=" * 100)
        
        for row in cursor.fetchall():
            barcode, name, brand, protein, fat, fiber = row
            name = name[:27] + "..." if name and len(name) > 30 else (name or "N/A")
            brand = brand[:17] + "..." if brand and len(brand) > 20 else (brand or "N/A")
            protein_str = f"{protein:.1f}%" if protein is not None else "N/A"
            fat_str = f"{fat:.1f}%" if fat is not None else "N/A"
            fiber_str = f"{fiber:.1f}%" if fiber is not None else "N/A"
            
            print(f"{barcode:<15} {name:<30} {brand:<20} {protein_str:<10} {fat_str:<10} {fiber_str:<10}")
    
    conn.close()


def show_product_details(barcode):
    """Show detailed information for a specific product."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM products WHERE barcode = ?", (barcode,))
    row = cursor.fetchone()
    
    if row:
        print("\n" + "=" * 60)
        print("Product Details")
        print("=" * 60)
        print(f"Barcode: {row[1]}")
        print(f"Name: {row[2] or 'N/A'}")
        print(f"Brand: {row[3] or 'N/A'}")
        print(f"\nIngredients:\n{row[4] or 'N/A'}")
        print(f"\nNutritional Information (per 100g):")
        print(f"  Protein: {row[5]:.1f}%" if row[5] else "  Protein: N/A")
        print(f"  Fat: {row[6]:.1f}%" if row[6] else "  Fat: N/A")
        print(f"  Fiber: {row[7]:.1f}%" if row[7] else "  Fiber: N/A")
        print(f"  Carbohydrates: {row[8]:.1f}%" if row[8] else "  Carbohydrates: N/A")
        print(f"  Energy: {row[9]:.1f} kcal" if row[9] else "  Energy: N/A")
        print(f"\nAdded to database: {row[10]}")
        print("=" * 60)
    else:
        print(f"No product found with barcode: {barcode}")
    
    conn.close()


def search_by_brand(brand):
    """Search for products by brand name."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT barcode, name, brand 
        FROM products 
        WHERE brand LIKE ? 
        ORDER BY name
    """, (f"%{brand}%",))
    
    rows = cursor.fetchall()
    
    if rows:
        print(f"\nFound {len(rows)} product(s) matching brand '{brand}':")
        print("-" * 60)
        for row in rows:
            print(f"Barcode: {row[0]}")
            print(f"Name: {row[1] or 'N/A'}")
            print(f"Brand: {row[2] or 'N/A'}")
            print("-" * 60)
    else:
        print(f"No products found for brand: {brand}")
    
    conn.close()


def get_high_protein_products(min_protein=10.0):
    """Find products with protein content above a threshold."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT barcode, name, brand, protein_100g 
        FROM products 
        WHERE protein_100g >= ? 
        ORDER BY protein_100g DESC
    """, (min_protein,))
    
    rows = cursor.fetchall()
    
    if rows:
        print(f"\nHigh Protein Products (>= {min_protein}%):")
        print("-" * 80)
        for row in rows:
            print(f"{row[1] or 'N/A'} ({row[2] or 'N/A'})")
            print(f"  Protein: {row[3]:.1f}% | Barcode: {row[0]}")
            print("-" * 80)
    else:
        print(f"No products found with protein >= {min_protein}%")
    
    conn.close()


def main():
    """Main function demonstrating various queries."""
    print("Pet Food Database Query Examples\n")
    
    # Show all products
    show_all_products()
    
    # Example: Show details for a specific barcode (if data exists)
    # Uncomment and update with a valid barcode from your database:
    # show_product_details("3564700266403")
    
    # Example: Search by brand
    # Uncomment and update with a brand name:
    # search_by_brand("Whiskas")
    
    # Example: Find high protein products
    # Uncomment to find products with protein >= 10%:
    # get_high_protein_products(10.0)


if __name__ == "__main__":
    main()
