import re
import uuid
from application.core.configuration_loader import get_configuration

configuration = get_configuration()

# This mapping defines storage routes from an alias (client web: storage-settings)
STORAGE_SETTINGS = [
    {
        "id": "organization.profile.company_beneficial_owner_document",
        "bucket": configuration.S3_BUCKET_STORAGE,
        "path": "ORGANIZATIONS/{organization}/profile",
        "key": "company_beneficial_owner_document_#hash#.{extension}"
    },
    {
        "id": "organization.profile.senior_manager_corporation_document",
        "bucket": configuration.S3_BUCKET_STORAGE,
        "path": "ORGANIZATIONS/{organization}/profile",
        "key": "senior_manager_corporation_document_#hash#.{extension}"
    },
    {
        "id": "organization.profile.senior_manager_address_document",
        "bucket": configuration.S3_BUCKET_STORAGE,
        "path": "ORGANIZATIONS/{organization}/profile",
        "key": "senior_manager_address_document_#hash#.{extension}"
    },
    {
        "id": "organization.profile.company_administrator_corporation_document",
        "bucket": configuration.S3_BUCKET_STORAGE,
        "path": "ORGANIZATIONS/{organization}/profile",
        "key": "company_administrator_corporation_document_#hash#.{extension}"
    },
    {
        "id": "organization.profile.company_administrator_identity_document",
        "bucket": configuration.S3_BUCKET_STORAGE,
        "path": "ORGANIZATIONS/{organization}/profile",
        "key": "company_administrator_identity_document_#hash#.{extension}"
    },
    {
        "id": "organization.profile.company_administrator_address_document",
        "bucket": configuration.S3_BUCKET_STORAGE,
        "path": "ORGANIZATIONS/{organization}/profile",
        "key": "company_administrator_address_document_#hash#.{extension}"
    },
    {
        "id": "organization.profile.corporation_address_document",
        "bucket": configuration.S3_BUCKET_STORAGE,
        "path": "ORGANIZATIONS/{organization}/profile",
        "key": "corporation_address_document_#hash#.{extension}"
    },
    {
        "id": "organization.profile.corporation_registry_document",
        "bucket": configuration.S3_BUCKET_STORAGE,
        "path": "ORGANIZATIONS/{organization}/profile",
        "key": "corporation_registry_document_#hash#.{extension}"
    },
    {
        "id": "organization.profile.corporation_article_document",
        "bucket": configuration.S3_BUCKET_STORAGE,
        "path": "ORGANIZATIONS/{organization}/profile",
        "key": "corporation_article_document_#hash#.{extension}"
    },
    {
        "id": "organization.trades.trade_product_file",
        "bucket": configuration.S3_BUCKET_STORAGE,
        "path": "ORGANIZATIONS/{organization}/trades/{trade}",
        "key": "trade_product_file_#hash#.{extension}"
    },
    {
        "id": "organization.trades.trade_packaging_file",
        "bucket": configuration.S3_BUCKET_STORAGE,
        "path": "ORGANIZATIONS/{organization}/trades/{trade}",
        "key": "trade_packaging_file_#hash#.{extension}"
    },
    {
        "id": "organization.trades.trade_miscellaneous_file",
        "bucket": configuration.S3_BUCKET_STORAGE,
        "path": "ORGANIZATIONS/{organization}/trades/{trade}",
        "key": "trade_miscellaneous_file_#hash#.{extension}"
    },
    {
        "id": "organization.trades.contracts.contract_unsigned_document",
        "bucket": configuration.S3_BUCKET_STORAGE,
        "path": "ORGANIZATIONS/{organization}/trades/{trade}/contract",
        "key": "contract_unsigned_document_#hash#.{extension}"
    },
    {
        "id": "organization.trades.contracts.contract_signature_document",
        "bucket": configuration.S3_BUCKET_STORAGE,
        "path": "ORGANIZATIONS/{organization}/trades/{trade}/contract",
        "key": "contract_signature_document_#hash#.{extension}"
    },
    {
        "id": "organization.trades.contracts.contract_signed_document",
        "bucket": configuration.S3_BUCKET_STORAGE,
        "path": "ORGANIZATIONS/{organization}/trades/{trade}/contract",
        "key": "contract_signed_document_#hash#.{extension}"
    }
]


def get_storage_location(alias, params):

    _storage_location = next((location for location in STORAGE_SETTINGS if location.get("id") == alias), None)

    if _storage_location:
        # Clean params
        for key in params:
            params.update({key: re.sub(r"[^a-z0-9_]", "", re.sub(r" ", "_", params.get(key).lower()))})

        # Set hash param
        _storage_location.update({"key": _storage_location.get("key").replace("#hash#", _generate_hash())})

        # Set collection params
        _storage_location.update({"path": _storage_location.get("path").format(**params)})

        return _storage_location

    return None


def _generate_hash():
    return uuid.uuid4().hex[:-15]