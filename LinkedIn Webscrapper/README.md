# LinkedIn Web Scraping

## About the Project
I’m running an exploratory data analysis (EDA) to find the best keywords to be used on a CV or LinkedIn profile for better results in a job hunt.

First, I leveraged [Viola Mao’s web scraping code](https://maoviola.medium.com/a-complete-guide-to-web-scraping-linkedin-job-postings-ad290fcaa97f) and modified it to serve my specific LinkedIn layout. Since the website is changing often, one needs to get the right element paths from the website’s HTML code. I will explain here the different parts of my working code for future references. The following snippets were ran using a Python notebook.

The code is divided in four sections:
1. Setup
2. Browse
3. Extract
4. Load

## CODE EXPLANATION

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
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import time
import random
import pandas as pd
```

Filters were applied from LinkedIn as follows:  

Job searched: Marketing Automation.  
Location: Île-de-France, France.  
Experience: Entry level.  

Once these filters are applied onto the URL, it looked like this:  

```
url = 'https://www.linkedin.com/jobs/search?keywords=Marketing%20Automation&
location=%C3%8Ele-de-France%2C%20France&locationId=&geoId=104246759&f_TPR=&f_E=2&position=1&pageNum=0'

```
Now, we setup chromedriver and assign it to an object called wd.

```Python
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--lang=en-US")
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
We also create some functions to ensure element visibility and ensuring the programs interaction with those elements.

```Python
def human_like_delay():
    time.sleep(random.uniform(2, 5))

# Function to scroll down the page and wait for jobs to load
def wait_for_jobs_to_load(wd, previous_job_count):
    # Scroll to the bottom of the list to trigger loading
    wd.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
    
    # Wait for the new jobs to load by checking the change in the number of listed jobs
    try:
        WebDriverWait(wd, 30).until(
            lambda driver: len(driver.find_elements(By.CSS_SELECTOR, ".jobs-search__results-list li")) > previous_job_count
        )
    except TimeoutException:
        print("Timed out waiting for jobs to load.")
    time.sleep(1)  # A short sleep to ensure that all jobs are fully loaded

# Ensure visibility of element and click
def ensure_visibility_and_click(wd, xpath):
    element = WebDriverWait(wd, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    wd.execute_script("arguments[0].scrollIntoView(true);", element)
    element.click()
    human_like_delay()

def wait_for_job_details(wd):
    loading_indicator = (By.CSS_SELECTOR, 'loading-indicator-css-selector')  # Replace with actual loading indicator if applicable
    try:
        # Wait until the loading indicator is gone before scraping
        WebDriverWait(wd, 10).until(EC.invisibility_of_element(loading_indicator))
    except TimeoutException:
        print("Loading indicator did not disappear - potential rate limiting.")
```



### 2. BROWSE

To let the code know when to stop, we must extract the number of job posts everytime we run the program. For that, we need to find the number from the HTML script. Next, the code to assign the number to a variable called no_of_jobs and the snippet to iterate through all of them, considering that there is a 25 job display limit per page. The code scrolls down the webpage to reveal more job postings and clicks on the ‘Next Page’ buttons at the bottom. Then, the code finds the list of all job postings and counts how many there are. We get the total number as an output.

```Python
no_of_jobs = int(wd.find_element(By.CSS_SELECTOR,"h1>span").get_attribute("innerText"))
current_jobs = 0

while current_jobs < no_of_jobs:
    wait_for_jobs_to_load(wd, current_jobs)
    current_jobs = len(wd.find_elements(By.CSS_SELECTOR, ".jobs-search__results-list li"))
    # Here you can also add a break condition if the current_jobs does not change after scrolling
    # This is a safety measure to prevent an infinite loop
    if current_jobs >= no_of_jobs:
        break

# BROWSE ALL THE JOB POSTINGS
i = 2
while i <= int(no_of_jobs/25)+1: 
    wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    i = i + 1
    try:
        wd.find_element(By.XPATH, "/html/body/main/div/section/button").click()
        time.sleep(5)
    except:
        pass
        time.sleep(5)

# FIND ALL THE JOBS
job_lists = wd.find_element(By.CLASS_NAME,"jobs-search__results-list")
jobs = job_lists.find_elements(By.TAG_NAME, "li") # return a list

len(jobs)
```

### 3. EXTRACT

This code will extract the following data:  

Job title  
Company  
Location  
When it was posted  
Post’s URL  

```Python
job_id= []
job_title = []
company_name = []
location = []
date = []
job_link = []

for job in jobs:

    entity_urn = job.find_element(By.CSS_SELECTOR, 'div').get_attribute('data-entity-urn')
    if entity_urn:
        job_id0 = entity_urn.split(':')[-1]
        job_id.append(job_id0)
    else:
        job_id.append('N/A')

    #main-content > section.two-pane-serp-page__results-list > ul > li:nth-child(3) > div
    
    job_title0 = job.find_element(By.CSS_SELECTOR,'h3').get_attribute('innerText')
    job_title.append(job_title0)

    company_name0 = job.find_element(By.CSS_SELECTOR,'h4').get_attribute('innerText')
    company_name.append(company_name0)
    
    location0 = job.find_element(By.CSS_SELECTOR, 'div> span').get_attribute('innerText')
    location.append(location0)
    
    date0 = job.find_element(By.CSS_SELECTOR,'div>div>time').get_attribute('datetime')
    date.append(date0)
    
    job_link0 = job.find_element(By.CSS_SELECTOR,'a').get_attribute('href')
    job_link.append(job_link0)
```

As for the second part of the extracting code, we will be getting:  

Job description  
Experience level  
Employment type  
Job function  
Industry  

```Python
jd = []
seniority = []
emp_type = []
job_func = []
industries = []

jd_path = 'body > div.base-serp-page > div > section > div.details-pane__content.details-pane__content--show > div > section.core-section-container.my-3.description > div > div.description__text.description__text--rich > section > div'
seniority_path = 'body > div.base-serp-page > div > section > div.details-pane__content.details-pane__content--show > div > section.core-section-container.my-3.description > div > ul > li:nth-child(1) > span'  
emp_type_path = 'body > div.base-serp-page > div > section > div.details-pane__content.details-pane__content--show > div > section.core-section-container.my-3.description > div > ul > li:nth-child(2) > span'
job_func_path = 'body > div.base-serp-page > div > section > div.details-pane__content.details-pane__content--show > div > section.core-section-container.my-3.description > div > ul > li:nth-child(3) > span'  
industries_path = 'body > div.base-serp-page > div > section > div.details-pane__content.details-pane__content--show > div > section.core-section-container.my-3.description > div > ul > li:nth-child(4) > span'  
show_more_button_path = 'body > div.base-serp-page > div > section > div.details-pane__content.details-pane__content--show > div > section.core-section-container.my-3.description > div > div > section > button.show-more-less-html__button.show-more-less-button.show-more-less-html__button--more.\!ml-0\.5'



for i in range(len(jobs)):
    try:
        # Click the job to open the details - Use i to click the correct job
        job = jobs[i]
        job.click()
        time.sleep(random.uniform(0.5, 2))  # Replace with human_like_delay if defined

        show_more_button = WebDriverWait(wd, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, show_more_button_path)))
        show_more_button.click()

        # Extract job details
        jd_element = wd.find_element(By.CSS_SELECTOR, jd_path)
        jd_text = jd_element.text  # Use .text to get the text content
        jd.append(jd_text)

        seniority_element = wd.find_element(By.CSS_SELECTOR, seniority_path)
        seniority_text = seniority_element.text
        seniority.append(seniority_text)

        emp_type_element = wd.find_element(By.CSS_SELECTOR, emp_type_path)
        emp_type_text = emp_type_element.text
        emp_type.append(emp_type_text)

        job_func_element = wd.find_element(By.CSS_SELECTOR, job_func_path)
        job_func_text = job_func_element.text
        job_func.append(job_func_text)

        industries_element = wd.find_element(By.CSS_SELECTOR, industries_path)
        industries_text = industries_element.text
        industries.append(industries_text)

    except Exception as e:
        # Append "NA" or any other placeholder if there's an error
        jd.append("NA")
        seniority.append("NA")
        emp_type.append("NA")
        job_func.append("NA")
        industries.append("NA")
        print(f"Error extracting details for job {i+1}: {e}")
```

### 4. LOAD

Finally, the next snippet will transfer the appended elements into an Excel file. Note that in the last line the name of the file is set to the specific job search done at the time.

```Python
job_data = pd.DataFrame({'ID': job_id,
'date': date,
'company': company_name,
'title': job_title,
'location': location,
'description': jd,
'level': seniority,
'type': emp_type,
'function': job_func,
'industry': industries,
'link': job_link
})
# cleaning description column
job_data['description'] = job_data['description'].str.replace('\n',' ')
job_data.to_excel('LinkedInJobData_MarketingAutomation.xlsx', index = False)
```

We are all set. After this an Excel file will appear on a designated by user folder.  

![Python_WebScrapperI_1](https://github.com/zefrios/Python/assets/83305620/782537a9-8efd-41ba-a690-4e1088e37792)


**NOTE: This code was made for recreative purposes only. Please make sure that you can scrape the content from a website before.***
