resource "google_monitoring_notification_channel" "email" {
  display_name = "Bigquery alert notificatio demo"
  type = "email"
  labels = {
    email_address = "yogesh.gaikar@ttec.com",
	email_address = "amit.bajpai@ttec.com"
  } 
}


resource "google_monitoring_alert_policy" "alert_policy" {
  display_name = "Bigquery error"
  combiner = "OR"
  alert_strategy {
      notification_rate_limit {
        period = "300s"

      }
    }
  conditions {
    display_name = "Bigquery test error"
    condition_matched_log {
	filter = "protoPayload.methodName=\"jobservice.jobcompleted\" AND resource.type=\"bigquery_resource\""
	
	 }
  }
		notification_channels = [
		"${google_monitoring_notification_channel.email.name}"
		]
  documentation {
    mime_type = "text/markdown"
    content   = "This is a notification of error logs"
  }
}




