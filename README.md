# GrocX API

A robust FastAPI application that compares product prices across multiple e-commerce platforms, allowing users to find the best deals and optimize their shopping basket for the lowest total price.

## Features

* **Multi-platform Price Comparison** : Scrape and compare prices from four major e-commerce platforms
* **Basket Optimization** : Find the optimal distribution of products across platforms for the lowest total cost
* **Product Name Mapping** : Automatically map generic product names to platform-specific listings
* **Concurrent Scraping** : Efficiently fetch data from multiple sources simultaneously
* **Caching** : Reduce latency and external requests with intelligent caching
* **RESTful API** : Clean, well-documented endpoints with request validation

## Tech Stack

* **FastAPI** : High-performance web framework for building APIs
* **Pydantic** : Data validation and settings management
* **Asyncio** : Asynchronous I/O for concurrent operations
* **Docker** : Containerization for consistent deployment
* **pytest** : Comprehensive test suite

## Installation

### Prerequisites

* Python 3.9+
* pip

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/lifeayush/grocX_backend.git
   cd grocX_backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file based on the example:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Running with Docker

```bash
docker build -t grocX_backend .
docker run -p 8000:8000 grocX_backend
```

### Running locally

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## Usage

### API Endpoints

#### Get Prices

```
POST /api/v1/prices
```

Request body:

```json
{
  "products": [
    {"name": "Milk", "quantity": 1},
    {"name": "Bread", "quantity": 2},
    {"name": "Eggs", "quantity": 1}
  ],
  "optimize": true
}
```

Response:

```json
{
  "basket": {
    "total_price": 12.47,
    "platforms": [
      {
        "name": "Platform A",
        "products": [
          {"name": "Milk", "price": 2.99, "quantity": 1}
        ],
        "subtotal": 2.99
      },
      {
        "name": "Platform C",
        "products": [
          {"name": "Bread", "price": 2.49, "quantity": 2},
          {"name": "Eggs", "price": 4.50, "quantity": 1}
        ],
        "subtotal": 9.48
      }
    ]
  },
  "price_comparison": [
    {
      "product": "Milk",
      "prices": [
        {"platform": "Platform A", "price": 2.99},
        {"platform": "Platform B", "price": 3.49},
        {"platform": "Platform C", "price": 3.29},
        {"platform": "Platform D", "price": 3.15}
      ]
    },
    // Additional products...
  ]
}
```

## Project Structure

The project structure and the LLD is highlighted in the docs directory of the repository

## Adding a New Platform

To add support for a new e-commerce/quick-commerce platform:

1. Create a new scraper class in `app/scrapers/` that inherits from `BaseScraper`
2. Implement the required methods: `get_price()` and `get_discount()`
3. Add platform-specific product mappings to `data/product_mappings.json`
4. Register the new scraper in `app/services/scraper_manager.py`

## Testing

Run the test suite with:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=app
```

    

<p align="center">🚀 Created with ❤️ by Ayush Patil 🚀</p>
