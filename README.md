# SARA Omnia

The **SARA Omnia** provides an automated process to upload data to Omnia Timeseries API. For more information about **Omnia Timeseries API**, see [Omnia](https://github.com/equinor/OmniaPlant)

## Required Environment Variables

| Env var       | Description                    |
| ------------- | ------------------------------ |
| CLIENT_ID     | Omnia Timeseries Client ID     |
| CLIENT_SECRET | Omnia Timeseries Client Secret |

### Fast API App

App is running default at `localhost:8000/docs`

### Build the Docker image

```bash
docker build -t sara-omnia:test .
```

Export env vars

```bash
export CLIENT_ID="<your-source-storage-account>"
export CLIENT_SECRET="<your-source-storage-connection-string>"
```

### Upload a datapoint to Omnia

```bash
docker run --rm \
    -e CLIENT_ID="$CLIENT_ID" \
    -e CLIENT_SECRET="$CLIENT_SECRET" \
    -e ENVIRONMENT=development \
    sara-omnia:test \
    python main.py \
      --CLIENT_ID "{\"storageAccount\": \"$CLIENT_ID\", \"blobContainer\": \"$BLOB_CONTAINER\", \"blobName\": \"apprentices.jpg\"}" \
      --CLIENT_SECRET "{\"storageAccount\": \"$CLIENT_SECRET\", \"blobContainer\": \"$BLOB_CONTAINER\", \"blobName\": \"apprentices.jpg\"}"
```
