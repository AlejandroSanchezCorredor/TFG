from application.core.scheduler import SchedulerTasker
from application.core.aws.ses import send_email
from application.functions.faker.create_fake_property import create_fake_property
from faker import Faker
import random

fake = Faker('es_ES')
state = [
    "Open/Bookable",
    "Closed/Not bookable",
]

@SchedulerTasker.task('get_properties')
def get_properties(event, context):
    print("Obteniendo las propiedades...")

    if random.random() < 0.6:
        print("Creando una nueva propiedad...")
        property= create_fake_property(fake, state)
        msg = "Se ha creado una nueva propiedad: " + str(property)
        send_email(msg, recipient="alech.maria@hotmail.com", subject="Obtención de propiedades")
    else:
        msg = "No se ha obtenido ninguna propiedad nueva"
        send_email(msg, recipient="alech.maria@hotmail.com", subject="Obtención de propiedades")