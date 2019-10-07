# Service: Lists
/lists API which creates, reads, updates and deletes list items in the table.

### Set python version
```
pyenv versions
pyenv local 3.6.8
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

*Get List:*
```
sam local invoke GetListFunction --event events/get_list.json --env-vars env_vars/test_env.json
```

*Update List Title:*
```
sam local invoke UpdateListFunction --event events/update_list_title.json --env-vars env_vars/test_env.json
```

*Update List Description:*
```
sam local invoke UpdateListFunction --event events/update_list_description.json --env-vars env_vars/test_env.json
```

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
