from seleniumwire import webdriver


def open_browser():
    # Address of the machine running Selenium Wire.
    # Explicitly use 127.0.0.1 rather than localhost
    # if remote session is running locally.
    sw_options = {
        'addr': '0.0.0.0',
        'auto_config': False,
        'port': 35813
        }

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--proxy-server=airflow-container:35813')
    chrome_options.add_argument('--ignore-certificate-errors')

    driver = webdriver.Remote(
        command_executor="http://selenium-hub:4444",
        options=chrome_options,
        seleniumwire_options=sw_options
        )
    return driver
