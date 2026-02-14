# MCP Deployment Guide - Gmail Send Skill

This guide provides comprehensive instructions for deploying the Gmail Send Skill as an MCP (Model Context Protocol) server for integration with AI agents like Claude Desktop.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Claude Desktop Integration](#claude-desktop-integration)
6. [Testing & Verification](#testing--verification)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Configuration](#advanced-configuration)
9. [Security Considerations](#security-considerations)
10. [Maintenance](#maintenance)

## 📖 Overview

### What is MCP?

Model Context Protocol (MCP) is a standardized protocol for connecting AI agents to external tools and data sources. It enables AI assistants to:

- Execute functions (tools)
- Access structured data (resources)
- Use prompt templates (prompts)

### Gmail Send Skill Features

- **Email Sending**: Send emails via Gmail SMTP with App Password authentication
- **Markdown Support**: Automatic conversion of Markdown content to HTML
- **Rich Error Reporting**: Detailed success/failure feedback
- **MCP Compatible**: Full MCP protocol support for AI agent integration
- **Security Focused**: App Password authentication, input validation

## 🔧 Prerequisites

### System Requirements

- **Operating System**: macOS, Linux, or Windows
- **Python**: Version 3.7 or higher
- **Network**: Internet connection for SMTP access
- **Gmail Account**: With 2-Factor Authentication enabled

### Gmail Setup

1. **Enable 2-Factor Authentication**:
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable 2-Step Verification

2. **Generate App Password**:
   - In Security settings → 2-Step Verification → App Passwords
   - Select "Mail" as the app
   - Generate and save the 16-character password
   - Example format: `abcd efgh ijkl mnop`

### AI Agent Requirements

- **Claude Desktop**: Version with MCP support
- **Other MCP Clients**: Any client supporting MCP protocol

## 🚀 Installation

### Method 1: Automated Installation (Recommended)

```bash
# Clone or download the project
git clone <repository-url>
cd mcp-server-gmail-send

# Run installation script
chmod +x install.sh
./install.sh
```

The installation script will:
- ✅ Check Python version
- ✅ Install dependencies
- ✅ Test the skill
- ✅ Update configuration files
- ✅ Set up backup directory

### Method 2: Manual Installation

```bash
# 1. Prepare environment
cd mcp-server-gmail-send
python3 --version  # Verify Python 3.7+

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Test installation
python3 mcp_server.py --test

# 4. Update configuration paths
# Edit mcp_config.json and claude_desktop_config.json
# Replace paths with your actual installation directory
```

### Dependencies

The skill requires these Python packages:

```txt
# Core (built-in)
smtplib     # SMTP client
email       # Email message handling
json        # JSON serialization
logging     # Logging functionality

# Optional
markdown>=3.4.0  # For Markdown to HTML conversion
```

## ⚙️ Configuration

### MCP Server Configuration

Edit `mcp_config.json` with your installation path:

```json
{
  "mcpServers": {
    "gmail-send": {
      "command": "python",
      "args": [
        "/absolute/path/to/your/mcp-server-gmail-send/mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "/absolute/path/to/your/mcp-server-gmail-send"
      },
      "description": "Gmail Send Skill - Send emails via Gmail using App Password authentication",
      "version": "1.0.0",
      "capabilities": {
        "tools": true,
        "resources": true,
        "prompts": true
      },
      "settings": {
        "timeout": 30000,
        "retries": 3
      }
    }
  }
}
```

### Claude Desktop Configuration

Update `claude_desktop_config.json` for Claude integration:

```json
{
  "mcpServers": {
    "gmail-send": {
      "command": "python",
      "args": [
        "/absolute/path/to/your/mcp-server-gmail-send/mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "/absolute/path/to/your/mcp-server-gmail-send"
      }
    }
  }
}
```

### Environment Variables (Optional)

For additional security, you can use environment variables:

```bash
# Set environment variables
export GMAIL_SEND_LOG_LEVEL=INFO
export GMAIL_SEND_TIMEOUT=30
```

## 🔌 Claude Desktop Integration

### Step 1: Locate Claude Desktop Configuration

Find the Claude Desktop configuration directory:

```bash
# macOS
~/Library/Application Support/Claude/claude_desktop_config.json

# Linux
~/.config/claude/claude_desktop_config.json

# Windows
%APPDATA%\Claude\claude_desktop_config.json
```

### Step 2: Backup Existing Configuration

```bash
# Create backup
cp "~/Library/Application Support/Claude/claude_desktop_config.json" backup/
```

### Step 3: Update Configuration

**Option A: Replace Configuration (if no existing MCP servers)**
```bash
cp claude_desktop_config.json "~/Library/Application Support/Claude/claude_desktop_config.json"
```

**Option B: Merge Configuration (if existing MCP servers)**
```json
{
  "mcpServers": {
    "existing-server": {
      "command": "...",
      "args": ["..."]
    },
    "gmail-send": {
      "command": "python",
      "args": [
        "/absolute/path/to/your/mcp-server-gmail-send/mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "/absolute/path/to/your/mcp-server-gmail-send"
      }
    }
  }
}
```

### Step 4: Restart Claude Desktop

Close and restart Claude Desktop for changes to take effect.

## 🧪 Testing & Verification

### Pre-Deployment Testing

```bash
# 1. Test skill functionality
python3 gmail_send_skill.py

# 2. Test MCP server
python3 mcp_server.py --test

# 3. Run comprehensive tests
python3 test_gmail_skill.py

# 4. Check version information
python3 version.py --info
```

### MCP Server Testing

```bash
# Start MCP server in test mode
python3 mcp_server.py --test
```

Expected output:
```
✓ Server info: gmail-send-mcp-server v1.0.0
✓ Available tools: 1
  - gmail_send: Send email via Gmail using App Password authentication...
✓ Available resources: 2
  - skill://gmail_send/status: Current status of Gmail Send skill...
  - skill://gmail_send/last_result: Last email sending result...
✓ Available prompts: 1
  - gmail_send_help: Get help and usage instructions...

✓ All tests passed! Server is ready.
```

### Claude Desktop Verification

1. **Open Claude Desktop**
2. **Check for MCP Connection**:
   - Look for connection indicators in the interface
   - Check for "gmail-send" in available tools

3. **Test Tool Access**:
   ```
   Can you show me the available tools?
   ```
   
   Claude should list "gmail_send" among available functions.

4. **Test Function Call**:
   ```
   Help me understand the gmail_send function
   ```
   
   Claude should provide information about the function's parameters and usage.

## 🔍 Troubleshooting

### Common Issues

#### 1. Python Path Issues

**Error**: `ModuleNotFoundError: No module named 'gmail_send_skill'`

**Solutions**:
```bash
# Check current directory
pwd
ls -la gmail_send_skill.py

# Update PYTHONPATH in configuration
"env": {
  "PYTHONPATH": "/correct/path/to/mcp-server-gmail-send"
}

# Verify Python can find modules
python3 -c "import gmail_send_skill; print('OK')"
```

#### 2. Permission Issues

**Error**: `Permission denied: /path/to/mcp_server.py`

**Solutions**:
```bash
# Make script executable
chmod +x mcp_server.py

# Check file permissions
ls -la mcp_server.py

# Alternative: Use python3 explicitly
"command": "python3"  # instead of just "python"
```

#### 3. MCP Connection Issues

**Error**: Claude Desktop doesn't recognize the MCP server

**Solutions**:
```bash
# 1. Verify configuration syntax
python3 -m json.tool claude_desktop_config.json

# 2. Check Claude Desktop logs (macOS)
tail -f ~/Library/Logs/Claude/claude-desktop.log

# 3. Test MCP server manually
python3 mcp_server.py --test

# 4. Restart Claude Desktop completely
```

#### 4. SMTP Authentication Issues

**Error**: `Authentication failed`

**Solutions**:
- Verify App Password is exactly 16 characters
- Remove any spaces from App Password in function calls
- Ensure 2FA is enabled on Gmail account
- Generate a new App Password if needed
- Check for typos in Gmail username

### Log Analysis

#### MCP Server Logs

```bash
# View MCP server logs
tail -f gmail_send_mcp.log

# Enable debug logging
export PYTHONPATH=. 
LOGLEVEL=DEBUG python3 mcp_server.py
```

#### Claude Desktop Logs

```bash
# macOS
tail -f ~/Library/Logs/Claude/claude-desktop.log

# Linux
tail -f ~/.local/share/Claude/logs/claude-desktop.log

# Windows
# Check Windows Event Viewer or application logs
```

### Diagnostic Commands

```bash
# System diagnostics
python3 --version
which python3
pip3 list | grep markdown

# Skill diagnostics  
python3 -c "from gmail_send_skill import GmailSendSkill; print('Skill import OK')"
python3 -c "from skill_compat import ExecutionContext; print('Compat import OK')"

# Network diagnostics
telnet smtp.gmail.com 587
```

## 🔧 Advanced Configuration

### Custom SMTP Settings

For enterprise Gmail or G Suite accounts:

```python
# In gmail_send_skill.py, modify __init__ method:
def __init__(self):
    self.smtp_server = "smtp.gmail.com"     # Default
    # For G Suite: self.smtp_server = "smtp-relay.gmail.com" 
    self.smtp_port = 587                    # TLS port
    # For SSL: self.smtp_port = 465
```

### Timeout Configuration

Adjust timeouts for slower networks:

```json
{
  "mcpServers": {
    "gmail-send": {
      "command": "python",
      "args": ["mcp_server.py"],
      "settings": {
        "timeout": 60000,  // 60 seconds
        "retries": 5
      }
    }
  }
}
```

### Logging Configuration

Enable detailed logging:

```python
# In mcp_server.py, modify logging setup:
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gmail_send_mcp.log'),
        logging.StreamHandler(sys.stderr)
    ]
)
```

### Resource Customization

Add custom MCP resources:

```python
# In gmail_send_skill.py, extend get_mcp_resources():
def get_mcp_resources(self) -> List[McpResource]:
    base_resources = super().get_mcp_resources()
    
    custom_resources = [
        McpResource(
            uri="skill://gmail_send/templates",
            name="email_templates",
            description="Available email templates",
            mime_type="application/json"
        )
    ]
    
    return base_resources + custom_resources
```

## 🔒 Security Considerations

### 1. Credential Security

**App Passwords**:
- ✅ Store securely, never in configuration files
- ✅ Use secure credential management systems
- ✅ Rotate passwords regularly
- ❌ Never commit to version control

**Configuration Files**:
```bash
# Secure configuration files
chmod 600 claude_desktop_config.json
chmod 600 mcp_config.json

# Add to .gitignore
echo "*_local.json" >> .gitignore
echo "*.log" >> .gitignore
```

### 2. Network Security

**SMTP Connections**:
- ✅ Always use TLS encryption (port 587)
- ✅ Verify SSL certificates
- ✅ Use secure DNS

**Firewall Rules**:
```bash
# Allow SMTP outbound (if needed)
# Port 587 for TLS
# Port 465 for SSL (legacy)
```

### 3. Access Control

**File Permissions**:
```bash
# Restrict access to skill files
chmod 755 mcp_server.py
chmod 644 gmail_send_skill.py
chmod 644 skill_compat.py
```

**Process Security**:
- Run MCP server with minimal privileges
- Consider containerization for production deployments

### 4. Input Validation

The skill includes comprehensive validation:
- Email address format validation
- App Password format validation
- Content sanitization
- Parameter type checking

## 🔄 Maintenance

### Regular Updates

1. **Check for Updates**:
   ```bash
   python3 version.py --check-updates
   ```

2. **Backup Configuration**:
   ```bash
   cp claude_desktop_config.json backup/
   cp mcp_config.json backup/
   ```

3. **Update Skill**:
   ```bash
   git pull origin main  # If using git
   ./install.sh          # Re-run installation
   ```

### Monitoring

#### Log Rotation

```bash
# Setup log rotation (Linux/macOS)
# Add to /etc/logrotate.d/gmail-send-mcp
/path/to/mcp-server-gmail-send/gmail_send_mcp.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 user user
}
```

#### Health Checks

```bash
# Create health check script
cat > health_check.sh << 'EOF'
#!/bin/bash
cd /path/to/mcp-server-gmail-send
python3 mcp_server.py --test > /dev/null 2>&1
echo $?
EOF

chmod +x health_check.sh
```

### Backup Strategy

1. **Configuration Backup**:
   ```bash
   tar -czf gmail-send-backup-$(date +%Y%m%d).tar.gz \
       *.json *.py *.md requirements.txt
   ```

2. **Automated Backup**:
   ```bash
   # Add to crontab for daily backups
   0 2 * * * /path/to/backup-script.sh
   ```

## 📊 Performance Optimization

### Connection Pooling

For high-volume usage, consider SMTP connection pooling:

```python
# Advanced: Implement connection pooling
class SMTPPool:
    def __init__(self, max_connections=5):
        self.max_connections = max_connections
        self.pool = []
    
    def get_connection(self):
        # Implement connection reuse logic
        pass
```

### Rate Limiting

Implement rate limiting to avoid Gmail limits:

```python
# Add rate limiting
import time
from functools import wraps

def rate_limit(calls_per_minute=60):
    def decorator(func):
        last_called = [0.0]
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            min_interval = 60.0 / calls_per_minute
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            last_called[0] = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

## 🆘 Support Resources

### Documentation
- **MCP Protocol**: [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- **Claude Desktop**: [Anthropic Documentation](https://docs.anthropic.com/)
- **Gmail API**: [Google Gmail Documentation](https://developers.google.com/gmail)

### Community
- **GitHub Issues**: Report bugs and request features
- **Discussions**: Join community discussions
- **Contributions**: Submit improvements via pull requests

### Professional Support
For enterprise deployments:
- Custom integration support
- Performance optimization
- Security hardening
- Compliance assistance

---

**MCP Deployment Guide v1.0.0** - Gmail Send Skill for AI-Powered Applications