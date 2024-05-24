import json
import random
from application.models.properties_model import Properties
from application.core.aws.ses import send_email
from application.core.configuration_loader import get_configuration

def create_fake_property(fake, state):
    configuration = get_configuration()
    property_id = fake.uuid4()
    user_name = fake.name()
    property_pk = f"{user_name}#{property_id}"

    property= Properties(
        pk=property_pk,
        property_name =fake.company(),
        description= ' '.join(random.choices(state)),
        scores=json.dumps({"value for money": random.randint(1, 10), "staff": random.randint(1, 10), "facilities": random.randint(1, 10), "cleanliness": random.randint(1, 10), "comfort": random.randint(1, 10), "location": random.randint(1, 10)}),
        location=fake.address()
    )

    propiedad_dict = property.to_dict()

    try:
        property.save()
    except Exception as e:
        msg = "Error al guardar la reserva en la base de datos."
        send_email(msg, recipient=configuration.SES_EMAIL_SENDER, subject="Guardando reserva")
        print(msg + "\n")
    
    return propiedad_dict