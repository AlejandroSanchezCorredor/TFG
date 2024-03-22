import json
from application.core.configuration_loader import get_configuration
from application.core.http.http_error import HTTPError
import http.client

def verify_recaptcha_token(token):
    config = get_configuration()
    METHOD = 'POST'
    URL = f'{getattr(config, "RECAPTCHA_PATH")}?secret={getattr(config, "RECAPTCHA_SECRET_KEY")}&response={token}'

    conn = http.client.HTTPSConnection(f'{getattr(config, "RECAPTCHA_HOST")}', timeout=5.00)
    conn.request(method=METHOD, url=URL)
    response = conn.getresponse()

    response_body = json.loads(response.read().decode())
    if not response_body.get('success'):
        raise HTTPError(401, f'Recaptcha not verified')
