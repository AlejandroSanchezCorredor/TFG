import os, json
from application.core.configuration_loader import get_configuration
from application.models.users_model import Permissions, Modules, Roles, RolesModulesPermissions, UsersResourcesJobs
from application.models.companies_model import CompaniesLevels, CompaniesResourcesServices, CompaniesResourcesTypes, \
    CompaniesProfileSections
from application.models.resources_model import Regions, Subregions, Countries, Ports, Commodities, TemplatesFiles
from application.models.portfolio_model import PortfolioServices, PortfolioProducts, PortfolioProductsCategories, \
    PortfolioProductsSubcategories, PortfolioProductsPackaging
from application.core.sql.defaults.sql_layer import SQLLayer
from application.core.sql import db_get_or_create

RESOURCES_PATH = os.path.abspath("../../../application_resources/db_datasource")


@SQLLayer()
def insert_regions():
    print('REGIONS')

    # [REGIONS] Static default info
    regions = [
        {'name': 'Africa'},
        {'name': 'Americas'},
        {'name': 'Asia'},
        {'name': 'Europe'},
        {'name': 'Oceania'},
        {'name': 'Polar'}
    ]

    for index, region in enumerate(regions):
        _, _flag = db_get_or_create(Regions, **region)
        print(f'[{index + 1}/{len(regions)}] Existing: {not _flag} \n> {region}')


@SQLLayer()
def insert_subregions():
    print('SUBREGIONS')

    # [SUBREGIONS] Static default info
    subregions = [
        {"name": "Australia and New Zealand", "region": "Oceania"},
        {"name": "Caribbean", "region": "Americas"},
        {"name": "Central America", "region": "Americas"},
        {"name": "Central Asia", "region": "Asia"},
        {"name": "Eastern Africa", "region": "Africa"},
        {"name": "Eastern Asia", "region": "Asia"},
        {"name": "Eastern Europe", "region": "Europe"},
        {"name": "Melanesia", "region": "Oceania"},
        {"name": "Micronesia", "region": "Oceania"},
        {"name": "Middle Africa", "region": "Africa"},
        {"name": "Northern Africa", "region": "Africa"},
        {"name": "Northern America", "region": "Americas"},
        {"name": "Northern Europe", "region": "Europe"},
        {"name": "Polynesia", "region": "Oceania"},
        {"name": "South America", "region": "Americas"},
        {"name": "South-Eastern Asia", "region": "Asia"},
        {"name": "Southern Africa", "region": "Africa"},
        {"name": "Southern Asia", "region": "Asia"},
        {"name": "Southern Europe", "region": "Europe"},
        {"name": "Western Africa", "region": "Africa"},
        {"name": "Western Asia", "region": "Asia"},
        {"name": "Western Europe", "region": "Europe"},
        {"name": "Polar", "region": "Polar"}
    ]

    for index, subregion in enumerate(subregions):
        _, _flag = db_get_or_create(Subregions, **subregion)
        print(f'[{index + 1}/{len(subregions)}] Existing: {not _flag} \n> {subregion}')


@SQLLayer()
def insert_countries():
    # [COUNTRIES] Static default info
    # > DATASOURCE: https://raw.githubusercontent.com/annexare/Countries/master/dist/countries.min.json)
    COUNTRIES_FILE = 'countries_ALL.json'

    with open(f'{RESOURCES_PATH}/{COUNTRIES_FILE}') as json_file:
        data = json.load(json_file)
        for index, item in enumerate(data['countries']):
            print(f'[{index + 1}/{len(data["countries"])}] Country: {item.get("name", None)}')
            db_get_or_create(Countries, **item)


@SQLLayer()
def insert_ports():
    # [PORTS] Static default info
    # > DATASOURCE: https://www.npmjs.com/package/rx-sea-ports
    PORTS_FILE = 'ports_ALL.json'

    with open(f'{RESOURCES_PATH}/{PORTS_FILE}') as json_file:
        data = json.load(json_file)
        for index, item in enumerate(data['ports']):
            print(f'[{index + 1}/{len(data["ports"])}] Port: {item.get("code", None)}')
            db_get_or_create(Ports, **item)


@SQLLayer()
def insert_permissions():

    print('PERMISSIONS')

    # [PERMISSIONS] Static default info
    permissions = [
        {'code': 'GET', 'description': 'Consult information'},
        {'code': 'UPDATE', 'description': 'Update information'},
        {'code': 'INSERT', 'description': 'Insert information'},
        {'code': 'DELETE', 'description': 'Delete information'}
    ]

    for index, permission in enumerate(permissions):
        _, _flag = db_get_or_create(Permissions, **permission)
        print(f'[{index + 1}/{len(permissions)}] Existing: {not _flag} \n> {permission}')


@SQLLayer()
def insert_modules():

    print('MODULES')

    # [MODULES] Static default info
    modules = [
        # COMPANY MODULES
        {'name': 'dashboard', 'code': 'module_dashboard', 'path': '/dashboard', 'description': 'Dashboard view', 'is_active': True},
        {'name': 'platform_tour', 'code': 'module_platform_tour', 'path': '/platform-tour', 'description': 'Platform tour view', 'is_active': True},
        {'name': 'market_insights', 'code': 'module_market_insights', 'path': '/market-insights', 'description': 'Market insights view', 'is_active': True},
        {'name': 'market_participants', 'code': 'module_market_participants', 'path': '/market-participants', 'description': 'Market participants view', 'is_active': True},
        {'name': 'trades_management', 'code': 'module_trades_management', 'path': '/trades/management', 'description': 'Trades management company view', 'is_active': True},
        {'name': 'trades_request', 'code': 'module_trades_request', 'path': '/trades/request', 'description': 'Trades request company view', 'is_active': True},
        {'name': 'trades_market', 'code': 'module_trades_market', 'path': '/trades/market', 'description': 'Trades market company view', 'is_active': True},
        {'name': 'unfilled_trades', 'code': 'module_unfilled_trades', 'path': '/trades/unfilled', 'description': 'Unfilled trades market view', 'is_active': True},
        {'name': 'deals_request', 'code': 'module_deals_request', 'path': '/deals/request', 'description': 'Deals request company view', 'is_active': True},
        {'name': 'contracts', 'code': 'module_contracts', 'path': '/contracts', 'description': 'Contracts view', 'is_active': True},
        {'name': 'chats', 'code': 'module_chats', 'path': '/chats', 'description': 'Chats view', 'is_active': True},


        # ADMIN MODULES
        {'name': 'admin_register', 'code': 'module_admin_register', 'path': '/admin/register-management', 'description': 'Admin register view', 'is_active': True},
        {'name': 'admin_organization', 'code': 'module_admin_organization', 'path': '/admin/organization-management', 'description': 'Admin organization view', 'is_active': True},
        {'name': 'admin_configuration', 'code': 'module_admin_configuration', 'path': '/admin/configuration-management', 'description': 'Admin configuration view', 'is_active': True},
        {'name': 'admin_company_groups', 'code': 'module_admin_company_groups', 'path': '/admin/company-groups-management', 'description': 'Admin company groups view', 'is_active': True},
        {'name': 'admin_work', 'code': 'module_admin_work', 'path': '/admin/work-management', 'description': 'Admin work view', 'is_active': True},
        {'name': 'admin_access', 'code': 'module_admin_access', 'path': '/admin/access-management', 'description': 'Admin access view', 'is_active': True},
        {'name': 'admin_user', 'code': 'module_admin_user', 'path': '/admin/user-management', 'description': 'Admin user view', 'is_active': True},
        {'name': 'mass_emails', 'code': 'module_mass_emails', 'path': '/admin/mass-emails', 'description': 'Mass emails view', 'is_active': True},
        {'name': 'admin_product_defaults', 'code': 'module_admin_product_defaults', 'path': '/admin/product_defaults', 'description': 'Default trades admin', 'is_active': True},
        {'name': 'admin_trade_volume', 'code': 'module_admin_trade_volume', 'path': '/admin/trade_volume', 'description': 'Trade Volume admin', 'is_active': True},

        # ORGANIZATION MODULES
        {'name': 'organization_company', 'code': 'module_organization_company', 'path': '/organization/company-management', 'description': 'Organization company view', 'is_active': True},
        {'name': 'organization_employees', 'code': 'module_organization_employees', 'path': '/organization/employees-management', 'description': 'Organization employees view', 'is_active': True},
        {'name': 'public_profile', 'code': 'module_public_profile', 'path': '/organization/public-profile', 'description': 'Public profile view', 'is_active': True},


        # OTHER (TODO: Delete)
        {'name': 'widgets', 'code': 'module_widgets', 'path': '/widgets', 'description': 'Widgets view', 'is_active': True},
    ]

    for index, module in enumerate(modules):
        _, _flag = db_get_or_create(Modules, **module)
        print(f'[{index + 1}/{len(modules)}] Existing: {not _flag} \n> {module}')


@SQLLayer()
def insert_roles():

    print('ROLES')

    # [ROLES] Static default info
    roles = [
        {
            'definition': {'name': 'system_administrator', 'description': 'System administrator'},
            'actions': ['GET', 'UPDATE', 'INSERT', 'DELETE'],
            'modules': [
                # COMPANY ACCESS (TODO: Review)
                'module_dashboard', 'module_market_insights', 'module_market_participants', 'module_organization_company', 'module_organization_employees', 'module_public_profile',
                'module_trades_management', 'module_trades_request', 'module_trades_market', 'module_unfilled_trades', 'module_contracts', 'module_chats', 'module_deals_request',
                # ADMIN ACCESS
                'module_admin_register', 'module_admin_organization', 'module_admin_configuration', 'module_admin_access', 'module_admin_work', 'module_admin_user',
                'module_mass_emails', 'module_admin_product_defaults', 'module_admin_trade_volume',
                # OTHER
                'module_widgets'
            ]
        },
        {
            'definition': {'name': 'platform_admin', 'description': 'Platform Admin'},
            'actions': ['GET', 'UPDATE', 'INSERT', 'DELETE'],
            'modules': [
                'module_dashboard', 'module_market_insights', 'module_market_participants', 'module_organization_company', 'module_organization_employees',
                'module_public_profile', 'module_trades_management', 'module_trades_request', 'module_trades_market', 'module_unfilled_trades', 'module_contracts', 'module_chats', 'module_deals_request',
                'module_admin_register', 'module_admin_organization', 'module_admin_configuration', 'module_admin_access', 'module_admin_user', 'module_admin_product_defaults', 'module_admin_trade_volume',
            ]
        },
        {
            'definition': {'name': 'company_guest', 'description': 'Company guest'},
            'actions': ['GET'],
            'modules': ['module_dashboard']
        },
        {
            'definition': {'name': 'company_administrator', 'description': 'Company administrator'},
            'actions': ['GET', 'UPDATE', 'INSERT', 'DELETE'],
            'modules': ['module_dashboard', 'module_market_participants', 'module_market_insights', 'module_organization_company',
                        'module_organization_employees', 'module_public_profile', 'module_trades_management', 'module_trades_request', 'module_trades_market', 'module_unfilled_trades', 'module_contracts', 'module_chats']
        },
        {
            'definition': {'name': 'company_employee', 'description': 'Company employee'},
            'actions': ['GET', 'UPDATE', 'INSERT', 'DELETE'],
            'modules': ['module_dashboard', 'module_market_participants', 'module_market_insights',
                        'module_trades_management', 'module_trades_request', 'module_trades_market', 'module_unfilled_trades', 'module_contracts', 'module_chats']
        },
        {
            'definition': {'name': 'company_migration', 'description': 'Company migration'},
            'actions': ['GET', 'UPDATE', 'INSERT', 'DELETE'],
            'modules': ['module_dashboard', 'module_market_insights', 'module_market_participants',
                        'module_organization_employees', 'module_public_profile', 'module_trades_management', 'module_trades_request', 'module_trades_market', 'module_unfilled_trades', 'module_contracts', 'module_chats']
        },
        {
            'definition': {'name': 'company_host', 'description': 'Company host'},
            'actions': ['GET'],
            'modules': ['module_dashboard', 'module_organization_company', 'module_trades_management', 'module_trades_request', 'module_trades_market', 'module_unfilled_trades','module_contracts','module_market_insights', 'module_market_participants', 'module_organization_company', 'module_public_profile']
        }
    ]

    roles_modules_permissions = RolesModulesPermissions.query.filter().delete()
    permissions = Permissions.query.filter().all()
    modules = Modules.query.filter().all()

    for index, role in enumerate(roles):
        _role, _flag = db_get_or_create(Roles, **role['definition'])

        print(f'[{index + 1}/{len(roles)}] Existing: {not _flag} \n> {role["definition"]}')
        for module in modules:
            if module.code in role['modules']:
                for permission in permissions:
                    if permission.code in role['actions']:
                        _action = {'role_id': _role.id, 'module_id': module.id, 'permission_id': permission.id}
                        db_get_or_create(RolesModulesPermissions, **_action)
                        print(f'>> [ACCESS] ({permission.code}) => {module.name}')


@SQLLayer()
def insert_commodities():

    print('COMMODITIES')

    # [COMMODITIES] Static default info
    commodities = [
        {'name': 'Global', 'threshold': 20000},
        {'name': 'Barley', 'threshold': 0},
        {'name': 'Cocoa', 'threshold': 0},
        {'name': 'Coffee', 'threshold': 0},
        {'name': 'Corn', 'threshold': 0},
        {'name': 'Cotton', 'threshold': 0},
        {'name': 'Fertilizers', 'threshold': 0},
        {'name': 'Oats', 'threshold': 0},
        {'name': 'Wood/pulp/paper', 'threshold': 0},
        {'name': 'Pulses', 'threshold': 20000},
        {'name': 'Rapeseed', 'threshold': 0},
        {'name': 'Rice', 'threshold': 0},
        {'name': 'Soybean', 'threshold': 0},
        {'name': 'Sugar', 'threshold': 0},
        {'name': 'Wheat', 'threshold': 0},
        {'name': 'Oilseeds', 'threshold': 0}
    ]

    for index, commodity in enumerate(commodities):
        _, _flag = db_get_or_create(Commodities, **commodity)
        print(f'[{index + 1}/{len(commodities)}] Existing: {not _flag} \n> {commodity}')


@SQLLayer()
def insert_users_resources_jobs():

    print('USERS JOBS')

    # [JOBS] Static default info
    jobs = [
        {'name': 'Admin Coordinator'},
        {'name': 'Assistant Director'},
        {'name': 'CEO'},
        {'name': 'Chairman Of The Board Of Directors'},
        {'name': 'Commercial Director'},
        {'name': 'Controller'},
        {'name': 'CFO'},
        {'name': 'COO'},
        {'name': 'Deputy Managing Director'},
        {'name': 'Executive Director'},
        {'name': 'Export Coordinator'},
        {'name': 'Export Director'},
        {'name': 'Export Manager'},
        {'name': 'General Manager'},
        {'name': 'International Department Manager'},
        {'name': 'Management Consultant'},
        {'name': 'Managing Director'},
        {'name': 'Marketing Manager'},
        {'name': 'Office Manager'},
        {'name': 'Operations Director'},
        {'name': 'Owner'},
        {'name': 'Partner'},
        {'name': 'Product Manager'},
        {'name': 'Purchasing Director'},
        {'name': 'Purchasing Manager'},
        {'name': 'Sales Director'},
        {'name': 'Sales Manager'},
        {'name': 'Partner'},
        {'name': 'Trader'}
    ]

    for index, job in enumerate(jobs):
        _, _flag = db_get_or_create(UsersResourcesJobs, **job)
        print(f'[{index + 1}/{len(jobs)}] Existing: {not _flag} \n> {job}')


@SQLLayer()
def insert_companies_levels():

    print('COMPANIES LEVELS')

    # [COMPANIES LEVELS] Static default info
    levels = [
        {'name': 'Company Level 1', 'tag': 'Small company'},
        {'name': 'Company Level 2', 'tag': 'Medium company'},
        {'name': 'Company Level 3', 'tag': 'Large company'}
    ]

    for index, level in enumerate(levels):
        _, _flag = db_get_or_create(CompaniesLevels, **level)
        print(f'[{index + 1}/{len(level)}] Existing: {not _flag} \n> {level}')


@SQLLayer()
def insert_companies_resources_services():

    print('COMPANIES SERVICES')

    # [COMPANIES TYPES] Static default info
    services = [
        {'name': 'Cargo Inspection'},
        {'name': 'Insurance'},
        {'name': 'Land Freight Service'},
        {'name': 'Sea Freight Service'},
        {'name': 'Trade Finance'}
    ]

    for index, service in enumerate(services):
        _, _flag = db_get_or_create(CompaniesResourcesServices, **service)
        print(f'[{index + 1}/{len(service)}] Existing: {not _flag} \n> {service}')


@SQLLayer()
def insert_companies_resources_types():

    print('COMPANIES TYPES')

    # [COMPANIES TYPES] Static default info
    types = [
        {'name': 'Broker'},
        {'name': 'Exporter'},
        {'name': 'Importer'},
        {'name': 'International Distributor'},
        {'name': 'International Trading Company'},
        {'name': 'Local Distributor'},
        {'name': 'Service Provider - Inspection'},
        {'name': 'Service Provider - Insurance'},
        {'name': 'Service Provider - Shipping'},
        {'name': 'Service Provider - Trade Finance'},
    ]

    for index, type in enumerate(types):
        _, _flag = db_get_or_create(CompaniesResourcesTypes, **type)
        print(f'[{index + 1}/{len(types)}] Existing: {not _flag} \n> {type}')


@SQLLayer()
def insert_companies_profile_sections():

    print('COMPANIES PROFILE SECTIONS')

    # [COMPANIES PROFILE  SECTIONS] Static default info
    sections = [
        {'company_level_ids': [1, 2, 3], 'name': 'Company Details', 'tag': 'section_company_details', 'is_required': False},
        {'company_level_ids': [1, 2, 3], 'name': 'Beneficial Owner', 'tag': 'section_beneficial_owner', 'is_required': False},
        {'company_level_ids': [2, 3],    'name': 'Authorised Signatory', 'tag': 'section_authorisation_signatory', 'is_required': False},
        {'company_level_ids': [2, 3],    'name': 'Authorised Administrator', 'tag': 'section_authorisation_administrator', 'is_required': True},
        {'company_level_ids': [2],       'name': 'Bank reference', 'tag': 'section_bank_reference', 'is_required': False},
        {'company_level_ids': [2, 3],    'name': 'Company Documents', 'tag': 'section_company_documents', 'is_required': False},
        {'company_level_ids': [1, 2, 3], 'name': 'Consent', 'tag': 'section_consent', 'is_required': True}
    ]

    for index, section in enumerate(sections):
        _, _flag = db_get_or_create(CompaniesProfileSections, **section)
        print(f'[{index + 1}/{len(sections)}] Existing: {not _flag} \n> {section}')


@SQLLayer()
def insert_portfolio_services():
    # [PORFOLIO > SERVICES] Static default info
    # > DATASOURCE: Requirements
    PORTFOLIO_FILE = 'portfolio_ALL.json'

    print('PORTFOLIO SERVICES')

    with open(f'{RESOURCES_PATH}/{PORTFOLIO_FILE}') as json_file:
        data = json.load(json_file)
        for index, item in enumerate(data['services']):
            print(f'[{index + 1}/{len(data["services"])}] Portfolio > Service: {item.get("code", None)}')
            db_get_or_create(PortfolioServices, **item)


@SQLLayer()
def insert_portfolio_products():
    # [PORFOLIO > SERVICES] Static default info
    # > DATASOURCE: Requirements
    PORTFOLIO_FILE = 'portfolio_ALL.json'

    print('PORTFOLIO PRODUCTS')

    with open(f'{RESOURCES_PATH}/{PORTFOLIO_FILE}') as json_file:
        data = json.load(json_file)
        for index, item in enumerate(data['products']):
            print(f'[{index + 1}/{len(data["products"])}] Portfolio > Product: {item.get("code", None)}')
            db_get_or_create(PortfolioProducts, **item)


@SQLLayer()
def insert_portfolio_products_categories():
    # [PORFOLIO > SERVICES] Static default info
    # > DATASOURCE: Requirements
    PORTFOLIO_FILE = 'portfolio_ALL.json'

    print('PORTFOLIO PRODUCTS > CATEGORIES')

    with open(f'{RESOURCES_PATH}/{PORTFOLIO_FILE}') as json_file:
        data = json.load(json_file)
        for index, item in enumerate(data['products_categories']):
            print(f'[{index + 1}/{len(data["products_categories"])}] Portfolio > Product Category: {item.get("code", None)}')
            db_get_or_create(PortfolioProductsCategories, **item)


@SQLLayer()
def insert_portfolio_products_subcategories():
    # [PORFOLIO > SERVICES] Static default info
    # > DATASOURCE: Requirements
    PORTFOLIO_FILE = 'portfolio_ALL.json'

    print('PORTFOLIO PRODUCTS > SUBCATEGORIES')

    with open(f'{RESOURCES_PATH}/{PORTFOLIO_FILE}') as json_file:
        data = json.load(json_file)
        for index, item in enumerate(data['products_subcategories']):
            print(f'[{index + 1}/{len(data["products_subcategories"])}] Portfolio > Product Subcategory: {item.get("code", None)}')
            db_get_or_create(PortfolioProductsSubcategories, **item)


@SQLLayer()
def insert_portfolio_products_packaging():
    # [PORFOLIO > SERVICES] Static default info
    # > DATASOURCE: Requirements
    PORTFOLIO_FILE = 'portfolio_ALL.json'

    print('PORTFOLIO PRODUCTS > PACKAGING')

    with open(f'{RESOURCES_PATH}/{PORTFOLIO_FILE}') as json_file:
        data = json.load(json_file)
        for index, item in enumerate(data['products_packaging']):
            print(f'[{index + 1}/{len(data["products_packaging"])}] Portfolio > Product Packaging: {item.get("code", None)}')
            db_get_or_create(PortfolioProductsPackaging, **item)


@SQLLayer()
def insert_templates_files():

    print('TEMPLATES FILES')

    configuration = get_configuration()

    # [TEMPLATE FILES] Static default info
    # TODO: Take file_path from centralized method with routes resources (¿get_storage_settings()?)
    templates_files = [
        {
            'user_email': configuration.APP_BOT,
            'file_name': 'Common CFR Container Contract',
            'file_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'file_tag': 'trades#contracts',
            'file_path': 'TEMPLATES/COMMON_CFR_CONTAINER_ContractTemplate_nosignature.docx',
            'file_description': 'Common CFR Container Contract Template.'
        },
        {
            'user_email': configuration.APP_BOT,
            'file_name': 'Common CFR Vessel Contract',
            'file_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'file_tag': 'trades#contracts',
            'file_path': 'TEMPLATES/COMMON_CFR_VESSEL_ContractTemplate_nosignature.docx',
            'file_description': 'Common CFR Vessel Contract Template.'
        },
        {
            'user_email': configuration.APP_BOT,
            'file_name': 'Common CIF Container Contract',
            'file_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'file_tag': 'trades#contracts',
            'file_path': 'TEMPLATES/COMMON_CIF_CONTAINER_ContractTemplate_nosignature.docx',
            'file_description': 'Common CIF Container Contract Template.'
        },
        {
            'user_email': configuration.APP_BOT,
            'file_name': 'Common CIF Vessel Contract',
            'file_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'file_tag': 'trades#contracts',
            'file_path': 'TEMPLATES/COMMON_CIF_VESSEL_ContractTemplate_nosignature.docx',
            'file_description': 'Common CIF Vessel Contract Template.'
        },
        {
            'user_email': configuration.APP_BOT,
            'file_name': 'Common FOB Container Contract',
            'file_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'file_tag': 'trades#contracts',
            'file_path': 'TEMPLATES/COMMON_FOB_CONTAINER_ContractTemplate_nosignature.docx',
            'file_description': 'Common FOB Container Contract Template.'
        },
        {
            'user_email': configuration.APP_BOT,
            'file_name': 'Common FOB Vessel Contract',
            'file_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'file_tag': 'trades#contracts',
            'file_path': 'TEMPLATES/COMMON_FOB_VESSEL_ContractTemplate_nosignature.docx',
            'file_description': 'Common FOB Vessel Contract Template.'
        },
        {
            'user_email': configuration.APP_BOT,
            'file_name': 'Fertilizer CFR Container Contract',
            'file_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'file_tag': 'trades#contracts',
            'file_path': 'TEMPLATES/FERTILIZER_CFR_CONTAINER_ContractTemplate_nosignature.docx',
            'file_description': 'Fertilizer CFR Container Contract Template.'
        },
        {
            'user_email': configuration.APP_BOT,
            'file_name': 'Fertilizer CFR Vessel Contract',
            'file_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'file_tag': 'trades#contracts',
            'file_path': 'TEMPLATES/FERTILIZER_CFR_VESSEL_ContractTemplate_nosignature.docx',
            'file_description': 'Fertilizer CFR Vessel Contract Template.'
        },
        {
            'user_email': configuration.APP_BOT,
            'file_name': 'Fertilizer CIF Container Contract',
            'file_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'file_tag': 'trades#contracts',
            'file_path': 'TEMPLATES/FERTILIZER_CIF_CONTAINER_ContractTemplate_nosignature.docx',
            'file_description': 'Fertilizer CIF Container Contract Template.'
        },
        {
            'user_email': configuration.APP_BOT,
            'file_name': 'Fertilizer CIF Vessel Contract',
            'file_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'file_tag': 'trades#contracts',
            'file_path': 'TEMPLATES/FERTILIZER_CIF_VESSEL_ContractTemplate_nosignature.docx',
            'file_description': 'Fertilizer CIF Vessel Contract Template.'
        },
        {
            'user_email': configuration.APP_BOT,
            'file_name': 'Fertilizer FOB Container Contract',
            'file_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'file_tag': 'trades#contracts',
            'file_path': 'TEMPLATES/FERTILIZER_FOB_CONTAINER_ContractTemplate_nosignature.docx',
            'file_description': 'Fertilizer FOB Container Contract Template.'
        },
        {
            'user_email': configuration.APP_BOT,
            'file_name': 'Fertilizer FOB Vessel Contract',
            'file_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'file_tag': 'trades#contracts',
            'file_path': 'TEMPLATES/FERTILIZER_FOB_VESSEL_ContractTemplate_nosignature.docx',
            'file_description': 'Fertilizer FOB Vessel Contract Template.'
        },
        {
            'user_email': configuration.APP_BOT,
            'file_name': 'Digital Signature',
            'file_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'file_tag': 'trades#contracts',
            'file_path': 'TEMPLATES/ContractTemplate_signature.docx',
            'file_description': 'Digital Signature Template, common for all contracts.'
        }
    ]

    for index, file in enumerate(templates_files):
        _, _flag = db_get_or_create(TemplatesFiles, **file)
        print(f'[{index + 1}/{len(templates_files)}] Existing: {not _flag} \n> {file}')


# # TODO: Test method to include individual permissions (delete)
# @SQLLayer()
# def insert_policies_testing():
#     from application.models.users_model import Users, UsersModulesPermissions
#     print('POLICIES')
#
#     # [ROLES] Static default info
#     policies = [
#         {
#             'user_email': 'cmesas@grupovermon.com',
#             'actions': ['GET'],
#             'modules': ['module_market_participants']
#         }
#     ]
#
#     permissions = Permissions.query.filter().all()
#     modules = Modules.query.filter().all()
#
#     for index, policy in enumerate(policies):
#         _user = Users.query.filter_by(email=policy['user_email']).first()
#
#         print(f'[{index + 1}/{len(policies)}]  {policy["user_email"]}')
#         for module in modules:
#             if module.code in policy['modules']:
#                 for permission in permissions:
#                     if permission.code in policy['actions']:
#                         _action = {'user_id': _user.id, 'module_id': module.id, 'permission_id': permission.id}
#                         db_get_or_create(UsersModulesPermissions, **_action)
#                         print(f'>> [ACCESS] ({permission.code}) => {module.name}')



# insert_regions()
# insert_subregions()
# insert_countries()
# insert_ports()
# insert_permissions()
# insert_modules()
# insert_roles()
# insert_commodities()
# insert_companies_levels()
# insert_companies_resources_services()
# insert_companies_resources_types()
# insert_companies_profile_sections()
# insert_users_resources_jobs()
# insert_portfolio_services()
# insert_portfolio_products()
# insert_portfolio_products_categories()
# insert_portfolio_products_subcategories()
# insert_portfolio_products_packaging()
# insert_templates_files()
