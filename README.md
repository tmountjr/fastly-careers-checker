# Fastly Careers Checker

This project pulls the underlying data for Fastly's Careers page (https://www.fastly.com/about/careers/current-openings) and compares it to the last time that data was pulled to find new jobs that were added.

## Running locally

Assuming python 3.9 and pip are installed:
```
$ pip install -r requirements.txt
$ python main.py
```

## Running as a Docker container
The Docker version of this app uses cron to check at midnight UTC every day and print the results out to Docker logs. Build the image and then run it in daemon mode. Using Docker Desktop is the easiest way to run the container and monitor the results.

## Caveats
* Only reports new jobs added, not ones that were updated or removed.
* No notification channels, just log output.
