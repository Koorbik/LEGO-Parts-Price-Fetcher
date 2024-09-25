# PATH for chromedriver (it may differ CHECK IN YOUR SYSTEM!!!)
PATH = "C:\\Program Files (x86)\\chromedriver.exe"

# Rebrickable API Key (PROVIDE YOUR OWN API KEY)
# https://rebrickable.com/api/
API_KEY = 'your_rebrickable_api_key'

# Default LEGO set name
SET_NAME = "Stitch"

SET_NUMBER = ""

# File path for cookies
COOKIES_FILE = "cookies.pkl"

# Number of threads to use for fetching part prices
MAX_WORKERS = 10

# Selenium options
SELENIUM_OPTIONS = [
    "--disable-extensions",
    "--disable-infobars",
    "--start-maximized",
    "--disable-gpu",
    "--no-sandbox",
    "--disable-dev-shm-usage"
]

USER_AGENT = 'fake browser'

PART_PRICE_LABELS = ['Total Qty:', 'Min Price:', 'Avg Price:', 'Qty Avg Price:', 'Max Price:']
