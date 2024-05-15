from selenium import webdriver
import time
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from application.core.configuration_loader import get_configuration
import boto3


def extranet_booking_page(driver):
    driver.get(r"https://account.booking.com/sign-in?op_token=EgVvYXV0aCJHChQ2Wjcyb0hPZDM2Tm43emszcGlyaBIJYXV0aG9yaXplGhpodHRwczovL2FkbWluLmJvb2tpbmcuY29tLyoCe31CBGNvZGUqEjCXqamk1vEmOgBCAFi36MCvBg")
    print(driver.title)

def extranet_booking_login(driver):
    configuration = get_configuration()
    print("Configuración obtenida")
    try:
        time.sleep(5)
        try:
            cookies = driver.find_element(by=By.ID, value='onetrust-accept-btn-handler') 
            cookies.click() # Aceptar cookies
            time.sleep(3)
        except NoSuchElementException:
            pass
        
        except ElementNotInteractableException:
            pass
        
        user = configuration.BOOKING_EXTRANET_USER
        print(user)
        email = driver.find_element(by=By.ID, value='loginname') 
        email.send_keys(user)
        time.sleep(5)
        try:
            enter_email = driver.find_element(by=By.XPATH, value='//*[@id="root"]/div/div/div[2]/div[1]/div/div/div/div/div/div/div/form/div[2]/div[2]/button')
        except NoSuchElementException:
            enter_email = driver.find_element(by=By.XPATH, value='//*[@id="root"]/div/div/div/div[2]/div[1]/div/div/div/div/div/div/form/div[3]/button')

        enter_email.click() # Introducimos el email
        time.sleep(3)
        password_element = driver.find_element(by=By.ID, value='password') 
        password = configuration.BOOKING_EXTRANET_PASSWORD
        print(password)
        password_element.send_keys(password)
        time.sleep(4)
        try:
            enter_password = driver.find_element(by=By.XPATH, value='//*[@id="root"]/div/div/div/div[2]/div[1]/div/div/div/div/div/div/form/div[2]/button')
        except NoSuchElementException:
            enter_password = driver.find_element(by=By.XPATH, value='//*[@id="root"]/div/div/div[2]/div[1]/div/div/div/div/div/div/div/form/div/div[2]/div/button')

        enter_password.click() # Introducimos la contraseña
        time.sleep(10)

        cookies = driver.find_element(by=By.ID, value='onetrust-accept-btn-handler') 
        cookies.click()

    except ElementNotInteractableException:
        print("Ha saltado el MFA")
        
        '''
        screenshot_path = '/tmp/screenshot.png'

        driver.save_screenshot(screenshot_path)
        s3 = boto3.client('s3')
        with open(screenshot_path, 'rb') as data:
            s3.upload_fileobj(data, 'prueba-capturas', 'screenshot.png')
        '''

        time.sleep(35)
        cookies = driver.find_element(by=By.ID, value='onetrust-accept-btn-handler') 
        cookies.click()
        time.sleep(6)
    return user
