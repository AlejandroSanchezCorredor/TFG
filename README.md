# [VERMON] CHECKIT Application (Serverless)

[comment]: <> (TODO: Update readme)

## Index
    
- [Introduction](#introduction)
- [Environment](#environment)
- [Serverless](#serverless)
- [Configuration](#configuration)
- [Develop](#develop)
- [Dependencies: Layers](#layers)
- [Domains: Route53 + Certificates](#aws_route53)
- [Authentication: Cognito](#aws_cognito)
- [Database: SQLAlchemy + Alembic](#bbdd_sqlalchemy_alembic)
- [Database: Static data](#db_static_data)
- [Host and Storage: S3 + Cloudfront](#aws_s3_cloudfront)
- [Mail Management: SES](#aws_ses)
- [Job Queue: SQS](#aws_sqs)
- [Webpush](#webpush)
- [Deployment](#deployment)


<a name="introduction"></a>
## Introduction

This repository contains the code of the serverless architecture of the CHECKIT proyect. By means of this file README.md it 
pretends to define the integrated services, as well as the way to implement and deploy the serverless architecture


<a name="environment"></a>
## Environment
The proyect works on the following base versions of the used technologies:
* Python 3.10
* Node v16

<a name="serverless"></a>
## Serverless
The proyect is developed by a infrastructure orientated as code making use of the serverless framework.
[serverless](https://www.serverless.com/framework/docs).

This framework provides different tools for the cloud architecture development  (AWS in this case) that allows the
management of these services.
Inside the framework's tools we can differentiate:
- Framework development: This framework is free use and provides the different tools for the cloud architectures develop
(AWS in our case) and the management of the services included in the backend.
- Monitoriation platform: This platform is completly optional (It has a free layer) and allows monitoring the deployed resources
with framework directly from the cloud selected(AWS). This provides a dashboard with usage metrics, errors, deployed services, ...
that allows you to do an agile monitoring and high level with the resources on use.

To use this monitoring platform (Remember that is totally optional) is neccesary to link to a serverless account and configure
the scheme .yaml, specifically to configure the organitation and the application linked to the account, in this way:
```yml
org: checkitplatform # organization name
app: checkit-application # app name
```

If it includes the information about the organitation and the serverless app, this will force you to log in the console.
```console
foo@bar:~$ serverless <login/logout>
```

Alternatively it can generate a environment variable that serverless will take to link the deployment with the
monitoring dashboard (this alternative is the integrated in the processes of ci)
```console
foo@bar:~$ export SERVERLESS_ACCESS_KEY=<serverless_access_key>
```


<a name="configuration"></a>
## Configuration

Once you have cloned the repository, is recomendable to create a virtual environment to be able to work with the specify
versions of the packages, which are included in the file _requirements.txt_.

```console
foo@bar:~$ python3 -m venv venv
foo@bar:~$ source venv/bin/activate (linux)
foo@bar:~$ source venv/Scripts/activate (windows)
```

Subsequently, they have to be installed from the file:

```console
foo@bar:~$ pip3 install -r requirements.txt
```

As the framework uses the node libraries, is also necessary to install the dependencies and the additional plugins:

```console
foo@bar:~$ npm install
```


<a name="desarrollo"></a>
## Develop

For working more easily in a local develop environment with the API Rest develop (Using the API Gateway),
it includes a complementary plugin: serverless-offline.
**Documentación**: https://github.com/dherault/serverless-offline

These plugins allow to simulate in locally the functionality of the API Rest to be deployedin the API Gateway. For launching the
servicce:

```console
foo@bar:~$ serverless offline --noPrependStageInUrl --stage <develop/preproduction/production>
```
**Note**: *Important the parameter ----noPrependStageInUrl so in local doens't take in acount the stage, that is the way that internally
the lambda will execute.*

In a complementary way it adds a second plugin that will allow us to simulate the events in local:
serverless-offline-scheduler
**Documentación**: https://github.com/ajmath/serverless-offline-scheduler

This plugin works automatically with the previous one.

<a name="layers"></a>
## Dependencies: Layers

To avoid loading the lambdas with libraries code and dependencies, it defines a _layer_ with the necessary requirements to
run the software in the defined runtime.
The installation of the dependencies are done by the usage of the complementary plugin called
[serverless-python-requirements](https://www.serverless.com/plugins/serverless-python-requirements).
This plugin allows the automatized installation of the dependecies automatically with the usage of the file
_requirements.txt_.

In this case, the defined  _layer_  is deployed on a different stack in order to use more than one layer and 
in the margin of the main code.
Each one of the _stacks has its own file _serverless-<nombre>.yml_ and the deployment it's done in the following way:

```console
foo@bar:~$ serverless deploy -c serverless_requirements.yml --stage production (--verbose [extra info])
```

```console
foo@bar:~$ serverless deploy -c serverless_requirements.yml --stage preproduction (--verbose [extra info])
```

```console
foo@bar:~$ serverless deploy -c serverless_requirements.yml --stage develop (--verbose [extra info])
```

Once the deployment of all the _layers_ are done and they had been created correctly, we can assign them to a _lambda_ by
the following way (example):

```yml
auth:
    handler: application/handler.api
    layers:
      - ${cf:${self:service}-requirements-${self:provider.stage}.PythonRequirementsLambdaLayerQualifiedArn}
```


<a name="aws_route53"></a>
## Domains: Route53 + Certificates

**[IMPORTANT]** First the API Gateway had to be deployed.

This proyect is configure on a adquired domain [app.checkit.grupovermon.linl](app.checkit.grupovermon.linl) / [app.checkit.group](app.checkit.group) on which we will work
with the following services:
- CloudFormation: The traffic of the hosted app in S3 will be served from CloudFormation on the custom domain.
- API Gateway: The deployed endpoints also will work on the defined domain.
- SES: Notification source mails will also be configured on the domain.

Those domains that have been registered via Route 53 do not need any further configuration beyond the mandatory 
and should be created from the interface. Once this is done, if you want to use this domain for API Gateway endpoints
it is necessary to make use of two plugins:

- [serverless-certificate-creator](https://www.npmjs.com/package/serverless-certificate-creator)
- [serverless-domain-manager](https://www.npmjs.com/package/serverless-domain-manager)

Once these plugins have been installed, the following information must be added to the file _serverless.yml_ 
(example taken from [Serverless](https://www.serverless.com/plugins/serverless-certificate-creator#description)):

```yml
custom:
  customDomain:
    domainName: certcreatorsample.greenelephant.io
    certificateName: 'certcreatorsample.greenelephant.io'
    basePath: ''
    stage: ${self:provider.stage}
    createRoute53Record: true
  customCertificate:
    certificateName: 'certcreatorsample.greenelephant.io' //required
    idempotencyToken: 'certcreatorsamplegreenelephantio' //optional
    // optional default is false. if you set it to true you will get a new file (after executing serverless create-cert), that contains certificate info that you can use in your deploy pipeline, alternativly as an array
    writeCertInfoToFile: true
    // optional, only used when writeCertInfoToFile is set to true. It sets the name of the file containing the cert info
    certInfoFileName: "certs/${self:provider.stage}/cert-info.yml"
    region: eu-west-1 //optional
    hostedZoneNames: 'greenelephant.io.' //required if hostedZoneIds is not set
    tags:
      Name: 'somedomain.com'
      Environment: 'prod'
    //optional default false. this is useful if you managed to delete your certificate but the dns validation records still exist
    rewriteRecords: false
```

This configuration is defined in the following file: _aws_acm_certificates.yml_ + _aws_route53.yml_
- customDomain: Configuration for the generation of the domain and its configuration in the project.
- customCertificate: Configuration for automated certificate generation for work with API Gateway.

Once the necessary information has been completed, the certificate and the domain must be created (important the order).
For this, we will make use of the installed plugins

- First we must create the ACM certificate (the command to delete the certificate is included).:

(Creation)
```console
foo@bar:~$ serverless create-cert --stage production
```
```console
foo@bar:~$ serverless create-cert --stage preproduction
```
```console
foo@bar:~$ serverless create-cert --stage develop
```

(Deleted)
```console
foo@bar:~$ serverless remove-cert --stage production
```
```console
foo@bar:~$ serverless remove-cert --stage preproduction
```
```console
foo@bar:~$ serverless remove-cert --stage develop
```

- A continuación se debe de crear el dominio (esta acción puede tardar incluso 40 minutos). También se incluye el comando por si se desea eliminar el dominio:

(Creation)
```console
foo@bar:~$ serverless create_domain --stage production
```
```console
foo@bar:~$ serverless create_domain --stage preproduction
```
```console
foo@bar:~$ serverless create_domain --stage develop
```

(Deleted)
```console
foo@bar:~$ serverless delete_domain --stage production
```
```console
foo@bar:~$ serverless delete_domain --stage preproduction
```
```console
foo@bar:~$ serverless delete_domain --stage develop
```

PD: If we want to reference the ARN of the certificate that has been created, we can do it directly like this:


```yml
[DEPRECATED]
${certificate:${self:custom.customCertificate.certificateName}:CertificateArn}
```
*NOTA: Now it will be necessary to indicate the ARN of the certificate for the environment directly with the variable: 

'cloudFrontAcmCertificateArn'


- Finally, to apply all these changes and get our API Gateway to have a custom domain we must
deploy the stack:

```console
foo@bar:~$ serverless deploy --stage production (--verbose [extra info])
```

```console
foo@bar:~$ serverless deploy --stage preproduction (--verbose [extra info])
```

```console
foo@bar:~$ serverless deploy --stage develop (--verbose [extra info])
```



<a name="aws_cognito"></a>
## Authentication: Cognito

Once the Cognito service is deployed and endpoint authentication against the Cognito service is defined, 
it can be helpful to manage users from the console to perform tests in a more agile way, therefore, it is defined:

### A) To register user from console

1. Register the user from the console:

```console
foo@bar:~$ aws cognito-idp sign-up --region {your-aws-region} --client-id {your-client-id} --username admin@example.com --password password123
```

2. Realizar la confirmación del usuario generado anteriormente:

```console
foo@bar:~$ aws cognito-idp admin-confirm-sign-up --region {your-aws-region} --user-pool-id {your-user-pool-id} --username admin@example.com
```

### B) To force password change from the console of an already created user

1. Obtener sesión de cambio de contraseña

```console
foo@bar:~$ aws cognito-idp admin-initiate-auth --user-pool-id {user-pool-id} --client-id {client_id} --auth-flow ADMIN_NO_SRP_AUTH --auth-parameters USERNAME={username},PASSWORD={current_password} --profile {profile_cli}
```
Si la petición se realiza correctamente devolverá un identificador de sesión que se utilizará en la próxima petición.

2. Operación de cambio de contraseña

```console
foo@bar:~$ aws cognito-idp admin-respond-to-auth-challenge --user-pool-id {user_pool_id} --client-id {client_id} --challenge-name NEW_PASSWORD_REQUIRED --challenge-responses NEW_PASSWORD={new_password},USERNAME={username} --profile {profile} --session {previous_session}
```
* La sesión tiene una caducidad aprox de unos 2-5 min

### To obtain user token from console

3. Generate a file named _auth.json_, which must contain the following (it will allow the token to be generated later):

```json
{
    "UserPoolId": "{your-user-pool-id}",
    "ClientId": "{your-client-id}",
    "AuthFlow": "ADMIN_NO_SRP_AUTH",
    "AuthParameters": {
        "USERNAME": "admin@example.com",
        "PASSWORD": "password123"
    }
}
```

4. Finally, to obtain the user's token, the following command must be executed. In this command we will obtain the _IdToken_, _AccessToken_ y _AccessToken_.

```console
foo@bar:~$ aws cognito-idp admin-initiate-auth --region {your-aws-region} --cli-input-json file://auth.json
```

If we want to verify if the endpoint authorization with Cognito has been done correctly, we go to the following application [Postman](https://www.postman.com/downloads/) and enter the url of the endpoint.

First we will get the following message, which indicates that we must establish the token to be able to make the request, that is, Cognito is running:

```json
{
    "message": "Unauthorized"
}
```

Ultimately, we go inside Postman to the tab _Authorization_ and select the type _Bearer Token_. 
Within the field _Token_ copy the variable _IdToken_ obtained earlier and make the request again. 
If everything went as it should, the corresponding code of the endpoint will have been executed..


<a name="bbdd_sqlachemy_alembic"></a>
## Database: SQLAlchemy + Alembic

The application makes use of the ORM  [SQLAlchemy](https://www.sqlalchemy.org/) to work with the database and allow 
information management from the database with a better structure through self-managed objects.

In the directory _application/models/_ are all the mapped models of the database, that is to say, each one of the classes implemented in these files corresponds to each table of the database. 
of the classes implemented in these files correspond to each table of the database with which the system will work.

In addition to this layer, it is completed with a database change manager (alembic).
To learn about database management and change control see: [Alembic](alembic/README.md)

The way to configure this library on the project is as follows:

In the file _alembic.ini_ must be modified the parameter _sqlalchemy.url_, in our case it has been established 
by means of an environment variable called _DATABASE_URL_. In this part it is also important to modify the engine of the 
the database.

```ini
sqlalchemy.url = mysql+pymysql://%(DB_USER)s:%(DB_PASSWORD)s@%(DB_URL)s:%(DB_PORT)s/%(DB_NAME)s
```
On the other hand, in the file _alembic/env.py_, the following must be configured to define the data to be used from db:

```python
# here we allow ourselves to pass interpolation vars to alembic.ini
# from the host env
sys.path.append(os.getcwd())
section = config.config_ini_section
config.set_section_option(section, "DB_USER", os.environ['RDS_MASTER_USER'])
config.set_section_option(section, "DB_PASSWORD", os.environ['RDS_MASTER_PASSWORD'])
config.set_section_option(section, "DB_URL", os.environ['RDS_AURORA_ENDPOINT'])
config.set_section_option(section, "DB_PORT", os.environ['RDS_AURORA_PORT'])
config.set_section_option(section, "DB_NAME", os.environ['RDS_AURORA_DB'])
```

In the above part of the code, each of the environment variables is extracted, which by interpolation can be used in the file 
can be used in the _alembic.ini_.

The models defined from the Base on which all these models extend are referenced below.:
```python
# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
from application.core.sql import Base
target_metadata = Base.metadata
```

Once the above has been done, to perform migration or revision of the database we must execute the following command 
following command:

```console
foo@bar:~$ alembic revision --autogenerate -m 'Modificación realizada'
```

This will generate a file in _alembic/versions/_ with the corresponding modifications (upgrade and downgrade).
For these modifications to take effect and be performed on the database, we must execute the following command:


```console
foo@bar:~$ alembic upgrade head
```


<a name="bbdd_datos_estaticos"></a>
## Database: Static data

This project contains a series of static data, that is, static information directly dependent on the business logic that must be inserted initially with the creation of the database.
that must be inserted initially at the same time as the database is created. For this purpose, the following has been implemented
a file called _init_database.py_ has been implemented and is located in the directory _application/functions/_.

This file is used to import data from multiple tables..


<a name="aws_s3_cloudfront"></a>
## Host y Storage: S3 + Cloudfront

The project makes use of 2 buckets of S3:
- Bucket for storing multimedia content: files managed by the application. <bucket privado>
- Bucket to host the web application. <bucket público>

For the correct operation and configuration of CloudFront in the app content bucket, both a Distribution and a DNS resource must be created. 
both a Distribution resource and a DNS resource.
The latter has a somewhat special configuration, since it must be taken into account that the field _HostedZoneId_ at 
CloudFront, this ID must always be set, as indicated in the 
[documentación oficial de AWS](https://docs.aws.amazon.com/es_es/AWSCloudFormation/latest/UserGuide/aws-properties-route53-aliastarget.html).

```yml
WebsiteDNSName:
Type: AWS::Route53::RecordSetGroup
Properties:
  HostedZoneName: '${self:custom.customDomainName}.'
  RecordSets:
  - Name: 'dev.${self:custom.customDomainName}'
    Type: A
    AliasTarget:
      HostedZoneId: <hostedZoneId>
      DNSName: !GetAtt [S3BucketAppFrontDistribution, DomainName]
```

On the other hand, one aspect that should be taken into account as it is very important and can affect other services is that the certificates added to CloudFront can only be in the US East (N. Virginia Region). 
that the certificates that are added to CloudFront can only be in the US East (N. Virginia) Region. 
As a consequence of this, since our API Gateway is in another region, the endpoints must be created of type _edge_.


<a name="aws_ses"></a>
## Mail Management: SES

Based on the configured domain, the possibility of using e-mails under this domain to send information via e-mail is integrated..

> *Since this process cannot be automated in CloudFront, or the solutions reviewed involve high complexity, this configuration has been done manually through the AWS console.*

> *Configuration to be performed:*
> - *The domain in question has been verified by the SES service. [app.checkit.grupovermon.link] / [app.checkit.group]. Since it is a self-managed domain in Route53, rule creation is delegated directly to AWS management.*
> - *Once verified (it may take a few minutes) we proceed to the creation of an email under the domain, in this case [no-reply@checkit.grupovermon.linl] / [no-reply@checkit.group]
> - *IMPORTANT: Here we find a problem, and it is that the verification of the mail requires the reception of a mail in this mail (of which there is no inbox), so an additional configuration is made..*
> - *To redirect and notify the outgoing/incoming mails, we take advantage of the SSM service, we create a rule and a topic that forwards the mails to another mail account from which we can accept the verification of the application mail..*
> - *Check that the DNS associated with SMTP has been created.!*

> *[+ Info] https://medium.com/responsetap-engineering/easily-create-email-addresses-for-your-route53-custom-domain-589d099dd0f2#:~:text=New%20Email%20Address-,In%20the%20AWS%20console%2C%20navigate%20to%20SES%20%3E%20Identity%20Management%20%3E,%2Dreply%40example.com.*


<a name="aws_sqs"></a>
## Job Queue: SQS

Work queue functionality is integrated to decouple asynchronous actions for indirect actions or actions external to the platform (sending emails, synchronizations to external services, telegram notifications, ...). 
the platform (sending emails, synchronizations to external services, telegram notifications, ...) by adding a queue structure with a main queue (policy of 3 retries every 1 minute) and a
queue structure with a main queue (policy of 3 retries every 1 minute) and an associated error queue where messages are passed in case of failure 
messages are passed on in case they could not be consumed.
- Messages are kept in the main queue for a maximum of 2 days if they are not consumed.
- Messages are kept in the error queue for a maximum of 7 days if they are not consumed.


<a name="webpush"></a>
## Webpush

Webpush notification functionality is integrated on the web application on the different browsers and operating systems supported.
operating systems.
In order to work with the webpush protocol it is necessary to generate the pair of keys that will allow to communicate and encrypt the information between client and server.
the information between client and server, for this:

```console
# Private key generation (PEM format)
foo@bar:~$ openssl ecparam -genkey -name prime256v1 -noout -out private_key.pem

# Public key generation + conversion (Base64 DER)
foo@bar:~$ openssl ec -in private_key.pem -pubout -outform DER|tail -c 65|base64|tr -d '=' |tr '/+' '_-' >> public.key

# Private key generation + conversion (Base64 DER)
foo@bar:~$ openssl ec -in private_key.pem -outform DER|tail -c +8|head -c 32|base64|tr -d '=' |tr '/+' '_-' >> private.key
```

**Note**: *By default, if the parameter is not included it will be set to _preproduction_.*


<a name="despliegue"></a>
## Deployment

In order to be able to deploy the backend in any region and in different environments, the _serverless.yml_ file has been configured to accept the _stage_ as parameter.


```console
foo@bar:~$ serverless deploy --stage production (--verbose [extra info])
```

```console
foo@bar:~$ serverless deploy --stage preproduction (--verbose [extra info])
```

```console
foo@bar:~$ serverless deploy --stage develop (--verbose [extra info])
```


**Note**: *By default, if the parameter is not included it will be set to _preproduction_.*



## Known problems

#### Environment variables

With respect to the environment variables used in the functions (Lambda) there is a problem related to the database variables (RDS Aurora). 
The first time a _deploy_ is performed, it appears that they do not exist and therefore it is convenient to comment them,
A search is being carried out in order to find a solution as soon as possible to avoid having to perform the deployment twice. 
(Investigate the _Export_ function in the _Outputs_).

#### Cognito's Triggers

A series of triggers have been added to Cognito, in order to automate or modify certain elements of the resource. 
of the resource. These triggers have been set in the main file of the environment, thats is, in the _serverless.yml_.

In numerous occasions we have noticed that, when doing a _deploy_ the triggers disappear from the Cognito _pool_ and therefore, they are not executed when they should. 
It seems to be a known bug among users of the _serverless_ framework. 


**Note**:  *This behavior appears to occur when any modification is made to the cognito service after the triggers have already been configured.
triggers have already been configured.

In this link you can follow the incidence: [Github](https://github.com/serverless/serverless/issues/7510)
