from application.core.scheduler import SchedulerTasker
from application.core.aws.ses import send_email
#from selenium import webdriver
import os
#from selenium.webdriver.chrome.service import Service
import json


@SchedulerTasker.task('get_flats')
def get_flats(event, context): # Funcion que será para obtener los pisos de la extranet de booking
    print("Obteniendo los pisos")
    
    #ini_driver()
    #driver= ini_driver()
    #print(driver)
    #extranet_booking_page(driver)