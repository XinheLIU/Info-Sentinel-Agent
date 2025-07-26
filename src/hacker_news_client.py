import requests
from bs4 import BeautifulSoup

class HackerNewsClient:
    def __init__(self):
        self.url = 'https://news.ycombinator.com/'

    def fetch_top_stories(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()  # Will raise an HTTPError for bad responses
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Hacker News page: {e}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        stories = soup.find_all('tr', class_='athing')

        top_stories = []
        for story in stories:
            title_tag = story.find('span', class_='titleline')
            if title_tag:
                a_tag = title_tag.find('a')
                if a_tag:
                    title = a_tag.text
                    link = a_tag.get('href')
                    top_stories.append({'title': title, 'link': link})
        
        return top_stories

if __name__ == "__main__":
    client = HackerNewsClient()
    stories = client.fetch_top_stories()
    if stories:
        for idx, story in enumerate(stories, start=1):
            print(f"{idx}. {story['title']}")
            print(f"   Link: {story['link']}")
    else:
        print("No stories found or error fetching stories.")
