from gcloud import datastore

if __name__ == "__main__":
    client = datastore.Client("facebook-rnn")
    query = client.query(kind="Message")
    query.add_filter("text", "=", "None")
    query.keys_only()
    results = list(query.fetch())
    print("Found "+str(len(results))+" items.")
    print("Deleting entities.")
    for message in results:
        client.delete(message.key)
    print("Done.")