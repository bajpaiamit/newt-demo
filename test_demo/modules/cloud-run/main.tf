resource "google_cloud_run_service" "sftpfileextractor" {
  name     = "nexidia-step1-sftpfileextractor"
  location = "us-central1"
  metadata {
    annotations = {
      "run.googleapis.com/ingress": "internal"
    }
  }
  template {
    spec {
      containers {
        image = "us-central1-docker.pkg.dev/eid-dw-dev-a5cf/cloud-run-repo/sftp_file_extractor:tag1"
		resources {
          limits = {
            cpu = "1000m"         
            memory = "512Mi"
          }
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
	
}
}
	output "url1" {
	value = "${google_cloud_run_service.sftpfileextractor.status[0].url}"
	
}

resource "google_cloud_run_service" "sftpfileprocess" {
  name     = "nexidia-step2-sftpfileprocess"
  location = "us-central1"
  metadata {
    annotations = {
      "run.googleapis.com/ingress": "internal"
    }
  }
  template {
    spec {
      containers {
        image = "us-central1-docker.pkg.dev/eid-dw-dev-a5cf/cloud-run-repo/sftp_file_process:tag1"
		resources {
          limits = {
            cpu = "1000m"         
            memory = "2Gi"
          }
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
	
}
}
	output "url2" {
    value = "${google_cloud_run_service.sftpfileprocess.status[0].url}"

}

resource "google_cloud_run_service" "decryptandextract" {
  name     = "nexidia-step3-decryptandextract"
  location = "us-central1"
  metadata {
    annotations = {
      "run.googleapis.com/ingress": "internal"
    }
  }
  template {
    spec {
      containers {
        image = "us-central1-docker.pkg.dev/eid-dw-dev-a5cf/cloud-run-repo/decrypt_and_extract:tag1"
		resources {
          limits = {
            cpu = "1000m"         
            memory = "2Gi"
          }
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}
output "url3" {
  value = "${google_cloud_run_service.decryptandextract.status[0].url}"
}

resource "google_cloud_run_service" "gcstobq" {
  name     = "nexidia-step4-gcstobq"
  location = "us-central1"
  metadata {
    annotations = {
      "run.googleapis.com/ingress": "internal"
    }
  }
  template {
    spec {
      containers {
        image = "us-central1-docker.pkg.dev/eid-dw-dev-a5cf/cloud-run-repo/gcs_to_bq:tag1"
		resources {
          limits = {
            cpu = "1000m"         
            memory = "2Gi"
          }
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}
output "url4" {
  value = "${google_cloud_run_service.gcstobq.status[0].url}"
}

resource "google_cloud_run_service" "dlpdatacatalog" {
  name     = "nexidia-step5-dlpdatacatalog"
  location = "us-central1"
  metadata {
    annotations = {
      "run.googleapis.com/ingress": "internal"
    }
  }
  template {
    spec {
      containers {
        image = "us-central1-docker.pkg.dev/eid-dw-dev-a5cf/cloud-run-repo/dlp_data_catalog:tag1"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}
output "url5" {
  value = "${google_cloud_run_service.dlpdatacatalog.status[0].url}"
}

resource "google_cloud_run_service" "tagresults" {
  name     = "nexidia-step6-tagresults"
  location = "us-central1"
  metadata {
    annotations = {
      "run.googleapis.com/ingress": "internal"
    }
  }
  template {
    spec {
      containers {
        image = "us-central1-docker.pkg.dev/eid-dw-dev-a5cf/cloud-run-repo/tag_results:tag1"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

output "url6" {
  value = "${google_cloud_run_service.tagresults.status[0].url}"
}



data "google_iam_policy" "noauth" {
  binding {
    role = "roles/run.invoker"
    members = [
      "serviceAccount:sa-terraform-devops-rw@eid-dw-dev-a5cf.iam.gserviceaccount.com",
    ]
  }
}




/*resource "google_cloud_scheduler_job" "scheduled_job" {
  name             = "cloudrun-scheduler"
  description      = "It will show the tags"
  schedule         = "* 22 * * *"
  time_zone        = "America/Chicago"

  http_target {
    http_method = "GET"
      uri = "${google_cloud_run_service.sftpfileextractor.status[0].url}"
	 
    oidc_token {
      service_account_email = "sa-terraform-devops-rw@eid-dw-dev-a5cf.iam.gserviceaccount.com"
    }
  }
}

*/






















