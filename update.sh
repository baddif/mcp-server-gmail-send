#!/bin/bash
# Gmail Send Skill - Update Script
# Automated update process with backup and rollback capability

set -e  # Exit on error

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

echo "🔄 Gmail Send Skill - Update Script"
echo "==================================="

# Get current directory
UPDATE_DIR=$(pwd)
BACKUP_DIR="$UPDATE_DIR/backup"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

print_info "Update directory: $UPDATE_DIR"
print_info "Backup directory: $BACKUP_DIR"

# Check if we're in the right directory
if [ ! -f "gmail_send_skill.py" ]; then
    print_error "Not in Gmail Send Skill directory. Please cd to the correct directory."
    exit 1
fi

# Create backup directory if it doesn't exist
if [ ! -d "$BACKUP_DIR" ]; then
    mkdir -p "$BACKUP_DIR"
    print_status "Created backup directory"
fi

# Function to backup files
backup_files() {
    print_info "Creating backup..."
    
    # Create timestamped backup
    BACKUP_FILE="$BACKUP_DIR/gmail_send_backup_$TIMESTAMP.tar.gz"
    
    # Backup current installation
    tar -czf "$BACKUP_FILE" \
        *.py *.json *.md *.txt *.sh \
        --exclude=backup \
        --exclude=__pycache__ \
        --exclude=*.log \
        2>/dev/null || true
    
    if [ -f "$BACKUP_FILE" ]; then
        print_status "Backup created: $BACKUP_FILE"
    else
        print_warning "Backup creation failed, continuing anyway..."
    fi
    
    # Backup Claude Desktop config if it exists
    CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
    if [ -f "$CLAUDE_CONFIG" ]; then
        cp "$CLAUDE_CONFIG" "$BACKUP_DIR/claude_desktop_config_$TIMESTAMP.json"
        print_status "Claude Desktop config backed up"
    fi
}

# Function to check current version
check_current_version() {
    print_info "Checking current version..."
    
    if [ -f "version.py" ]; then
        CURRENT_VERSION=$(python3 version.py --version 2>/dev/null || echo "unknown")
        print_status "Current version: $CURRENT_VERSION"
    else
        print_warning "Version file not found"
        CURRENT_VERSION="unknown"
    fi
}

# Function to update from git
update_from_git() {
    print_info "Updating from Git repository..."
    
    # Check if git repository
    if [ -d ".git" ]; then
        # Stash any local changes
        git stash push -m "Auto-stash before update $TIMESTAMP" 2>/dev/null || true
        
        # Fetch latest changes
        if git fetch origin main; then
            print_status "Fetched latest changes"
        else
            print_error "Failed to fetch from Git repository"
            return 1
        fi
        
        # Check for conflicts
        if git merge --dry-run origin/main >/dev/null 2>&1; then
            # Safe to merge
            git merge origin/main
            print_status "Updated from Git successfully"
        else
            print_error "Merge conflicts detected. Manual intervention required."
            print_info "Run 'git status' and resolve conflicts manually"
            return 1
        fi
    else
        print_warning "Not a Git repository. Manual update required."
        return 1
    fi
}

# Function to update dependencies
update_dependencies() {
    print_info "Updating dependencies..."
    
    if [ -f "requirements.txt" ]; then
        if pip3 install -r requirements.txt --upgrade; then
            print_status "Dependencies updated"
        else
            print_warning "Some dependencies failed to update"
        fi
    else
        print_warning "requirements.txt not found"
    fi
}

# Function to update configuration files
update_configuration() {
    print_info "Updating configuration files..."
    
    # Update paths in configuration files
    if [ -f "mcp_config.json.template" ]; then
        sed "s|/Users/dif/Projects/LectureProject/mcp-server-gmail-send|$UPDATE_DIR|g" \
            mcp_config.json.template > mcp_config.json
        print_status "Updated mcp_config.json"
    fi
    
    if [ -f "claude_desktop_config.json.template" ]; then
        sed "s|/Users/dif/Projects/LectureProject/mcp-server-gmail-send|$UPDATE_DIR|g" \
            claude_desktop_config.json.template > claude_desktop_config.json
        print_status "Updated claude_desktop_config.json"
    fi
}

# Function to test the update
test_update() {
    print_info "Testing updated installation..."
    
    # Test skill import
    if python3 -c "from gmail_send_skill import GmailSendSkill; print('Import OK')" 2>/dev/null; then
        print_status "Skill import test passed"
    else
        print_error "Skill import test failed"
        return 1
    fi
    
    # Test MCP server
    if python3 mcp_server.py --test >/dev/null 2>&1; then
        print_status "MCP server test passed"
    else
        print_error "MCP server test failed"
        return 1
    fi
    
    # Test version
    if [ -f "version.py" ]; then
        NEW_VERSION=$(python3 version.py --version 2>/dev/null || echo "unknown")
        print_status "New version: $NEW_VERSION"
        
        if [ "$NEW_VERSION" != "$CURRENT_VERSION" ]; then
            print_status "Version updated from $CURRENT_VERSION to $NEW_VERSION"
        else
            print_info "Version unchanged: $CURRENT_VERSION"
        fi
    fi
}

# Function to rollback
rollback() {
    print_error "Rolling back to previous version..."
    
    # Find latest backup
    LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/gmail_send_backup_*.tar.gz 2>/dev/null | head -n1)
    
    if [ -f "$LATEST_BACKUP" ]; then
        print_info "Restoring from: $LATEST_BACKUP"
        
        # Extract backup
        tar -xzf "$LATEST_BACKUP" -C "$UPDATE_DIR"
        print_status "Rollback completed"
        
        # Test rollback
        if python3 mcp_server.py --test >/dev/null 2>&1; then
            print_status "Rollback verification passed"
        else
            print_error "Rollback verification failed"
        fi
    else
        print_error "No backup found for rollback"
    fi
}

# Function to clean up old backups
cleanup_backups() {
    print_info "Cleaning up old backups (keeping last 5)..."
    
    # Remove old backups (keep 5 most recent)
    ls -t "$BACKUP_DIR"/gmail_send_backup_*.tar.gz 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null || true
    
    BACKUP_COUNT=$(ls "$BACKUP_DIR"/gmail_send_backup_*.tar.gz 2>/dev/null | wc -l || echo 0)
    print_status "Kept $BACKUP_COUNT backups"
}

# Main update process
main() {
    print_info "Starting update process..."
    
    # Check current version
    check_current_version
    
    # Create backup
    backup_files
    
    # Update from Git
    if update_from_git; then
        print_status "Git update completed"
    else
        print_warning "Git update failed, trying alternative methods..."
        
        # Alternative: Check for manual updates
        print_info "Please manually download and extract the latest version"
        read -p "Press Enter after updating files manually..." -r
    fi
    
    # Update dependencies
    update_dependencies
    
    # Update configuration
    update_configuration
    
    # Test the update
    if test_update; then
        print_status "Update completed successfully!"
        
        # Clean up old backups
        cleanup_backups
        
        # Show new version info
        if [ -f "version.py" ]; then
            echo ""
            python3 version.py --info
        fi
        
        print_info "Update process completed successfully!"
        print_warning "Remember to restart Claude Desktop if you're using it"
        
    else
        print_error "Update testing failed!"
        
        # Ask for rollback
        echo ""
        read -p "Would you like to rollback to the previous version? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rollback
        else
            print_warning "Update failed but rollback skipped"
            print_info "Check the logs and fix issues manually"
        fi
    fi
}

# Command line options
case "${1:-}" in
    "--help"|"-h")
        echo "Gmail Send Skill Update Script"
        echo ""
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --backup-only  Create backup only, no update"
        echo "  --test-only    Test current installation only"
        echo "  --rollback     Rollback to previous version"
        echo "  --cleanup      Clean up old backups only"
        echo ""
        exit 0
        ;;
    "--backup-only")
        check_current_version
        backup_files
        print_status "Backup completed"
        ;;
    "--test-only")
        check_current_version
        test_update
        ;;
    "--rollback")
        rollback
        ;;
    "--cleanup")
        cleanup_backups
        ;;
    *)
        main
        ;;
esac