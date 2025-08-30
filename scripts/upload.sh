#!/bin/bash

# MYCC Package Upload Script
# Uploads built packages to conda repository using rattler upload

set -e  # Exit on any error

# Configuration
REPO_URL="${PREFIX_SERVER_URL:-https://prefix.dev}"
CHANNEL="${PREFIX_CHANNEL:-meta-forge}"
OUTPUT_DIR="./output"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if packages exist across all platforms
check_packages() {
    local package_type="$1"
    
    if [ ! -d "./output" ]; then
        echo "ERROR: Output directory ./output does not exist" >&2
        echo "Run 'pixi run -e build build-all' to build packages first" >&2
        exit 1
    fi
    
    local basic_packages=()
    local full_packages=()
    local platforms=()
    
    # Find all platform directories (only real package directories)
    for platform_dir in ./output/*/; do
        if [ -d "$platform_dir" ]; then
            local platform=$(basename "$platform_dir")
            
            # Skip non-package directories
            if [[ "$platform" == "bld" || "$platform" == "src_cache" || "$platform" == "test" || "$platform" == "noarch" ]]; then
                continue
            fi
            
            platforms+=("$platform")
            
            # Find basic packages
            local basic_found=false
            for package in "$platform_dir"mycc-*.conda; do
                if [[ -f "$package" && ! "$package" =~ mycc-full ]]; then
                    basic_packages+=("$package")
                    basic_found=true
                    break
                fi
            done
            
            # Find full packages  
            local full_found=false
            for package in "$platform_dir"mycc-full-*.conda; do
                if [[ -f "$package" ]]; then
                    full_packages+=("$package")
                    full_found=true
                    break
                fi
            done
            
            if [ "$basic_found" = false ] || [ "$full_found" = false ]; then
                echo "WARNING: Missing packages for platform: $platform" >&2
            fi
        fi
    done
    
    if [ ${#basic_packages[@]} -eq 0 ] && [ ${#full_packages[@]} -eq 0 ]; then
        echo "ERROR: No packages found in any platform directory" >&2
        echo "Available platforms: ${platforms[*]}" >&2
        exit 1
    fi
    
    # Output to stderr for logging, but return packages to stdout
    echo "Found packages across ${#platforms[@]} platform(s): ${platforms[*]}" >&2
    for package in "${basic_packages[@]}"; do
        echo "  Basic: $(basename "$(dirname "$package")")/$(basename "$package")" >&2
    done
    for package in "${full_packages[@]}"; do
        echo "  Full:  $(basename "$(dirname "$package")")/$(basename "$package")" >&2
    done
    
    # Return packages based on type requested (to stdout)
    case "$package_type" in
        "basic")
            printf '%s\n' "${basic_packages[@]}"
            ;;
        "full") 
            printf '%s\n' "${full_packages[@]}"
            ;;
        *)
            printf '%s\n' "${basic_packages[@]}" "${full_packages[@]}"
            ;;
    esac
}

# Upload packages
upload_packages() {
    local packages=($1)
    
    log_info "Uploading packages to $REPO_URL..."
    
    for package in "${packages[@]}"; do
        log_info "Uploading $(basename "$package")..."
        
        if rattler-build upload prefix "$package" --url "$REPO_URL" --channel "$CHANNEL"; then
            log_success "Successfully uploaded $(basename "$package")"
        else
            log_error "Failed to upload $(basename "$package")"
            exit 1
        fi
    done
}

# Main function
main() {
    log_info "MYCC Package Upload Script"
    log_info "=========================="
    
    # Check if rattler-build is available
    if ! command -v rattler-build &> /dev/null; then
        log_error "rattler-build command not found. Please install rattler-build first:"
        log_info "  pip install rattler-build"
        log_info "  or use: pixi add rattler-build"
        exit 1
    fi
    
    # Parse command line arguments
    case "${1:-all}" in
        "basic")
            log_info "Uploading basic packages from all platforms"
            mapfile -t packages < <(check_packages "basic")
            ;;
        "full")
            log_info "Uploading full packages from all platforms"
            mapfile -t packages < <(check_packages "full")
            ;;
        "all"|"")
            log_info "Uploading all packages from all platforms"
            mapfile -t packages < <(check_packages "all")
            ;;
        "help"|"-h"|"--help")
            echo "Usage: $0 [basic|full|all|help]"
            echo ""
            echo "Options:"
            echo "  basic    Upload only the basic package (mycc)"
            echo "  full     Upload only the full package (mycc-full)"
            echo "  all      Upload both packages (default)"
            echo "  help     Show this help message"
            echo ""
            echo "Environment variables:"
            echo "  PREFIX_SERVER_URL   Server URL (default: https://prefix.dev)"
            echo "  PREFIX_CHANNEL      Channel name (default: meta-forge)"
            echo "  PREFIX_API_KEY      API key for authentication"
            echo ""
            echo "Examples:"
            echo "  $0                    # Upload both packages"
            echo "  $0 basic              # Upload basic package only"
            echo "  $0 full               # Upload full package only"
            echo "  PREFIX_CHANNEL=my-channel $0  # Use custom channel"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            log_info "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
    
    # Show what will be uploaded
    if [ ${#packages[@]} -eq 0 ]; then
        log_error "No packages found to upload"
        exit 1
    fi
    
    echo ""
    log_info "Packages to upload (${#packages[@]} total):"
    for package in "${packages[@]}"; do
        log_info "  $(basename "$(dirname "$package")")/$(basename "$package")"
    done
    
    # Confirm upload
    echo ""
    log_warning "About to upload to: $REPO_URL/$CHANNEL"
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Upload cancelled"
        exit 0
    fi
    
    # Upload packages
    upload_packages "${packages[@]}"
    
    log_success "All packages uploaded successfully!"
    log_info "Packages are now available at: $REPO_URL/$CHANNEL"
}

# Run main function
main "$@"