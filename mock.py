from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test():
    # Define positions of interest
    positions_of_interest = ["manager", "engineer", "developer", "software", "recruiting", "systems"]

    # Initialize WebDriver (Make sure to set the path to your ChromeDriver)
    driver_path = "/path/to/chromedriver"
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()

    # Load the LinkedIn search page
    linkedin_url = "https://www.linkedin.com/login"
    driver.get(linkedin_url)

    # Log in (replace with your credentials)
    username = driver.find_element(By.ID, "username")
    password = driver.find_element(By.ID, "password")
    username.send_keys("your_email@example.com")
    password.send_keys("your_password")
    password.send_keys(Keys.RETURN)

    # Wait for the page to load and navigate to your search URL
    search_url = "https://www.linkedin.com/search/results/people/?currentCompany=%5B%221586%22%5D&origin=FACETED_SEARCH&schoolFilter=18159&sid=uit"
    driver.get(search_url)

    # Wait until the search results load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.artdeco-card"))
    )

    # Process each result
    results = driver.find_elements(By.CSS_SELECTOR, "div.artdeco-card")
    for result in results:
        try:
            # Extract name
            name_element = result.find_element(By.CSS_SELECTOR, "span.entity-result__title-text")
            name = name_element.text.strip()

            # Extract profile link
            profile_link = result.find_element(By.TAG_NAME, "a").get_attribute("href")

            # Extract position
            position_element = result.find_element(By.CSS_SELECTOR, "div.entity-result__primary-subtitle")
            position = position_element.text.lower()

            # Check if the position matches criteria
            if any(keyword in position for keyword in positions_of_interest):
                print(f"Name: {name}, Position: {position}, Profile Link: {profile_link}")

                # Check for 'Connect' button and click
                try:
                    connect_button = result.find_element(By.XPATH, "//button[contains(text(), 'Connect')]")
                    connect_button.click()
                    time.sleep(2)  # Wait for modal to load

                    # Confirm the connection request
                    send_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Send')]")
                    send_button.click()
                    print(f"Connection request sent to {name}")
                except Exception as e:
                    print(f"No connect button for {name}. Moving to the next person.")
            else:
                print(f"Position does not match criteria for {name}.")
        except Exception as e:
            print(f"Error processing result: {e}")

    # Close the browser
    driver.quit()

test()

# def get_all_alumni(driver):
    # driver.get("https://www.linkedin.com/search/results/people/?currentCompany=%5B%221586%22%5D&origin=FACETED_SEARCH&schoolFilter=18159&sid=uit")
    # time.sleep(constants.DELAY)  # Wait for the page to load
    # # Total number of results to iterate (adjust as needed)
    # # total_results = 10  # Set this to the expected total number of results you want to process

    # ellipsis_set = set()  # To track non-numeric pagination buttons (e.g., "...")
    # while True:
    #     scroll_and_scrape(driver)
    #     time.sleep(constants.DELAY)

    #     # Locate the main container holding all search results
    #     results_container = driver.find_element(By.CSS_SELECTOR, "div.search-results-container")

    #     # Fetch all individual result elements within the container
    #     result_elements = results_container.find_elements(By.CSS_SELECTOR, "li")

    #     # Filter only profile-related elements
    #     profile_elements = []
    #     for result in result_elements:
    #         try:
    #             # Check for a specific element that confirms it's a profile (e.g., name or "Connect" button)
    #             result.find_element(By.CSS_SELECTOR, "span[aria-hidden='true']")  # Name element
    #             profile_elements.append(result)
    #         except Exception:
    #             # Skip elements that are not profiles
    #             pass

    #     print(f"Found {len(profile_elements)} valid profiles on the current page.")

    #     # Process the filtered profiles
    #     for i, result in enumerate(profile_elements, start=1):
    #         print(f"\nProcessing profile {i}:")
    #         try:
    #             # Extract the name
    #             try:
    #                 name_element = result.find_element(By.CSS_SELECTOR, "span[aria-hidden='true']")
    #                 name = name_element.text.strip()
    #                 print(f"  Name: {name}")
    #             except Exception as e:
    #                 print(f"  Name not found. Error")

    #             # Extract the profile link
    #             try:
    #                 profile_link_element = result.find_element(By.CSS_SELECTOR, "a[data-test-app-aware-link]")
    #                 profile_link = profile_link_element.get_attribute("href")
    #                 print(f"  Profile Link: {profile_link}")
    #             except Exception as e:
    #                 print(f"  Profile link not found. Error")

    #             # Extract the position/headline
    #             try:
    #                 position_element = result.find_element(By.XPATH, ".//div[contains(@class, 't-14 t-black t-normal')]")
    #                 position = position_element.text.strip()
    #                 print(f"  Position: {position}")
    #             except Exception as e:
    #                 print(f"  Position not found. Error")

    #             # Check and log the "Connect" button
    #             try:
    #                 connect_button = result.find_element(By.XPATH, ".//button//span[text()='Connect']")
    #                 # connect_button.click()
    #                 print(f"  {connect_button.text} request sent to {name}")
    #             except Exception:
    #                 print("  No 'Connect' button found.")
    #         except Exception as e:
    #             print(f"Finished")

        
    #     # Iterate over results using the provided XPath template
    #     # for i in range(1, total_results + 1):  # Increment by 2 based on your example (1, 3, 5, etc.)
    #     #     try:
    #     #         # Construct the XPath dynamically
    #     #         result_xpath = f"/html/body/div[6]/div[3]/div[2]/div/div[1]/main/div/div/div[3]/div/ul/li[{i}]"
    #     #         # Find the result element
    #     #         result = driver.find_element(By.XPATH, result_xpath)

    #     #         print(f"\nProcessing result: {i}")
                
    #     #         # Extract the name
    #     #         try:
    #     #             name_element = result.find_element(By.XPATH, ".//span[@aria-hidden='true']")
    #     #             name = name_element.text.strip()
    #     #             print(f"  Name: {name}")
    #     #         except Exception as e:
    #     #             print(f"  Name not found. Error: {e}")
    #     #             # Locate the main container holding all search results


    #     #         # Extract the profile link
    #     #         try:
    #     #             profile_link = result.find_element(By.XPATH, ".//a").get_attribute("href")
    #     #             print(f"  Profile Link: {profile_link}")
    #     #         except Exception:
    #     #             print("  Profile link not found.")
                
    #     #         # Extract the position
    #     #         try:
    #     #             position_element = result.find_element(By.XPATH, ".//div[contains(@class, 't-14 t-black t-normal')]")
    #     #             position = position_element.text.strip()
    #     #             print(f"  Position: {position}")
    #     #         except Exception as e:
    #     #             print(f"  Position not found. Error")
                
    #     #         # Check for and click the "Connect" button
    #     #         try:
    #     #             connect_button = result.find_element(By.XPATH, ".//button//span[text()='Connect']")
    #     #             # connect_button.click()
    #     #             print(f"  {connect_button.text} request sent to {name}")
    #     #         except Exception:
    #     #             print("  No 'Connect' button found.")
    #     #     except Exception as e:
    #     #         print(f"Finished")
    #     #         break
    #     # if not navigate_to_next_page(driver, ellipsis_set):  # Try navigating to the next page
    #         break