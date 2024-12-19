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
from utils import constants

found_jobs = set()
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


def login_to_linkedin(driver):
    """Log in to LinkedIn."""
    driver.get(constants.LOGIN)
    time.sleep(constants.DELAY)

    email_field = driver.find_element(By.ID, "username")
    password_field = driver.find_element(By.ID, "password")
    email_field.send_keys(constants.MY_CC_EMAIL)
    password_field.send_keys(constants.PASSWORD)
    password_field.send_keys(Keys.RETURN)
    time.sleep(constants.DELAY)
    time.sleep(100)


def search_jobs(driver, job_title):
    """Search for jobs on LinkedIn."""
    time.sleep(constants.DELAY)

    try:
        search_box = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "/html/body/div[5]/header/div/div/div/div[2]/div[2]/div/div/input[1]") 
            )
        )
        search_box.click()
        search_box.send_keys(job_title)
        search_box.send_keys(Keys.RETURN)
        time.sleep(constants.DELAY)
    except Exception as e:
        print(f"Error interacting with the search box: {e}")


def apply_filters(driver):
    """Apply 'Entry Level' experience filter."""
    try:
        experience_filter = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "/html/body/div[5]/div[3]/div[4]/section/div/section/div/div/div/ul/li[4]/div/span/button")
            )
        )
        experience_filter.click()
        time.sleep(constants.DELAY)

        entry_level_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//html/body/div[5]/div[3]/div[4]/section/div/section/div/div/div/ul/li[4]/div/div/div/div[1]/div/form/fieldset/div[1]/ul/li[2]/label/p/span[1]")
            )
        )
        entry_level_option.click()
        time.sleep(constants.DELAY)

        show_results_button = driver.find_element(
            By.XPATH,
            "/html/body/div[5]/div[3]/div[4]/section/div/section/div/div/div/ul/li[4]/div/div/div/div[1]/div/form/fieldset/div[2]/button[2]",
        )
        show_results_button.click()
        time.sleep(constants.DELAY)
    except Exception as e:
        print(f"Error applying filter: {e}")


def scrape_jobs(driver):
    """Scrape job postings and handle alumni-related interactions."""
    try:
        jobs_block = driver.find_element(By.CSS_SELECTOR, ".scaffold-layout__list")
        jobs_list = jobs_block.find_elements(By.CSS_SELECTOR, ".scaffold-layout__list-item")

        for n, job in enumerate(jobs_list, start=1):
            driver.execute_script("arguments[0].scrollIntoView();", job)
            if any(
                phrase in job.text
                for phrase in (
                    "school alum works here",
                    "connections work here",
                    "connection works here",
                    "school alum work here",
                )
            ):
                print(n, " ", job.text)
        time.sleep(constants.DELAY)
    except Exception as e:
        print(f"Error scraping jobs: {e}")
    
def handle_pagination(driver):
    """
    Handle job postings pagination by processing each page and navigating to the next one.
    """
    ellipsis_set = set()  # To track non-numeric pagination buttons (e.g., "...")
    results_list = []
    while True:
        process_current_page(driver, results_list)  # Process jobs on the current page
        if not navigate_to_next_page(driver, ellipsis_set):  # Try navigating to the next page
            break  # Exit loop if no next page is available
    write_to_json(results_list)

def process_job(driver, job, index, results_list):
    """Process a single job posting."""
    global found_jobs
    try:
        print(job.text)
        alumni_text_element = job.find_element(By.CLASS_NAME, "job-card-container__job-insight-text")
        company_name = job.find_element(By.CLASS_NAME, "artdeco-entity-lockup__subtitle").text
        # if 1 < 0:
        if any(
            phrase in alumni_text_element.text
            for phrase in (
                "school alum works here",
                "connections work here",
                "connection works here",
                "school alum work here",
            )
        ) and company_name not in found_jobs:
            print(f"Job #{index + 1}: Found alumni information.")
            found_jobs.add(company_name)
            profile_data = handle_alumni_action_new(driver, company_name)
            if profile_data:
                results_list.append(profile_data)
        else:
            print(f"Job #{index + 1}: No alumni information")
    except Exception as e:
        print(f"Error processing job #{index + 1}: {e}")

def handle_alumni_action_new(driver, company_name):
    try:
        url ="https://www.linkedin.com/search/results/all/"
        driver.execute_script("window.open(arguments[0], '_blank');", url)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(constants.DELAY)
        
        search_input = driver.find_element(By.XPATH, "/html/body/div[5]/header/div/div/div/div[1]/input")
        search_input.click()
        search_input.send_keys(company_name)
        search_input.send_keys(Keys.RETURN)

        profile_data = {
            "company_name": company_name,
            "profiles": []
        }

        print("Trying to click") 
        possible_alumni = driver.find_element(By.CSS_SELECTOR, ".reusable-search-simple-insight__text-container")
        possible_alumni.click()
        print("Clicked the possibles")
        time.sleep(constants.DELAY)

        current_url = driver.current_url
        modified_url = modify_link(current_url)
        driver.get(modified_url)
        time.sleep(constants.DELAY)
        profile_data["profiles"] = get_all_alumni(driver)
        time.sleep(constants.DELAY)

        # Close the new tab and return to the main window
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return profile_data
    except:
        profile_data = {
            "company_name": company_name,
            "profiles": None
        }
        return profile_data

def handle_alumni_action(driver, alumni_text_element):
    """Handle actions related to alumni information in job postings."""
    try:
        alumni_text_element.click()  # Click the element to navigate
        time.sleep(constants.DELAY)  # Allow time for the page to load

        # Extract the company name and navigate to the company page
        company_name_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "/html/body/div[5]/div[3]/div[4]/div/div/main/div/div[2]/div[2]/div/div[2]/div/div[1]/div/div[1]/div/div[1]/div/div[1]/div[1]/div/a")
            )
        )
        company_name = company_name_element.text
        company_url = company_name_element.get_attribute("href")

        print(f"Opening company link for: {company_name}")
        driver.execute_script("window.open(arguments[0], '_blank');", company_url)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(constants.DELAY)

        profile_data = {
            "company_name": company_name,
            "profiles": []
        }

        print("Trying to click") 
        possible_alumni = driver.find_element(By.CSS_SELECTOR, "a.link-without-visited-state.t-black--light h2.t-black--light")
        alumni_text = possible_alumni.text.strip()
        
        if "other company alumni" in alumni_text:
            possible_alumni.click()
            print("Clicked the possibles")
            time.sleep(constants.DELAY)

            current_url = driver.current_url
            modified_url = modify_link(current_url)
            driver.get(modified_url)
            time.sleep(constants.DELAY)
            profile_data["profiles"] = get_all_alumni(driver)
            time.sleep(constants.DELAY)

        # Close the new tab and return to the main window
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return profile_data
    except Exception as e:
        print(f"Error handling alumni action: {e}")
        return None

def modify_link(link1, school_filter=constants.SCHOOL_FILTER):
    # Parse the URLs
    parsed_link1 = urlparse(link1)
    
    # Extract query parameters as dictionaries
    query_params1 = parse_qs(parsed_link1.query)
    
    # Check for extra parameters in Link 1
    extra_params = {
        key: value
        for key, value in query_params1.items()
        if key not in {"currentCompany", "origin"}
    }
    
    if extra_params:
        print("Extra parameters in Link 1:", extra_params)
    
    # Construct Link 3 by modifying Link 1
    query_params1["origin"] = ["FACETED_SEARCH"]
    query_params1["schoolFilter"] = [school_filter]
    
    # Remove unwanted parameters
    query_params1.pop("pastCompany", None)
    query_params1.pop("sid", None)  # You can decide if this is necessary to keep/remove

    # Build the new query string and URL
    new_query = urlencode(query_params1, doseq=True)
    new_link3 = urlunparse(
        parsed_link1._replace(query=new_query)
    )
    
    return new_link3

def process_current_page(driver, results_list):
    """
    Process all job listings on the current page.
    """
    scrape_jobs(driver)  # Call the scrape_jobs function
    job_listings = driver.find_elements(By.CLASS_NAME, "job-card-container")
    print(f"Found {len(job_listings)} job postings.")
    for index, job in enumerate(job_listings):
        process_job(driver, job, index, results_list)

def scroll_and_scrape(driver, max_scroll_attempts=10):
    scroll_pause_time = 1  # Pause time between scrolls
    last_height = driver.execute_script("return document.body.scrollHeight")  # Get initial page height
    print(last_height)
    scroll_attempt = 0

    while scroll_attempt < max_scroll_attempts:
        print(f"Scroll attempt {scroll_attempt + 1}")

        # Scroll down to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)  # Wait for new content to load

        # Get new page height after scrolling
        new_height = driver.execute_script("return document.body.scrollHeight")
        print(new_height)
        # Break the loop if no new content is loaded
        if new_height == last_height:
            print("No new content loaded. Stopping scroll.")
            break

        last_height = new_height  # Update last_height to new height
        print(last_height)
        scroll_attempt += 1

    print("Finished scrolling. Starting scraping process.")

def navigate_to_next_page(driver, ellipsis_set):
    """
    Navigate to the next page in the pagination.

    Returns:
        bool: True if navigation to the next page was successful, False otherwise.
    """
    try:
        # Wait for pagination buttons to load
        print("Waiting for pagination buttons...")
        # Locate all pagination buttons
        time.sleep(constants.DELAY)
        pagination_buttons = driver.find_elements(By.XPATH, "//ul[contains(@class, 'artdeco-pagination__pages')]/li/button")
        print(f"Found {len(pagination_buttons)} pagination buttons.")

        # Wait for the current page button to be visible
        print("Waiting for the current page button...")
        time.sleep(constants.DELAY)
        current_page_element = driver.find_elements(By.XPATH, "//li[contains(@class, 'active selected')]/button")
        current_page = int(current_page_element.text)
        print(f"Currently on page: {current_page}")

        # Iterate through pagination buttons
        for button in pagination_buttons:
            button_text = button.text.strip()

            # Handle non-numeric buttons (e.g., "...")
            if not button_text.isdigit():
                if '...' in ellipsis_set:
                    continue
                else:
                    print(f"Non-numeric button ('{button_text}') detected, clicking to reveal more pages.")
                    button.click()
                    ellipsis_set.add('...')
                    time.sleep(constants.DELAY)  # Wait for the UI to refresh
                    return True

            # Navigate to the next numerical page
            if int(button_text) == current_page + 1:
                print(f"Navigating to page {button_text}")
                button.click()
                time.sleep(constants.DELAY)  # Wait for the page to load
                return True

        print("No more pages available.")
        return False  # No next page found

    except Exception as e:
        print(f"No pages found")
        return False
    
def get_all_alumni(driver):
    # driver.get("https://www.linkedin.com/search/results/people/?currentCompany=%5B%221586%22%5D&origin=FACETED_SEARCH&schoolFilter=18159&sid=uit")
    alumni_profiles = []
    time.sleep(constants.DELAY)  # Wait for the page to load
    ellipsis_set = set()  # To track non-numeric pagination buttons (e.g., "...")
    while True:
        scroll_and_scrape(driver)
        time.sleep(constants.DELAY)

        # Locate the main container holding all search results
        results_container = driver.find_element(By.CSS_SELECTOR, "div.search-results-container")
        result_elements = results_container.find_elements(By.CSS_SELECTOR, "li")

        # Filter only profile-related elements
        profile_elements = []
        for result in result_elements:
            try:
                # Check for a specific element that confirms it's a profile (e.g., name or "Connect" button)
                result.find_element(By.CSS_SELECTOR, "span[aria-hidden='true']")  # Name element
                profile_elements.append(result)
            except Exception:
                # Skip elements that are not profiles
                pass

        print(f"Found {len(profile_elements)} valid profiles on the current page.")

        # Process the filtered profiles
        for i, result in enumerate(profile_elements, start=1):
            print(f"\nProcessing profile {i}:")
            try:
                # Extract the name
                try:
                    name_element = result.find_element(By.CSS_SELECTOR, "span[aria-hidden='true']")
                    name = name_element.text.strip()
                    print(f"  Name: {name}")
                except Exception:
                    name = "Not Found"
                    print(f"  Name not found. Error")

                # Extract the profile link
                try:
                    profile_link_element = result.find_element(By.CSS_SELECTOR, "a[data-test-app-aware-link]")
                    profile_link = profile_link_element.get_attribute("href")
                    print(f"  Profile Link: {profile_link}")
                except Exception:
                    profile_link = "Not Found"
                    print(f"  Profile link not found. Error")

                # Extract the position/headline
                try:
                    position_element = result.find_element(By.XPATH, ".//div[contains(@class, 't-14 t-black t-normal')]")
                    position = position_element.text.strip()
                    print(f"  Position: {position}")
                except Exception as e:
                    position = "Not found"
                    print(f"  Position not found. Error")

                # Check and log the "Connect" button
                try:
                    connect_button = result.find_element(By.XPATH, ".//button//span[text()='Connect']")
                    # connect_button.click()
                    print(f"  {connect_button.text} request sent to {name}")
                except Exception:
                    print("  No 'Connect' button found.")
                
                alumni_profiles.append({
                    "name": name,
                    "profile_link": profile_link,
                    "position": position
                })
            except Exception as e:
                print(f"Finished")
        if not navigate_to_next_page(driver, ellipsis_set):  # Try navigating to the next page
            break
    return alumni_profiles

def convert_to_integer(input_string):
    """Convert a string with non-numeric characters to an integer."""
    numeric_part = re.sub(r"[^\d]", "", input_string)
    return int(numeric_part)

def write_to_json(data, filename="linkedin_alumni.json"):
    """Write the collected data to a JSON file."""
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)
    print(f"Data written to {filename}")

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

def check_login_status():
    """Main function to orchestrate the LinkedIn job scraping process."""
    driver = setup_driver()
    driver.get(constants.LINKEDIN_JOB)  # Replace with the website URL
    try:
        load_cookies(driver, 'chatcookies.json')
        search_jobs(driver, "Software Engineer")
        apply_filters(driver)
        handle_pagination(driver)
        pdb.set_trace()
    finally:
        driver.quit()

check_login_status()
