from selenium import webdriver
from tempfile import mkdtemp

def ini_driver():
    options = webdriver.ChromeOptions()  # Para poder incluir opciones personalizadas en nuestro navegador
    service = webdriver.ChromeService("/opt/chromedriver")  # Definimos el servicio de ChromeDriver

    # Opciones para evitar la detección como bot
    options.binary_location = '/opt/chrome/chrome'  # Definimos la ubicación del binario de Chrome
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")  # Establecemos el user-agent del navegador
    options.add_argument("--disable-notifications")  # Desactivamos las notificaciones
    options.add_experimental_option("excludeSwitches", ["enable-automation"])  # Excluimos la opción de automatización
    options.add_experimental_option("useAutomationExtension", False)  # Desactivamos la extensión de automatización
    options.add_argument("--disable-blink-features=AutomationControlled")  # Desactivamos las características de Blink relacionadas con la automatización
    options.add_argument("--hide-scrollbars")  # Ocultamos las barras de desplazamiento
    options.add_argument("--disable-infobars")  # Desactivamos las barras de información
    options.add_argument("--start-maximized")  # Iniciamos el navegador con pantalla completa

    # Opciones para poder ejecutar el driver en Lambda
    options.add_argument("--headless=new")  # Iniciamos el navegador en modo headless
    options.add_argument('--no-sandbox')  # Desactivamos el modo sandbox
    options.add_argument("--disable-gpu")  # Desactivamos el uso de la GPU
    options.add_argument("--single-process")  # Forzamos al navegador a usar un solo proceso
    options.add_argument("--disable-dev-shm-usage")  # Desactivamos el uso de /dev/shm
    options.add_argument("--disable-dev-tools")  # Desactivamos las herramientas de desarrollador
    options.add_argument("--no-zygote")  # Desactivamos el proceso zygote de Chrome
    options.add_argument(f"--user-data-dir={mkdtemp()}")  # Establecemos el directorio de datos del usuario
    options.add_argument(f"--data-path={mkdtemp()}")  # Establecemos la ruta de los datos
    options.add_argument(f"--disk-cache-dir={mkdtemp()}")  # Establecemos el directorio de la caché del disco

    # Opciones para evitar la detección como bot
    options.add_argument("--disable-extensions")  # Desactivamos las extensiones
    options.add_argument("--disable-web-security")  # Desactivamos la seguridad web
    options.add_argument("--no-proxy-server")  # Desactivamos el servidor proxy
    options.add_argument("--enable-precise-memory-info")  # Habilitamos la información precisa de la memoria
    options.add_argument("--ignore-certificate-errors")  # Ignoramos los errores de certificado
    options.add_argument("--disable-popup-blocking")  # Desactivamos el bloqueo de popups

    chrome = webdriver.Chrome(options=options, service=service)  # Inicializa el driver de Chrome con las opciones y el servicio definidos

    return chrome  # Devuelve el driver de Chrome