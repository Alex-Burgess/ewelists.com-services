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
sam local invoke CreateListFunction --event event.json
```
