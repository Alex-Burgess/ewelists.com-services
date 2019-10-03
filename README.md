# ewelists.com-services
Main serverless functions and APIs for ewelists application

Services:
* Create - link to readme file


### Create a new SAM serverless api and function
```
sam init --runtime python3.6 --name lists
```

### Test a function locally
```
sam local invoke CreateListFunction --event events/event.json --env-vars env_vars/test_env.json
```

### Set python version
```
pyenv versions
pyenv local 3.6.8
```

### Create an s3 bucket for SAM builds
```
aws cloudformation create-stack --stack-name sam-builds-lists --template-body file://sam-builds-bucket.yaml
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
