# Import Dependencies
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt


def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': "C:\\Users\\A Girl's Lenovo\\.wdm\\drivers\\chromedriver\\win32\\89.0.4389.23\\chromedriver.exe"}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_p = mars_news(browser)
    hemisphere_image_urls = mars_hemispheres(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_p,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres": hemisphere_image_urls
    }

    # End the automated browsing session and return data
    browser.quit()
    return data

# Scrape Mars News
def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    # set up the HTML parser:
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Begin our scraping
        slide_elem = news_soup.select_one('div.list_text')
        slide_elem.find('div', class_= 'content_title')

        # Use the parent element to find the first `a` tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None
        
    return news_title, news_p

# Scrape Featured Image
def featured_image(browser):

    # Visit URL
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'
    
    return img_url

# Scrape Mars Facts
def mars_facts():
    # Add try/except for error handling
    try:
        # use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]

    except BaseException:
        return None

    # Assign columns and set index to dataframe
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)

    # Convert dataframe to HTML format
    return df.to_html(classes="table table-striped")

# Scrape Mars Hemispheres
def mars_hemispheres(browser):

    # Visit URL
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # Create empty list to hold the images and titles.
    hemisphere_image_urls = []

    # Retrieve the image urls and titles for each hemisphere.
    for i in range(4):

        # Find and click the relevant hemisphere page link.
        hemisphere_url = browser.find_by_tag("div.description a.itemLink.product-item")[i]
        hemisphere_url.click()
                
        # Parse the resulting html with soup.
        html = browser.html
        img_soup = soup(html, 'html.parser')
                
        # Look inside the <li /> tag for full image url.
        list_item = img_soup.find('li')
        img_url_rel = list_item.find('a')['href']
        # Look inside the <h2 /> tag for text with a class of 'title.'
        title_rel = img_soup.select_one('h2', class_='title').get_text()

        # Store title and img_url values.
        hemispheres = {"title": title_rel, "img_url": img_url_rel}

        # Append values to dictionary.
        hemisphere_image_urls.append(hemispheres)

        # go back to 'url.'
        browser.back()

    # Print the list that holds the dictionary of each image url and title.
    return hemisphere_image_urls

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())