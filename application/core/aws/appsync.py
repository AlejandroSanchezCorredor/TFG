import json
from gql import gql
from gql.client import Client
from gql.transport.requests import RequestsHTTPTransport
from boto3 import Session as AWSSession
from requests_aws4auth import AWS4Auth
from application.core.configuration_loader import get_configuration


def make_client():
    configuration = get_configuration()

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    session = AWSSession()
    credentials = session.get_credentials().get_frozen_credentials()

    auth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        configuration.AWS_REGION,
        'appsync',
        session_token=credentials.token
    )

    transport = RequestsHTTPTransport(url=configuration.APPSYNC_ENDPOINT, headers=headers, auth=auth)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    return client


def execute_operation(operation, params):
    client = make_client()

    # TODO: Control response
    response = client.execute(gql(operation), params)
    print(response)
