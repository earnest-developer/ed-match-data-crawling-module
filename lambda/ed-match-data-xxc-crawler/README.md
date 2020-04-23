# ed-match-data-xxc-crawler  

# Setting up the development environment  

This Python module can be run in many ways but the recommended rig is following:  

- IDE: Visual Studio Code
- Interpreter: Python 3.7.x (defined in `.vscode/settings`)
- Linter: flake8 (defined in `.vscode/settings`)

The Python Virtual Environment is not committed and will need configuration.  

Run `python3 -m venv .venv` under *workspace root*  
Run `pip install requests boto3 bs4 python-dateutil` to install dependant modules

Make sure the correct development settings are selected in VS Code by pressing  
`Ctrl + Shift + P` and `>Python: Select Interpreter/Linter`   

# Running locally

This application is made to be hosted on AWS Lambda and as such some constraints are inherited when it comes  
to running it locally. 

The SAM CLI Tool is *not* used for local debugging (PITA), instead should debug by running the unit tests under  
`test_crawler_function.py`. Make sure to enable breaking on `Raised Exceptions` on VS Code and use the provided `launch.json` file  

Set the following variables in the shell that will run this application.

`export BASE_CRAWL_URL='https://www.xxx.xx.xx'`
`export JOB_QUEUE_URL='https://sqs.eu-west-2.amazonaws.com/xxx/ed-match-data-crawling-module-crawler-jobs'`
`export MATCH_DATA_INGEST_QUEUE_URL='https://sqs.eu-west-2.amazonaws.com/xxx/ed-match-data-crawling-module-ingest.fifo'`

## Running locally via SAM

```
sam build
sam local invoke "CrawlerXXC" -e events/sqs-new-crawl-job.json --env-vars env.json
```

To pass an environment variable to the SAM tool just add it in `env.json`  

# Manual Deployment via SAM

Given the AWS CLI is configured, deployment is easy: 

```
sam deploy
```

Both source code and any infrastructure changes will be applied. If things get stuck, delete the stack from CloudFormation.

# Application Logic

The application gets invoked when it receives a "Crawl Job" SQS message. Sample message under `events`  

The base URL to crawl from is retrieved from the `BASE_CRAWL_URL` host environment variable  

It batches football matches by date and sends the data over to the ingest queue