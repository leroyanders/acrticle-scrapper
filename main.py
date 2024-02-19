from flask import Flask, request, jsonify
from modules.parser import ArticleParser
from threading import Thread
import queue

app = Flask(__name__)

def process_article(url, result_queue):
    try:
        article_parser = ArticleParser(url)
        result_queue.put({'article': article_parser.article_data})
    except Exception as e:
        result_queue.put({'error': str(e)})

@app.route('/health')
def healthcheck():
    return jsonify({'ok': True})

@app.route('/', methods=['POST'])
def scrape():
    data = request.get_json()

    if 'url' not in data or not isinstance(data['url'], str):
        return jsonify({'error': 'Invalid JSON format or missing URL'}), 400

    result_queue = queue.Queue()
    thread = Thread(target=process_article, args=(data['url'], result_queue))
    thread.start()
    thread.join()  # Wait for the thread to finish execution

    result = result_queue.get()
    if 'error' in result:
        return jsonify({'error': result['error']}), 500
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(debug=True, port=7732, threaded=True)
