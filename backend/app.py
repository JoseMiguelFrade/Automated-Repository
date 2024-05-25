
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
from pdfcrawler.crawler.helper import parse_result_to_dict, compute_md5, format_date
from bson.objectid import ObjectId
from RSSConsumer import parse_rss_feed_EurLex, parse_rss_feed_DRE, extract_eurlex_links, extract_dre_links
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


def worker(queue, app, stop_event, socketio, output_dir, depth, thread_id, crawl_in_depth):
    while not stop_event.is_set() and not queue.empty():
        url = queue.get()
        try:
            crawl(app, stop_event, socketio, url, output_dir, depth, crawl_in_depth=crawl_in_depth)
        finally:
            queue.task_done()



@app.route('/start-crawler', methods=['POST'])
def start_crawler():
    stop_event.clear()  # Reset the event for a new crawling session
    request_data = request.get_json()
    url_list = request_data.get('urls', [])
    depth = request_data.get('depth', 1)
    crawl_in_depth = request_data.get('crawl_in_depth', False)
    print(f"crawl_in_depth: {crawl_in_depth}")

    # Check if the url_list contains a single concatenated URL string
    if len(url_list) == 1 and ('http://' in url_list[0] or 'https://' in url_list[0]):
        urls = url_list[0].split('http://')
        url_list = []
        for url in urls:
            if url:
                url_list.append('http://' + url if 'http://' not in url else url)
        urls = url_list[0].split('https://')
        url_list = []
        for url in urls:
            if url:
                url_list.append('https://' + url if 'https://' not in url else url)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(current_dir, 'crawling_test')

    queue = Queue()
    for url in url_list:
        queue.put(url)

    num_worker_threads = 5
    for i in range(num_worker_threads):
        thread_id = f'thread_{i}'
        thread = threading.Thread(target=worker, args=(queue, app, stop_event, socketio, output_dir, depth, thread_id, crawl_in_depth))
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

@app.route('/update-repo', methods=['POST'])
def update_repo():
    stop_crawler()
    subdir = request.json.get('subdir')
    total_queries = int(request.json.get('total_queries', 10))  # Default to 10 if not provided
    gpt_3_5_count = int(request.json.get('gpt_3_5_count', 4))  # Default to 4 if not provided
    if not subdir:
        return jsonify({'error': 'Missing subdir parameter'}), 400

    # Define directories
    base_dir = os.path.dirname(os.path.abspath(__file__))
    accepted_files_dir = os.path.join(base_dir, "accepted_files")
    rejected_files_dir = os.path.join(base_dir, "rejected_files")
    duplicated_files_dir = os.path.join(base_dir, "duplicated_files")
    crawling_test_dir = os.path.join(base_dir, "crawling_test", subdir)
    os.makedirs(accepted_files_dir, exist_ok=True)
    os.makedirs(rejected_files_dir, exist_ok=True)
    os.makedirs(duplicated_files_dir, exist_ok=True)

    # Get the list of first 50 PDFs in the specified subdir
    pdf_files = [os.path.join(crawling_test_dir, f) for f in os.listdir(crawling_test_dir) if f.endswith('.pdf')][:total_queries]

    for pdf_path in pdf_files:
        try:
            # Compute MD5 hash of the PDF file
            with open(pdf_path, 'rb') as pdf_file:
                pdf_data = pdf_file.read()
                pdf_hash = compute_md5(pdf_data)

            # Check for duplicate hash in the Documents collection
            if documents_collection.find_one({'pdf_hash': pdf_hash}):
                # Move to duplicated_files directory
                duplicated_file_path = os.path.join(duplicated_files_dir, os.path.basename(pdf_path))
                shutil.move(pdf_path, duplicated_file_path)
                print(f"Duplicated document {os.path.basename(pdf_path)} moved to duplicated_files.")
                continue

            # Analyze the document using the function from gpt_repo
            result = gpt_repo.analyze_document(pdf_path, total_queries, gpt_3_5_count)
            result_dict = parse_result_to_dict(result)

            # Check if the document is related
            if result_dict.get("is_related", "").lower() == "yes":
                # Store the PDF in GridFS and MongoDB
                with open(pdf_path, 'rb') as pdf_file:
                    pdf_file_id = fs.put(pdf_file, filename=os.path.basename(pdf_path))
                    result_dict['pdf_file_id'] = str(pdf_file_id)

                # Fetch the upload date from GridFS
                fs_files_collection = db['fs.files']
                fs_file_entry = fs_files_collection.find_one({'_id': pdf_file_id})
                upload_date = fs_file_entry.get('uploadDate')
                if upload_date:
                    formatted_upload_date = format_date(upload_date)
                    result_dict['upload_date'] = formatted_upload_date

                # Add the computed MD5 hash to the document
                result_dict['pdf_hash'] = pdf_hash

                # Insert the document into the Documents collection
                document_id = documents_collection.insert_one(result_dict).inserted_id

                # Move to accepted_files directory
                accepted_file_path = os.path.join(accepted_files_dir, os.path.basename(pdf_path))
                shutil.move(pdf_path, accepted_file_path)
                print(f"Accepted document {os.path.basename(pdf_path)} added to database with ID {document_id}.")

            else:
                # Move to rejected_files directory
                rejected_file_path = os.path.join(rejected_files_dir, os.path.basename(pdf_path))
                shutil.move(pdf_path, rejected_file_path)
                print(f"Rejected document {os.path.basename(pdf_path)} moved to rejected_files.")

        except gridfs.NoFile:
            print(f"No file found for id {pdf_file_id}")
        except Exception as e:
            print(f"Error processing document {os.path.basename(pdf_path)}: {e}")

    return jsonify({'result': 'Update completed'}), 200


# @app.route('/update-repo', methods=['POST'])
# def update_repo():
#     stop_crawler()
#     subdir = request.json.get('subdir')
#     total_queries = int(request.json.get('total_queries', 10))  # Default to 10 if not provided
#     gpt_3_5_count = int(request.json.get('gpt_3_5_count', 4))  # Default to 4 if not provided
#     if not subdir:
#         return jsonify({'error': 'Missing subdir parameter'}), 400
#     # Define directories
#     base_dir = os.path.dirname(os.path.abspath(__file__))
#     accepted_files_dir = os.path.join(base_dir, "accepted_files")
#     rejected_files_dir = os.path.join(base_dir, "rejected_files")
#     #specified_subdir = "data.europa.eu"
#     #specified_subdir = "diariodarepublica.pt" 
#     crawling_test_dir = os.path.join(base_dir, "crawling_test", subdir)
#     os.makedirs(accepted_files_dir, exist_ok=True)
#     os.makedirs(rejected_files_dir, exist_ok=True)

#     # Get the list of first 50 PDFs in the specified subdir
#     pdf_files = [os.path.join(crawling_test_dir, f) for f in os.listdir(crawling_test_dir) if f.endswith('.pdf')][:10]

#     for pdf_path in pdf_files:
#         # Analyze the document using the function from gpt_repo
#         result = gpt_repo.analyze_document(pdf_path,total_queries, gpt_3_5_count)
#         result_dict = parse_result_to_dict(result)

#         # Check if the document is related
#         #print(result_dict)
#         if result_dict.get("is_related", "").lower() == "yes":
#                        # Store the PDF in GridFS and MongoDB
#             #print("related")
#             with open(pdf_path, 'rb') as pdf_file:
                

#                 pdf_file_id = fs.put(pdf_file, filename=os.path.basename(pdf_path))
#                 result_dict['pdf_file_id'] = str(pdf_file_id)
#                 document_id = documents_collection.insert_one(result_dict).inserted_id

#                 # Move to accepted_files directory
#             accepted_file_path = os.path.join(accepted_files_dir, os.path.basename(pdf_path))
#             shutil.move(pdf_path, accepted_file_path)
            
#         else:
#              # Move to rejected_files directory
#             rejected_file_path = os.path.join(rejected_files_dir, os.path.basename(pdf_path))
#             shutil.move(pdf_path, rejected_file_path)

#     return jsonify({'result': 'Update completed'}), 200

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
    fs_files_collection = db['fs.files']
    try:
        # Fetch the document from the Documents collection
        document = documents_collection.find_one({'_id': ObjectId(id)})
        if not document:
            return jsonify({'error': 'Document not found'}), 404

        pdf_file_id = document.get('pdf_file_id')
        if not pdf_file_id:
            return jsonify({'error': 'PDF file ID not found in document'}), 404

    
        file_document = fs_files_collection.find_one({'_id': ObjectId(pdf_file_id)})
        if not file_document:
            return jsonify({'error': 'File not found in fs.files collection'}), 404

        filename = file_document.get('filename')
        if not filename:
            return jsonify({'error': 'Filename not found'}), 404

        # Define directories
        base_dir = os.path.dirname(os.path.abspath(__file__))
        accepted_files_dir = os.path.join(base_dir, "accepted_files")
        manual_deleted_dir = os.path.join(base_dir, "manual_deleted")
        os.makedirs(manual_deleted_dir, exist_ok=True)

        # Move file from accepted_files to manual_deleted
        source_path = os.path.join(accepted_files_dir, filename)
        destination_path = os.path.join(manual_deleted_dir, filename)

        # Check if the file exists before moving
        if os.path.exists(source_path):
            shutil.move(source_path, destination_path)
        else:
            return jsonify({'error': 'File not found in accepted_files directory'}), 404

        # Delete document from collections
        documents_collection.delete_one({'_id': ObjectId(id)})
        fs_files_collection.delete_one({'_id': ObjectId(pdf_file_id)})

        return jsonify({'message': 'Document successfully deleted and moved to manual_deleted directory'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/update-document/<id>', methods=['PUT'])
def update_document(id):
    try:
        
        # Convert the id string to ObjectId
        object_id = ObjectId(id)
        
        # Get the update data from the request body
        update_data = request.json
        #print(update_data)
        # Remove the '_id' field from the update data if it exists
        update_data.pop('_id', None)

        # Perform the update in MongoDB
       # Convert related_docs from string to array if necessary
        #print(update_data)
        if 'related_docs' in update_data and isinstance(update_data['related_docs'], str):
            update_data['related_docs'] = update_data['related_docs'].split('|')

        elif isinstance(update_data['related_docs'], list) and update_data['related_docs'] and isinstance(update_data['related_docs'][0], str):
            updated_related_docs = []
            for doc in update_data['related_docs']:
                # Extract individual documents from the formatted string
                extracted_docs = doc.split('|')
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
    #print(data)
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

@app.route('/areas', methods=['GET'])
def get_areas():
    pipeline = [
        # Split the 'area' field if it contains '/'
        {"$project": {
            "areas": {
                "$split": ["$area", "/"]
            }
        }},
        # Unwind the array to handle documents with multiple areas
        {"$unwind": "$areas"},
        # Trim any leading or trailing whitespace
        {"$project": {
            "area": {"$trim": {"input": "$areas"}}
        }},
        # Group by the trimmed 'area' and count each one
        {"$group": {"_id": "$area", "count": {"$sum": 1}}}
    ]
    results = documents_collection.aggregate(pipeline)
    data = {result["_id"]: result["count"] for result in results}
    return jsonify(data)

@app.route('/document_counts_by_year', methods=['GET'])
def get_document_counts_by_year():
    origin = request.args.get('origin')
    pipeline = []

    # Adjust the $match stage to include both "EU" and "European Union" if the origin is "EU"
    if origin:
        if origin.lower() == 'eu':
            pipeline.append({"$match": {"origin": {"$in": ["EU", "European Union"]}}})
        elif origin.lower() != 'all':
            pipeline.append({"$match": {"origin": origin}})

    # Continue with the rest of the pipeline
    pipeline.extend([
        {
            "$project": {
                "year": {
                    "$dateToString": {
                        "format": "%Y",
                        "date": {
                            "$dateFromString": {
                                "dateString": "$date",
                                "format": "%d/%m/%Y"
                            }
                        }
                    }
                }
            }
        },
        {
            "$group": {
                "_id": "$year",
                "count": {"$sum": 1}
            }
        },
        {
            "$sort": {"_id": 1}
        }
    ])

    results = documents_collection.aggregate(pipeline)
    data = [{"year": result["_id"], "count": result["count"]} for result in results]
    return jsonify(data)

@app.route('/area_counts_by_year', methods=['GET'])
def get_area_counts_by_year():
    pipeline = [
        {
            "$addFields": {
                "parsedDate": {
                    "$dateFromString": {
                        "dateString": "$date",
                        "format": "%d/%m/%Y"
                    }
                }
            }
        },
        {
            "$addFields": {
                "year": {
                    "$dateToString": {
                        "format": "%Y",
                        "date": "$parsedDate"
                    }
                }
            }
        },
        {
            "$project": {
                "year": 1,
                "areas": {"$split": ["$area", "/"]}
            }
        },
        {"$unwind": "$areas"},
        {
            "$project": {
                "year": 1,
                "area": {"$trim": {"input": "$areas"}}
            }
        },
        {
            "$group": {
                "_id": {
                    "year": "$year",
                    "area": "$area"
                },
                "count": {"$sum": 1}
            }
        },
        {
            "$group": {
                "_id": "$_id.year",
                "areas": {
                    "$push": {
                        "area": "$_id.area",
                        "count": "$count"
                    }
                }
            }
        },
        {
            "$sort": {"_id": 1}
        }
    ]
    results = documents_collection.aggregate(pipeline)
    data = [
        {
            "year": result["_id"],
            "areas": result["areas"]
        } for result in results
    ]
    return jsonify(data)

@app.route('/list-subdirs', methods=['GET'])
def list_subdirs():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    crawling_test_dir = os.path.join(base_dir, "crawling_test")
    
    # List only directories
    subdirs = [d for d in os.listdir(crawling_test_dir) if os.path.isdir(os.path.join(crawling_test_dir, d))]
    
    return jsonify(subdirs)

@app.route('/fetch-recent-documents', methods=['GET'])
def fetch_recent_documents():
    try:
        eurlex_items = parse_rss_feed_EurLex()
        tretas_items = parse_rss_feed_DRE()
        all_items = eurlex_items + tretas_items
        return jsonify(all_items)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/pre-crawl', methods=['POST'])
def pre_crawl():
    data = request.json
    print(f"Received data for pre-crawl: {data}")

    eurlex_links = [item['link'] for item in data if item['source'] == 'EurLex']
    dre_links = [item['link'] for item in data if item['source'] == 'DRE']

    eurlex_extracted_links = extract_eurlex_links(eurlex_links)
    dre_extracted_links = extract_dre_links(dre_links)

    all_links = eurlex_extracted_links + dre_extracted_links
    print(f"All extracted links: {all_links}")

    response = jsonify({
        'urls': all_links if all_links else [],  # Ensure it's an array
        'message': 'Data processed successfully'
    })
    return response


if __name__ == '__main__':
      socketio.run(app, host='127.0.0.1', port=5000)
      
