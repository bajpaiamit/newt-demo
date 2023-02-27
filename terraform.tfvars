terraform {
  # The configuration for this backend will be filled in by Terragrunt
  required_version = ">= 0.12.18"
  required_providers {
    google = ">= 4.0"
  }
}


variable "project_id" {
  type    = string
  default = "noc-test-project"
}

variable "image_repository" {
  type    = string
  default = "us-central1-docker.pkg.dev"
}


variable "services" {
  default = [
    {
      name  = "nexidia-step1-sftpfileextractor"
      imagetag = "sftp_file_extractor:tag1"
	  cpu = "1000m"   
	  memory = "512Mi"
    },
	{
      name  = "nexidia-step2-sftpfileprocess"
      imagetag = "sftp_file_process:tag1"
	  cpu = "1000m"   
	  memory = "2Gi"
    },{
      name  = "nexidia-step3-decryptandextract"
      imagetag = "decrypt_and_extract:tag1"
	  cpu = "1000m"   
	  memory = "2Gi"
    },{
      name  = "nexidia-step4-gcstobq"
      imagetag = "gcs_to_bq:tag1"
	  cpu = "1000m"   
	  memory = "2Gi"
    },{
      name  = "nexidia-step5-dlpdatacatalog"
      imagetag = "dlp_data_catalog:tag1"
	  cpu = "1000m"   
	  memory = "512Mi"
    },{
      name  = "nexidia-step6-tagresults"
      imagetag = "tag_results:tag1"
	  cpu = "1000m"   
	  memory = "512Mi"
    }
   
  ]
}
resource "google_cloud_run_service" "service" {
  project = "noc-test-project"
  count = length(var.services)
  name     = var.services[count.index].name
  location = "us-central1"
  
  metadata {
    annotations = {
      "run.googleapis.com/ingress": "internal"
    }
  }
  template {
    spec {
      containers {
        #image = "${var.image_repository}/${var.project_id}/cloud-run-repo/${var.services[count.index].imagetag}"
        image = "us-docker.pkg.dev/cloudrun/container/hello"
	    resources {
          limits = {
            cpu = "${var.services[count.index].cpu}"         
            memory = "${var.services[count.index].memory}"    
            
          }
        }
      }
      timeout_seconds = 600
      service_account_name = "test-gke@noc-test-project.iam.gserviceaccount.com"
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
	
}
}
  

output "serviceUrls" {
  value = [for service in google_cloud_run_service.service : service.status[0].url]
}


data "google_iam_policy" "noauth" {
  binding {
    role = "roles/run.invoker"
    members = [
      "serviceAccount:sa-cloudrun-nexidia-rw@eid-dw-dev-a5cf.iam.gserviceaccount.com",
    ]
  }
}
