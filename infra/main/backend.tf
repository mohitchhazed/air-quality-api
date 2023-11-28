terraform {
  backend "gcs" {
    bucket = "bucket-tfstate-31d41a3134f954ed"
    prefix = "terraform/state"
  }
}