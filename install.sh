#!/bin/bash
# Gmail Send Skill Installation Script
# Automated setup for the Gmail Send MCP Server

set -e  # Exit on error

echo "🚀 Gmail Send Skill - Installation Script"
echo "========================================"

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

# Check Python version
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.7+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
print_status "Found Python $PYTHON_VERSION"

# Check Python version requirement
if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 7) else 1)"; then
    print_status "Python version meets requirements (3.7+)"
else
    print_error "Python 3.7+ is required. Current version: $PYTHON_VERSION"
    exit 1
fi

# Get current directory
INSTALL_DIR=$(pwd)
print_status "Installation directory: $INSTALL_DIR"

# Install optional dependencies
echo ""
echo "Installing dependencies..."
if pip3 install -r requirements.txt; then
    print_status "Dependencies installed successfully"
else
    print_warning "Some dependencies failed to install. Markdown support may not be available."
fi

# Test the skill
echo ""
echo "Testing Gmail Send Skill..."
if python3 mcp_server.py --test; then
    print_status "Skill test passed"
else
    print_error "Skill test failed. Please check the installation."
    exit 1
fi

# Create backup directory
if [ ! -d "backup" ]; then
    mkdir backup
    print_status "Created backup directory"
fi

# Update configuration paths
echo ""
echo "Updating configuration files..."

# Update MCP config with current path
sed -i.bak "s|/Users/dif/Projects/LectureProject/mcp-server-gmail-send|$INSTALL_DIR|g" mcp_config.json
sed -i.bak "s|/Users/dif/Projects/LectureProject/mcp-server-gmail-send|$INSTALL_DIR|g" claude_desktop_config.json

print_status "Configuration files updated with current path"

# Make scripts executable
chmod +x mcp_server.py 2>/dev/null || true
chmod +x version.py 2>/dev/null || true

print_status "Made scripts executable"

# Display next steps
echo ""
echo "📋 Installation Complete!"
echo "========================"
echo ""
echo "Next Steps:"
echo "1. 🔧 Setup Gmail App Password:"
echo "   • Go to Google Account settings"
echo "   • Enable 2-Factor Authentication"
echo "   • Generate App Password for 'Mail'"
echo "   • Save the 16-character password"
echo ""
echo "2. 🔌 Integrate with Claude Desktop:"
echo "   • Copy configuration: cp claude_desktop_config.json ~/Library/Application\\ Support/Claude/claude_desktop_config.json"
echo "   • Or merge with existing config"
echo "   • Restart Claude Desktop"
echo ""
echo "3. 🧪 Test the installation:"
echo "   • python3 mcp_server.py --test"
echo "   • python3 version.py --info"
echo ""
echo "4. 📖 Usage Examples:"
echo "   • See Gmail_Send_USAGE.md (when created)"
echo "   • Check MCP_DEPLOYMENT.md (when created)"
echo ""
echo "📂 Configuration Files:"
echo "   • mcp_config.json - Full MCP configuration"
echo "   • claude_desktop_config.json - Claude Desktop config"
echo "   • requirements.txt - Python dependencies"
echo ""
echo "🆘 Troubleshooting:"
echo "   • Check logs: tail -f gmail_send_mcp.log"
echo "   • Test skill: python3 gmail_send_skill.py"
echo "   • Version info: python3 version.py --info"
echo ""
print_status "Gmail Send Skill is ready to use!"

# Optional: Test with Claude Desktop
echo ""
read -p "Would you like to copy the configuration to Claude Desktop? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
    CLAUDE_CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"
    
    if [ ! -d "$CLAUDE_CONFIG_DIR" ]; then
        print_warning "Claude Desktop configuration directory not found."
        print_warning "Please install Claude Desktop first or manually copy the configuration."
    else
        if [ -f "$CLAUDE_CONFIG_FILE" ]; then
            cp "$CLAUDE_CONFIG_FILE" backup/claude_desktop_config_backup.json
            print_status "Existing Claude config backed up"
        fi
        
        cp claude_desktop_config.json "$CLAUDE_CONFIG_FILE"
        print_status "Configuration copied to Claude Desktop"
        print_warning "Please restart Claude Desktop for changes to take effect"
    fi
fi

echo ""
print_status "Installation script completed!"
print_warning "Remember: Never commit real Gmail credentials to version control"