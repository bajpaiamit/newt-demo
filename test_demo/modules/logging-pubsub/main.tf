module "log_export" {
  source                 = "terraform-google-modules/log-export/google"
  destination_uri        = "${module.destination.destination_uri}"
  filter                 = "log_id(\"cloudaudit.googleapis.com/activity\") OR log_id(\"cloudaudit.googleapis.com/access_transparency\") OR log_id(\"cloudaudit.googleapis.com/system_event\")" 
  log_sink_name          = "pubsub_logsink"
  parent_resource_id     = var.gcp_project_id
  parent_resource_type   = "project"
  unique_writer_identity = true
}

module "destination" {
  source                   = "terraform-google-modules/log-export/google//modules/pubsub"
  project_id               = var.gcp_project_id
  topic_name               = "sampletest-topic"
  #subscriber_id            = "sa-pubsub-nexidia-rw"
  log_sink_writer_identity = "${module.log_export.writer_identity}"
  create_subscriber        = true
}