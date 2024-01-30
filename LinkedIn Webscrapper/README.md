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

```
url = "https://www.linkedin.com/jobs/search/?currentJobId=3744994460&distance=
25&f_E=2&f_TPR=r2592000&geoId=104246759&keywords=Marketing%20Automation&origin=
JOB_SEARCH_PAGE_JOB_FILTER&refresh=true"
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

### 2. BROWSE

To let the code know when to stop, we must extract the number of job posts everytime we run the program. For that, we need to find the number from the HTML script. Next, the code to assign the number to a variable called no_of_jobs and the snippet to iterate through all of them, considering that there is a 25 job display limit per page. The code scrolls down the webpage to reveal more job postings and clicks on the ‘Next Page’ buttons at the bottom. Then, the code finds the list of all job postings and counts how many there are. We get the total number as an output.

```Python
no_of_jobs = int(wd.find_element(By.CSS_SELECTOR,"h1>span").get_attribute("innerText"))

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
    job_id0 = job.get_attribute('data-job-id')
    job_id.append(job_id0)
    
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

As for the second part of the extracting code, we will be extracting:  

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
max_words = 15

for item in range(len(jobs)):
    print(f"Processing item {item + 1}: {job_title[item]} at {company_name[item]}")
    # clicking job to view job details
    job_click_path = f"//*[@id='main-content']/section[2]/ul/li[{item}]/div/a"
    
    try:
                element = WebDriverWait(wd, 10).until(EC.element_to_be_clickable((By.XPATH, job_click_path)))
                wd.execute_script("arguments[0].scrollIntoView(true);", element)
                element.click()

                # Additional wait, if needed, to ensure the page has loaded
                WebDriverWait(wd, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR,'h3')))
                
                
    except ElementClickInterceptedException:
                print(f"Click intercepted for item {item+1}. Trying alternative.")
                # Alternative click using ActionChains
                ActionChains(wd).move_to_element(element).click().perform()

    except TimeoutException:
        print(f"Timeout waiting for clickable element for item {item+1}.")
                
    except Exception as e:
                print(f"Error clicking item {item+1}: {e}")


    # XPath for 'Show More' button
    show_more_button_path = '/html/body/div[1]/div/section/div[2]/div/section[1]/div/div/section/button[1]'

    # Check if 'Show More' button is present and click it
    try:
        # Wait for the 'Show More' button to be clickable
        show_more_button = WebDriverWait(wd, 5).until(EC.element_to_be_clickable((By.XPATH, show_more_button_path)))
        show_more_button.click()

        # EXTRACTING DATA FROM THE JOB POST
        jd_path = '/html/body/div[1]/div/section/div[2]/div/section[1]/div/div/section/div'
        jd0 = job.find_element(By.XPATH, jd_path).get_attribute('innerText')
        jd.append(jd0)
        words = jd0.split()
        first_15_words = " ".join(words[:max_words])
        print(f"Appended job description for {[item+1]}: {first_15_words}")


    except TimeoutException:
        # Handle the case where the button is not clickable within the timeout
        jd.append("NA")
        print(f"Timeout waiting for 'Show More' button for {[item+1]}: {job_title[item]} at {company_name[item]}")
    except NoSuchElementException:
        # Handle the case where 'Show More' button does not exist
        jd.append("NA")
        print(f"No 'Show More' button found for this job listing {[item+1]}: {job_title[item]} at {company_name[item]}")


    # EXTRACTING SENIORITTY
    try:
       seniority_path = '/html/body/div[1]/div/section/div[2]/div/section[1]/div/ul/li[1]/span'
       seniority0 = job.find_element(By.XPATH, seniority_path).get_attribute('innerText')
       seniority.append(seniority0)
       print(f"Appended seniority for {[item+1]}: {seniority0}")
    
    except NoSuchElementException:
        seniority.append("NA")
        print(f"Couldn't append seniority for {[item+1]}: {job_title[item]} at {company_name[item]}")
       
    
    # EXTRACTING EMPLOYMENT TYPE
    try:
       emp_type_path = '/html/body/div[1]/div/section/div[2]/div/section[1]/div/ul/li[2]/span'
       emp_type0 = job.find_element(By.XPATH, emp_type_path).get_attribute('innerText')
       emp_type.append(emp_type0)
       print(f"Appended employment type for {[item+1]}: {emp_type0}")
    
    except NoSuchElementException:
        emp_type.append("NA")
        print(f"Couldn't append employment type for {[item+1]}: {job_title[item]} at {company_name[item]}")
    
    # EXTRACT DEPARTMENT
    try:
       job_func_path = '/html/body/div[1]/div/section/div[2]/div/section[1]/div/ul/li[3]/span'
       job_func_element = job.find_element(By.XPATH, job_func_path).get_attribute('innerText')
       job_func.append(job_func_element)
       print(f"Appended department for {[item+1]}: {job_func_element}")
    
    except NoSuchElementException:
        job_func.append("NA")
        print(f"Couldn't append department for {[item+1]}: {job_title[item]} at {company_name[item]}")
    
    
    #  EXTRACT INDUSTRY
    try:
        industries_path = '/html/body/div[1]/div/section/div[2]/div/section[1]/div/ul/li[4]/span'
        industry_element = WebDriverWait(wd, 10).until(EC.visibility_of_element_located((By.XPATH, industries_path)))
        industry_text = industry_element.get_attribute('innerText')
        industries.append(industry_text)
        print(f"Appended industry for {[item+1]}: {industry_text}")

    except TimeoutException:
        print(f"Timeout while trying to extract industry for {[item+1]}.")
        industries.append("NA")

    except Exception as e:
        industries.append("NA")
        print(f"Exception occurred for item {item + 1}: {e}")

    except NoSuchElementException:
            job_func.append("NA")
            print(f"Couldn't append department for {[item+1]}: {job_title[item]} at {company_name[item]}")
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
