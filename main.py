import os
from os.path import join, dirname
from dotenv import load_dotenv

import serpapi
from dotenv import load_dotenv
import httpx
from bs4 import BeautifulSoup
import re
import csv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

SERP_API_KEY = os.environ.get("SERP_API_KEY")

class serpScrape:
    def __init__(self):
        pass

    def search(self, search="ducks", engine="duckduckgo",\
               loc="Australia"):
        '''Available search engines: `bing`, `google`, `duckduckgo`, `yahoo`.\n
        Search query defaults to `ducks` if nothing is input\n
        Search engine defaults to `duckduckgo` if nothing is input'''
        
        # Ensures that there is a valid input for engine
        if engine not in ['bing','google','duckduckgo','yahoo']:
            return "Input Error: search engine unavailable"

        # params = {
        #     "q": search,
        #     "location": loc,
        #     "google_domain": "google.co.nz",
        #     "hl": "hi",
        #     "gl": "in",
        #     "api_key": "-"
        # }

        # params['q'] = search
        # params['engine'] = engine
        
        # if loc:
        #     params['location'] = loc

        client = serpapi.Client(api_key=SERP_API_KEY)
        results = client.search({
        'engine': engine,
        'q': search,
        'location': loc,
        'google_domain': 'google.com.au',
        'gl': 'au',
        'num': 1000
        })

        return results
    
    def scrape_emails(self, link: str):
        print(f"Scraping: {link}")
        emails = []
        page_response = httpx.get(url=link)
        soup = BeautifulSoup(page_response.text, "html.parser")

        for link in soup.findAll("a", attrs={"href": re.compile("^mailto:")}):
            email = link.get("href").replace("mailto:", "")
            emails.append(email)

        return emails
    
scrape = serpScrape()
results = scrape.search(search="cleaning distributor supplier",engine='google')

results_de_duplicate = []
for ele in results["organic_results"]:
    if ele['link'].split('/')[2] not in results_de_duplicate:
        try:
            results_de_duplicate.append({'title': ele['title'],
                                        'link': f"https://{ele['link'].split('/')[2]}",
                                        'email': scrape.scrape_emails(f"https://{ele['link'].split('/')[2]}")
                                        })
        except Exception as e:
            print(e)
            results_de_duplicate.append({'title': ele['title'],
                                        'link': f"https://{ele['link'].split('/')[2]}",
                                        'email': "None"})
                                        

with open('output.csv', 'w', newline='') as csvfile:
    fieldnames = ['title', 'link', 'email']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results_de_duplicate)