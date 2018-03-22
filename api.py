from flask import Flask, request, jsonify

from finn import scrape_ad

app = Flask(__name__)


@app.route('/', methods=['GET'])
def ad_detail():
    ad_url = request.args.get('ad')
    if not ad_url:
        return jsonify(**{'error': 'Missing param ad. Try /?ad=https://www.finn.no/realestate/homes/ad.html&quest;finnkode=KODE'})

    ad = scrape_ad(ad_url)

    return jsonify(ad=ad, url=ad_url)


if __name__ == '__main__':
    app.run(debug=True, port=5001)
