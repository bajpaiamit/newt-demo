# TTEC-Revenueleakage

### The DOCKERFILE
We housed all of the microservice code in a single respository. In order to make extensibility  easier, we templated a 
DOCKERFILE to build a particular image based on `build_args`. This DOCKERFILE can be extended out as much as needed to 
add functionality as time goes on. Extending is as easy as adding a new microservice folder and adding a new stage in 
the DOCKERFILE that corresponds to the stage name.

### Build the image
We wrote a quick Makefile to build and deploy the images. This is an example to build an image:  
`make build ENV="sftp_extract" PROJECT_ID="YOUR_PROJECT_ID" DOCKER_REPO="YOUR-DOCKER-REPO" REGION="us-west2"`

Where `ENV` corresponds to the folder that the build files are in. This will create and image, tag it, and submit the 
image to Artifact Registry. The remaining variables can be passed at execution time or set to static fields in the 
Makefile itself to ease execution. 

To deploy the cloud run service, simply run:  
`make deploy ENV="sftp_extract" PROJECT_ID="YOUR_PROJECT_ID"`  

### Running a Job  
The base processing runs off of a configuration file. That file, along with potentially other parameters, are passed to 
the Cloud Run service via PubSub. This is an example configuration:  
```json
{
    "decrypt_and_extract": {
        "output_bucket": "output-file-bucket",
        "project_id": "some-processing-project",
        "secret_file_path": "gs://secret-bucket/path/to/secret",
        "secret_id": "gpg-secret",
        "next_topic": "dlp_data_catalog"
    },
    "dlp_data_catalog": {
        "project_id": "some-processing-project",
        "location": "global",
        "bucket_name": "output-file-bucket",
        "min_likelihood": "POSSIBLE",
        "next_topic": "gcs_to_bq"
    },
    "gcs_to_bq": {
        "project_id": "some-processing-project",
        "metadata-file": "add_metadata.sql"
    },
    "sftp_extract": {
        "project_id": "some-processing-project",
        "secret_id": "sftp-credentials",
        "output_bucket": "output-file-bucket",
        "next_topic": "decrypt_and_extract"
    }
}
```

That would get saved into a GCS bucket, and then the process would get triggered by sending a message to PubSub:
```json
{
  "conf_path": "gs://micro-service-process-config/config.json"
} 
```
The value, in this case, is the path where the config is stored.