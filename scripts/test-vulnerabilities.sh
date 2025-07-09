#!/bin/bash

# Comprehensive vulnerability testing script
# Tests multiple Docker images and provides detailed security analysis

set -e

echo "🔍 CITYPULSE VULNERABILITY TESTING SUITE"
echo "========================================"

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

# Function to install Trivy if not present
install_trivy() {
    if ! command -v trivy &> /dev/null; then
        print_status "Installing Trivy..."
        curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
        print_success "Trivy installed successfully"
    else
        print_status "Trivy already installed"
    fi
}

# Function to scan image with Trivy
scan_image() {
    local image_name=$1
    local dockerfile=$2
    
    print_status "Building image: $image_name"
    if docker build -f "$dockerfile" -t "$image_name" .; then
        print_success "Image built successfully: $image_name"
    else
        print_error "Failed to build image: $image_name"
        return 1
    fi
    
    print_status "Scanning $image_name for vulnerabilities..."
    
    # Comprehensive scan with multiple output formats
    echo "----------------------------------------"
    echo "VULNERABILITY SCAN RESULTS: $image_name"
    echo "----------------------------------------"
    
    # Basic vulnerability scan
    trivy image --severity HIGH,CRITICAL "$image_name"
    
    # Detailed JSON report
    trivy image --format json --output "${image_name//[^a-zA-Z0-9]/_}_scan.json" "$image_name"
    
    # Count vulnerabilities
    local vuln_count=$(trivy image --format json "$image_name" 2>/dev/null | jq '[.Results[]?.Vulnerabilities[]?] | length' 2>/dev/null || echo "unknown")
    
    echo "Total vulnerabilities found: $vuln_count"
    
    # Test functionality
    print_status "Testing Apache Beam compatibility..."
    if docker run --rm "$image_name" python -c "import apache_beam; print('Apache Beam import successful')"; then
        print_success "Apache Beam compatibility confirmed"
    else
        print_error "Apache Beam compatibility failed"
    fi
    
    echo ""
}

# Function to compare results
compare_results() {
    print_status "VULNERABILITY COMPARISON SUMMARY"
    echo "================================"
    
    for json_file in *_scan.json; do
        if [[ -f "$json_file" ]]; then
            local image_name=$(basename "$json_file" _scan.json)
            local vuln_count=$(jq '[.Results[]?.Vulnerabilities[]?] | length' "$json_file" 2>/dev/null || echo "0")
            local critical_count=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity == "CRITICAL")] | length' "$json_file" 2>/dev/null || echo "0")
            local high_count=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity == "HIGH")] | length' "$json_file" 2>/dev/null || echo "0")
            
            printf "%-25s | Total: %-3s | Critical: %-3s | High: %-3s\n" "$image_name" "$vuln_count" "$critical_count" "$high_count"
        fi
    done
    
    echo ""
    print_status "RECOMMENDATION:"
    echo "Choose the image with the lowest vulnerability count."
    echo "Distroless images typically have 0-1 vulnerabilities."
}

# Main execution
main() {
    print_status "Starting vulnerability assessment..."
    
    # Install Trivy
    install_trivy
    
    # Test different approaches
    print_status "Testing multiple Docker approaches..."
    
    # Test distroless optimized (should have minimal vulnerabilities)
    if [[ -f "Dockerfile.distroless-optimized" ]]; then
        scan_image "citypulse:distroless-optimized" "Dockerfile.distroless-optimized"
    fi
    
    # Test Trivy-optimized Alpine
    if [[ -f "Dockerfile.trivy-optimized" ]]; then
        scan_image "citypulse:trivy-optimized" "Dockerfile.trivy-optimized"
    fi
    
    # Test existing minimal approach
    if [[ -f "Dockerfile.minimal" ]]; then
        scan_image "citypulse:minimal" "Dockerfile.minimal"
    fi
    
    # Test current Alpine approach
    if [[ -f "Dockerfile" ]]; then
        scan_image "citypulse:alpine" "Dockerfile"
    fi
    
    # Compare all results
    compare_results
    
    print_success "Vulnerability assessment complete!"
    print_status "Check the *_scan.json files for detailed reports."
}

# Run main function
main "$@"
