from flask import Flask, request, jsonify
from modules.parser import ArticleParser

app = Flask(__name__)

@app.route('/health')
def healthcheck():
    return jsonify({'ok': True})

@app.route('/', methods=['POST'])
def scrape():
    data = request.get_json()

    if 'url' not in data or not isinstance(data['url'], str):
        return jsonify({'error': 'Invalid JSON format or missing URL'}), 400

    try:
        article_parser = ArticleParser(data['url'])
        return jsonify({'article': article_parser.article_data}), 200
    except Exception as e:
        return jsonify({'error': e})

if __name__ == '__main__':
    app.run(debug=True, port=7732)
