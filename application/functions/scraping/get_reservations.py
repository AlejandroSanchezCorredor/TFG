from application.core.scheduler import SchedulerTasker
from datetime import datetime, timedelta
from application.core.aws.ses import send_email
from faker import Faker

fake = Faker('es_ES')
from application.models.reservations_model import Reservations
from application.models.properties_model import Properties
import random

@SchedulerTasker.task('get_reservations')
def get_reservations(event, context): # Función con la que se obtendrán las reservas de la extranet de booking
    print("Obteniendo las reservas")
    #print("Prueba Scheduler")
    #today = datetime.datetime.now()
    #print("Hora actual:", today.strftime("%H:%M:%S"))

    # Captura la salida de print en una variable
    #output = ""
    #output += "Prueba Scheduler\n"
    #today = datetime.datetime.now()
    #output += f"Hora actual: {today.strftime('%H:%M:%S')}"

    #send_email(output, recipient="alech.maria@hotmail.com", subject="Resultado de la prueba")

    # Generar datos de reserva simulados
    
    reserva_id = fake.uuid4()
    client_name = fake.name()

    # Escanea todas las propiedades y las pone en una lista
    propiedades = list(Properties.scan())

    # Verifica si la lista está vacía
    if not propiedades:
        print("No existen propiedades para asignar a la reserva.")

    # Selecciona una propiedad al azar
    propiedad = random.choice(propiedades)

    # Usa la pk de la propiedad para crear la pk de la reserva
    user_name, propiedad_id = propiedad.pk.split("#")

    # Genera una fecha de reserva (sk) que esté dentro de 3 a 4 días
    sk_date = datetime.now() + timedelta(days=random.randint(3, 4))

    # Genera una fecha de salida (check_out_date) que esté dentro de 1 a 3 días después de la fecha de reserva
    check_out_date = sk_date + timedelta(days=random.randint(1, 3))

    reserva = Reservations(
        pk=f"{user_name}#{propiedad_id}#{reserva_id}",
        sk=sk_date.isoformat(),
        check_out_date=check_out_date.isoformat(),
        bedrooms_n=str(random.randint(1, 5)),
        people_n=str(random.randint(1, 10)),
        price=str(random.randint(50, 500)),
        idiom='en',
        client_name=client_name
    )

    reserva_dict = reserva.to_dict()

    reserva.save()

    print("Reserva guardada:", reserva_dict)

    

