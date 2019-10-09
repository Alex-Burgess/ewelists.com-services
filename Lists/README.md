# Service: Lists
/lists API which creates, reads, updates and deletes list items in the table.


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
File: pytest tests/test_solve.py
Class: pytest tests/test_solve.py::TestSolveCompletePuzzles
Unit Test: pytest tests/test_solve.py::TestSolveCompletePuzzles::test_solve_puzzle_easy
```

### Local Function Tests
*Create:*
```
sam local invoke CreateListFunction --event events/create_list.json --env-vars env_vars/test_env.json
```

*Delete:*
```
sam local invoke DeleteListFunction --event events/delete_list.json --env-vars env_vars/test_env.json
```

*Get All Lists:*
```
sam local invoke ListAllFunction --event events/get_all_lists.json --env-vars env_vars/test_env.json
```

*Get List:*
```
sam local invoke GetListFunction --event events/get_list.json --env-vars env_vars/test_env.json
```

*Update List Details:*
```
sam local invoke UpdateListFunction --event events/update_list_details.json --env-vars env_vars/test_env.json
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
sam logs -n Function --stack-name Service-Solve-Staging
```

Tail logs, e.g. whilst executing function test:
```
sam logs -n Function --stack-name Service-Solve-Staging --tail
```

## Deployment
### Deploy to test environment
```
sam build

sam package \
    --output-template-file packaged.yaml \
    --s3-bucket sam-builds-lists

sam deploy \
    --template-file packaged.yaml \
    --stack-name Service-lists-test \
    --capabilities CAPABILITY_NAMED_IAM
```
