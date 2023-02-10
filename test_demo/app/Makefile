ENV=hello
REGION=us-central1
PROCESS_NAME=$(subst _,,${ENV})
DOCKER_REPO=cloud-run-repo
PROJECT_ID=eid-dw-dev-a5cf
MEMORY=512M
STEP=0
PROCESS_SOURCE=nexidia
SERVICE_NAME=${PROCESS_SOURCE}-step${STEP}-${PROCESS_NAME}


build:
	gcloud builds submit --region ${REGION} --config configs/cloudbuild.yaml --substitutions=_REGION=${REGION},\
	_DOCKER_REPO=${DOCKER_REPO},_ENV=${ENV}

deploy:
	gcloud run update service ${SERVICE_NAME} --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/${DOCKER_REPO}/${ENV}:tag1 \
	--region ${REGION} --no-allow-unauthenticated --ingress internal --memory=${MEMORY} --timeout=10m \
	--service-account "sa-cloudrun-nexidia-rw@eid-dw-dev-a5cf.iam.gserviceaccount.com"

test:
	gcloud run update service ${SERVICE_NAME} --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/${DOCKER_REPO}/${ENV}:tag1 \
	--region ${REGION} --allow-unauthenticated

build_sftp_file_extractor:
	make build ENV="sftp_file_extractor"

deploy_sftp_file_extractor:
	make deploy ENV="sftp_file_extractor" STEP="1"

build_sftp_file_process:
	make build ENV="sftp_file_process"

deploy_sftp_file_process:
	make deploy ENV="sftp_file_process" MEMORY="2G" STEP="2"

build_decrypt_and_extract:
	make build ENV="decrypt_and_extract"

deploy_decrypt_and_extract:
	make deploy ENV="decrypt_and_extract" MEMORY="2G" STEP="3"

build_gcs_to_bq:
	make build ENV="gcs_to_bq"

deploy_gcs_to_bq:
	make deploy ENV="gcs_to_bq" MEMORY="2G" STEP="4"

build_dlp_data_catalog:
	make build ENV="dlp_data_catalog"

deploy_dlp_data_catalog:
	make deploy ENV="dlp_data_catalog" STEP="5"

build_tag_results:
	make build ENV="tag_results"

deploy_tag_results:
	make deploy ENV="tag_results" STEP="6"

install_gcs_to_bq:
	make build_gcs_to_bq
	make deploy_gcs_to_bq

install_sftp_file_extractor:
	make build_sftp_file_extractor
	make deploy_sftp_file_extractor

install_sftp_file_process:
	make build_sftp_file_process
	make deploy_sftp_file_process

install_decrypt_and_extract:
	make build_decrypt_and_extract
	make deploy_decrypt_and_extract

install_dlp_data_catalog:
	make build_dlp_data_catalog
	make deploy_dlp_data_catalog

install_tag_results:
	make build_tag_results
	make deploy_tag_results

all:
	make install_sftp_file_extractor
	make install_sftp_file_process
	make install_decrypt_and_extract
	make install_gcs_to_bq
	make install_dlp_data_catalog
	make install_tag_results


deploy_all:
	make deploy_gcs_to_bq
	make deploy_sftp_file_extractor
	make deploy_sftp_file_process
	make deploy_decrypt_and_extract
	make deploy_dlp_data_catalog
	make deploy_tag_results
