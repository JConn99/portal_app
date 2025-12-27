import os
from dotenv import load_dotenv
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from serpapi import GoogleSearch
import re
import pandas as pd
import streamlit as st

SERPAPI_KEY = st.secrets["SERPAPI_KEY"]
#import sqlite3

load_dotenv()

example_response = json.load(open("example_response.json"))
example_response = example_response.get("organic_results", [])

people_table = pd.DataFrame()

#SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def search_google(query):
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results.get("organic_results", [])

def filter_results_by_domain(organic_results):
    target_domains = {
        'roster': 'roster',
        'x': 'x.com',
        'hudl': 'hudl.com'
    }
    filtered_data = []
    for result in organic_results:
        link = result.get('link', '')
        category = None
        if target_domains['roster'] in link:
            category = 'roster'
        elif target_domains['x'] in link:
            category = 'x'
        elif target_domains['hudl'] in link:
            category = 'hudl'
        if category:
            filtered_data.append({
                'category': category,
                'title': result.get('title'),
                'link': result.get('link'),
                'position': result.get('position'),
                'source': result.get('source')
            })
    return filtered_data


def select_top_per_category(filtered_data):
    top_results = {}
    for item in filtered_data:
        category = item['category']
        position = item.get('position', float('inf'))
        if category not in top_results or position < top_results[category].get('position', float('inf')):
            top_results[category] = item
    return list(top_results.values())

def get_roster_url(top_results):
    roster_link = None
    for item in top_results:
        if item['category'] == 'roster':
            roster_link = item['link']
            break
    if not roster_link:
        print("No roster link found.")
        return None

    return roster_link
    
def get_base_url(full_url):
    parsed = urlparse(full_url)
    return f"{parsed.scheme}://{parsed.netloc}"

def scrape_player_bio_from_html(roster_url):
    """
    Scrape player biographical information from roster page HTML
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(roster_url, headers=headers)

    base_url = get_base_url(roster_url)
    
    if response.status_code != 200:
        print(f"Error {response.status_code}: Failed to fetch page")
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    player_data = {}
    
    # Bio fields - they're in a definition list (dl/dt/dd structure)
    # Find all dt (term) and dd (definition) pairs
    dt_tags = soup.find_all('dt')
    dd_tags = soup.find_all('dd')
    
    for dt, dd in zip(dt_tags, dd_tags):
        label = dt.get_text(strip=True).replace(':', '').lower()
        value = dd.get_text(strip=True)
        
        # Check for combined height/weight (D1 format)
        if 'ht./wt' in label or 'ht/wt' in label:
            # Parse "5-10 / 210" format
            ht_wt_match = re.match(r'(\d+-\d+)\s*/\s*(\d+)', value)
            if ht_wt_match:
                player_data['height'] = ht_wt_match.group(1)
                player_data['weight'] = ht_wt_match.group(2)
        
        # Separate height field (D2 format)
        elif 'height' in label and 'weight' not in label:
            player_data['height'] = value
        
        # Separate weight field (D2 format)
        elif 'weight' in label and 'height' not in label:
            player_data['weight'] = value
        
        # Position
        elif 'position' in label:
            player_data['position'] = value
        
        # Class/Year
        elif 'class' in label:
            player_data['class'] = value
        
        # Hometown
        elif 'hometown' in label:
            player_data['hometown'] = value
        
        # Previous School
        elif 'prev school' in label or 'previous school' in label:
            player_data['previous_school'] = value
        elif 'high school' in label:
            player_data['high_school'] = value
        
        # Major
        elif 'major' in label:
            player_data['major'] = value
    
    # Profile Image - look for the player photo
    img_tag = soup.find('div', class_='sidearm-roster-player-image')
    if img_tag:
        img_tag = img_tag.find('img')
    else:
        img_tag = soup.find('div', class_='rosterbio__player__image').find('img') if soup.find('div', class_='rosterbio__player__image') else None
    
    if img_tag:
        img_src = img_tag.get('src')
        # Make sure it's a full URL
        if img_src and not img_src.startswith('http'):
            img_src = f"{base_url}{img_src}"  # Use the base URL from roster_url
        player_data['profile_image'] = img_src
    
    return player_data

def get_player_info(name, school, people_table=people_table):

    #name = input("Enter the player's name: ")
    #school = input("Enter the school name: ")

    query = f"{name} {school}"

    # 1. Search Google
    organic_results = search_google(query)

    # 2. Filter relevant links
    filtered = filter_results_by_domain(organic_results) ### MAKE SURE TO CHANGE BACK
    #filtered = filter_results_by_domain(example_response)

    # 3. Get top links per category
    top_links = select_top_per_category(filtered)

    # 4. Extract links
    roster_link = next((item['link'] for item in top_links if item['category'] == 'roster'), "")
    x_link = next((item['link'] for item in top_links if item['category'] == 'x'), "")
    hudl_link = next((item['link'] for item in top_links if item['category'] == 'hudl'), "")

    # 5. Scrape roster info
    if not roster_link:
        print("No roster link found. Cannot scrape roster information.")
        return None  # or handle it as needed
    roster_info = scrape_player_bio_from_html(roster_link) or {}

    # 6. Build player dict
    player = {
        "name": name,
        "position": roster_info.get("position", ""),
        "height": roster_info.get("height", ""),
        "weight": roster_info.get("weight", ""),
        "class": roster_info.get("class", ""),
        "hometown": roster_info.get("hometown", ""),
        "previous_school": roster_info.get("previous_school", ""),
        "major": roster_info.get("major", ""),
        "profile_image": roster_info.get("profile_image", ""),
        "roster_link": roster_link,
        "x_link": x_link,
        "hudl_link": hudl_link
    }
    
    if not roster_info:
        print("No roster information found for the player.")
        return None

    # Save player information to the DataFrame
    people_table = pd.concat([people_table, pd.DataFrame([player])], ignore_index=True)

    return people_table


# filtered_results = filter_results_by_domain(example_response)
# filtered_results = select_top_per_category(filtered_results)

# roster_info = scrape_player_bio_from_html(get_roster_url(filtered_results))

#test = get_player_info("Tucker Griffin", "William Jewell College")
#print(test)



