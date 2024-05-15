import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException
from application.core.scheduler import SchedulerTasker
from application.models.reservations_model import Reservations
from application.functions.web_scraping.login_booking import extranet_booking_page, extranet_booking_login
from application.functions.web_scraping.ini_driver import ini_driver
from application.core.aws.ses import send_email
from application.core.configuration_loader import get_configuration

def extract_reservation_info(driver):
    checkout_date_element = driver.find_element(By.XPATH, "//p[@class='res-content__label' and span='Check-out']/following-sibling::p[@class='res-content__info res-content__info--emphasized']/span")
    checkout_date = checkout_date_element.text
    check_out_date = datetime.strptime(checkout_date, "%a, %b %d, %Y").strftime("%b %d, %Y")
    print(check_out_date)

    bedrooms_element = driver.find_element(By.XPATH, "//p[@class='res-content__label' and span='Total rooms']/following-sibling::p[@class='res-content__info']")
    bedrooms_n = bedrooms_element.text.strip()
    print(bedrooms_n)

    people_n_element = driver.find_element(By.XPATH, "//p[@class='res-content__label' and span='Total guests:']/following-sibling::p[@class='res-content__info']")
    people_n = people_n_element.text.strip()
    print(people_n)

    total_price_element = driver.find_element(By.XPATH, "//p[@class='res-content__label' and span='Total price']/following-sibling::p[@class='res-content__info res-content__info--emphasized']")
    total_price = total_price_element.find_element(By.TAG_NAME, "span").text.strip()
    print(total_price)

    idiom_element = driver.find_element(By.XPATH, "//span[@class='bui-flag__text']")
    idiom = idiom_element.text.strip()
    print(idiom)

    client_name_element = driver.find_element(By.XPATH, "//span[@data-test-id='reservation-overview-name']")
    client_name = client_name_element.text.strip()
    print(client_name)

    return check_out_date, bedrooms_n, people_n, total_price, idiom, client_name


def show_full_reservation(driver, reservation_number_element, current_window):
    reservation_number_element.click()
    time.sleep(5)
    driver.switch_to.window(driver.window_handles[-1])
    try:
        return extract_reservation_info(driver)
    except NoSuchElementException:
        print("Ha saltado el MFA")
        time.sleep(35)
        return extract_reservation_info(driver)
    finally:
        time.sleep(2)
        driver.switch_to.window(current_window)


@SchedulerTasker.task('get_reservations_scraped')
def get_reservations_scraped(event, context):
    configuration = get_configuration()

    driver = ini_driver()

    extranet_booking_page(driver)
    time.sleep(2)

    user = extranet_booking_login(driver)
    time.sleep(5)

    try:    
        more_properties = driver.find_element(By.XPATH, "//button[@aria-controls='property-selector']")
        more_properties.click()
        time.sleep(2)
        all_properties = driver.find_elements(By.CSS_SELECTOR, "a.property-selector-list-item")
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
                time.sleep(5)

            property_id = driver.find_element(By.CLASS_NAME, "property-selector-dropdown__property-id").text.strip()
            print(property_id)
            property_id = user + "#" + property_id

            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(3)

            try:
                no_arrivals_message = driver.find_element(By.XPATH, "//p[@class='bui-empty-state__text']/span") # Comprobamos si no hay reservas
                print("No hay reservas en este apartamento:", property_id)
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(2)
                driver.execute_script("window.scrollTo(0, 0);") # En la parte superior de la página será donde encontramos todas las propiedades
                time.sleep(2)

            except NoSuchElementException:
                view_all_reservations = driver.find_element(By.XPATH, "//a[@class='bui-button bui-button--secondary homepage-activity-tab__view-all']")
                view_all_reservations.click()
                time.sleep(5)
                driver.switch_to.window(driver.window_handles[-1])

                while True: # Obtenemos todas las reservas de la propiedad en la que nos encontremos
                    time.sleep(3)
            
                    reservation_rows = driver.find_elements(By.XPATH, '//*[@id="main-content"]/div/div[2]/table/tbody/tr')
                    time.sleep(3)
                    for i, row in enumerate(reservation_rows): # Iteramos sobre cada reserva
                        time.sleep(5)
                        xpath_reservation_number = f'//*[@id="main-content"]/div/div[2]/table/tbody/tr[{i+1}]/td[8]/a'
                        reservation_number_element = driver.find_element(By.XPATH, xpath_reservation_number)
                        reservation_number = reservation_number_element.text.strip()
                        id_reservation = property_id + "#" + reservation_number

                        xpath_check_in_date = f'//*[@id="main-content"]/div/div[2]/table/tbody/tr[{i+1}]/td[@data-heading="Check-in"]/span'
                        check_in_date_element = driver.find_element(By.XPATH, xpath_check_in_date)
                        check_in_date = check_in_date_element.text.strip()
                        print(id_reservation)
                        print(check_in_date)

                        current_window = driver.current_window_handle # Guardamos la página principales donde están todas las reservas

                        # Entramos a los detalles de la reserva en la que nos encontramos
                        check_out_date, bedrooms_n, people_n, price, idiom, client_name  = show_full_reservation(driver,reservation_number_element,current_window)

                        reservation = Reservations(
                            pk=id_reservation,
                            sk=check_in_date,  # Usamos fecha de check-in como sk
                            check_out_date= check_out_date,
                            bedrooms_n=bedrooms_n,
                            people_n=people_n,
                            price=price, 
                            idiom=idiom,
                            client_name=client_name,
                        )
                        reservation.save()
                        msg = "Se ha obtenido la reserva: " + str(id_reservation)
                        send_email(msg, recipient=configuration.SES_EMAIL_SENDER, subject="Obtención de reservas")

                        driver.execute_script("window.scrollBy(0, 300);")

                    # Boton de Next para ver mas reservas
                    next_button = driver.find_element(By.XPATH, "//li[@data-test-id='pagination-next-link-li']")
                    if "bui-pagination__item--disabled" not in next_button.get_attribute("class"):
                        next_button.click()
                        time.sleep(5)  
                        print("Cargando mas reservas para la propiedad:", property_id)
                    else:
                        print("No hay mas reservas para la propiedad:", property_id)
                        break
                    
                driver.switch_to.window(driver.window_handles[0])
                driver.execute_script("window.scrollBy(0, 1800);")
                time.sleep(3)

    except NoSuchElementException:
        print("Ha saltado el MFA")
