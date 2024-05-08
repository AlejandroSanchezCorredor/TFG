from application.core.scheduler import SchedulerTasker
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
#from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from tempfile import mkdtemp
import boto3

#@SchedulerTasker.task('prueba')
def miprueba(event, context): # Función con la que se obtendrán las reservas de la extranet de booking

    # Captura la salida de print en una variable
    output = ""
    output += "Prueba Scheduler\n"
    #today = datetime.datetime.now()
    #output += f"Hora actual: {today.strftime('%H:%M:%S')}"

    #send_email(output, recipient="alech.maria@hotmail.com", subject="Resultado de la prueba")

    ini_driver()
    driver= ini_driver()
    print(driver)
    extranet_booking_page(driver)
    login(driver)
    time.sleep(5)

    # Define the absolute path for the screenshot in the /tmp directory
    screenshot_path = '/tmp/screenshot.png'

    driver.save_screenshot(screenshot_path)
    s3 = boto3.client('s3')
    with open(screenshot_path, 'rb') as data:
        s3.upload_fileobj(data, 'prueba-capturas', 'screenshot.png')

    # Encontrar el elemento span por su XPath
    xpath = "//span[@class='bui-text bui-text--variant-body_2 bui-text--color-neutral' and normalize-space()='Apartamentos Albacete']"
    element = driver.find_element(by=By.XPATH, value=xpath)

    # Obtener el texto del elemento
    texto = element.text.strip()

    return{
        'statusCode': 200,
        'body': texto
    }



def ini_driver():
    options = webdriver.ChromeOptions()
    service = webdriver.ChromeService("/opt/chromedriver")

    options.binary_location = '/opt/chrome/chrome'
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")
    options.add_argument("--disable-notifications")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--hide-scrollbars")
    options.add_argument("--disable-infobars")
    options.add_argument("--start-maximized")

    options.add_argument("--headless=new")
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")
    #options.add_argument("--window-size=1280x1696")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--no-zygote")
    options.add_argument(f"--user-data-dir={mkdtemp()}")
    options.add_argument(f"--data-path={mkdtemp()}")
    options.add_argument(f"--disk-cache-dir={mkdtemp()}")
    #options.add_argument("--remote-debugging-port=9222")

    chrome = webdriver.Chrome(options=options, service=service)

    return chrome


def extranet_booking_page(driver):
    driver.get(r"https://account.booking.com/sign-in?op_token=EgVvYXV0aCJHChQ2Wjcyb0hPZDM2Tm43emszcGlyaBIJYXV0aG9yaXplGhpodHRwczovL2FkbWluLmJvb2tpbmcuY29tLyoCe31CBGNvZGUqEjCXqamk1vEmOgBCAFi36MCvBg")
    print(driver.title)


def login(driver):
    time.sleep(5)

    # Aceptar cookies
    try:
        cookies = driver.find_element(by=By.ID, value='onetrust-accept-btn-handler') 
        cookies.click()
        print("Cookies aceptadas 1")
        time.sleep(3)
    except NoSuchElementException:
        pass
    
    except ElementNotInteractableException:
        pass

    email = driver.find_element(by=By.ID, value='loginname') 
    email.send_keys("frcantos@gmail.com")
    time.sleep(4)
    
     # Intentar encontrar el botón con el primer XPath
    try:
        enter_email = driver.find_element(by=By.XPATH, value='//*[@id="root"]/div/div/div[2]/div[1]/div/div/div/div/div/div/div/form/div[2]/div[2]/button')
    except NoSuchElementException:
        # Si no se encuentra, intentar con el segundo XPath
        enter_email = driver.find_element(by=By.XPATH, value='//*[@id="root"]/div/div/div/div[2]/div[1]/div/div/div/div/div/div/form/div[3]/button')

    enter_email.click()
    print("Email introducido")
    time.sleep(4)
    password = driver.find_element(by=By.ID, value='password') 
    password.send_keys("49.PE:m4DqmeCL/")
    time.sleep(4)

    # Intentar encontrar el botón con el primer XPath
    try:
        enter_password = driver.find_element(by=By.XPATH, value='//*[@id="root"]/div/div/div/div[2]/div[1]/div/div/div/div/div/div/form/div[2]/button')
    except NoSuchElementException:
        # Si no se encuentra, intentar con el segundo XPath
        enter_password = driver.find_element(by=By.XPATH, value='//*[@id="root"]/div/div/div[2]/div[1]/div/div/div/div/div/div/div/form/div/div[2]/div/button')

    enter_password.click()
    print("Contraseña introducida")
    time.sleep(10)

    # Aceptar cookies
    try:
        cookies = driver.find_element(by=By.ID, value='onetrust-accept-btn-handler') 
        cookies.click()
        print("Cookies aceptadas 2")
        time.sleep(3)
    except NoSuchElementException:
        pass
    
    except ElementNotInteractableException:
        pass
