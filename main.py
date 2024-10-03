from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import csv

# Step 1: Read Order IDs from order.txt file
with open('order.txt', 'r') as file:
    order_ids = [line.strip() for line in file.readlines()]

# Set up Chrome options (can be modified for other browsers)
chrome_options = Options()
chrome_options.add_argument("--start-maximized")

# Initialize the WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# List to store order details
order_data = []

# Loop through each order ID and process one by one
for order_id in order_ids:
    try:
        # Step 2: Go to the Delhivery website
        driver.get("https://www.delhivery.com/")

        # Wait for the page to load completely
        time.sleep(5)

        # Step 3: Click on the 'Order Id' tab link
        order_id_link = driver.find_element(By.XPATH, "//a[contains(text(), 'Order Id')]")
        order_id_link.click()

        # Wait for the page to load the Order Id input section
        # time.sleep(1)

        # Step 4: Locate the input field for the Order ID and enter the current Order ID
        order_id_input = driver.find_element(By.XPATH, "//input[@placeholder='Enter your Order Id']")
        order_id_input.clear()  # Clear any previous value
        order_id_input.send_keys(order_id)  # Send the current Order ID

        # Step 5: Locate and click the 'Track Order' button
        track_order_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Track Order')]")
        track_order_button.click()

        # Wait for the page to load the tracking results
        time.sleep(5)

        # Step 6: Use BeautifulSoup to parse the page content
        page_source = driver.page_source  # Get the page source after the order is tracked
        soup = BeautifulSoup(page_source, 'html.parser')

        # Extract tracking details
        track_id_text = 'Track ID not found'
        delivery_date_text = 'Delivery Date not found'
        order_statuses_text = 'Statuses not found'
        through_text = 'B2B'  # Default value for Through

        # Extract the track ID (modify based on the actual HTML structure)
        track_id = soup.find('div', class_='track-id mobile-show-css d-flex')
        if track_id:
            track_id_text = track_id.get_text(strip=True).replace('TRACKING ID', '').strip()

            # Determine "Through" based on the first character of the Track ID
            if track_id_text.startswith('6'):
                through_text = 'SURFACE'
            elif track_id_text.startswith('1'):
                through_text = 'EXPRESS'
            else:
                through_text = 'B2B'

        # Extract the delivery date (modify based on the actual HTML structure)
        delivery_date = soup.find('div', class_='delivery-date')
        if delivery_date:
            delivery_date_text = delivery_date.get_text(strip=True)

        # Extract the order status (adjust based on actual HTML structure)
        statuses = soup.find_all('button', class_='btn-outline-info')
        if statuses:
            order_statuses_text = ", ".join([status.get_text(strip=True) for status in statuses])

        # Add data to the list
        order_data.append([order_id, track_id_text, delivery_date_text, order_statuses_text, through_text])

    except Exception as e:
        print(f"Error processing Order ID: {order_id}. Error: {e}")
        # Move to the next order in case of an error

    # Optional: Add a short wait before processing the next Order ID
    time.sleep(2)

# Step 7: Write data to CSV
with open('order_tracking_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['Order ID', 'Track ID', 'Delivery Date', 'Order Statuses', 'Through'])  # Header
    csvwriter.writerows(order_data)  # Write the order data

# Step 8: Close the browser after all tasks are completed
driver.quit()

print("Data extraction complete. Check the 'order_tracking_data.csv' file.")
