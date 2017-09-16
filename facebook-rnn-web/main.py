from flask import Flask, render_template, jsonify, request
from google.appengine.api import datastore_errors, memcache
from google.appengine.ext import ndb
import random


class Message(ndb.Model):
    text = ndb.StringProperty()
    length = ndb.IntegerProperty()
    created = ndb.DateTimeProperty()

smallest_entity_key = memcache.get('smallest_entity_key')
if smallest_entity_key is None:
    smallest_entity_key = Message.query().order(Message.key).get(keys_only=True).integer_id()
    memcache.add('smallest_entity_key', str(smallest_entity_key))

biggest_entity_key = memcache.get('biggest_entity_key')
if biggest_entity_key is None:
    biggest_entity_key = Message.query().order(-Message.key).get(keys_only=True).integer_id()
    memcache.add('biggest_entity_key', str(biggest_entity_key))

app = Flask(__name__)


@app.route('/')
def root_page():
    return render_template('layout.html')


@app.route('/next')
def update_message():
    random_key = ndb.Key('Message', random.randint(int(smallest_entity_key), int(biggest_entity_key)))
    try:
        single_entity = Message.query(Message.key <= random_key).get()
        update_text = single_entity.text
    except(datastore_errors.Timeout, datastore_errors.InternalError):
        update_text = "<span style=\'color: red\'>There was an internal error with the database. Sorry!</span>"
    return jsonify(update=update_text)


if __name__ == '__main__':
    app.run(debug=False)
