import requests
from bs4 import BeautifulSoup
import csv
import time
from tqdm import tqdm

# Base URL of the website
base_url = "https://luxeurs.com"

# Send a GET request to the homepage
homePage = requests.get(base_url)

# List to store product data
products = []

# Check if the request was successful
if homePage.status_code == 200:
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(homePage.text, 'html.parser')
    
    # Find all product links on the homepage
    product_links = soup.find_all('div', class_='product-card__name')
    
    # Loop through each product link with tqdm progress bar
    for link in tqdm(product_links, desc="Scraping Products", unit="product"):
        # Construct the complete URL
        product_url = base_url + link.a['href']
        
        # Send a GET request to the product page
        product_page = requests.get(product_url)
        
        if product_page.status_code == 200:
            # Parse the product page content
            product_soup = BeautifulSoup(product_page.text, 'html.parser')
            
            # Extract the title
            title = product_soup.find('h1', class_='product-single__title').get_text(strip=True)
            
            # Extract the price
            sale_price_tag = product_soup.find('span', class_='js-product-price')
            if sale_price_tag:
                price = sale_price_tag.get_text(strip=True)
            else:
                price_tag = product_soup.find('span', class_='money')
                price = price_tag.get_text(strip=True) if price_tag else "Price not available"
            
            # Extract the description
            description_div = product_soup.find('div', id='js-more-info-tabs-1')
            description = description_div.get_text(strip=True) if description_div else "No description available"
            
            # Extract image URLs
            image_tags = product_soup.find_all('img', class_='mfp-image')
            images = [img['src'] for img in image_tags if 'src' in img.attrs]
            
            # Append the data to the list
            products.append({
                'Title': title,
                'Price': price,
                'Description': description,
                'Images': ', '.join(images)  # Join image URLs with a comma
            })
        else:
            print(f"Failed to retrieve product page: {product_url}")
        
        time.sleep(2)

    # Save the data to a CSV file
    with open('products.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Title', 'Price', 'Description', 'Images'])
        writer.writeheader()
        writer.writerows(products)
    
    print("Data saved to products.csv")
else:
    print("Failed to retrieve the homepage.")
