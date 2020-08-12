import json

import redis
import os
from flask import Flask, request, jsonify

from finn import scrape_ad

app = Flask(__name__)

redis_service = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
cache_duration = int(os.getenv('CACHE_DURATION_SECONDS', 23 * 60 * 60))


@app.route('/', methods=['GET'])
def ad_detail():
    finnkode = request.args.get('finnkode')
    if not finnkode or not finnkode.isdigit():
        return jsonify(**{'error': 'Missing or invalid param finnkode. Try /?finnkode=KODE'})

    cache_key = f'finn-ad:{finnkode}'
    ad = redis_service.get(cache_key)
    if not ad:
        ad = scrape_ad(finnkode)
        redis_service.set(cache_key, json.dumps(ad), cache_duration)
    else:
        ad = json.loads(ad)

    return jsonify(ad=ad)


if __name__ == '__main__':
    app.run(debug=True)
