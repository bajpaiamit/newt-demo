resource "google_pubsub_topic" "topic1" {
  name = "sftp_file_extract"
}

resource "google_pubsub_subscription" "topic1" {
  name  = "sftp_file_extractor_sub"
  topic = google_pubsub_topic.topic1.name
  ack_deadline_seconds = 600

 push_config {
    push_endpoint = "https://nexidia-step1-sftpfileextractor-qdi54elyea-uc.a.run.app"
    oidc_token {
      service_account_email = "test-gke@noc-test-project.iam.gserviceaccount.com"
      }
    }
}

resource "google_pubsub_topic" "topic2" {
  name = "sftp_file_process"
}

resource "google_pubsub_subscription" "topic2" {
  name  = "sftp_file_processor_sub"
  topic = google_pubsub_topic.topic2.name
  ack_deadline_seconds = 600

 push_config {
    push_endpoint = "https://nexidia-step2-sftpfileprocess-qdi54elyea-uc.a.run.app"
    oidc_token {
      service_account_email = "test-gke@noc-test-project.iam.gserviceaccount.com"
      }
    }
}
resource "google_pubsub_topic" "topic3" {
  name = "decrypt_and_extract"
}

resource "google_pubsub_subscription" "topic3" {
  name  = "decrypt_and_extract_sub"
  topic = google_pubsub_topic.topic3.name
  ack_deadline_seconds = 600

 push_config {
    push_endpoint = "https://nexidia-step3-decryptandextract-qdi54elyea-uc.a.run.app"
	oidc_token {
      service_account_email = "test-gke@noc-test-project.iam.gserviceaccount.com"
      }
    }
}

resource "google_pubsub_topic" "topic4" {
  name = "gcs_to_bq"
}

resource "google_pubsub_subscription" "topic4" {
  name  = "gcs_to_bq_sub"
  topic = google_pubsub_topic.topic4.name
  ack_deadline_seconds = 600

 push_config {
    push_endpoint = "https://nexidia-step4-gcstobq-qdi54elyea-uc.a.run.app"
    oidc_token {
      service_account_email = "test-gke@noc-test-project.iam.gserviceaccount.com"
      }
    }
}

resource "google_pubsub_topic" "topic5" {
  name = "dlp_data_catalog"
}

resource "google_pubsub_subscription" "topic5" {
  name  = "dlp_data_catalog_sub"
  topic = google_pubsub_topic.topic5.name
  ack_deadline_seconds = 600

 push_config {
    push_endpoint = "https://nexidia-step5-dlpdatacatalog-qdi54elyea-uc.a.run.app"
    oidc_token {
      service_account_email = "test-gke@noc-test-project.iam.gserviceaccount.com"
      }
    }
}

resource "google_pubsub_topic" "topic6" {
  name = "tag_results"
}

resource "google_pubsub_subscription" "topic6" {
  name  = "tag_results"
  topic = google_pubsub_topic.topic6.name
  ack_deadline_seconds = 600

 push_config {
    push_endpoint = "https://nexidia-step6-tagresults-qdi54elyea-uc.a.run.app"
    oidc_token {
      service_account_email = "test-gke@noc-test-project.iam.gserviceaccount.com"
      }
    }
}

resource "google_cloud_scheduler_job" "job" {
  name        = "Publish-the-message-to-topic1"
  description = "test job"
  schedule    = "0 22 * * *"
  time_zone   = "America/Chicago"

  pubsub_target {
    # topic.id is the topic's full resource name.
    topic_name = google_pubsub_topic.topic1.id
    data       = base64encode("{\"conf_path\": \"gs://tte-eid-d-gcs-nexidia-stage/config/config.json\"}")
  }
 }