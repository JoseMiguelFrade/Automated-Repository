
import warnings
from urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)
from flask import Flask, request
from flask_cors import CORS
import os
from pdfcrawler.crawler import crawl
import threading
from flask_socketio import SocketIO
import threading
from pdfcrawler.crawler import Crawler
from pdfcrawler.crawler.downloaders import RequestsDownloader

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')
CORS(app)

# Dictionary to keep track of threads and their stop flags
crawler_threads = {}
crawler_instances = {}

def start_crawler_thread(crawl_url, thread_id):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(current_dir, 'crawling_test')
    while not crawler_threads[thread_id]["stop"]:
        crawl(app, socketio, url=crawl_url, output_dir=output_dir, method='rendered')

@app.route('/start-crawler', methods=['POST'])
def start_crawler():
    request_data = request.get_json()
    url_list = request_data.get('urls', [])
    downloader = RequestsDownloader()  # Create downloader instance

    for url in url_list:
        thread_id = hash(url)
        if thread_id not in crawler_instances:
            crawler = Crawler(app, socketio, downloader)
            thread = threading.Thread(target=crawler.crawl, args=(url, 2))
            thread.start()
            crawler_instances[thread_id] = {"crawler": crawler, "thread": thread}
    
    return {'message': f'Crawler started for {len(url_list)} URLs'}, 200

@app.route('/stop-crawler', methods=['POST'])
def stop_crawler():
    # Create a list of keys to iterate over
    thread_ids = list(crawler_instances.keys())

    for thread_id in thread_ids:
        instance = crawler_instances[thread_id]
        instance["crawler"].stop()  # Call the stop method of the Crawler instance
        if instance["thread"].is_alive():
            instance["thread"].join()  # Wait for the thread to finish
        del crawler_instances[thread_id]  # Remove the instance from the dictionary

    return {'message': 'All crawlers stopped'}, 200

@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        if file.filename.endswith('.txt'):
            filename = file.filename
            file.save(os.path.join(r'..\backend\settings', filename))
            return {'message': 'File uploaded successfully'}, 200
        return {'message': 'Invalid file'}, 400
    return {'message': 'No file was uploaded'}, 400



    

     #socketio.start_background_task(crawl, app, socketio, url='https://www.ipleiria.pt/', output_dir='C:/Users/josem/Desktop/Webcrawler/backend/pdfcrawler/crawler/crawling_test', method='rendered')
   
    # return {'message': 'Crawler started'}, 200

@app.route('/soc', methods=['GET'])
def test_socket():
    socketio.emit('test_event', {'message': 'Test message from server'})
    return {'message': 'WebSocket test event emitted'}, 200




if __name__ == '__main__':
      socketio.run(app, host='127.0.0.1', port=5000)
      
