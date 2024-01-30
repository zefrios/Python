# LinkedIn Web Scraping

## About the Project
I’m running an exploratory data analysis (EDA) to find the best keywords to be used on a CV or LinkedIn profile for better results in a job hunt.

First, I leveraged [Viola Mao’s web scraping code](https://maoviola.medium.com/a-complete-guide-to-web-scraping-linkedin-job-postings-ad290fcaa97f) and modified it to serve my specific LinkedIn layout. Since the website is changing often, one needs to get the right element paths from the website’s HTML code. I will explain here the different parts of my working code for future references. The following snippets were ran using a Python notebook.

The code is divided in four sections:
1. Setup
2. Browse
3. Extract
4. Load

### 1. SETUP
For the first part, we will use the Python selenium library to make web requests to Google Chrome. In this case, the driver used is Chromedriver. Note that we will also need to import modules like Webdriver so you can command a browser (like Chrome, Firefox, etc.) to perform various tasks such as opening a URL, clicking buttons, scraping web pages, etc. I used Visual Studio Code to run this section.

We will also use some selenium classes to allow the scraper to get the data correctly. Selenium is a tool primarily used for automating web applications for testing purposes. It allows you to interact with and control web browsers programmatically.

First we will use the By class, which is used to locate elements within a web page. It provides various methods to find elements, such as by ID, XPATH, CSS selector, etc.

WebDriverWait, which is a Selenium class used to wait for a certain condition to occur before proceeding further in the code. It helps in creating more reliable and stable scripts, especially when working with dynamic web pages.

expected_conditions (commonly aliased as EC). These are common conditions provided by Selenium used in conjunction with WebDriverWait to wait for certain conditions, like the presence of an element, the element to be clickable, etc.

This imports Python’s built-in time module, which provides various time-related functions. It's often used in web scraping to pause the execution of the script for a specified amount of time (e.g., time.sleep(5) pauses for 5 seconds), which can be useful to mimic human browsing behavior or to wait for a web page to load.

I used the pandas library for data analysis and handling tasks, such as reading and writing to various file formats (CSV, Excel, etc.), cleaning, transforming, and analyzing data.

This code’s objective is to scrape jobs for a determined position from LinkedIn. Please note that the following code runs on the site without being logged into my account. If you would like to scrape while logged in to your account, you would have to add a snippet of code that logs in the user everytime the program runs.

```Python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
```

Filters were applied from LinkedIn as follows:

Job searched: Marketing Automation.
Location: Île-de-France, France.
Experience: Entry level.
Once these filters are applied onto the URL, it looked like this:

```Python
url = 'https://www.linkedin.com/jobs/search/?currentJobId=3744994460&distance=
25&f_E=2&f_TPR=r2592000&geoId=104246759&keywords=Marketing%20Automation&origin=
JOB_SEARCH_PAGE_JOB_FILTER&refresh=true'
```
Now, we setup chromedriver and assign it to an object called wd.

```Python
wd = webdriver.Chrome()
wd.maximize_window()
wd.get(url)
time.sleep(2)
```
Once the browser opens, there might be some elements like log in and cookie banners that need to be removed before proceeding. We can achieve that adding:
```Python
try:
    wd.find_element(By.XPATH, '//*[@id="artdeco-global-alert-container"]/div/section/div/div[2]/button[2]').click()
    time.sleep(2)
    wd.find_element(By.XPATH, '/html/body/div[3]/button').click()
except:
    print(f"No banners found. Proceeding.")
    pass
```
