from flask import Flask
from flask import request, jsonify
#from flask_restful import Resource, Api
import os
import sqlite3

app = Flask(__name__)
app.config["DEBUG"] = True
#api = Api(app)
############## TEST DATA #####################
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# Create some test data for our catalog in the form of a list of dictionaries.
#books = [
#    {'id': 0,
#     'title': 'A Fire Upon the Deep',
#     'author': 'Vernor Vinge',
#     'first_sentence': 'The coldsleep itself was dreamless.',
#     'year_published': '1992'},
#    {'id': 1,
#     'title': 'The Ones Who Walk Away From Omelas',
#     'author': 'Ursula K. Le Guin',
#     'first_sentence': 'With a clamor of bells that set the swallows soaring, the Festival of Summer came to the city Omelas, bright-towered by the sea.',
#     'published': '1973'},
#    {'id': 2,
#     'title': 'Dhalgren',
#     'author': 'Samuel R. Delany',
#     'first_sentence': 'to wound the autumnal city.',
#     'published': '1975'},
#    {'id': 99,
#     'title': 'No record found',
#     'author': 'No record found',
#     'first_sentence': 'No record found',
#     'published': 'No record found'}
#]

##############################################
###############ROUTES#########################
#Route 1: Front Page
@app.route('/', methods=['GET'])
def home():
    return "<h1>Distant Reading Archive</h1><p>This site is a prototype API for distant reading of science fiction novels.</p>"
# A route to return all of the available entries in our catalog.

#Route 2: JSON all data
@app.route('/api/v1/resources/books/all', methods=['GET'])
def api_all():
    conn = sqlite3.connect('books.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_books = cur.execute('SELECT * FROM books;').fetchall()
    return jsonify(all_books)

#Route 3: JSON Lookup
#@app.route('/api/v1/resources/books', methods=['GET'])
#def api_id():
#    if 'id' in request.args:
#        id = int(request.args['id'])
#    else:
#        return "Error: No id field provided. Please specify an id."
#    results = []
#    for book in books:
#        if book['id'] == id:
#            results.append(book)
#    return jsonify(results)
@app.route('/api/v1/resources/books', methods=['GET'])
def api_filter():
    query_parameters = request.args

    id = query_parameters.get('id')
    published = query_parameters.get('published')
    author = query_parameters.get('author')

    query = "SELECT * FROM books WHERE"
    to_filter = []

    if id:
        query += ' id=? AND'
        to_filter.append(id)
    if published:
        query += ' published=? AND'
        to_filter.append(published)
    if author:
        query += ' author=? AND'
        to_filter.append(author)
    if not (id or published or author):
        return page_not_found(404)

    query = query[:-4] + ';'

    conn = sqlite3.connect('books.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    results = cur.execute(query, to_filter).fetchall()

    return jsonify(results)
#Route 4: Error handling
@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

###############################################

#class sayHello(Resource):
#    def get(self):
#        return {'hello': 'kube-updated'}

#api.add_resource(sayHello, '/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3000)))
#app.run()
