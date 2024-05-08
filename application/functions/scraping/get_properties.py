from application.core.scheduler import SchedulerTasker
from application.core.aws.ses import send_email
#from selenium import webdriver
import os
#from selenium.webdriver.chrome.service import Service
import json

# Parte de datos simulados
from faker import Faker
import random
from application.models.properties_model import Properties


fake = Faker('es_ES')
state = [
    "Open/Bookable",
    "Closed/Not bookable",
]

@SchedulerTasker.task('get_properties')
def get_properties(event, context): # Funcion que será para obtener los pisos de la extranet de booking
    print("Obteniendo los pisos")


    # Generar datos de propiedad simulados
    propiedad_id = fake.uuid4()
    user_name = fake.name()
    propiedad_pk = f"{user_name}#{propiedad_id}"

    propiedad= Properties(
        pk=propiedad_pk,
        property_name=fake.company(),
        description= ' '.join(random.choices(state)),
        scores=json.dumps({"value for money": random.randint(1, 10), "staff": random.randint(1, 10), "facilities": random.randint(1, 10), "cleanliness": random.randint(1, 10), "comfort": random.randint(1, 10), "location": random.randint(1, 10)}),
        location=fake.address()

    )

    propiedad_dict = propiedad.to_dict()

    propiedad.save()

    print("Propiedad guardada:", propiedad_dict)

    #ini_driver()
    #driver= ini_driver()
    #print(driver)
    #extranet_booking_page(driver)