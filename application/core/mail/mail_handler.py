from datetime import datetime
from application.core.configuration_loader import get_configuration

DEFAULT_LANGUAGE = 'en-EN'
DEFAULT_TEMPLATE_PATH = 'application/core/mail/templates'

TRADES_MARKET_PATH = 'trades/market'
LIVE_CONTRACTS_PATH = 'contracts'
UNSUBSCRIBE_PATH = 'email-unsubscribe'

def mail_environment(func):
    config = get_configuration()

    ENVIRONMENT_TOOLBAR = {
        'production': '',
        'preproduction': open(f'{DEFAULT_TEMPLATE_PATH}/snipets/email_toolbar_environment.html').read(),
        'develop': open(f'{DEFAULT_TEMPLATE_PATH}/snipets/email_toolbar_environment.html').read()
    }

    def wrapper(*args, **kwargs):
        _message, _subject = func(*args, **kwargs)
        if _message:
            _toolbar = ENVIRONMENT_TOOLBAR.get(config.AWS_STAGE, "")
            _toolbar = _toolbar.replace('#ENVIRONMENT#', config.AWS_STAGE)

            _message = _message.replace('#ENVIRONMENT#', f'{_toolbar}')
            _message = _message.replace('#CLOUDFRONT_DOMAIN#', config.CLOUDFRONT_DOMAIN)
        return _message, _subject
    return wrapper


@mail_environment
def get_cognito_invitation_email(username, user_name, admin_name, code, language=DEFAULT_LANGUAGE):

    TEMPLATE = f'{DEFAULT_TEMPLATE_PATH}/cognito_invitation_email.html'
    SUBJECT = 'Welcome to Digital Commodity Exchange'

    message = open(TEMPLATE).read()

    message = message.replace('#COGNITO_USER_NAME#', user_name)
    message = message.replace('#COGNITO_ADMIN_NAME#', admin_name)
    message = message.replace('#COGNITO_USERNAME#', username)
    message = message.replace('#COGNITO_PASSWORD_CODE#', code)

    return message, SUBJECT


@mail_environment
def get_cognito_confirmation_email(username, email, code, language=DEFAULT_LANGUAGE):
    """Get message and subject email
    notification for cognito user
    confirmation operation

    :param username: string
    :param email: string
    :param code: string
    :param language: string
    :return: the string (message as HTML), string (subject)
    """

    config = get_configuration()

    # TODO: prepared to work with different languages {var: language} to select respective template
    URL_CONFIRMATION = f'{config.CLOUDFRONT_DOMAIN}/auth/confirmation?username={username}&confirmation_code={code}'
    TEMPLATE = f'{DEFAULT_TEMPLATE_PATH}/cognito_confirmation_email.html'
    SUBJECT = 'Activate your account on Digital Commodity Exchange'

    message = open(TEMPLATE).read()

    message = message.replace('#COGNITO_USER_EMAIL#', email)
    message = message.replace('#COGNITO_CONFIRMATION_CODE#', code)
    message = message.replace('#COGNITO_URL_CALLBACK#', URL_CONFIRMATION)

    return message, SUBJECT


@mail_environment
def get_cognito_forgot_email(username, email, code, language=DEFAULT_LANGUAGE):
    """Get message and subject email
    notification for cognito user
    forgot operation

    :param username: string
    :param email: string
    :param code: string
    :param language: string
    :return: the string (message as HTML), string (subject)
    """

    config = get_configuration()

    # TODO: prepared to work with different languages {var: language} to select respective template
    URL_CONFIRMATION = f'{config.CLOUDFRONT_DOMAIN}/auth/forgot?username={username}&confirmation_code={code}'
    TEMPLATE = f'{DEFAULT_TEMPLATE_PATH}/cognito_forgot_email.html'
    SUBJECT = 'Recover your Account'

    message = open(TEMPLATE).read()

    message = message.replace('#COGNITO_USER_EMAIL#', email)
    message = message.replace('#COGNITO_CONFIRMATION_CODE#', code)
    message = message.replace('#COGNITO_URL_CALLBACK#', URL_CONFIRMATION)

    return message, SUBJECT


@mail_environment
def get_company_revision_email(email, status, language=DEFAULT_LANGUAGE):
    """Get message and subject email
    notification for application ROI
    operation logic

    :param email: string
    :param status: string
    :param language: string
    :return: the string (message as HTML), string (subject)
    """

    # TODO: prepared to work with different languages {var: language} to select respective template
    # TODO: Template for duplicated status company ¿?
    TEMPLATE_OPTIONS = {
        'confirmed': f'{DEFAULT_TEMPLATE_PATH}/company_revision_confirmed_email.html',
        # 'rejected': f'{DEFAULT_TEMPLATE_PATH}/company_revision_rejected_email.html',
        'rejected': None,
        'duplicated': None,
    }

    SUBJECT_OPTIONS = {
        'confirmed': 'Complete company registration on Digital Commodity Exchange',
        # 'rejected': 'Your application to join Digital Commodity Exchange',
        'rejected': None,
        'duplicated': None,
    }

    TEMPLATE = TEMPLATE_OPTIONS.get(status, None)
    SUBJECT = SUBJECT_OPTIONS.get(status, None)
    message = None

    if TEMPLATE:
        message = open(TEMPLATE).read()

        message = message.replace('#USER_EMAIL#', email)

    return message, SUBJECT


@mail_environment
def get_organization_revision_email(status, first_name=None, comment=None, language=DEFAULT_LANGUAGE):
    """Get message and subject email
    notification for application CR
    operation logic

    :param status: string
    :param first_name: string
    :param comment: string
    :param language: string
    :return: the string (message as HTML), string (subject)
    """

    # TODO: prepared to work with different languages {var: language} to select respective template
    # TODO: Template for review status company ¿?
    TEMPLATE_OPTIONS = {
        'draft': f'{DEFAULT_TEMPLATE_PATH}/organization_revision_draft_email.html',
        'approved': f'{DEFAULT_TEMPLATE_PATH}/organization_revision_approved_email.html',
        'rejected': f'{DEFAULT_TEMPLATE_PATH}/organization_revision_rejected_email.html',
        'review': None,
    }

    SUBJECT_OPTIONS = {
        'draft': 'Your company registration has been placed in draft status.',
        'approved': 'Your company registration has been approved- start trading now',
        'rejected': 'Your application to join Digital Commodity Exchange',
        'review': None,
    }

    TEMPLATE = TEMPLATE_OPTIONS.get(status, None)
    SUBJECT = SUBJECT_OPTIONS.get(status, None)
    message = None

    if TEMPLATE:
        message = open(TEMPLATE).read()

        message = message.replace('#FIRST_NAME#', first_name if first_name else '')
        message = message.replace('#COMMENT#', comment if comment else '')

    return message, SUBJECT


@mail_environment
def get_contact_confirmation_email(first_name, last_name, id, code, language=DEFAULT_LANGUAGE):
    """Get message and subject email
    notification for contact user
    confirmation operation

    :param first_name: string
    :param last_name: string
    :param email: string
    :param code: string
    :param language: string
    :return: the string (message as HTML), string (subject)
    """

    config = get_configuration()

    # TODO: prepared to work with different languages {var: language} to select respective template
    URL_CONFIRMATION = f'{config.CLOUDFRONT_DOMAIN}/contact/confirmation?id={id}&confirmation_code={code}'
    TEMPLATE = f'{DEFAULT_TEMPLATE_PATH}/contact_confirmation_email.html'
    SUBJECT = 'Confirm your email address'

    message = open(TEMPLATE).read()

    message = message.replace('#CONTACT_FIRST_NAME#', first_name)
    message = message.replace('#CONTACT_LAST_NAME#', last_name)
    message = message.replace('#CONTACT_VERIFICATION_CODE#', code)
    message = message.replace('#CONTACT_URL_CALLBACK#', URL_CONFIRMATION)

    return message, SUBJECT

@mail_environment
def get_trade_email(status, first_name=None, comment=None, trade_reference=None, is_counter=False, contract_id=None, language=DEFAULT_LANGUAGE, to_origin_trade_owner=False):
    """Get message and subject email
    notification for trade
    operation action

    :param first_name: string
    :param comment: string
    :param trade_reference: string
    :param is_counter: boolean
    :param language: string
    :return: the string (message as HTML), string (subject)
    """

    TEMPLATE_OPTIONS = {
        'draft': None,
        'reviewed': None,
        'submitted': f'{DEFAULT_TEMPLATE_PATH}/trade_submitted_email.html',
        'accepted': f'{DEFAULT_TEMPLATE_PATH}/trade_accepted_email.html',
        'canceled': None,
        'expired': f'{DEFAULT_TEMPLATE_PATH}/trade_expired_email.html',
    }

    SUBJECT_OPTIONS = {
        'draft': None,
        'reviewed': None,
        'submitted': f'You have {"received" if to_origin_trade_owner else "submitted"} a new Counter Trade Request' if is_counter else 'You have submitted a new Trade Request',
        'accepted': 'You have accepted a new Counter Trade Request' if is_counter else 'You have accepted a new Trade Request',
        'canceled': None,
        'expired': 'Your Counter Trade has expired' if is_counter else 'Your Trade has expired',
    }

    # Mail subheader
    TRADE_SUBHEADER_OPTIONS = {
        'draft': None,
        'reviewed': None,
        'submitted': f'{"A" if to_origin_trade_owner else "Your"} counter Trade Request has been submitted' if is_counter else 'Your trade request has been submitted',
        'accepted': 'Your counter Trade Request has been accepted' if is_counter else 'Your trade request has been accepted',
        'canceled': None,
        'expired': 'Your Counter Trade has expired' if is_counter else 'Your Trade has expired',
    }

    TEMPLATE = TEMPLATE_OPTIONS.get(status, None)
    SUBJECT = SUBJECT_OPTIONS.get(status, None)
    TRADE_SUBHEADER = TRADE_SUBHEADER_OPTIONS.get(status, None)

    message = None
    if TEMPLATE:
        message = open(TEMPLATE).read()

        message = message.replace('#FIRST_NAME#', first_name if first_name else '')
        message = message.replace('#TRADE_SUBHEADER#', TRADE_SUBHEADER if TRADE_SUBHEADER else '')
        message = message.replace('#COMMENT#', comment if comment else '')

        # This is useful for Trade with status submitted template only
        # Whenever a Trade or Counter is submitted, a button should appear in the trade_submitted_email.html template that links to the original trade
        if status == 'submitted':
            message = message.replace('#TRADES_MARKET_PATH#', TRADES_MARKET_PATH if TRADES_MARKET_PATH else '')
            message = message.replace('#TRADE_REFERENCE#', trade_reference if trade_reference else '')

        if status == 'accepted':
            message = message.replace('#LIVE_CONTRACTS_PATH#', LIVE_CONTRACTS_PATH if LIVE_CONTRACTS_PATH else '')
            message = message.replace('#CONTRACT_ID#', contract_id if contract_id else '')

    return message, SUBJECT

@mail_environment
def get_contracts_documents_new_email(company_name, contract_number, language=DEFAULT_LANGUAGE):
    """Get message and subject email
    notification for new live contract document

    :param first_name: string
    :param comment: string
    :param trade_reference: string
    :param language: string
    :return: the string (message as HTML), string (subject)
    """


    # TODO: prepared to work with different languages {var: language} to select respective template
    TEMPLATE = f'{DEFAULT_TEMPLATE_PATH}/contracts_documents_new_email.html'
    SUBJECT = 'New document uploaded to your live contract'

    message = open(TEMPLATE).read()

    message = message.replace('#SRC_USER_COMPANY_NAME#', company_name)
    message = message.replace('#CONTRACT_NUMBER#', contract_number)
    message = message.replace('#LIVE_CONTRACTS_PATH#', LIVE_CONTRACTS_PATH)

    return message, SUBJECT

@mail_environment
def get_daily_summary_email(user, new_trades_table, expiring_trades_table, language=DEFAULT_LANGUAGE):
    """Get message and subject email
    notification for daily summary

    :param trades_table: string
    :param language: string
    :return: the string (message as HTML), string (subject)
    """

    TEMPLATE = f'{DEFAULT_TEMPLATE_PATH}/trades_daily_summary.html'
    SUBJECT = f'TFG_BOOKING Daily Trades Summary {datetime.utcnow().strftime("%Y-%m-%d")}'

    new_trades_title = 'Last submitted Trades:' if new_trades_table else ''
    expiring_trades_title = 'Next expiring Trades:' if expiring_trades_table else ''

    message = open(TEMPLATE).read()

    message = message.replace('#FIRST_NAME#', user.first_name)
    message = message.replace('#DATE#', datetime.utcnow().strftime("%Y-%m-%d"))
    message = message.replace('#NEW_TRADES_TITLE#', new_trades_title)
    message = message.replace('#NEW_TRADES_TABLE#', new_trades_table or '')
    message = message.replace('#EXPIRING_TRADES_TITLE#', expiring_trades_title)
    message = message.replace('#EXPIRING_TRADES_TABLE#', expiring_trades_table or '')
    message = message.replace('#UNSUBSCRIBE_PATH#', UNSUBSCRIBE_PATH)
    message = message.replace('#SUBSCRIPTION_REFERENCE#', user.subscription_reference)
    message = message.replace('#YEAR#', str(datetime.now().year))

    return message, SUBJECT


@mail_environment
def set_converted_users_summary_email(users, content, language=DEFAULT_LANGUAGE):
    """Sets the message and subject email
    notification for the summary of converted users in zoho

    :param users: Users(class)
    :param content: string
    :return string (message as HTML), string (subject)
    """

    TEMPLATE = f'{DEFAULT_TEMPLATE_PATH}/zoho_converted_users_email.html'
    SUBJECT = f'{datetime.utcnow().strftime("%Y-%m-%d")} - ZOHO Sync ({len(users)} contacts)'

    message = open(TEMPLATE).read()

    message = message.replace('#CONVERTED_USERS#', content)

    return message, SUBJECT