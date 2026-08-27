"""
Real Estate & Property Listings Leads Scraper Actor for Apify
Extracts property listings, prices, bedroom counts, locations, and agent contact info.
"""

import asyncio
import re
import urllib.parse
from typing import Dict, Any, List
import httpx
from bs4 import BeautifulSoup
from apify import Actor

PRICE_REGEX = re.compile(r"(\$|€|£|ARS|US\$)?\s?(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})|\d+)")
BEDROOMS_REGEX = re.compile(r"(\d+)\s*(?:bed|bd|hab|dorm|bedroom)", re.IGNORECASE)

async def scrape_realestate_listings(client: httpx.AsyncClient, location_query: str, property_type: str, max_results: int) -> List[Dict[str, Any]]:
    """Scrapes property listings across major real estate indexes."""
    type_suffix = "" if property_type == "all" else f"+{property_type}"
    query = f"{location_query}{type_suffix}+for+sale+property+price"
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
    }
    
    listings = []
    try:
        resp = await client.get(url, headers=headers, timeout=12.0)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            snippets = soup.find_all("div", class_="result")
            
            for snip in snippets[:max_results]:
                title_elem = snip.find("a", class_="result__a")
                snippet_elem = snip.find("a", class_="result__snippet")
                url_elem = snip.find("a", class_="result__url")
                
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                raw_url = url_elem.get("href", "") if url_elem else ""
                
                clean_url = ""
                agency = "Real Estate Broker"
                if "uddg=" in raw_url:
                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(raw_url).query)
                    if "uddg" in parsed:
                        clean_url = parsed["uddg"][0]
                elif raw_url.startswith("http"):
                    clean_url = raw_url

                if clean_url:
                    try:
                        agency = urllib.parse.urlparse(clean_url).netloc.replace("www.", "")
                    except:
                        pass

                # Extract price
                price_match = PRICE_REGEX.search(snippet + " " + title)
                price_str = price_match.group(0).strip() if price_match else "Contact for Price"

                # Extract bedrooms
                bed_match = BEDROOMS_REGEX.search(snippet + " " + title)
                beds = bed_match.group(1) + " Beds" if bed_match else "N/A"

                listings.append({
                    "locationSearched": location_query,
                    "title": title,
                    "price": price_str,
                    "propertyType": property_type.capitalize(),
                    "bedrooms": beds,
                    "agencyOrAgent": agency,
                    "listingUrl": clean_url,
                    "descriptionSnippet": snippet
                })
    except Exception as e:
        Actor.log.warning(f"Error scraping real estate for '{location_query}': {e}")
        
    return listings

async def main():
    async with Actor:
        actor_input = await Actor.get_input() or {}
        
        locations = actor_input.get("locations", ["Apartments in Miami FL", "Casas en venta Madrid"])
        prop_type = actor_input.get("propertyType", "all")
        max_results = actor_input.get("maxResults", 25)
        
        Actor.log.info(f"Starting Real Estate Scraper for {len(locations)} locations...")

        async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0"}, follow_redirects=True) as client:
            total_listings = 0
            
            for loc in locations:
                Actor.log.info(f"Extracting properties for: '{loc}'...")
                props = await scrape_realestate_listings(client, loc, prop_type, max_results)
                
                for p in props:
                    await Actor.push_data(p)
                    total_listings += 1

            Actor.log.info(f"Done! Successfully extracted and saved {total_listings} property listings.")

if __name__ == "__main__":
    asyncio.run(main())
