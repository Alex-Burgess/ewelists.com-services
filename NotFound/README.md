# Service: NotFound
/notfound API which creates, reads, updates and deletes product items in the table.


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

### Local Function Tests
*Create:*
```
sam local invoke CreateProductFunction --event events/create_product.json --env-vars env_vars/test_env.json
```

### Local API Testing
Local testing of the API, ensures that API and lambda function are correctly configured.
1. Start API
    ```
    sam local start-api
    ```
1. Use local endpoint in browser or with Postman: `http://localhost:3000/solve`

## Logging
Get logs for last 10 minutes:
```
sam logs -n Function --stack-name Service-NotFound-Staging
```

## Deployment
### Deploy to test environment
```
sam build

sam package \
    --output-template-file packaged.yaml \
    --s3-bucket sam-builds-notfound

sam deploy \
    --template-file packaged.yaml \
    --stack-name Service-notfound-test \
    --capabilities CAPABILITY_NAMED_IAM
```
