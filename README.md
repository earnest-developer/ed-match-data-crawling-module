# ed-match-data-crawling-module
This is a mono repository of different services and cloud components. As a whole, the module's  
purpose is to scrape specific URLs then deduplicate, normalize and persists the data.  

Indicated as a crawling module in the Sports Predictions [architecture diagram](https://drive.google.com/file/d/1CE7FKSq8LaS-KvQZAYlxMyNxhMJoBQsX/view?usp=sharing) and consists of the following lambda workers:  

## ed-match-data-xxc-crawler
A stateless crawler that targets a specific URL. Can be scheduled to run nightly, if its run was fruitful it  
will enqueue the data to the ingest queue of ed-match-data-insertor.  

## ed-match-data-insertor
Dequeues deduplicated messages from an ingest queue. Inserts to the relational database

# infrastructure and manual deployments
The module's infrastructure is defined in the CloudFormation `template.yaml`. It consists of the lambdas as well as  
the cloud components that fulfill them.  

Given the AWS CLI is configured, deployment is easy: 

```
sam build
sam deploy
```

# local environment
These Python modules can be run in many ways but the recommended rig is following:  

- IDE: Visual Studio Code
- Interpreter: Python 3.7.x (defined in `.vscode/settings`)
- Linter: flake8 (defined in `.vscode/settings`)

The Python Virtual Environment is not committed and will need configuration.  

Run `python3 -m venv .venv` under *workspace root*  
Run `pip install requests boto3 localstack-client bs4 python-dateutil` to install dependant modules

Make sure the correct development settings are selected in VS Code by pressing  
`Ctrl + Shift + P` and `>Python: Select Interpreter/Linter`   

## development and debugging

This application is made to be hosted on AWS Lambda and as such some constraints are inherited when it comes  
to running it locally. 

The SAM CLI Tool is *not* used for local debugging (PITA), as instead each lambda can be run/debugged via its unit tests  
The AWS components are mocked using dockerized `localstack` and custom config.  

To bring all dependencies up: `docker-compose up --build`

Make sure to enable breaking on `Raised Exceptions` on VS Code and use the provided `launch.json` file for each lambda  

Managing environmental variables can be done via a `config_local.py` file in each lambda's root  

For ed-match-data-xxc-crawler

```
#! python3
# config_local.py -- A place for overwriting local environmental variables

BASE_CRAWL_URL = 'https://www.xxx.co.uk/'
JOB_QUEUE_URL = 'http://localhost:4576/queue/ed-match-data-crawling-module-xxc-crawler-jobs'
INSERTOR_INGEST_QUEUE_URL = 'http://localhost:4576/queue/ed-match-data-crawling-module-ingest.fifo'
```

For ed-match-data-insertor

```
#! python3
# config_local.py -- A place for overwriting local environmental variables

MATCH_DATA_NOTIFICATIONS_QUEUE_URL = 'http://localhost:4576/queue/ed-match-data-notifications'
```

Happy coding  