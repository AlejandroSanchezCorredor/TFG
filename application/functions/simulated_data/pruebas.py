import os
import time
from tempfile import mkdtemp
import boto3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from application.core.scheduler import SchedulerTasker
from application.functions.web_scraping.ini_driver import ini_driver
from application.functions.web_scraping.login_booking import extranet_booking_login
from application.functions.web_scraping.login_booking import extranet_booking_page


@SchedulerTasker.task('prueba')
def miprueba(event, context): # Función con la que se obtendrán las reservas de la extranet de booking

    # Captura la salida de print en una variable
    output = ""
    output += "Prueba Scheduler\n"
    #today = datetime.datetime.now()
    #output += f"Hora actual: {today.strftime('%H:%M:%S')}"

    #send_email(output, recipient="alech.maria@hotmail.com", subject="Resultado de la prueba")

    driver= ini_driver()
    print(driver)
    extranet_booking_page(driver)
    extranet_booking_login(driver)
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


