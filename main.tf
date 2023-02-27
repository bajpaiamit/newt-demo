resource "google_cloud_run_service" "service" {
  project = var.project_id
  count = length(var.services)
  name     = var.services[count.index].name
  location = var.location
  
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
