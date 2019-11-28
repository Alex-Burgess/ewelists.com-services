# Service: Contact
/contact API which is the backend for the contact us page.


## Testing
### Unit Testing
Python version 3.6 is used with the lambda, so a matching local python environment is also used:
```
pyenv local 3.6.8
```

To execute `pytest` against our `tests` folder to run our initial unit tests:
```
pytest
```

Test a specific file, class or test:
```
File: pytest tests/test_contact.py
```

### Create an s3 bucket for SAM builds
```
aws cloudformation create-stack --stack-name sam-builds-contact-test --template-body file://sam-builds-bucket.yaml
```

### Deploy to test environment
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
