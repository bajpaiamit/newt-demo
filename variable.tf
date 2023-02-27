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

