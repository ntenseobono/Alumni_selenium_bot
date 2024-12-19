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
from templates import body_template

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

SENT_EMAILS_FILE = 'sent_emails.json'
ALUMNI_INFO = 'manual_alumni.json'
if os.path.exists(SENT_EMAILS_FILE):
    with open(SENT_EMAILS_FILE, 'r') as f:
        sent_last_year = set(json.load(f))
else:
    sent_last_year = set()


PDF_FILE_PATH = 'Ntense_Obono_resume.pdf'

YOUR_EMAIL = "obonon@carleton.edu"
YOUR_PASSWORD = "opte zucg bdky revh"

HEADER = "Ntense Obono 2025' Carleton College Alumni Introduction and Networking"

KEYWORDS = ["computer science", "information science", "tech","economics", "mathematics", "statistics", "physics", "biology", "engineering", "developer", "development", "recruiter", "manager", "swe", "sde", "software"]

def contains_major_keywords(major_text):
    """Check if the major contains any of the defined keywords."""
    major_text = major_text.lower()  # Normalize the text to lowercase
    return any(re.search(rf"\b{keyword}\b", major_text) for keyword in KEYWORDS)

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


def save_sent_emails():
    with open(SENT_EMAILS_FILE, 'w') as f:
        json.dump(list(sent_last_year), f, indent=4)

def send_email(to_email, alumni_name, company, major, position):
    try:
        # Set up the email
        msg = MIMEMultipart()
        msg['From'] = YOUR_EMAIL
        msg['To'] = "drewmeyer28@gmail.com"
        msg['Subject'] = HEADER

        # Personalize the body
        if contains_major_keywords(major) or contains_major_keywords(position):
            if contains_major_keywords(major):
                print(f"Match found in major: {major}")
            if contains_major_keywords(position):
                print(f"Match found in position: {position}")
            body = body_template.SAME_CAREER_PATH_SAME_MAJORS.format(alumni_name=alumni_name, company=company)
        else:
            print("No match found in major or position.")
            body = body_template.DIFFERENT_CAREER_PATH_DIFFERENT_MAJORS.format(alumni_name=alumni_name, company=company)
        msg.attach(MIMEText(body, 'plain'))

        with open(PDF_FILE_PATH, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(PDF_FILE_PATH)}")
            msg.attach(part)
        
        # Connect to Gmail and send the email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(YOUR_EMAIL, YOUR_PASSWORD)
        server.send_message(msg)
        server.quit()

        print(f"Email sent to {alumni_name} ({to_email})")
        sent_last_year.add(to_email) 
        save_sent_emails()
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
with open(ALUMNI_INFO, 'r') as f:
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
        position = alumni['position']
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
                        send_email(email, name.split()[0], company_name, major, position)
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



