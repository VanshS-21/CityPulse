# PowerShell script to set up the Google Cloud environment and apply Terraform configuration

# Check if gcloud is installed
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Error "Google Cloud SDK is not installed. Please install it from https://cloud.google.com/sdk/docs/install"
    exit 1
}

# Check if terraform is installed
if (-not (Get-Command terraform -ErrorAction SilentlyContinue)) {
    Write-Error "Terraform is not installed. Please install it from https://www.terraform.io/downloads.html"
    exit 1
}

# Check if terraform.tfvars exists
if (-not (Test-Path "terraform.tfvars")) {
    Write-Host "Please create terraform.tfvars file by copying terraform.tfvars.example and filling in your values."
    Copy-Item "terraform.tfvars.example" -Destination "terraform.tfvars" -ErrorAction SilentlyContinue
    Write-Host "I've created terraform.tfvars for you. Please edit it with your project details and run this script again."
    exit 0
}

# Initialize Terraform
Write-Host "Initializing Terraform..." -ForegroundColor Cyan
terraform init

if ($LASTEXITCODE -ne 0) {
    Write-Error "Terraform initialization failed. Please check the error messages above."
    exit 1
}

# Show the execution plan
Write-Host "Showing execution plan..." -ForegroundColor Cyan
terraform plan -out=tfplan

if ($LASTEXITCODE -ne 0) {
    Write-Error "Terraform plan failed. Please check the error messages above."
    exit 1
}

# Ask for confirmation
$confirmation = Read-Host "Do you want to apply these changes? (yes/no)"
if ($confirmation -ne 'yes') {
    Write-Host "Aborting..."
    exit 0
}

# Apply the changes
Write-Host "Applying Terraform configuration..." -ForegroundColor Cyan
terraform apply "tfplan"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  CityPulse Infrastructure Deployed!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    terraform output -json | ConvertFrom-Json | Format-List
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Save the service account key if you need it for local development"
    Write-Host "2. Configure your application with the provided outputs"
    Write-Host "3. Check the README.md for more information"
} else {
    Write-Error "Terraform apply failed. Please check the error messages above."
    exit 1
}
