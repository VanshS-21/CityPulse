#!/bin/bash

# CityPulse Infrastructure Validation Script
# Validates infrastructure configuration and deployment readiness

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Validation counters
ERRORS=0
WARNINGS=0

# Function to increment error counter
add_error() {
    print_error "$1"
    ((ERRORS++))
}

# Function to increment warning counter
add_warning() {
    print_warning "$1"
    ((WARNINGS++))
}

print_status "🔍 CITYPULSE INFRASTRUCTURE VALIDATION"
echo "======================================"
echo ""

# Check 1: Terraform Configuration
print_status "1. Validating Terraform Configuration..."

if [ ! -f "infra/terraform/main.tf" ]; then
    add_error "main.tf not found in infra/terraform/"
else
    print_success "main.tf found"
fi

if [ ! -f "infra/terraform/variables.tf" ]; then
    add_error "variables.tf not found"
else
    print_success "variables.tf found"
fi

if [ ! -f "infra/terraform/resources.tf" ]; then
    add_error "resources.tf not found"
else
    print_success "resources.tf found"
fi

# Check for hardcoded credentials
if grep -r "citypulse-21-90f84cb134a2.json" infra/terraform/ 2>/dev/null; then
    add_error "Hardcoded credentials found in Terraform files"
else
    print_success "No hardcoded credentials found"
fi

# Check 2: Environment Configuration
print_status "2. Validating Environment Configuration..."

if [ ! -f "infra/terraform/terraform.tfvars" ]; then
    if [ -f "infra/terraform/terraform.tfvars.example" ]; then
        add_warning "terraform.tfvars not found, but example exists"
        print_status "Creating terraform.tfvars from example..."
        cp infra/terraform/terraform.tfvars.example infra/terraform/terraform.tfvars
        print_warning "Please edit terraform.tfvars with your actual values"
    else
        add_error "terraform.tfvars and terraform.tfvars.example not found"
    fi
else
    print_success "terraform.tfvars found"
fi

# Check 3: GCP Authentication
print_status "3. Validating GCP Authentication..."

if ! command -v gcloud &> /dev/null; then
    add_error "gcloud CLI not installed"
else
    print_success "gcloud CLI installed"
    
    # Check if authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        add_warning "Not authenticated with gcloud. Run: gcloud auth login"
    else
        print_success "gcloud authenticated"
    fi
    
    # Check application default credentials
    if ! gcloud auth application-default print-access-token &>/dev/null; then
        add_warning "Application Default Credentials not set. Run: gcloud auth application-default login"
    else
        print_success "Application Default Credentials configured"
    fi
fi

# Check 4: Docker Configuration
print_status "4. Validating Docker Configuration..."

if ! command -v docker &> /dev/null; then
    add_error "Docker not installed"
else
    print_success "Docker installed"
    
    if ! docker info &> /dev/null; then
        add_error "Docker daemon not running"
    else
        print_success "Docker daemon running"
    fi
fi

# Check 5: Required Files
print_status "5. Validating Required Files..."

required_files=(
    "server/requirements.txt"
    "server/shared_models.py"
    "infra/docker/Dockerfile"
    "scripts/deploy-production.sh"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        add_error "Required file missing: $file"
    else
        print_success "Found: $file"
    fi
done

# Check 6: Security Validation
print_status "6. Validating Security Configuration..."

# Check for exposed secrets
if find . -name "*.json" -path "*/keys/*" 2>/dev/null | grep -q .; then
    add_error "Credential files found in keys directory"
else
    print_success "No credential files in keys directory"
fi

# Check .gitignore
if [ -f ".gitignore" ]; then
    if grep -q "keys/" .gitignore && grep -q "*.json" .gitignore; then
        print_success ".gitignore properly configured for secrets"
    else
        add_warning ".gitignore may not properly exclude secrets"
    fi
else
    add_error ".gitignore not found"
fi

# Summary
echo ""
print_status "📊 VALIDATION SUMMARY"
echo "===================="

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    print_success "✅ All validations passed! Infrastructure is ready for deployment."
    exit 0
elif [ $ERRORS -eq 0 ]; then
    print_warning "⚠️  Validation completed with $WARNINGS warning(s). Review and proceed with caution."
    exit 0
else
    print_error "❌ Validation failed with $ERRORS error(s) and $WARNINGS warning(s)."
    echo ""
    print_status "Please fix the errors above before proceeding with deployment."
    exit 1
fi
