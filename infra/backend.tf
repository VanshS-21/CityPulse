# Configure the Google Cloud backend for storing Terraform state
terraform {
  backend "gcs" {
    # The bucket will be created manually to avoid circular dependencies
    bucket      = "citypulse-21-tfstate"
    prefix      = "terraform/state"
    credentials = "../keys/service-acc-key.json"
  }
}
