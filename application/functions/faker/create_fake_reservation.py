import random
from datetime import datetime, timedelta
from application.models.reservations_model import Reservations
from application.core.aws.ses import send_email
from application.core.configuration_loader import get_configuration

MIN_DAYS_CHECKIN = 3
MAX_DAYS_CHECKIN = 4
MIN_DAYS_CHECKOUT = 1
MAX_DAYS_CHECKOUT = 3
MIN_BEDROOMS = 1
MAX_BEDROOMS = 5
MIN_PEOPLE = 1
MAX_PEOPLE = 10
MIN_PRICE = 50
MAX_PRICE = 500
LANGUAGES = ['en', 'es', 'fr', 'de', 'it']

def create_fake_reservation(fake, user_name, propiedad_id):
    configuration = get_configuration()
    reservation_id = fake.uuid4()
    client_name = fake.name()

    sk_date = datetime.now() + timedelta(days=random.randint(MIN_DAYS_CHECKIN, MAX_DAYS_CHECKIN)) # Fecha de check-in es la sort key de la tabla Reservations
    check_out_date = sk_date + timedelta(days=random.randint(MIN_DAYS_CHECKOUT, MAX_DAYS_CHECKOUT))

    reservation = Reservations(
        pk=f"{user_name}#{propiedad_id}#{reservation_id}",
        sk=sk_date.isoformat(),
        check_out_date=check_out_date.isoformat(),
        bedrooms_n=str(random.randint(MIN_BEDROOMS, MAX_BEDROOMS)),
        people_n=str(random.randint(MIN_PEOPLE, MAX_PEOPLE)),
        price=str(random.randint(MIN_PRICE, MAX_PRICE)),
        idiom=random.choice(LANGUAGES),
        client_name=client_name
    )

    reservation_dict = reservation.to_dict()

    try:
        reservation.save()
    except Exception as e:
        msg = "Error al guardar la reserva en la base de datos."
        send_email(msg, recipient=configuration.SES_EMAIL_SENDER, subject="Guardando reserva")
        print(msg + "\n")
    
    return reservation_dict
