try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import NoSuchElementException
    from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
    import time
    print("All Modules are ok ...")

except Exception as e:
    print("Error in Imports ")

def ini_driver():
    # Crear un objeto de opciones del controlador
    options = webdriver.ChromeOptions()

    # Establecer el User-Agent
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")

    # Establecer la ruta del binario del navegador (el ejecutable)
    options.binary_location = r"C:\Users\ascorredor\TFG\chrome-win64\chrome-win64\chrome.exe"

    # Inicializar el controlador con las opciones
    driver = webdriver.Chrome(options=options)

    return driver


def booking_page(driver):
    driver.get("https://www.booking.com/index.es.html")
    print(driver.title)

def search_location(location,driver):
    time.sleep(3)
    loc_search = driver.find_element(by=By.ID, value=':re:')
    loc_search.send_keys(location)
    time.sleep(2)
    # Hay dos búsquedas ya que el XPATH del botón de buscar a veces cambia, si es la primera vez que lo pulsas tiene un XPATH y si
    # después intentas seguir buscando, tiene otro XPATH
    
    # Intentar buscar el botón de búsqueda con el primer XPath
    try:
        search_button = driver.find_element(by=By.XPATH, value='//*[@id="indexsearch"]/div[2]/div/form/div[1]/div[4]/button')
    except NoSuchElementException:
        # Si no se encuentra, intentar con el segundo XPath
        search_button = driver.find_element(by=By.XPATH, value='//*[@id="bodyconstraint-inner"]/div[2]/div/div[1]/div/form/div[1]/div[4]/button')
        
    search_button.click()

    time.sleep(1)
    # Por si se quiere borrar el texto que aparece en la caja de búsqueda
    x_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="bodyconstraint-inner"]/div[2]/div/div[1]/div/form/div[1]/div[1]/div/div/div[1]/div/div/div[3]/span')))
    x_box.click()
    
    #login()
    #loc_search.send_keys(Keys.ENTER)



# Extraer la información de los pisos en una página ####################################################################################################
def extract_info_from_page(driver):
    apartments = driver.find_elements(By.XPATH, '//div[@data-testid="property-card"]')
    for apartment in apartments:
        name = apartment.find_element(By.XPATH, './/div[@data-testid="title"]').text.strip()
        try:
            score = apartment.find_element(By.CSS_SELECTOR, 'div[aria-label^="Puntuación"]')
            score = score.text.strip()
        except NoSuchElementException:
            score = "Nueva propiedad sin puntuación"
        print(f"Nombre: {name}\nPuntuacion: {score}")



# Método para obtener la última página de pisos disponible
def find_last_page_number(driver):
    page_buttons = WebDriverWait(driver, 10).until( EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'button.a83ed08757.a2028338ea')))

    page_numbers = []

    # Obtener el número de cada botón
    for button in page_buttons:
        page_number = button.get_attribute("aria-label").strip()
        if page_number.isdigit():  # Verificar que el atributo aria-label sea un número
            page_numbers.append(int(page_number))

    # Obtener el último número de la página
    last_page_number = max(page_numbers)

    print("La última página disponible es la:", last_page_number)
    return last_page_number


def get_apartments_paginated(driver):
    # Extraer información de los pisos en la página actual (página 1)
    print("Resultados de la página 1:")
    extract_info_from_page(driver) 

    last_page_number = find_last_page_number(driver)

    # Iterar sobre las páginas del 2 al 4
    for page in range(2, last_page_number + 1):

        # Scroll hacia abajo para que carguen los botones de cambiar de página
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Click en cambio de página
        next_page = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, f'//button[@aria-label=" {page}"]')))
        next_page.click()

        # Esperar a que se carguen los resultados de la página
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//div[@data-testid="property-card"]')))

        # Extraer información de los pisos en la página actual
        print(f"\nResultados de la página {page}:")
        extract_info_from_page(driver)



# Método para saber si estamos en el final de una página
def at_page_end(driver):
    # Obtener la posición vertical actual del usuario
    current_scroll_position = driver.execute_script("return window.pageYOffset;")
    
    # Obtener el tamaño total de la página
    total_page_height = driver.execute_script("return document.body.scrollHeight;")
    
    # Obtener la altura de la ventana
    window_height = driver.execute_script("return window.innerHeight;")
    
    # Si la posición vertical actual está cerca del final de la página
    # (por ejemplo, a una distancia menor o igual a la altura de la ventana)
    if total_page_height - current_scroll_position <= window_height:
        print("Se llegó al final de la página sin encontrar botón de Cargar más resultados")
        return True
    return False



def get_apartments_load_button(driver):
    while not at_page_end(driver): # Mientras que exista el botón de "Cargar más resultados" hacemos click en él, si estamos al final de la
        # página, significa que ya no hay más botón "Cargar más resultados"
        try:
            # Scroll hacia abajo
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Esperamos carga del contenido
            time.sleep(2)
            
            # Buscar el botón de "Cargar más resultados"
            load_more = driver.find_element(By.XPATH, '//button[contains(@class, "a83ed08757") and contains(@class, "c21c56c305") and contains(@class, "bf0537ecb5") and contains(@class, "f671049264") and contains(@class, "deab83296e") and contains(@class, "af7297d90d")]')
            load_more.click()

        except NoSuchElementException:
            pass  # Si no se encuentra el botón, continuar el scroll

        except ElementClickInterceptedException:
            # El elemento está interceptado, continuar el scroll
            pass

    
    # Vemos si existe botón de cambiar de página o botón de "Cargar más resultados"
def check_paginated_button(driver):
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label=" 2"]')))
        return True
    except TimeoutException:
        return False
    


def get_apartments(driver):
    if check_paginated_button():
        get_apartments_paginated(driver)
    else:
        get_apartments_load_button(driver)



def lambda_handler(event, context):
    driver = ini_driver()
    booking_page(driver)
    location = "Albacete"
    search_location(location,driver)
    get_apartments(driver)

def scraping_booking(event, context):
    pisos = obtener_pisos()

    dynamodb()

    # Pasar los datos de los pisos a ChatGPT
    respuesta_chatgpt = modelogpt(pisos)

    # Devolver la respuesta de ChatGPT
    return {
        'statusCode': 200,
        'body': respuesta_chatgpt
    }

def obtener_pisos():
    # Simular datos de pisos (esto podría ser reemplazado por consultas reales a la base de datos o cargas de datos de DynamoDB)
    return [{
        "nombre": "Piso1",
        "puntuacion": "8.5"
    },
    {
        "nombre": "Piso2",
        "puntuacion": "9.5"
    },
    {
        "nombre": "Piso3",
        "puntuacion": "9.0"
    }]


def modelogpt(pisos):





