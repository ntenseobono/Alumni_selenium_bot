import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from utils import constants
import time
import random



def check_login_status():
    EMAIL = constants.MY_CC_EMAIL
    PASSWORD = constants.PASSWORD
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")  # Disable automation detection
    options.add_argument("start-maximized")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")  # Custom User-Agent

    # Initialize WebDriver
    driver = webdriver.Chrome(options=options)

    # Open LinkedIn login page
    driver.get(constants.LOGIN)
    time.sleep(random.uniform(2, 4))  # Random delay

    # Log in to LinkedIn
    email_field = driver.find_element(By.ID, "username")
    password_field = driver.find_element(By.ID, "password")
    email_field.send_keys(EMAIL)
    password_field.send_keys(PASSWORD)
    password_field.send_keys(Keys.RETURN)
    time.sleep(random.uniform(4, 6))  # Wait for login to complete

    # Navigate to LinkedIn Jobs page
    driver.get(constants.LINKEDIN_JOB)
    time.sleep(random.uniform(3, 5))

    try:
        # Wait for the search box to load
        search_box = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[5]/header/div/div/div/div[2]/div[2]/div/div/input[1]")))        
        # Interact with the search box
        search_box.click()  # Ensure the box is active
        search_box.send_keys("Software Engineer")
        search_box.send_keys(Keys.RETURN)
        time.sleep(random.uniform(3, 5))  # Wait for search results

        print("Search completed successfully.")
    except Exception as e:
        print(f"Error interacting with the search box: {e}")

    try:
        # Click the "Experience level" filter button
        experience_filter = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[5]/div[3]/div[4]/section/div/section/div/div/div/ul/li[4]/div/span/button")))
        experience_filter.click()
        time.sleep(2)  # Give the dropdown time to load

        # Select the "Entry level" option
        entry_level_option = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//html/body/div[5]/div[3]/div[4]/section/div/section/div/div/div/ul/li[4]/div/div/div/div[1]/div/form/fieldset/div[1]/ul/li[2]/label/p/span[1]")))
        entry_level_option.click()
        time.sleep(2)  # Wait for the page to reload with the filtered results

        show_results_button = driver.find_element(By.XPATH, "/html/body/div[5]/div[3]/div[4]/section/div/section/div/div/div/ul/li[4]/div/div/div/div[1]/div/form/fieldset/div[2]/button[2]")
        show_results_button.click()
        time.sleep(5)

        print("Applied 'Entry level' filter successfully.")
    except Exception as e:
        print(f"Error applying filter: {e}")

    # jobs_block= driver.find_element(By.XPATH, '/html/body/div[6]/div[3]/div[4]/div/div/main/div/div[2]/div[1]/div')
    # jobs_list = jobs_block.find_elements(By.XPATH, "./li[contains(@class, 'scaffold-layout__list-item')]")
    
    # n = 0
    jobs_block= driver.find_element(By.CSS_SELECTOR, '.scaffold-layout__list')
    jobs_list= jobs_block.find_elements(By.CSS_SELECTOR, '.scaffold-layout__list-item')
    n = 0
    for i in jobs_list:
        print("__________")
        n+=1
        driver.execute_script("arguments[0].scrollIntoView();", jobs_list[n-1])
        if "school alum works here" in i.text or "connections work here" in i.text or "connection works here" in i.text or "school alum work here":  
            print(n, " ",i.text)
    time.sleep(2)  # Wait for the page to reload with the filtered results




    # Locate all job postings
    while True:
    # Loop through each job listing
        job_listings = driver.find_elements(By.CLASS_NAME, "job-card-container")
        print(f"Found {len(job_listings)} job postings.")
        for index, job in enumerate(job_listings):
            try:
                # Check if "school alum works here" is mentioned
                print(job.text)
                alumni_text_element = job.find_element(By.CLASS_NAME, "job-card-container__job-insight-text")
                if "school alum works here" in alumni_text_element.text or "connections work here" in alumni_text_element.text or "connection works here" in alumni_text_element.text or "school alum work here":
                    print(f"Job #{index + 1}: Found alumni information.")
                    alumni_text_element.click()

                    company_name_element = job.find_element(By.XPATH, "/html/body/div[5]/div[3]/div[4]/div/div/main/div/div[2]/div[2]/div/div[2]/div/div[1]/div/div[1]/div/div[1]/div/div[1]/div[1]/div/a")
                    company_name = company_name_element.text
                    print(f"Opening company link for: {company_name}")

                    company_url = company_name_element.get_attribute("href")
                    driver.execute_script("window.open(arguments[0], '_blank');", company_url)

                    # Switch to the new tab
                    driver.switch_to.window(driver.window_handles[-1])
                    time.sleep(5) 
                    print("Trying to click")
                    possible_alumni = driver.find_element(By.XPATH, "/html/body/div[5]/div[3]/div/div[2]/div/div[2]/main/div[1]/section/div/div[2]/div[2]/div[2]/div/div/a/h2")
                    possible_alumni.click()
                    print("Clicked the possibles")
                    time.sleep(2)

                    print("Try comp filter")
                    company_filter = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[5]/div[3]/div[2]/section/div/nav/div/ul/li[4]/div/span/button")))
                    company_filter.click()
                    time.sleep(2) 
                    print("Completed comp filter")

                    print("Try reset company")
                    reset_company = driver.find_element(By.XPATH, "/html/body/div[5]/div[3]/div[2]/section/div/nav/div/ul/li[4]/div/div/div/div[1]/div/form/fieldset/div[2]/button[1]/span")
                    reset_company.click()
                    time.sleep(2) 
                    driver.find_element(By.XPATH, "/html/body/div[5]/div[3]/div[2]/section/div/nav/div/ul/li[4]/div/div/div/div[1]/div/form/fieldset/div[2]/button[2]/span").click()
                    print("Success reset company")
                    time.sleep(7) 
                    current_url = driver.current_url
                    modified_url = f"{current_url}&schoolFilter=%5B%2218159%22%5D&sid=eWq"
                    driver.get(modified_url)
                    time.sleep(2)

                    print("Typed 'Carleton College' in the input field.")
                    
                        

                    time.sleep(2)
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                else:
                    print(f"Job #{index + 1}: No alumni information")
            except:
                print(f"Not an alumni at #{index + 1}")
                pass
        
        time.sleep(10)
        # Locate all pagination buttons
        pagination_buttons = driver.find_elements(By.XPATH, "//ul[contains(@class, 'artdeco-pagination__pages')]/li/button")
        
        # Find the currently selected page
        current_page = driver.find_element(By.XPATH, "//li[contains(@class, 'active selected')]/button/span").text
        print(f"Currently on page: {current_page}")

        # Navigate to the next page in the list
        try:
            for button in pagination_buttons:
                if int(current_page) == button.text:
                    continue
                if int(button.text) == int(current_page) + 1:  # Find the next page by incrementing current page
                    print(f"Navigating to page {button.text}")
                    button.click()
                    time.sleep(5)  # Wait for the page to load
                    break
            else:
                print("No more pages available.")
                break  # Exit the loop if no next page is found
        except Exception as e:
            print(f"Error navigating to the next page: {e}")
            break 


    import pdb; pdb.set_trace()

    driver.quit()

def convert_to_integer(input_string):
    numeric_part = re.sub(r"[^\d]", "", input_string)
    return int(numeric_part)

check_login_status()