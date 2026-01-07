# pet-food-scrape

A Python script to fetch cat food product data from the OpenPetFoodFacts API and store it in a SQLite database.

## Features

- Fetches product data from OpenPetFoodFacts API (https://world.openpetfoodfacts.org)
- Parses JSON responses for product information
- Stores the following data in SQLite database:
  - Product name
  - Brand
  - Ingredients
  - Nutritional information (protein%, fat%, fiber%, carbohydrates%, energy)
- Handles API errors gracefully
- Includes example cat food barcodes

## Requirements

- Python 3.6 or higher
- No external dependencies (uses standard library only)

## Usage

1. Run the script:
```bash
python fetch_cat_food.py
```

2. The script will:
   - Create a SQLite database file named `pet_food.db`
   - Fetch data for each barcode in the example list
   - Store the parsed data in the database
   - Display a summary of results

## Database Schema

The `products` table contains:
- `id`: Auto-incrementing primary key
- `barcode`: Unique product barcode
- `name`: Product name
- `brand`: Brand name
- `ingredients`: Ingredients list
- `protein_100g`: Protein content per 100g
- `fat_100g`: Fat content per 100g
- `fiber_100g`: Fiber content per 100g
- `carbohydrates_100g`: Carbohydrate content per 100g
- `energy_kcal_100g`: Energy in kcal per 100g
- `created_at`: Timestamp of record creation

## Customization

To fetch data for different products, edit the `EXAMPLE_BARCODES` list in `fetch_cat_food.py`:

```python
EXAMPLE_BARCODES = [
    "your_barcode_1",
    "your_barcode_2",
    # Add more barcodes here
]
```

## License

See LICENSE file for details.