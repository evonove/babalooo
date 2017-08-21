# babalooo
### Running
`babalooo <list of json files specifying search parameters>`

`babalooo --help` lists available options.

#### Using PostgreSQL or Redis
By default, babalooo uses sqlite. You can choose which database to use with

`babalooo --database=[postgresql|redis]`

Servers must be already running; docker-compose is configured to run both PostgreSQL and Redis servers (`docker-compose up`)
### Required env vars
Environment variables
- AWS\_ACCESS\_KEY\_ID
- AWS\_SECRET\_ACCESS\_KEY
- AMAZON\_ASSOCIATE\_TAG
- AMAZON\_REGION
- EBAY\_APP\_ID

are required to access Ebay and Amazon for searching.
### Testing
Tests run with `tox` and don't require servers running.

Integration tests require the env vars mentioned above.

Redis Adapter tests require REDIS\_SERVER\_PATH env var.

Otherwise tests are skipped.
