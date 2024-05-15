import random
from faker import Faker
from application.core.scheduler import SchedulerTasker
from application.core.aws.ses import send_email
from application.functions.faker.create_fake_reservation import create_fake_reservation
from application.models.properties_model import Properties
from application.core.configuration_loader import get_configuration

fake = Faker('es_ES')

@SchedulerTasker.task('get_reservations')
def get_reservations(event, context): 
    configuration = get_configuration()
    print("Obteniendo las reservas")
    
    if random.random() < 0.6:
        try:
            properties = list(Properties.scan())
        except Exception as e:
            msg = "No existen propiedades para asignar a la reserva."
            send_email(msg, recipient=configuration.SES_EMAIL_SENDER, subject="Creación de reserva")
            return None
        
        property = random.choice(properties)
        user_name, property_id = property.pk.split("#")
        print("Creando una nueva reserva")
        reservation= create_fake_reservation(fake, user_name, property_id)
        msg = "Se ha creado una nueva reserva: " + str(reservation)
        send_email(msg, recipient=configuration.SES_EMAIL_SENDER, subject="Obtención de reservas")
    else:
        msg = "No existen nuevas reservas"
        send_email(msg, recipient=configuration.SES_EMAIL_SENDER, subject="Obtención de reservas")


    

