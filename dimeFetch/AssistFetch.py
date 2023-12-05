import os
import csv
import time
import numpy as np
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions

# Set up the Firefox options and WebDriver
service = FirefoxService()
options = FirefoxOptions()
options.add_argument('-headless')  # Uncomment if you run in headless mode
options.add_argument("--window-size=1920x,1080")
driver = webdriver.Firefox(service=service, options=options)

# Open the webpage
driver.get('https://www.nba.com/stats/players/passing?LastNGames=1&dir=D&sort=POTENTIAL_AST')

# Wait for the table data to load
print('1')
table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'nba-stats-content-block')))
print('2')

headers = table.find_elements(By.TAG_NAME, 'th')
print('3')

header_titles = [header.text for header in headers]
print("Logski")
print(header_titles)

# Replacing redundant "AST" with actual header name
header_titles[9] = "SecondaryAssists"
header_titles[10] = "PotentialAssists"
header_titles[11] = "AssistPointsCreated"
header_titles[12] = "AdjustedAssists"
header_titles[13] = "AstToPass%"
header_titles[14] = "AdjAstToPass%"

xbutton = WebDriverWait(driver,3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".onetrust-close-btn-handler.onetrust-close-btn-ui.banner-close-button.ot-close-icon")))
xbutton.click()


# Conditional assignments
if len(header_titles) > 9:
    header_titles[9] = "SecondaryAssists"
if len(header_titles) > 10:
    header_titles[10] = "PotentialAssists"
if len(header_titles) > 11:
    header_titles[11] = "AssistPointsCreated"

# Sort the table by clicking on the table header (sorting by rebounds)
time.sleep(np.random.uniform(3.80,6.0))
header_to_sort = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//th[text()="AST"]')))
time.sleep(np.random.uniform(1.0,1.45))
header_to_sort.click()
time.sleep(np.random.uniform(4.0,5.35))  # Replace with a more reliable wait condition

# Locate the dropdown by the known prefix of the class name
dropdown_prefix = "DropDown_select"  # This is the consistent prefix of the class name
dropdown = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, f"//select[starts-with(@class, '{dropdown_prefix}')]"))
)

# Select the 'All' option by its value
all_option_value = "-1"
all_option = dropdown.find_element(By.XPATH, f"//option[@value='{all_option_value}']")
all_option.click()

# Get the current date and time for the filename
current_time = datetime.now()
timestamp = current_time.strftime("%Y%m%d_%H%M%S")

#save .csv files to archive folder
directory = "AssistsArchive"
if not os.path.exists(directory):
    os.makedirs(directory)
    print(f"Directory '{directory}' created")

# Open a new CSV file with the timestamp in the name to save the data
filename = os.path.join(directory, f'passing_data_{timestamp}.csv')
table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'nba-stats-content-block')))

with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(header_titles)  # Write the headers to the CSV
    rows = table.find_elements(By.TAG_NAME, 'tr')
    for row in rows:
        # Get all the columns for the row
        cols = row.find_elements(By.TAG_NAME, 'td')
        # Write the columns to the CSV
        writer.writerow([col.text for col in cols])

# Close the driver
driver.quit()
