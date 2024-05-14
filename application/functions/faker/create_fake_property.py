import json
import random
from application.models.properties_model import Properties

def create_fake_property(fake, state):
    property_id = fake.uuid4()
    user_name = fake.name()
    property_pk = f"{user_name}#{property_id}"

    propiedad= Properties(
        pk=property_pk,
        property_name=fake.company(),
        description= ' '.join(random.choices(state)),
        scores=json.dumps({"value for money": random.randint(1, 10), "staff": random.randint(1, 10), "facilities": random.randint(1, 10), "cleanliness": random.randint(1, 10), "comfort": random.randint(1, 10), "location": random.randint(1, 10)}),
        location=fake.address()
    )

    propiedad_dict = propiedad.to_dict()
    propiedad.save()
    
    print("Propiedad almacenada en la base de datos:", propiedad_dict)
    return propiedad_dict