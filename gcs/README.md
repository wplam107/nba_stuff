# Google Cloud Store (GCS)
- GCS used as a data lake for data retrieved from NBA API
- Files loaded to GCS in newline delimited JSON format
- External packages/libraries: [```nba_api```](https://github.com/swar/nba_api)

## Setup
Note: Environmental variables were set locally with shell script for implicit authentication of Google Cloud Platform credentials and bucket name
```
#!/bin/sh
export GOOGLE_APPLICATION_CREDENTIALS="<path to JSON credentials>"
export BUCKET="<bucket name>"
```

## Data Extraction
- 2020-2021 Regular Season games ETL script: ```initial_games_script.py```