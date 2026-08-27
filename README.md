# Real Estate & Property Listings Leads Scraper

Extract real estate properties, house and apartment sales prices, square footage, locations, and real estate agent contact details from public property indexes.

## 🚀 Features

- **Multi-Location Search:** Query multiple cities, neighborhoods, and states in a single run.
- **Property Filtering:** Filter by property type (Apartment, House, Commercial, Land).
- **Price & Spec Extraction:** Captures price, number of bedrooms, and agency domain.
- **Export Options:** Download results in **Excel (XLSX)**, **CSV**, or **JSON**.

## 📥 Input Example

```json
{
  "locations": [
    "Condos for sale Miami Brickell",
    "Casas en venta Madrid Salamanca",
    "Apartments for sale New York Manhattan"
  ],
  "propertyType": "apartment",
  "maxResults": 50
}
```

## 📤 Output Format

Each record in the dataset includes:
- `locationSearched`: Searched location
- `title`: Property listing title
- `price`: Sale / rent price
- `propertyType`: Property category
- `bedrooms`: Number of bedrooms
- `agencyOrAgent`: Real estate agency / portal domain
- `listingUrl`: Direct property URL
- `descriptionSnippet`: Listing description and amenities
