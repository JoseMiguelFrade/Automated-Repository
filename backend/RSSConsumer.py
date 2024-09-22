
import requests
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import os




def parse_rss_feed_EurLex():
    response = requests.get("https://eur-lex.europa.eu/EN/display-feed.rss?myRssId=zqe4oZZy5EQwdPmi23VWOOJ7Hnc5iHHgxzcX8LKo3LU%3D")
    if response.status_code == 200:
        rss_content = response.content
       # print("RSS feed fetched successfully.")
        print(rss_content)
    else:
        raise Exception(f"Failed to fetch RSS feed. Status code: {response.status_code}")

    # Parse the RSS feed using ElementTree
    root = ET.fromstring(rss_content)
    extracted_items = []
    now = datetime.now()

    for item in root.findall('.//item'):
        title_element = item.find('title')
        link_element = item.find('link')
        pub_date_element = item.find('pubDate')

        if title_element is None or link_element is None or pub_date_element is None:
            continue

        title = title_element.text.split(':')[-1].strip()
        link = link_element.text
        pub_date_str = pub_date_element.text
        publication_date = datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S %z')

        # Ensure both dates are timezone-aware for comparison
        one_month_ago = now.astimezone(publication_date.tzinfo) - timedelta(days=90)

        if publication_date >= one_month_ago:
            extracted_items.append({
                'title': title,
                'link': link,
                'publication_date': publication_date.strftime('%H:%M:%S %d/%m/%Y'),
                'source': 'EurLex'
            })

    return extracted_items


def update_query_dates(url, start_date, end_date):
    updated_url = url.replace('come%C3%A7o:2020-01-01', f'come%C3%A7o:{start_date}')
    updated_url = updated_url.replace('fim:2020-12-05', f'fim:{end_date}')
    return updated_url

def parse_rss_feed_DRE():
    base_urls = [
        "https://dre.tretas.org/dre/rss/?q=come%C3%A7o:2020-01-01%20fim:2020-12-05%20tipo:%22LEI%22%20%22ciber%20espa%C3%A7o%22%20%22ciber%20seguran%C3%A7a%22",
        "https://dre.tretas.org/dre/rss/?q=come%C3%A7o:2020-01-01%20fim:2020-12-05%20tipo:%22DECRETO%20LEI%22%20%22ciber%20espa%C3%A7o%22%20%22ciber%20seguran%C3%A7a%22"
    ]

    now = datetime.now()
    one_year_ago = now - timedelta(days=365)
    start_date = one_year_ago.strftime('%Y-%m-%d')
    end_date = now.strftime('%Y-%m-%d')

    extracted_items = []

    for base_url in base_urls:
        try:
            url = update_query_dates(base_url, start_date, end_date)
            print(url)
            response = requests.get(url)
            if response.status_code == 200:
                rss_content = response.content
                print("RSS feed fetched successfully.")
                print(rss_content)
                root = ET.fromstring(rss_content)

                for item in root.findall('.//item'):
                    title_element = item.find('title')
                    link_element = item.find('link')
                    pub_date_element = item.find('pubDate')
                    description_element = item.find('description')

                    if title_element is None or link_element is None or pub_date_element is None or description_element is None:
                        continue

                    title = title_element.text
                    link = link_element.text
                    pub_date_str = pub_date_element.text
                    description = description_element.text

                    publication_date = datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S %z')

                    # Ensure both dates are timezone-aware for comparison
                    one_year_ago = one_year_ago.replace(tzinfo=publication_date.tzinfo)
                    now = now.replace(tzinfo=publication_date.tzinfo)

                    # Ensure the publication date is within the last year
                    if one_year_ago <= publication_date <= now:
                        extracted_items.append({
                            'title': title,
                            'link': link,
                            'description': description,
                            'publication_date': publication_date.strftime('%H:%M:%S %d/%m/%Y'),
                            'source': 'DRE'  # Identifier to distinguish the source
                        })
            else:
                raise Exception(f"Failed to fetch RSS feed. Status code: {response.status_code}")
        except Exception as e:
            print(f"Failed to fetch RSS feed. Error: {e}")

    return extracted_items


def extract_eurlex_links(links):
    extracted_links = []
    for link in links:
        try:
            response = requests.get(link, allow_redirects=True)
            if response.status_code == 200:
                extracted_links.append(response.url)
            else:
                print(f"Failed to retrieve EurLex link: {link}")
        except Exception as e:
            print(f"Error processing EurLex link {link}: {e}")
    return extracted_links

def extract_dre_links(links):
    extracted_links = []
    for link in links:
        try:
            response = requests.get(link)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                dre_link = soup.find('a', string='Documento na página oficial do DRE')
                if dre_link and dre_link['href']:
                    extracted_links.append(dre_link['href'])
                else:
                    print(f"No DRE link found in page: {link}")
            else:
                print(f"Failed to retrieve DRE link: {link}")
        except Exception as e:
            print(f"Error processing DRE link {link}: {e}")
    return extracted_links

