🏠 Fetch real estate listing from finn.no and make available as JSON response.

Requests to finn.no uses a randomized user agent. The response data is cached (with redis).

## Try it out
Hit the button below to create your own. You need a free Heroku account.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/nikolaik/pyfinn/tree/master)


## Installation

    pipenv install --three
    docker run -d -p 6379:6379 redis
    pipenv run api.py
    open 'http://localhost:5000/'

## Configuration

- `REDIS_URL` URL to to Redis instance. Default: `redis://localhost:6379/0`
- `CACHE_DURATION_SECONDS` How long we cache ad data. Default: `23 * 60 * 60` seconds.

## TODO
- Add example usage with Google Sheets/App Scripts