# ed-match-data-xxc-crawler  

The application gets invoked when it receives a "Crawl Job" SQS message. Sample message under `events`  

The base URL to crawl from is retrieved from the `BASE_CRAWL_URL` host environment variable  

It batches football matches by date and sends the data over to the ingest queue

Leverages concurrent processes for matches happening on the same day

It processes messages one at a time and does not get automatically invoked for retries