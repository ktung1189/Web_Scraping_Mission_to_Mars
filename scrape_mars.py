# Import Dependencies
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep


# Scrape function calls all other functions to go and grab info to be returned as a dict
def scrape():

    executable_path = {'executable_path': '/Users/ktung/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=False)
    
    # Call mars_news function to get title and paragraph
    title, paragraph = mars_news(browser)
    
    # Run the functions below and store into a dictionary
    results = {
        "title": title,
        "paragraph": paragraph,
        "image_URL": mars_image(browser),
        "weather": mars_weather_tweet(browser),
        "facts": mars_facts(),
        "hemispheres": mars_hemis(browser),
    }

    # Quit the browser and return the scraped results
    browser.quit()
    return results

# Function to get most recent news title and associated paragraph
def mars_news(browser):
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    html = browser.html
    mars_news_soup = BeautifulSoup(html, 'html.parser')

    
    title = mars_news_soup.find('div', class_='content_title').text
    paragraph = mars_news_soup.find('div', class_='article_teaser_body').text
    return title, paragraph


# Function to get image from the jpl website
def mars_image(browser):
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Go to 'FULL IMAGE', then to 'more info'
    # Seems without sleep it is returning a error
    browser.click_link_by_partial_text('FULL IMAGE')
    sleep(1)
    browser.click_link_by_partial_text('more info')

    html = browser.html
    image_soup = BeautifulSoup(html, 'html.parser')

    # Scrape the URL and return
    feat_img_url = image_soup.find('figure', class_='lede').a['href']
    feat_img_full_url = f'https://www.jpl.nasa.gov{feat_img_url}'
    return feat_img_full_url

#Function to get weather data from Tweeter 
def mars_weather_tweet(browser):
    url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url)
    html = browser.html
    tweet_soup = BeautifulSoup(html, 'html.parser')
    
    # Scrape the tweet info and return
    tweet = tweet_soup.find('p', class_='TweetTextSize').text
    return tweet
    
# Function to get mars data and coverting to a html table
def mars_facts():
    url = 'https://space-facts.com/mars/'
    tables = pd.read_html(url)
    df = tables[1]
    df.columns = ['Property', 'Value']
    # Set index to property in preparation for import into MongoDB
    df.set_index('Property', inplace=True)
    
    # Convert to HTML table string and return
    return df.to_html()
    

# Function to get the images of the different hemispheres of mars
def mars_hemis(browser):
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    
    html = browser.html
    hemi_soup = BeautifulSoup(html, 'html.parser')

    hemi_strings = []
    # Finding all the links that are available for the different hemispheres
    links = hemi_soup.find_all('h3')
    
    # Loop through links to find all text
    for hemi in links:
        hemi_strings.append(hemi.text)

    # Create a list for image urls
    hemisphere_image_urls = []

    # Loop through the hemisphere links to obtain the images
    for hemi in hemi_strings:
        # Initialize a dictionary for the hemisphere
        hemi_dict = {}
        
        # Click on the link with the corresponding text
        browser.click_link_by_partial_text(hemi)
        
        # Scrape the image url string and store into the dictionary
        hemi_dict["img_url"] = browser.find_by_text('Sample')['href']
        
        # The hemisphere title is already in hemi_strings, so store it into the dictionary
        hemi_dict["title"] = hemi
        
        # Add the dictionary to hemisphere_image_urls
        hemisphere_image_urls.append(hemi_dict)
    
        # Click the 'Back' button
        browser.back()
    
    return hemisphere_image_urls