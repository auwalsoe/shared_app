from google.cloud import storage
def read_file(bucket_name, file_path, client):
    bucket = client.bucket(bucket_name)
    content = bucket.blob(file_path).download_as_string().decode("utf-8")
    return content

def download_blob_as_bytes(bucket_name, source_blob_name, client):
    """Downloads a blob from the bucket and returns its content as bytes."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    content = blob.download_as_bytes()
    return content