# ewelists.com-services
Backend Serverless functions and APIs for the [Ewelists](https://github.com/Ewelists/ewelists.com) application.

More general information about these services and the application as a whole is available at [Ewelists](https://github.com/Ewelists/ewelists.com).


## Contents

- [General](#general)
  - [Create a new SAM project](#create-a-new-sam-project)
  - [Builds Bucket](#builds-bucket)
  - [Unit Testing](#unit-testing)
  - [Local Lambda Function Tests](#local-lambda-function-tests)
  - [Local API Testing](#local-api-testing)
  - [Logging](#logging)
- [Contact](#contact)
- [Lists](#lists)
- [NotFound](#notfound)
- [Products](#products)


## General

### Setup Environment
The local python environment is kept in sync with the python environment we use in pipeline codebuild project, which is currently 3.7.6.
```
pyenv install 3.7.6
pyenv local 3.7.6
pip install moto pytest requests_mock boto3
pip install -r Lists/requirements.txt
```

### Create a new SAM project

To create a new SAM serverless api and function project structure:
```
sam init --runtime python3.7 --name lists
```

### Builds Bucket

When packaging a service for deployment to the test environment, an S3 bucket is required to store the builds.  To create this:
```
aws s3 mb sam-builds-contact-test
```

### Unit Testing
Example test executions:
```
All: pytest
File: pytest tests/test_create.py
Class: pytest tests/test_create.py::TestPutItemInTable
Unit Test: pytest tests/test_create.py::TestCreateMain::test_create_main
```

### Local Lambda Function Tests
Lambda functions can be invoked locally as follows:
```
sam local invoke CreateListFunction --event events/create_list.json --env-vars env_vars/test_env.json
```

### Local API Testing
APIs can also be testing locally.  For example, running the command below in the Lists directory, will make a local endpoint available at `http://localhost:3000/lists`.
```
sam local start-api
```

### Logging
Get logs for last 10 minutes:
```
sam logs -n CreateListFunction --stack-name Service-lists-test
```

Tail logs, e.g. whilst executing function test:
```
sam logs -n CreateListFunction --stack-name Service-lists-test --tail
```


## Contact

/contact API which is the backend for the contact us page.

**Build and Deploy**

```
sam build

sam package \
    --output-template-file packaged.yaml \
    --s3-bucket sam-builds-contact-test

sam deploy \
    --template-file packaged.yaml \
    --stack-name Service-contact-test \
    --capabilities CAPABILITY_NAMED_IAM
```

## Lists
/lists API which creates, reads, updates and deletes list items in the table.  Some of the services require a SES email template, so these must be created first for the first deployment.  After the initial creation, the code and email templates can be updated/deployed independently as required.

**Create Email Templates**

Create bucket that will
```
aws s3 mb s3://email-templates-ewelists-test
```

Copy email templates to bucket:
```
cd ewelists.com-services/cloudformation
aws s3 cp . s3://email-templates-ewelists-test/ --recursive --exclude "*" --include "email-template-*"
```

Create email template stack:
```
aws cloudformation create-stack --stack-name Email-Templates-Test \
 --template-body file://email-templates-master-stack.yaml \
 --parameters ParameterKey=Environment,ParameterValue=test \
    ParameterKey=BucketEndpoint,ParameterValue=https://email-templates-ewelists-test.s3-eu-west-1.amazonaws.com
```

To update email template stack:
```
aws cloudformation update-stack --stack-name Email-Templates-Test \
 --template-body file://email-templates-master-stack.yaml \
 --parameters ParameterKey=Environment,ParameterValue=test \
    ParameterKey=BucketEndpoint,ParameterValue=https://email-templates-ewelists-test.s3-eu-west-1.amazonaws.com
```

**Build and Deploy**

```
sam build

sam package \
    --output-template-file packaged.yaml \
    --s3-bucket sam-builds-lists-test

sam deploy \
    --template-file packaged.yaml \
    --stack-name Service-lists-test \
    --capabilities CAPABILITY_NAMED_IAM
```

## NotFound
/notfound API which creates, reads, updates and deletes product items in the table.

**Build and Deploy**

```
sam build

sam package \
    --output-template-file packaged.yaml \
    --s3-bucket sam-builds-notfound-test

sam deploy \
    --template-file packaged.yaml \
    --stack-name Service-notfound-test \
    --capabilities CAPABILITY_NAMED_IAM
```

## Products
/products API which creates, reads, updates and deletes product items in the table.

**Build and Deploy**

```
sam build

sam package \
    --output-template-file packaged.yaml \
    --s3-bucket sam-builds-products-test

sam deploy \
    --template-file packaged.yaml \
    --stack-name Service-products-test \
    --capabilities CAPABILITY_NAMED_IAM
```
