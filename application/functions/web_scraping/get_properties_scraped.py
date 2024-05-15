import json
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotInteractableException
from application.core.scheduler import SchedulerTasker
from application.models.properties_model import Properties
from application.functions.web_scraping.login_booking import extranet_booking_page, extranet_booking_login
from application.functions.web_scraping.ini_driver import ini_driver
from application.core.aws.ses import send_email
from application.core.configuration_loader import get_configuration

def get_all_scores(driver):
    # Cambiamos a la nueva ventana abierta
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(5)

    # Hacemos click en las puntuaciones
    #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    driver.execute_script("window.scrollBy(0, 1000);")
    all_reviews = driver.find_element(By.XPATH, '//span[text()="View all reviews"]')  
    driver.execute_script("arguments[0].scrollIntoView();", all_reviews)
    all_reviews.click()
    time.sleep(5)

    driver.switch_to.window(driver.window_handles[-1])
    driver.execute_script("window.scrollBy(0, 300);")
    time.sleep(4)

    # Obtenemos las puntuaciones completas
    show_more_puntuaciones = driver.find_element(By.XPATH, '//*[@id="main-content"]/div/div[3]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[2]/div/button/span')
    show_more_puntuaciones.click()
    time.sleep(4)

    attributes = ["Facilities", "Staff", "Location", "Comfort", "Cleanliness", "Value for money"]  # Lista de atributos a buscar
    scores = {}
    for attribute in attributes:
        elemento_puntuacion = driver.find_element(By.XPATH, f'//div[@class="bui-score-bar__header"]/h2/span[text()="{attribute}"]/../../span[@class="bui-score-bar__score"]')
        puntuacion = elemento_puntuacion.text
        # Guarda la puntuación en el diccionario bajo el nombre del atributo
        scores[attribute.lower()] = puntuacion

    time.sleep(2)
    driver.back()
    
    time.sleep(1)
    driver.execute_script("window.scrollTo(0, 0);") # Subimos al principio de la página, donde están las demás propiedades a seleccionar

    return scores


def get_location(driver,current_window):
    show_location = driver.find_element(By.XPATH, "//a[@class='ext-header__property-preview bui-link bui-link--primary']")
    show_location.click()
    driver.switch_to.window(driver.window_handles[-1]) # Cambiamos a la nueva ventana abierta
    time.sleep(5)

    location_element = driver.find_element(By.CSS_SELECTOR, "span.hp_address_subtitle")
    location = location_element.text.strip()
    time.sleep(1)

    # Vuelve a la ventana original
    driver.switch_to.window(current_window)
    time.sleep(2)
    
    driver.execute_script("window.scrollBy(0, 0);") # Subimos al principio de la página, donde están las demás propiedades a seleccionar

    return location


def get_name_state(driver):
    element = driver.find_element(By.CSS_SELECTOR, "h1.bui-page-header__title") # Encuentra el elemento que contiene el nombre de la propiedad
    name = driver.execute_script("return arguments[0].firstChild.textContent.trim();", element) # Obtiene el nombre 
    spans = element.find_elements(By.CSS_SELECTOR, "span") # Encuentra todos los elementos <span> para obtener el estado de la propiedad
    state = spans[-1].text.strip() if spans else "" # Obtiene el estado de la propiedad si está disponible
    
    return name, state

@SchedulerTasker.task('get_properties_scraped')
def get_properties_scraped(event, context):
    configuration = get_configuration()
    print("Configuración obtenida")

    driver = ini_driver()

    extranet_booking_page(driver)
    time.sleep(2)

    user = extranet_booking_login(driver)
    time.sleep(5)

    more_properties = driver.find_element(By.XPATH, "//button[@aria-controls='property-selector']") # Botón para mostrar más propiedades
    more_properties.click()
    time.sleep(2)
    all_properties = driver.find_elements(By.CSS_SELECTOR, "a.property-selector-list-item") # Obtenemos la lista de propiedades
    time.sleep(2)

    for i, propiedad in enumerate(all_properties):
        
        if i != 0: # Si no es la primera propiedad, hacemos clic en las siguientes
            try:
                propiedad.click()
            except ElementNotInteractableException:
                more_properties = driver.find_element(By.XPATH, "//button[@aria-controls='property-selector']")
                more_properties.click()
                propiedad.click()
            time.sleep(5)
            driver.switch_to.window(driver.window_handles[-1])
            
        current_window = driver.current_window_handle # Guardamos la ventana principal de cada propiedad para después volver a ella

        property_id = driver.find_element(By.CLASS_NAME, "property-selector-dropdown__property-id").text.strip()
        property_id = user + "#" + property_id

        property_name, property_state = get_name_state(driver)
        scores = get_all_scores(driver)
        scores_str = json.dumps(scores)
        location = get_location(driver,current_window)

        property = Properties(
            pk=property_id,
            property_name=property_name,
            description=property_state,
            scores=scores_str,
            location=location
        )
        property.save()
    
        msg = "Se ha obtenido la propiedad: " + str(property_id)
        send_email(msg, recipient=configuration.SES_EMAIL_SENDER, subject="Obtención de propiedades")

        driver.switch_to.window(driver.window_handles[0]) # Cambiamos a la ventana principal
        driver.execute_script("window.scrollBy(0, 0);") # Subimos al principio de la página, donde están las demás propiedades a seleccionar
        time.sleep(3)