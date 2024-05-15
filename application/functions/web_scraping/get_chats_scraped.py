import time
import uuid
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from application.core.scheduler import SchedulerTasker
from application.models.chats_model import Chats
from application.models.reservations_model import Reservations
from application.models.properties_model import Properties
from application.functions.web_scraping.login_booking import extranet_booking_page, extranet_booking_login
from application.functions.web_scraping.ini_driver import ini_driver
from application.services.gpt_service import get_gpt_response
from application.core.configuration_loader import get_configuration
from application.core.aws.ses import send_email


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


def get_messages(driver):
    messages = []
    messages_element = driver.find_elements(By.XPATH , '//div[contains(@class, "conversation-message")]')

    for message in messages_element: # Recorremos los mensajes de cada conversación
        # Compramos si el mensaje lo envía el propietario (partner) o el cliente (guest)
        if "conversation-message--from-guest" in message.get_attribute("class"):
            author = "guest"
        elif "conversation-message--from-partner" in message.get_attribute("class"):
            author = "partner"
        else:
            # Si el mensaje no es ni del propieatario ni del cliente, lo ignoramos
            continue
        
        try:
            content = message.find_element(By.XPATH, ".//p[@dir='ltr']").text
        except NoSuchElementException:
            # Si no se encuentra el contenido, continúa con el siguiente mensaje
            print("No se ha encontrado el boton de más mensajes")
            continue
        
        # Almacenamos el autor y el contenido del mensaje en la lista
        messages.append({"author": author, "content": content})
        return messages
    
def get_conversations(driver, property_id, user_name, configuration):
    # Obtenemos todos los mensajes sin leer
    unread_messages = driver.find_elements(By.XPATH, '//li[contains(@class, "messages-list-li") and not(contains(@class, "messages-list-item--selected"))]')
    current_window = driver.current_window_handle

    for i, message_element in enumerate(unread_messages): # Iteramos sobre cada conversación
        message_element.click()
        time.sleep(5)

        client_name_element = message_element.find_element(By.XPATH, './/div[@class="messages-list-item__guest-name"]')
        client_name = client_name_element.text.strip()
  
        conversation_date_element = message_element.find_element(By.XPATH, './/div[@class="messages-list-item__timestamp bui-f-font-caption bui-f-color-grayscale"]')
        conversation_date = conversation_date_element.text.strip()

        reservation_id_element = driver.find_element(By.XPATH, '//div[contains(@class, "reservation-details__item-title") and span[contains(text(), "Booking reference number:")]]/following-sibling::div[@class="reservation-details__item-content"]')
        reservation_id = reservation_id_element.text.strip()

        conversation_id = property_id + "#" + reservation_id + "#" + str(uuid.uuid4()) 

        check_in_date_element = driver.find_element(By.XPATH, '//div[@class="reservation-details__item-title bui-f-font-caption"]/span[text()="Arrival:"]/parent::div/following-sibling::div[@class="reservation-details__item-content"]')
        check_in_date = check_in_date_element.text.strip()
        check_in_date = datetime.strptime(check_in_date, "%a, %b %d, %Y").strftime("%b %d, %Y") 

        messages = get_messages(driver)

        property_query = Properties.query(property_id)
        property = []
        for result in property_query:
            property.append(result.to_dict())
        print("Propiedad obtenida de la base de datos", property)

        reservation_query = Reservations.query(
            property_id + "#" + reservation_id,
            Reservations.sk == check_in_date 
        )
        print("Buscando por pk", property_id + "#" + reservation_id)
        print("Buscando por sk", check_in_date)
        
        reservation = []
        for result in reservation_query:
            reservation.append(result.to_dict())

        if not reservation: # Existen casos en que hay una conversación para una reserva futura que aún no está almacenada en la base de datos, en estos casos, obtenemos la reserva
            print(f"La reserva del cliente {client_name} no ha sido almacenada en la base de datos. Obteniendo la reserva...")
            view_reservation_details = driver.find_element(By.XPATH, "//a[contains(@class,'reservation-details__link') and contains(@class,'bui-link--primary') and contains(@target,'_blank')]")
            view_reservation_details.click()
            time.sleep(5)

            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(3)
            
            check_out_date, bedrooms_n, people_n, price, idiom, client_name  = show_full_reservation(driver, current_window)

            new_reservation = Reservations(
                pk=property_id + "#" + reservation_id,
                sk=check_in_date,  
                check_out_date= check_out_date,
                bedrooms_n=bedrooms_n,
                people_n=people_n,
                price=price, 
                idiom=idiom,
                client_name=client_name,
            )
            new_reservation.save()

            print("Reserva guardada en la base de datos", new_reservation)
            reservation.append(new_reservation.to_dict())

        print("Reserva obtenida de la base de datos", reservation)

        # Combinamos todos los datos en un solo diccionario
        context = {
            "mensajes": messages,
            "property": property,
            "reservation": reservation
        }

        gpt_answer= get_gpt_response(context)
        print("Chat GPT ha respondido\n" +gpt_answer)

        messages.append({"author": "partner", "content": gpt_answer})

        # Verificar si hay más mensajes
        more_messages_button = None
        try:
            more_messages_button = driver.find_element(By.XPATH, '//li[contains(@class, "bui-list__item") and .//button[contains(@class, "bui-link--primary")]]')
        except NoSuchElementException:
            pass
        
        if more_messages_button:
            more_messages_button.click()
            time.sleep(5)

        mfa_element = driver.find_elements(By.XPATH, '//h1[contains(text(), "Verify your identity")]')
        mfa = driver.find_elements(By.XPATH, "//a[contains(@class, 'icon-nav-list__item') and contains(@class, 'nw-sms-verification-link')]")
        if mfa_element or mfa:
            print("Ha saltado el MFA")
            msg = "Ha saltado el MFA"
            send_email(msg, recipient=configuration.SES_EMAIL_SENDER, subject="Resultado de la prueba")
            time.sleep(30) 
            #get_chats_MFA(driver, user_name, id_apartamento)

        else:
            message = Chats(
                pk=conversation_id, 
                sk=conversation_date, 
                sender=user_name,
                receiver=client_name,
                response=messages
            )
            message.save()
        
    # Volvemos a la ventana principal
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(5)




@SchedulerTasker.task('get_chats_scraped')
def get_chats_scraped(event, context):
    configuration = get_configuration()

    driver = ini_driver()

    extranet_booking_page(driver)
    time.sleep(2)

    user = extranet_booking_login(driver)
    time.sleep(5)

    more_properties = driver.find_element(By.XPATH, "//button[@aria-controls='property-selector']")
    more_properties.click()
    time.sleep(2)
    all_properties = driver.find_elements(By.CSS_SELECTOR, "a.property-selector-list-item")
    time.sleep(2)

    for i, propiedad in enumerate(all_properties):
        id_element = driver.find_element(By.CLASS_NAME, "property-selector-dropdown__property-id").text.strip()
        id_apartamento = user + "#" + id_element
        time.sleep(2)
        
        driver.execute_script("window.scrollBy(0, 1800);")
        time.sleep(3)

        try:
            no_unanswered_messages = driver.find_element(By.XPATH, "//p[@class='bui-empty-state__text']/span") # Comprobamos si no hay mensajes sin responder
            msg = "No hay mensajes sin responder para el apartamento " + id_apartamento
            send_email(msg, recipient=configuration.SES_EMAIL_SENDER, subject="Resultado de la prueba")

        except NoSuchElementException:
            view_all_messages = driver.find_element(By.XPATH, "//a[@class='homepage-messages-button-cta bui-button bui-button--secondary']")
            view_all_messages.click()
            time.sleep(10)
            # Cambiar al nuevo controlador de ventana
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(2)
            mfa_element = driver.find_elements(By.XPATH, '//h1[contains(text(), "Verify your identity")]')
            mfa = driver.find_elements(By.XPATH, "//a[contains(@class, 'icon-nav-list__item') and contains(@class, 'nw-sms-verification-link')]")
            if mfa_element or mfa:
                print("Ha saltado el MFA BUENO")
                msg = "Ha saltado el MFA"
                send_email(msg, recipient=configuration.SES_EMAIL_SENDER, subject="Resultado de la prueba")
                time.sleep(30) 
                #get_chats_MFA(driver, user, id_apartamento)

            time.sleep(5)
            
            try: # A veces sale una ventana emergente tipo tutorial
                # Si se encuentra un botón Next, es el del tutorial
                next_button = driver.find_element(By.XPATH, '//button[@type="button" and @class="bui-button bui-button--primary"]/span[@class="bui-button__text" and contains(normalize-space(text()), "Next")]')
                # Click en la pantalla para saltar tutorial
                actions = ActionChains(driver)
                actions.move_by_offset(1, 100) 
                actions.click()
                actions.perform()
                #next_button.click()
            except NoSuchElementException:
                try:
                    close_button = driver.find_element(By.XPATH, '//button[@type="button" and @class="bui-modal__close"]')
                    close_button.click()
                except NoSuchElementException:
                    pass

            get_conversations(driver, id_apartamento, user, configuration)

