from selenium import webdriver
import time
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from application.core.configuration_loader import get_configuration

def ini_driver():
    print("Iniciando driver")
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")
    options.add_argument("--disable-notifications")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--hide-scrollbars")
    options.add_argument("--disable-infobars")
    options.add_argument("--start-maximized")
    options.binary_location = r"C:\Users\ascorredor\TFG\chrome-win64\chrome-win64\chrome.exe" # ¿Poner esta ruta en otro sitio?

    driver = webdriver.Chrome(options=options)

    return driver


def extranet_booking_page(driver):
    driver.get("https://account.booking.com/sign-in?op_token=EgVvYXV0aCJHChQ2Wjcyb0hPZDM2Tm43emszcGlyaBIJYXV0aG9yaXplGhpodHRwczovL2FkbWluLmJvb2tpbmcuY29tLyoCe31CBGNvZGUqEjCXqamk1vEmOgBCAFi36MCvBg")
    print(driver.title)

def login(driver):
    configuration = get_configuration()
    print("Configuracion obtenida")
    time.sleep(5)

    # Aceptar cookies
    try:
        cookies = driver.find_element(by=By.ID, value='onetrust-accept-btn-handler') 
        cookies.click()
        time.sleep(3)
    except NoSuchElementException:
        pass
    
    except ElementNotInteractableException:
        pass

    email = driver.find_element(by=By.ID, value='loginname') 
    email.send_keys(configuration.BOOKING_EXTRANET_USER)
    print(configuration.BOOKING_EXTRANET_USER)
    time.sleep(4)
    
     # Intentar encontrar el botón con el primer XPath
    try:
        enter_email = driver.find_element(by=By.XPATH, value='//*[@id="root"]/div/div/div[2]/div[1]/div/div/div/div/div/div/div/form/div[2]/div[2]/button')
    except NoSuchElementException:
        # Si no se encuentra, intentar con el segundo XPath
        enter_email = driver.find_element(by=By.XPATH, value='//*[@id="root"]/div/div/div/div[2]/div[1]/div/div/div/div/div/div/form/div[3]/button')

    enter_email.click()
    time.sleep(4)
    password = driver.find_element(by=By.ID, value='password') 
    password.send_keys(configuration.BOOKING_EXTRANET_PASSWORD)
    print(configuration.BOOKING_EXTRANET_PASSWORD)
    time.sleep(4)

    # Intentar encontrar el botón con el primer XPath
    try:
        enter_password = driver.find_element(by=By.XPATH, value='//*[@id="root"]/div/div/div/div[2]/div[1]/div/div/div/div/div/div/form/div[2]/button')
    except NoSuchElementException:
        # Si no se encuentra, intentar con el segundo XPath
        enter_password = driver.find_element(by=By.XPATH, value='//*[@id="root"]/div/div/div[2]/div[1]/div/div/div/div/div/div/div/form/div/div[2]/div/button')

    enter_password.click()
    time.sleep(10)
    # Aceptar cookies
    cookies = driver.find_element(by=By.ID, value='onetrust-accept-btn-handler') 
    cookies.click()