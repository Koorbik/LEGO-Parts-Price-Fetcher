import requests
import pickle
import os
import urllib.parse
import re
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import PATH, API_KEY, SET_NAME, COOKIES_FILE, SELENIUM_OPTIONS, USER_AGENT, PART_PRICE_LABELS, MAX_WORKERS, \
    CSV_FILE

PART_NUMBERS = []


def create_driver():
    options = Options()
    for option in SELENIUM_OPTIONS:
        options.add_argument(option)

    service = Service(PATH)
    return webdriver.Chrome(service=service, options=options)


def save_cookies(driver, file_path=COOKIES_FILE):
    with open(file_path, 'wb') as file:
        pickle.dump(driver.get_cookies(), file)


def load_cookies(file_path=COOKIES_FILE):
    with open(file_path, 'rb') as file:
        return pickle.load(file)


def login_to_bricklink(driver):
    driver.get('https://www.bricklink.com/v2/main.page')
    input("Please log in manually, then press Enter to continue...")

    save_cookies(driver, COOKIES_FILE)


def search_lego_set_by_name(set_name):
    # Define the API endpoint for searching sets
    encoded_name = urllib.parse.quote(set_name)  # URL encode the set name
    url = f"https://rebrickable.com/api/v3/lego/sets/?search={encoded_name}"

    headers = {'Authorization': f'key {API_KEY}'}

    # Make the API request to search for sets by name
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        sets = data['results']

        if sets:
            # If one or more sets are found, print the name and set number of each set
            for i, lego_set in enumerate(sets, start=1):
                print(f"{i}. {lego_set['name']} (Set Number: {lego_set['set_num']})")
            choice = input("Enter which set you are interested in: ")
            return sets[int(choice) - 1]
        else:
            print(f"No sets found with the name '{set_name}'")
            return None
    else:
        print(f"Failed to search sets. Status code: {response.status_code}")
        return None


def get_lego_set_parts(set_name, set_number=None):
    if set_number is not None:
        headers = {'Authorization': f'key {API_KEY}'}
        page = 1
        page_size = 100  # The API might limit the number of results per page (e.g., 100)

        while True:
            url = f"https://rebrickable.com/api/v3/lego/sets/{set_number}/parts/?page={page}&page_size={page_size}"

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                parts = data['results']

                if not parts:
                    # No more parts to fetch, stop the loop
                    break

                for part in parts:
                    part_num = part['part']['part_num']
                    quantity = part['quantity']  # Fetch the quantity required for the set

                    cleaned_part_num = re.sub(r'\D', '', part_num)

                    if cleaned_part_num:
                        PART_NUMBERS.append((cleaned_part_num, quantity))  # Store part number and quantity as a tuple

                # If there's another page, increment the page number
                if data['next']:
                    page += 1
                else:
                    break
            else:
                print(f"Failed to fetch parts. Status code: {response.status_code}")
                break
    else:
        lego_set = search_lego_set_by_name(set_name)

        if lego_set:
            set_number = lego_set['set_num']
            set_name = lego_set['name']
            print(f"Found set: {lego_set['name']} (Set Number: {set_number})")

            try:
                get_lego_set_price_and_save_to_csv(set_name, set_number)
            except Exception:
                print(f"Failed to fetch LEGO set price for {set_name}\n")
                print("Proceeding with fetching prices for parts")
                # Continue with fetching parts even if the price fetch fails

            get_lego_set_parts(lego_set['name'], set_number)
        else:
            print(f"Could not find any set with the name: {set_name}")


def fetch_part_price(part_id):
    session = requests.Session()
    cookies = load_cookies()

    # Check if cookies were loaded properly
    if not cookies:
        print(f"No cookies found for part {part_id}.")
        return None

    for cookie in cookies:
        # Convert cookies to the format expected by bs4
        session.cookies.set(cookie['name'], cookie['value'])

    # Print cookies for debugging
    # print(f"Cookies applied for part {part_id}:")
    # for key, value in session.cookies.items():
    # print(f"{key}: {value}")

    body = session.get(
        f"https://www.bricklink.com/catalogPG.asp?itemType=P&itemNo={part_id}&itemSeq=1&colorID=0&v=P&priceGroup=Y&prDec=2",
        headers={'User-Agent': USER_AGENT}
    )

    if body.status_code != 200:
        print(f"Failed to fetch part {part_id}, Status Code: {body.status_code}")
        return None

    # Checking if the cookies were properly loaded and the user is logged in
    if "Login is required" in body.text:
        print(
            f"Login failed for part {part_id}. The cookies may be expired.")  # If you see this message, delete current cookies and relaunch the code
        return None

    soup = BeautifulSoup(body.content, 'html.parser')
    table = soup.select_one(
        '#id-main-legacy-table > tr > td > table:nth-of-type(3) > tr:nth-of-type(3) > td:nth-of-type(4) > table > tr > td > table'
    )

    if table:
        rows = table.find_all('tr')
        part_data = {}

        for row in rows:
            label = row.find('td').get_text(strip=True)
            value = row.find_all('td')[1].get_text(strip=True)

            if label in PART_PRICE_LABELS:
                part_data[label] = value

        return part_data
    else:
        return None


def save_to_csv(part_id, part_data, quantity, csv_file=CSV_FILE):
    file_exists = os.path.isfile(csv_file)

    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')

        if not file_exists:
            # Writing header if file doesn't exist
            writer.writerow(['Part ID', 'Quantity Needed', 'Min Price', 'Avg Price', 'Max Price'])

        # Clean each part of the data by replacing non-breaking spaces with regular spaces
        min_price = part_data.get('Min Price:', 'N/A').replace('\xa0', ' ').replace('.', ',') if part_data else 0
        avg_price = part_data.get('Avg Price:', 'N/A').replace('\xa0', ' ').replace('.', ',') if part_data else 0
        max_price = part_data.get('Max Price:', 'N/A').replace('\xa0', ' ').replace('.', ',') if part_data else 0

        row = [
            part_id,
            quantity,
            min_price,
            avg_price,
            max_price
        ]

        writer.writerow(row)


def calculate_total_price():
    total_min_price = 0
    total_avg_price = 0
    total_max_price = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_part = {executor.submit(fetch_part_price, part[0]): part for part in PART_NUMBERS}

        for future in tqdm(as_completed(future_to_part), total=len(future_to_part)):
            part, quantity = future_to_part[future]
            try:
                part_data = future.result()
                if part_data:
                    min_price = part_data.get('Min Price:', '0').replace('PLN\xa0', ' ')
                    avg_price = part_data.get('Avg Price:', '0').replace('PLN\xa0', ' ')
                    max_price = part_data.get('Max Price:', '0').replace('PLN\xa0', ' ')

                    min_price_value = float(min_price) if min_price != 'N/A' else 0
                    avg_price_value = float(avg_price) if avg_price != 'N/A' else 0
                    max_price_value = float(max_price) if max_price != 'N/A' else 0

                    total_min_price += min_price_value * quantity
                    total_avg_price += avg_price_value * quantity
                    total_max_price += max_price_value * quantity
                else:
                    print(f"\nFailed to fetch price for part {part}, defaulting to 0")
            except Exception as exc:
                print(f"Part {part} generated an exception: {exc}")

    return total_min_price, total_avg_price, total_max_price


def save_totals_to_csv(total_min_price, total_avg_price, total_max_price, csv_file=CSV_FILE):
    total_min_price = str(total_min_price).replace('.', ',')
    total_avg_price = str(total_avg_price).replace('.', ',')
    total_max_price = str(total_max_price).replace('.', ',')

    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')

        writer.writerow([])  # Add an empty row for spacing
        writer.writerow(['Total Min Price', 'Total Avg Price', 'Total Max Price'])
        writer.writerow([total_min_price, total_avg_price, total_max_price])


def get_lego_set_price_and_save_to_csv(set_name, set_number, csv_file=CSV_FILE):
    driver = create_driver()
    cleaned_set_name = set_name.replace(" ", "-")
    if "-" in set_number:
        cleaned_set_number = set_number.split("-")[0]
    else:
        cleaned_set_number = set_number

    driver.get(f"https://www.lego.com/pl-pl/product/{cleaned_set_name}-{cleaned_set_number}")

    try:
        price_element = driver.find_element(By.XPATH,
                                            '//*[@id="main-content"]/div/div[1]/div/div[2]/div[2]/div[2]/div/span')
        price = price_element.text

        with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')

            writer.writerow([])
            writer.writerow(['Lego Set Price'])
            writer.writerow([price])
            writer.writerow([])
    finally:
        driver.quit()


def main():
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)

    get_lego_set_parts(SET_NAME)

    if PART_NUMBERS:
        if not os.path.exists(COOKIES_FILE):
            driver = create_driver()
            try:
                login_to_bricklink(driver)
            finally:
                driver.quit()
        else:
            print("Cookies file already exists. Skipping login.")

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_part = {executor.submit(fetch_part_price, part[0]): part for part in PART_NUMBERS}

            for future in tqdm(as_completed(future_to_part), total=len(future_to_part)):
                part, quantity = future_to_part[future]
                try:
                    part_data = future.result()
                    save_to_csv(part, part_data, quantity)
                except Exception as exc:
                    print(f"Part {part} generated an exception: {exc}")
                    save_to_csv(part, None, quantity)

        total_min_price, total_avg_price, total_max_price = calculate_total_price()

        save_totals_to_csv(total_min_price, total_avg_price, total_max_price)
    else:
        print("Fetching parts for this LEGO set failed, please retry")


if __name__ == "__main__":
    main()
