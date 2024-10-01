# LEGO Set Parts Price Fetcher

This project automates the process of retrieving LEGO set parts from the Rebrickable API and fetching pricing information for those parts from Bricklink. It combines web scraping, API interaction, and multithreading to provide a streamlined method for comparing the cost of purchasing a full LEGO set versus building it using individual parts.

## Features

- **LEGO Set Search**: Search for LEGO sets by name using the Rebrickable API.
- **Parts Retrieval**: Fetch part numbers and quantities required for a specific LEGO set.
- **Price Scraper**: Scrape price details for LEGO parts from Bricklink.
- **Multithreaded Execution**: Use concurrent requests to speed up price retrieval.
- **Login Automation**: Automate Bricklink login with Selenium and save login session cookies for future use.
- **Total Price Calculation**: Compare the cost of individual parts with the price of the complete LEGO set.

## Installation 

**1. Clone the repository:**
```console
git clone <repository-url>
cd <repository-folder>
```
**2. Install dependencies:** Install the required Python packages using the **requirements.txt** file:
```console
pip install -r requirements.txt
```
**3. Download WebDriver:**
- This project uses Selenium with Chrome. Download the [ChromeDriver](https://googlechromelabs.github.io/chrome-for-testing/) that matches your Chrome browser version.
- Set the path to the ChromeDriver executable in the **config.py** file.

## Configuration

You need to set up the following in the config.py file:
- **Rebrickable API Key**: Obtain an API key from Rebrickable by signing up on their [website](https://rebrickable.com/api/).
- **File Path to Chrome Driver**: The path where your ChromeDriver executable is located.
- **Max Workers**: Set the maximum number of worker threads based on your machine's capabilities for concurrent requests.
- **LEGO Set Name**: The name of the LEGO set you want to search for.

## How does it work?

**1. Search for LEGO Set:**
- The script allows you to search for LEGO sets using the Rebrickable API by name. It lists available sets and prompts you to choose one.

**2. Retrieve LEGO Set Parts:**
- Once a set is selected, the script retrieves all its parts and their required quantities from Rebrickable.

**3. Fetch Pricing from Bricklink:**
- It scrapes Bricklink for pricing details of each part (min, average, and max price) and saves this information to a CSV file.
- If the user is not logged into Bricklink, Selenium automates the login process and saves cookies for future use.

**4. LEGO Set Price Fetch:**
- The script fetches the current price of the full LEGO set from the LEGO website and compares it to the total cost of the individual used parts.

**5. Price Calculation:**
- After retrieving all part prices, the script calculates the total minimum, average, and maximum prices for building the set from individual used parts.

**6. Save results:**
- The part details, prices, and total costs are saved in a CSV file for easy review.

## Notes
- If the cookies used for login expire, delete the cookies file (COOKIES_FILE) and run the script again to re-login.
- Ensure that the correct WebDriver version matches your browser for Selenium to work correctly.

## Future updates
- Even more speed improvement
- Choice of using used or new parts
- Visualization Tools
- GUI?

## License
This project is licensed under the MIT License.
