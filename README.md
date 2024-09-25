# LEGO Set Parts Price Fetcher

This project automates the retrieval of LEGO set parts from the Rebrickable API and fetches pricing information for those parts from Bricklink. It uses requests for API interaction, BeautifulSoup for web scraping, and Selenium to handle login automation on Bricklink. The aim is to streamline the process of comparing the cost of purchasing a LEGO set as a whole versus building it from scratch using used parts.

Future updates will include comparing LEGO set stock prices with the total cost of individual parts, enhancing the project's usefulness for LEGO enthusiasts and collectors.

## Features

- **LEGO Set Search**: Search for LEGO sets by name using the Rebrickable API.
- **Parts Retrieval**: Fetch part numbers of a LEGO set.
- **Price Scraper**: Scrape price details for LEGO parts from Bricklink.
- **Multithreaded Execution**: Fast price retrieval using concurrent requests with a thread pool.
- **Login Automation**: Automate Bricklink login with Selenium and save login session cookies for future use.


## Requirements

Listed in the requirements.txt. Installed with a command below:
```console
pip install -r requirements.txt
```
#### Web Driver
Make sure to have the correct WebDriver for your browser. The code is set up for Chrome, so you'll need to download the [ChromeDriver](https://googlechromelabs.github.io/chrome-for-testing/) and configure the path in config.py.

## Configuration

In the config.py file, you need to provide the following:
- **Rebrickable API Key**: Your personal API key to access the Rebrickable API.
- **File Path to Chrome Driver**: The path where your ChromeDriver executable is located.
- **Max Workers**: Set the maximum number of worker threads based on your machine's capabilities for concurrent requests.
- **LEGO Set Name**: The name of the LEGO set you want to search for. Alternatively, you can provide the **set number** (optional).

All other configurations can remain the same as in the example config.py file.