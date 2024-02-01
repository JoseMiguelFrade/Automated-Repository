
import warnings
from urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
from pdfcrawler.crawler import crawl
import threading
from flask_socketio import SocketIO
import threading
from pdfcrawler.crawler import crawl
from pdfcrawler.crawler.downloaders import RequestsDownloader
from pdfcrawler.crawler.handlers import ProcessHandler
from dotenv import load_dotenv
from queue import Queue
import gpt_repo  # Importing the gpt_repo module
from pymongo import MongoClient
from pdfcrawler.crawler.helper import parse_result_to_dict
from bson.objectid import ObjectId
import gridfs
import shutil
from io import BytesIO
#import json
load_dotenv()  # Load environment variables from .env file
app = Flask(__name__)

#MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['CyberlawRepo']
documents_collection = db['Documents']
fs = gridfs.GridFS(db)

socketio = SocketIO(app, cors_allowed_origins='*')
CORS(app)


crawler_threads = {}
stop_event = threading.Event()


def worker(queue, app, stop_event, socketio, output_dir, depth, thread_id):
    while not stop_event.is_set() and not queue.empty():
        url = queue.get()
        try:
            crawl(app, stop_event, socketio, url, output_dir, depth)
        finally:
            queue.task_done()



@app.route('/start-crawler', methods=['POST'])
def start_crawler():
    stop_event.clear()  # Reset the event for a new crawling session
    request_data = request.get_json()
    url_list = request_data.get('urls', [])
    depth = request_data.get('depth', 1)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(current_dir, 'crawling_test')

    queue = Queue()
    for url in url_list:
        queue.put(url)

    num_worker_threads = 5
    for i in range(num_worker_threads):
        thread_id = f'thread_{i}'
        thread = threading.Thread(target=worker, args=(queue, app, stop_event, socketio, output_dir, depth, thread_id))
        thread.start()
        crawler_threads[thread_id] = thread

    return {'message': f'Crawler started for {len(url_list)} URLs'}, 200

@app.route('/stop-crawler', methods=['POST'])
def stop_crawler():
    stop_event.set()  # Signal all crawlers to stop

    for thread_id, thread in list(crawler_threads.items()):
        if thread.is_alive():
            thread.join()
        if thread_id in crawler_threads:
            del crawler_threads[thread_id]

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

@app.route('/upload-keywords', methods=['POST'])
def upload_keywords():
    file = request.files.get('file')
    if file and file.filename.endswith('.txt'):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Corrected the path construction
        output_dir = os.path.join(current_dir, 'pdfcrawler', 'crawler', 'keywords')
        os.makedirs(output_dir, exist_ok=True)
        # Always save the file as 'keywords.txt' to ensure only one file exists
        file_path = os.path.join(output_dir, 'keywords.txt')
        file.save(file_path)
        return {'message': 'Keywords uploaded successfully'}, 200
    else:
        return {'message': 'Invalid file'}, 400

# @app.route('/update-repo', methods=['POST'])
# def update_repo():
#     stop_crawler()  # Assuming this is a function you've defined elsewhere

#     # Define directories
#     base_dir = os.path.dirname(os.path.abspath(__file__))
#     accepted_files_dir = os.path.join(base_dir, "accepted_files")
#     rejected_files_dir = os.path.join(base_dir, "rejected_files")
#     os.makedirs(accepted_files_dir, exist_ok=True)
#     os.makedirs(rejected_files_dir, exist_ok=True)

#     # Get the PDF path
#     relative_pdf_path = os.path.join("crawling_test", "diariodarepublica.pt", "testA.pdf")
#     pdf_path = os.path.join(base_dir, relative_pdf_path)

#     # Analyze the document using the function from gpt_repo
#     result = gpt_repo.analyze_document(pdf_path)
#     result_dict = parse_result_to_dict(result)

#     # Check if the document is related
#     if result_dict.get("is_related", "").lower() == "no":
#         # Store in rejected_files directory
#         rejected_file_path = os.path.join(rejected_files_dir, os.path.basename(pdf_path))
#         shutil.copy(pdf_path, rejected_file_path)
#         #delete file from crawling_test
#         os.remove(pdf_path)
#         return jsonify({'result': 'Rejected', 'reason': 'Not related'}), 200
#     else:
#         # Store the PDF in GridFS and MongoDB
#         with open(pdf_path, 'rb') as pdf_file:
#             pdf_file_id = fs.put(pdf_file, filename=os.path.basename(pdf_path))
#             result_dict['pdf_file_id'] = str(pdf_file_id)
#             document_id = documents_collection.insert_one(result_dict).inserted_id

#         # Copy to accepted_files directory
#         accepted_file_path = os.path.join(accepted_files_dir, os.path.basename(pdf_path))
#         shutil.copy(pdf_path, accepted_file_path)
#         #delete file from crawling_test
#         os.remove(pdf_path)
#         return jsonify({'result': 'Success', 'document_id': str(document_id), 'pdf_file_id': str(pdf_file_id)}), 200
@app.route('/update-repo', methods=['POST'])
def update_repo():
    stop_crawler()

    # Define directories
    base_dir = os.path.dirname(os.path.abspath(__file__))
    accepted_files_dir = os.path.join(base_dir, "accepted_files")
    rejected_files_dir = os.path.join(base_dir, "rejected_files")
    specified_subdir = "data.europa.eu" 
    crawling_test_dir = os.path.join(base_dir, "crawling_test", specified_subdir)
    os.makedirs(accepted_files_dir, exist_ok=True)
    os.makedirs(rejected_files_dir, exist_ok=True)

    # Get the list of first 50 PDFs in the specified subdir
    pdf_files = [os.path.join(crawling_test_dir, f) for f in os.listdir(crawling_test_dir) if f.endswith('.pdf')][:10]

    for pdf_path in pdf_files:
        # Analyze the document using the function from gpt_repo
        result = gpt_repo.analyze_document(pdf_path)
        result_dict = parse_result_to_dict(result)

        # Check if the document is related
        #print(result_dict)
        if result_dict.get("is_related", "").lower() == "yes":
                       # Store the PDF in GridFS and MongoDB
            #print("related")
            with open(pdf_path, 'rb') as pdf_file:
                

                pdf_file_id = fs.put(pdf_file, filename=os.path.basename(pdf_path))
                result_dict['pdf_file_id'] = str(pdf_file_id)
                document_id = documents_collection.insert_one(result_dict).inserted_id

                # Move to accepted_files directory
            accepted_file_path = os.path.join(accepted_files_dir, os.path.basename(pdf_path))
            shutil.move(pdf_path, accepted_file_path)
            
        else:
             # Move to rejected_files directory
            rejected_file_path = os.path.join(rejected_files_dir, os.path.basename(pdf_path))
            shutil.move(pdf_path, rejected_file_path)

    return jsonify({'result': 'Update completed'}), 200

@app.route('/get-documents', methods=['GET'])
def get_documents():
    try:
        documents = list(documents_collection.find({}))
        for doc in documents:
            doc['_id'] = str(doc['_id'])
        #print(documents)
        return jsonify({'documents': documents}), 200
    except Exception as e:
        return {'error': str(e)}, 500


@app.route('/get-document/<id>', methods=['GET'])
def get_document(id):
    try:
        # Convert the id string to ObjectId
        object_id = ObjectId(id)
        document = documents_collection.find_one({'_id': object_id})
        if document:
            # Convert ObjectId to string for JSON serialization
            document['_id'] = str(document['_id'])
            #print(document)
           # print(jsonify(document))
            return jsonify(document)
        else:
            return jsonify({'error': 'Document not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/delete-document/<id>', methods=['DELETE'])
def delete_document(id):
    try:
        result = documents_collection.delete_one({'_id': ObjectId(id)})
        if result.deleted_count:
            return jsonify({'message': 'Document successfully deleted'}), 200
        else:
            return jsonify({'error': 'Document not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/update-document/<id>', methods=['PUT'])
def update_document(id):
    try:
        # Convert the id string to ObjectId
        object_id = ObjectId(id)
        
        # Get the update data from the request body
        update_data = request.json

        # Remove the '_id' field from the update data if it exists
        update_data.pop('_id', None)

        # Perform the update in MongoDB
       # Convert related_docs from string to array if necessary
        print(update_data)
        if 'related_docs' in update_data and isinstance(update_data['related_docs'], str):
            update_data['related_docs'] = update_data['related_docs'].split('|')

        elif isinstance(update_data['related_docs'], list) and update_data['related_docs'] and isinstance(update_data['related_docs'][0], str):
            updated_related_docs = []
            for doc in update_data['related_docs']:
                # Extract individual documents from the formatted string
                extracted_docs = doc.replace('|', ' ').split(' ')
                for extracted_doc in extracted_docs:
                    updated_related_docs.append(extracted_doc.strip('<>')) # Remove any leading/trailing angle brackets
            update_data['related_docs'] = updated_related_docs


        result = documents_collection.update_one({'_id': object_id}, {'$set': update_data})

        if result.matched_count:
            return jsonify({'message': 'Document updated successfully'}), 200
        else:
            return jsonify({'error': 'Document not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get-pdf/<doc_id>')
def get_pdf(doc_id):
    try:
        # Retrieve the document from MongoDB to get the GridFS file ID
        document = documents_collection.find_one({'_id': ObjectId(doc_id)})
        if not document:
            return 'Document not found', 404

        # Use the GridFS file ID to retrieve the PDF file
        pdf_file_id = document.get('pdf_file_id')
        if not pdf_file_id:
            return 'PDF file not found', 404

        pdf_file = fs.get(ObjectId(pdf_file_id))
        return Response(pdf_file.read(), mimetype='application/pdf')
    except Exception as e:
        return str(e), 500


@app.route('/regenerateDoc', methods=['POST'])
def regenerate_doc():
    data = request.json
    document_id = ObjectId(data.get('documentId'))
    field = data.get('field')
    temperature = data.get('temperature')
    #print(f"document_id: {document_id}, field: {field}, temperature: {temperature}")
    # Fetch the document from MongoDB
    document = documents_collection.find_one({"_id": document_id})

    if not document:
        return jsonify({'error': 'Document not found'}), 404

    # Fetch the PDF file using GridFS file ID
    pdf_file_id = ObjectId(document.get('pdf_file_id'))
    if not pdf_file_id:
        return jsonify({'error': 'PDF file not found'}), 404

    pdf_file = fs.get(pdf_file_id)
    pdf_data = BytesIO(pdf_file.read())  # Convert the binary data to a BytesIO object

    # Regenerate the specified field
    
    regenerated_text = gpt_repo.regenerate_document_field(pdf_data, field, temperature)

    try:
        key, value = regenerated_text.split(':', 1)
        regenerated_text = {key.strip(): value.strip()}
    except ValueError:
        regenerated_text = {'error': 'Invalid response format'}

    return jsonify({'regeneratedText': regenerated_text}), 200


if __name__ == '__main__':
      socketio.run(app, host='127.0.0.1', port=5000)
      
