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
        # Set up the email
        msg = MIMEMultipart()
        msg['From'] = YOUR_EMAIL
        msg['To'] = ""
        msg['Subject'] = HEADER

        # Personalize the body
        body = BODY_TEMPLATE.format(alumni_name=alumni_name, company=company)
        msg.attach(MIMEText(body, 'plain'))

        # Connect to Gmail and send the email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(YOUR_EMAIL, YOUR_PASSWORD)
        server.send_message(msg)
        server.quit()

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
