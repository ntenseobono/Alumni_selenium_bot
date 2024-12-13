import json
import os
import re
import time
import pdb
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sent_last_year = set([
    "eve.fillenbaum@gmail.com",
    "grcote@gmail.com",
    "gerard.cote@oracle.com",
    "holdengreenberg@gmail.com",
    "gretchenkhall@gmail.com",
    "janeakelly95@gmail.com",
    "grant@swanjord.com",
    "keelerkb@gmail.com",
    "randy_smith@rdscg.com",
    "sophierouhandeh@gmail.com",
    "boycem00@gmail.com",
    "bhschuster@gmail.com",
    "lydia.auner@gmail.com",
    "natbeagley@gmail.com",
    "joanna_valliere@rocketmail.com",
    "concretecowboy@gmail.com",
    "ek.lagerquist@gmail.com",
    "sicelomasango@gmail.com",
    "rvsantacruz@gmail.com",
    "diane24601@gmail.com",
    "appachar.ar@gmail.com",
    "michael.e.a.habermann@gmail.com",
    "grace.a.e.moret@gmail.com",
    "hilarygt@gmail.com",
    "boycem00@gmail.com",
    "lmdownie1125@gmail.com",
    "downielm@gmail.com",
    "turnerdj32@gmail.com",
    "holdengreenberg@gmail.com",
    "eric.shin75@gmail.com",
    "eric.k.shin@pwc.com",
    "apspringborn@hotmail.com",
    "lara.livgard@mac.com",
    "fjennier@gmail.com",
    "terence.winsky@gmail.com",
    "gautam.khera@gmail.com",
    "harrisrachelanna@gmail.com",
    "linkedln",
    "annette.kurtz@hp.com",
    "nwyale@icloud.com",
    "goodgec@gmail.com",
    "colehanson42@gmail.com",
    "akral97@gmail.com",
    "kale.zicafoose@gmail.com",
    "egcarlson57@gmail.com",
    "brandyscholwinski@gmail.com",
    "sinhaamartya@gmail.com",
    "emily.noneman@gmail.com",
    "diane24601@gmail.com",
    "nivenmarie@gmail.com",
    "jmknopf@yahoo.com",
    "ricardo.v.santa.cruz@intel.com",
    "lrbell404@hotmail.com",
    "sam.ne.carruthers@gmail.com",
    "jvanvaler@yahoo.com",
    "jimmy.v.ly@gmail.com",
    "tedhickey545@gmail.com",
    "tatebosler@gmail.com",
    "campbellinfulleffect@gmail.com",
    "jka42@hotmail.com",
    "tim.munson@gmail.com",
    "kesterelli@gmail.com",
    "williams.megan88@gmail.com",
    "gordodki@gmail.com",
    "siobhan@mcmahon-holland.com",
    "davidchesebro@gmail.com",
    "choirofdream@gmail.com",
    "sansone1979@gmail.com",
    "havenil@aol.com",
    "davidechurch@gmail.com",
    "tyler.m.young@gmail.com",
    "scpeng@gmail.com",
    "escolad@gmail.com",
    "akuhn649@gmail.com",
    "michael.yurinich@gmail.com",
    "lucy.b.albin@gmail.com",
    "imaniritchards@gmail.com",
    "rachelosofsky@gmail.com"
])

YOUR_EMAIL = "obonon@carleton.edu"
YOUR_PASSWORD = "opte zucg bdky revh"

HEADER = "Ntense Obono 2025' Carleton College Alumni Introduction and Networking."
BODY_TEMPLATE = """
Hi {alumni_name},

My name is Ntense Obono, and I am currently a senior Computer Science major with a concentration in economics and mathematics at Carleton College.

I recently came across your LinkedIn profile and received your information from the alumni directory and noticed that your career path is quite similar to what I would like to pursue. As an individual who would like to break into the world of technology and finance, I would love just 20 minutes of your time to learn about your experience and what you do at {company} on a daily basis and what it's like to work in the field.

I am also interested in the entry-level Software Engineering position offered at {company}. I believe that my background can make me a great fit for the firm.

I have attached my resume just so you have a frame of reference for my education and experiences.

I look forward to hearing from you!

Sincerely,
Ntense
"""

def setup_driver():
    """Set up and return the Selenium WebDriver."""
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("start-maximized")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-renderer-backgrounding")
    return webdriver.Chrome(options=options)




def send_email(to_email, alumni_name, company):
    try:
        # # Set up the email
        # msg = MIMEMultipart()
        # msg['From'] = YOUR_EMAIL
        # msg['To'] = "wearsnext@gmail.com"
        # msg['Subject'] = HEADER

        # # Personalize the body
        # body = BODY_TEMPLATE.format(alumni_name=alumni_name, company=company)
        # msg.attach(MIMEText(body, 'plain'))

        # # Connect to Gmail and send the email
        # server = smtplib.SMTP('smtp.gmail.com', 587)
        # server.starttls()
        # server.login(YOUR_EMAIL, YOUR_PASSWORD)
        # server.send_message(msg)
        # server.quit()

        print(f"Email sent to {alumni_name} ({to_email})")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")

# Load cookies from the file
def load_cookies(driver, cookies_file):
    with open(cookies_file, 'r') as f:
        cookies = json.load(f)
        for cookie in cookies:
            # Add cookies only for the correct domain
            if "carleton.edu" in cookie['domain']:
                cookie['domain'] = ".carleton.edu"  # Adjust to match subdomains if needed
                try:
                    driver.add_cookie({
                        "name": cookie['name'],
                        "value": cookie['value'],
                        "domain": cookie['domain'],
                        "path": cookie['path'],
                        "secure": cookie['secure'],
                        "httpOnly": cookie['httpOnly']
                    })
                except Exception as e:
                    print(f"Error adding cookie {cookie['name']}: {e}")

# Initialize WebDriver
driver = setup_driver()
driver.get("https://www.carleton.edu/alumni/directory/")  # Replace with the website URL
base_url = "https://www.carleton.edu/alumni/directory/?fullName="
with open('alumni.json', 'r') as f:
    data = json.load(f)

load_cookies(driver, 'chatcookies.json')

# Refresh to apply cookies
driver.refresh()

base_url = "https://www.carleton.edu/alumni/directory/?fullName="

# Iterate through each company and their alumni
for company in data['jobs']:
    company_name = company['company_name']

    for alumni in company['alumni']:
        full_name = alumni['name'].replace(" ", "%20")
        search_url = f"{base_url}{full_name}"
        
        # Navigate to the search page
        driver.get(search_url)
        time.sleep(1)  # Wait for the page to load

        # Extract alumni details from the search results
        alumni_list = driver.find_elements(By.CSS_SELECTOR, "li.alumni-directory__person")
        for alum in alumni_list:
            try:
                name = alum.find_element(By.CSS_SELECTOR, ".alumni-directory__person-name").text
                major = alum.find_element(By.CLASS_NAME, "alumni-directory__person-span").text
                try:
                    employment = alum.find_element(By.CSS_SELECTOR, ".alumni-directory__employment").text
                except Exception as e:
                    employment = None  # Default value if the element is not found

                try:
                    email_element = alum.find_element(By.CSS_SELECTOR, ".alumni-directory__email a")
                    email = email_element.get_attribute("href").replace("mailto:", "")
                except Exception as e:
                    email = "Not found" 
                                
                # Check if the employment matches the company
                if email != "Not found" and (len(alumni_list) == 1 or company_name.lower() in employment.lower() or (alumni['name'].lower() in name and "Computer Science" in major))  :
                    if email.lower() in sent_last_year:
                        alumni['email_status'] = "Follow up"
                        print(f"Follow up on {name} at {email}")
                    else:
                        send_email(email, name.split()[0], company_name)
                        alumni['email_status'] = "Sent"
                    break  # Stop searching once a match is found
                else:
                    alumni['email_status'] = "Error"
                alumni['email'] = email 
            except Exception as e:
                alumni['email'] = "Error" 
                alumni['email_status'] = "Error"
                print(f"Error Processing {alumni['name']}")

# Save the updated data back to JSON
with open('alumni_updated.json', 'w') as f:
    json.dump(data, f, indent=4)

pdb.set_trace()
driver.quit()






# Continue with the automation
