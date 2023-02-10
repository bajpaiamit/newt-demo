gcloud builds submit --region=us-west2 --config configs/cloudbuild_decrypt_and_extract.yaml
gcloud run deploy decryptandextract --image=us-west2-docker.pkg.dev/sbox-jason-blythe/quickstart-docker-repo/decrypt_and_extract:tag1 --region us-central1
