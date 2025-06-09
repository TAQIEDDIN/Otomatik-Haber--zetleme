from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
from newspaper import Article
import nltk

nltk.download('punkt')

site = 'https://news.google.com/rss/search?q=politics'
op = urlopen(site)  # Open the site
rd = op.read()  # Read data from site
op.close()  # Close the object
sp_page = soup(rd, 'xml')  # Scrape data
news_list = sp_page.find_all('item')  # Find news items

print(news_list)

for news in news_list:
    print('Title: ', news.title.text)
    print('News Link: ', news.link.text)

    # ✅ Step 1: Try to get image from RSS <media:content>
    image_url = None
    media_content = news.find('media:content')
    if media_content and media_content.has_attr('url'):
        image_url = media_content['url']
    
    # ✅ Step 2: If no image in RSS, try extracting from <meta property="og:image">
    if not image_url:
        try:
            news_data = Article(news.link.text)
            news_data.download()
            news_data.parse()

            news_soup = soup(urlopen(news.link.text), 'html.parser')
            image_tag = news_soup.find("meta", property="og:image")
            if image_tag and image_tag["content"]:
                image_url = image_tag["content"]
            else:
                image_url = news_data.top_image  # Fallback
        except:
            image_url = None

    # ✅ Step 3: Display the final image link
    if image_url:
        print("News Poster Link: ", image_url)
    else:
        print("News Poster Link: No Image Found")

    print("News Summary: ", news_data.summary if 'news_data' in locals() else "Summary not available")
    print("Pub Date: ", news.pubDate.text)
    print('-' * 60)
