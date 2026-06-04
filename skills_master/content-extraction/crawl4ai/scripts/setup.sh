#!/bin/bash

# Crawl4AI Docker Setup Script
# This script sets up Crawl4AI with Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Crawl4AI Docker Setup Script        ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo ""

# Function to print colored messages
print_info() {
    echo -e "${BLUE}ℹ ${1}${NC}"
}

print_success() {
    echo -e "${GREEN}✓ ${1}${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ ${1}${NC}"
}

print_error() {
    echo -e "${RED}✗ ${1}${NC}"
}

# Check if Docker is installed
check_docker() {
    print_info "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed!"
        echo "Please install Docker from: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed!"
        echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
    
    # Check Docker version
    DOCKER_VERSION=$(docker version --format '{{.Server.Version}}')
    print_info "Docker version: ${DOCKER_VERSION}"
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running!"
        echo "Please start Docker and try again"
        exit 1
    fi
    
    print_success "Docker daemon is running"
}

# Check system resources
check_resources() {
    print_info "Checking system resources..."
    
    # Check available memory
    if command -v free &> /dev/null; then
        TOTAL_MEM=$(free -g | awk '/^Mem:/{print $2}')
        print_info "Total system memory: ${TOTAL_MEM}GB"
        
        if [ "$TOTAL_MEM" -lt 4 ]; then
            print_warning "Less than 4GB RAM detected. Crawl4AI may run slowly."
        else
            print_success "Sufficient memory available"
        fi
    fi
    
    # Check available disk space
    AVAILABLE_SPACE=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    print_info "Available disk space: ${AVAILABLE_SPACE}GB"
    
    if [ "$AVAILABLE_SPACE" -lt 10 ]; then
        print_warning "Less than 10GB disk space available"
    else
        print_success "Sufficient disk space available"
    fi
}

# Create directory structure
create_directories() {
    print_info "Creating directory structure..."
    
    mkdir -p data/downloads
    mkdir -p cache
    mkdir -p logs
    
    print_success "Directories created"
}

# Setup environment file
setup_env() {
    print_info "Setting up environment file..."
    
    if [ -f ".env" ]; then
        print_warning ".env file already exists"
        read -p "Do you want to overwrite it? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Keeping existing .env file"
            return
        fi
    fi
    
    # Copy template
    cp .env.template .env
    print_success ".env file created from template"
    
    # Prompt for API keys
    echo ""
    print_info "Please enter your API keys (press Enter to skip):"
    echo ""
    
    read -p "OpenAI API Key: " OPENAI_KEY
    read -p "Anthropic API Key: " ANTHROPIC_KEY
    read -p "Groq API Key: " GROQ_KEY
    
    # Update .env file
    if [ ! -z "$OPENAI_KEY" ]; then
        sed -i.bak "s/OPENAI_API_KEY=.*/OPENAI_API_KEY=$OPENAI_KEY/" .env
        print_success "OpenAI API key configured"
    fi
    
    if [ ! -z "$ANTHROPIC_KEY" ]; then
        sed -i.bak "s/ANTHROPIC_API_KEY=.*/ANTHROPIC_API_KEY=$ANTHROPIC_KEY/" .env
        print_success "Anthropic API key configured"
    fi
    
    if [ ! -z "$GROQ_KEY" ]; then
        sed -i.bak "s/GROQ_API_KEY=.*/GROQ_API_KEY=$GROQ_KEY/" .env
        print_success "Groq API key configured"
    fi
    
    rm -f .env.bak
}

# Pull Docker images
pull_images() {
    print_info "Pulling Docker images..."
    
    docker-compose pull
    
    print_success "Docker images pulled"
}

# Start services
start_services() {
    print_info "Starting Crawl4AI services..."
    
    docker-compose up -d
    
    print_success "Services started"
}

# Wait for services to be healthy
wait_for_health() {
    print_info "Waiting for services to be healthy..."
    
    MAX_ATTEMPTS=30
    ATTEMPT=0
    
    while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
        if docker-compose ps | grep -q "healthy"; then
            print_success "Services are healthy"
            return 0
        fi
        
        ATTEMPT=$((ATTEMPT + 1))
        echo -n "."
        sleep 2
    done
    
    print_warning "Services may not be fully healthy yet"
    return 1
}

# Test API endpoint
test_api() {
    print_info "Testing API endpoint..."
    
    sleep 5  # Give the service a moment to fully start
    
    if curl -s -f http://localhost:11235/health > /dev/null; then
        print_success "API is responding"
        echo ""
        print_info "Playground UI: http://localhost:11235/playground"
        print_info "API Endpoint: http://localhost:11235/crawl"
    else
        print_warning "API is not responding yet"
        echo "Check logs with: docker-compose logs -f crawl4ai"
    fi
}

# Show usage instructions
show_usage() {
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   Setup Complete!                      ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
    echo ""
    print_info "Quick Start Commands:"
    echo ""
    echo "  View logs:        docker-compose logs -f crawl4ai"
    echo "  Stop services:    docker-compose stop"
    echo "  Start services:   docker-compose start"
    echo "  Restart:          docker-compose restart"
    echo "  Remove:           docker-compose down"
    echo "  Update images:    docker-compose pull && docker-compose up -d"
    echo ""
    print_info "Access Points:"
    echo ""
    echo "  Playground UI:    http://localhost:11235/playground"
    echo "  API Health:       http://localhost:11235/health"
    echo "  API Docs:         http://localhost:11235/docs"
    echo ""
    print_info "Test with curl:"
    echo ""
    echo "  curl -X POST http://localhost:11235/crawl \\"
    echo "    -H 'Content-Type: application/json' \\"
    echo "    -d '{\"urls\": [\"https://example.com\"]}'"
    echo ""
    print_info "For more information, see SKILL.md"
    echo ""
}

# Main execution
main() {
    check_docker
    check_resources
    create_directories
    setup_env
    pull_images
    start_services
    wait_for_health
    test_api
    show_usage
}

# Run main function
main
