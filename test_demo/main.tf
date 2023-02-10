terraform {
  required_version = ">= 1.1.2"
   }


provider "google" {
  project     = var.gcp_project_id
  credentials = file(var.gcp_credentials)
  region      = var.gcp_region
 }

terraform {
  backend "gcs" {
    bucket = "bamitec-tfstate-qa"
    prefix = "terraform/state"
	
  } 
}

/*
module "Cloud_run" {
	source = "./modules/cloud-run"
	}
*/
module "pub-sub" {
	source = "./modules/pub-sub"
	}
/*
module "log_export"{
	source = "./modules/logging" 
	gcp_project_id = var.gcp_project_id
	}
	
module "Alertt_notification"{
	source = "./modules/Alerting-notification"
	}
 
*/


