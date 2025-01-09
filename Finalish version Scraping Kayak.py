from time import sleep, strftime
from random import randint
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

def parse_raw_text(raw_text):
    """Parse raw flight data text into a structured list of dictionaries."""
    # Split the text into sections based on "Save", "Share", or "Ad" keywords
    sections = re.split(r'\bSave\b|\bShare\b|\bAd\b', raw_text)

    flights = []
    for section in sections:
        # Clean up the section
        section = section.strip()
        if not section:
            continue

        # Extract data using regex
        match = re.search(
            r'(?P<date>\d{1,2}/\d{1,2})\n(?P<day>\w+)\n(?P<time>[\d:apm –]+)\n(?P<airline>[\w\s]+)\n'
            r'(?P<stops>\w+)\n(?P<duration>\d+h \d+m)\n(?P<from>\w+)\n-\n(?P<to>\w+)',
            section,
        )
        if match:
            flight = match.groupdict()

            # Optional: Extract price if available
            price_match = re.search(r'\$\d+', section)
            flight['price'] = price_match.group() if price_match else 'N/A'

            flights.append(flight)

    return flights

driver = webdriver.Chrome()
driver.maximize_window()

sleep(2)



# Function to load more results
def load_more():
    mistakes=0
    try:
        # Wait and click the "Show more results" button
        show_more_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                                        "//div[@role='button' and contains(@class, 'show-more-button') and text()='Show more results']"))
        )
        show_more_button.click()
    except:
        print("MISTAKEEEEE")
        mistakes+=1
        if mistakes>7:
            return 0




# Start scraping from Kayak
def start_kayak(city_from, city_to, date_start, date_end):
    kayak = ('https://www.kayak.com/flights/' + city_from + '-' + city_to +
             '/' + date_start + '-flexible/' + date_end + '-flexible?sort=bestflight_a')
    driver.get(kayak)

    for i in range(30):
        sleep(randint(1,7))
        try:
            load_more()
        except:
            print("Broke")
            continue



    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '//a[@class = "moreButton"]')))
        sleep(randint(2, 5))

        xp_popup_close = WebDriverWait(driver, 15).until(EC.element_to_be_clickable(
            (By.XPATH,
             '//button[contains(@id,"dialog-close") and contains(@class,"Button-No-Standard-Style close ")]')))[5]
        xp_popup_close.click()
    except Exception as e:
        print("No popup appeared or other error:", e)

    sleep(randint(1, 5))

    print('starting first scrape.....')
    df_flights_best = page_scrape()
    df_flights_best['sort'] = 'best'
    sleep(randint(2, 5))

    # Ensure the matrix prices section is fully loaded
    matrix = WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.XPATH, '//*[contains(@id,"FlexMatrixCell")]')))
    matrix = driver.find_elements(By.XPATH,'//*[contains(@id,"FlexMatrixCell")]')
    print("matrix", matrix)
    matrix_prices = [price.text.replace('$', '') for price in matrix]
    matrix_prices = [int(price) for price in matrix_prices if price != '']

    print('matrix prices', matrix_prices)

    matrix_prices = list(map(int, matrix_prices))
    matrix_min = min(matrix_prices)
    matrix_avg = sum(matrix_prices) / len(matrix_prices)
    print(matrix)

    sleep(randint(2, 5))



    '''for i in range(3):
        sleep(randint(5,7))
        load_more()'''




    if not os.path.exists('search_backups'):
        os.makedirs('search_backups')

    # Saving the final DataFrame as an Excel file
    final_df = pd.concat([df_flights_best])
    final_df.to_excel(os.path.join('search_backups', '{}_flights_{}-{}_from_{}_to_{}.xlsx'.format(
        strftime("%Y%m%d-%H%M"), city_from, city_to, date_start, date_end)), index=False)

    print('Excel file saved successfully in search_backups folder.')

    print('saved df.....')



# The page scraping function
def page_scrape():
    """This function takes care of the scraping part"""

    xp_sections = driver.find_elements(By.XPATH, '//*[@class="Fxw9"]')
    print('xp_sections', xp_sections)
    sections_list = [value.text for value in xp_sections]
    print("sections_list", sections_list)

    parsed_flights = parse_raw_text("\n".join(sections_list))
    print(parsed_flights)
    # Convert parsed data to a DataFrame
    flights_df = pd.DataFrame(parsed_flights)
    flights_df['timestamp'] = strftime("%Y_%m_%d-%Hh%Mmins")  # So we can know when it was scraped

    return flights_df

# Input details

city_from=['TUN','NBE','DJE', 'MIR']
city_to =  'PAR' #input('Where to? ')
date_start = '2025-01-10' #input('Search around which departure date? Please use YYYY-MM-DD format only ')
date_end = '2025-01-20' #input('Return when? Please use YYYY-MM-DD format only ')


#if we want to check different prices day to day, or hour to hour we can change the range and sleep amount
#keka najmou ncompariw 3ala periode atwel, but for convenience sake
#imma leave it at range(1) and no sleep
for n in range(4):
    start_kayak(city_from[n], city_to, date_start, date_end)
    print('iteration {} was complete @ {}'.format(n, strftime("%Y%m%d-%H%M")))


    sleep(1)
    print('sleep finished.....')

# Bonus: save a screenshot!
driver.save_screenshot('pythonscraping.png')

driver.quit()
