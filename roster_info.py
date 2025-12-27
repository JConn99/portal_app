import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def get_base_url(full_url):
    parsed = urlparse(full_url)
    return f"{parsed.scheme}://{parsed.netloc}"

# Example usage:
url = "https://athletics.uindy.edu/sports/football/roster/danny-royster/15047"
base_url = get_base_url(url)
print(base_url)  # Output: https://athletics.uindy.edu

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
    
    # Create a mapping of labels to values
    for dt, dd in zip(dt_tags, dd_tags):
        label = dt.get_text(strip=True).replace(':', '').lower()
        value = dd.get_text(strip=True)
        
        # Map to standardized field names
        if 'position' in label:
            player_data['position'] = value
        elif 'height' in label:
            player_data['height'] = value
        elif 'class' in label:
            player_data['class'] = value
        elif 'hometown' in label:
            player_data['hometown'] = value
        elif 'prev school' in label or 'previous school' in label:
            player_data['previous_school'] = value
        elif 'major' in label:
            player_data['major'] = value
    
    # Profile Image - look for the player photo
    img_tag = soup.find('div', class_='sidearm-roster-player-image').find('img')
    
    if img_tag:
        img_src = img_tag.get('src')
        # Make sure it's a full URL
        if img_src and not img_src.startswith('http'):
            img_src = f"{base_url}{img_src}"  # Use the base URL from roster_url
        player_data['profile_image'] = img_src
    
    return player_data


def extract_player_id(roster_url):
    """
    Extract player ID from roster URL
    """
    return roster_url.rstrip('/').split('/')[-1]

if __name__ == "__main__":
    test_url = "https://athletics.uindy.edu/sports/football/roster/danny-royster/15047"
    player_bio = scrape_player_bio_from_html(test_url)
    player_id = extract_player_id(test_url)
    
    print(f"Player ID: {player_id}")
    print("Player Bio:")
    for key, value in player_bio.items():
        print(f"{key}: {value}")