# Gmail Send Skill - MCP Server

🚀 **AI-Powered Email Sending Skill** with Model Context Protocol (MCP) support

Send emails via Gmail using App Password authentication with Markdown content support, specifically designed for AI agents and MCP-compatible applications.

## ✨ Features

### 📧 Core Email Functionality
- **Gmail SMTP Integration** - Send emails through Gmail's secure SMTP server (Port 587, TLS)
- **App Password Authentication** - Secure authentication using Gmail App Passwords
- **Rich Error Reporting** - Detailed success/failure feedback with error types
- **Input Validation** - Comprehensive email and parameter validation

### 📝 Enhanced Markdown Support (v1.1.0+)
- **Advanced Markdown Conversion** - Full markdown library support with extensions (BSD license)
- **Professional Email Styling** - Email-safe CSS with responsive design
- **Graceful Fallback System** - Basic Markdown converter when external library unavailable
- **Commercial License Compliance** - BSD-licensed dependencies for commercial use
- **Email Client Compatibility** - Optimized HTML for major email clients

### 🤖 AI Integration
- **MCP Compatible** - Full Model Context Protocol support for AI agents
- **OpenAI Function Calling** - Compatible with OpenAI Function Calling standard
- **Skill Framework** - Standalone and integrated execution modes

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd mcp-server-gmail-send

# Run automated installation
chmod +x install.sh
./install.sh
```

### 2. Gmail Setup

1. **Enable 2-Factor Authentication** in your Gmail account
2. **Generate App Password**:
   - Go to Google Account → Security → 2-Step Verification → App Passwords
   - Select "Mail" and generate password
   - Save the 16-character password (e.g., `abcd efgh ijkl mnop`)

### 3. Claude Desktop Integration

```bash
# Copy configuration to Claude Desktop
cp claude_desktop_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Restart Claude Desktop
```

### 4. Test the Setup

```bash
# Test the MCP server
python3 mcp_server.py --test

# Run comprehensive tests
python3 test_gmail_skill.py
```

## 📧 Usage Example

### Enhanced Markdown to HTML Conversion (v1.1.0+)

The skill now supports advanced Markdown conversion with professional email styling:

#### Supported Markdown Features
- **Headers** (H1-H6) with proper hierarchy
- **Text Formatting** - Bold, italic, strikethrough
- **Lists** - Ordered and unordered with nesting
- **Links** - Automatic link formatting
- **Code Blocks** - Syntax highlighting and inline code
- **Blockquotes** - Professional quote styling
- **Tables** - Responsive table design (with markdown library)

#### Email Styling Features
- 📱 **Responsive Design** - Adapts to desktop and mobile email clients
- 🎨 **Professional CSS** - Clean, modern email appearance
- 📧 **Email Client Compatibility** - Works with Gmail, Outlook, Apple Mail, etc.
- 🔧 **Graceful Fallback** - Basic conversion when advanced features unavailable

#### Markdown Content Example
```markdown
# Project Status Report

## Executive Summary
The project is **on track** with key milestones achieved:

### Completed Tasks ✅
1. User authentication system
2. Database schema design
3. API endpoints implementation

### In Progress 🚧
- Front-end development
- Integration testing
- Performance optimization

> **Note**: All deliverables are meeting quality standards.

For technical details, see: [Project Documentation](https://example.com/docs)

```python
def get_project_status():
    return "Active"
```
```

This Markdown will be converted to professional HTML email format automatically.

### Basic Email Sending

```python
from gmail_send_skill import GmailSendSkill
from skill_compat import ExecutionContext

# Initialize
skill = GmailSendSkill()
ctx = ExecutionContext()

# Send email
result = skill.execute(ctx,
    username="your.email@gmail.com",
    app_password="abcd efgh ijkl mnop", 
    content="# Hello World!\n\nThis is a **test** email with *markdown*.",
    to_email="recipient@example.com",
    subject="Test Email from Skill"
)

print(f"Success: {result['success']}")
```

### Via AI Agent (Claude Desktop)

Simply ask Claude:
```
Can you send an email using the gmail_send function? I need to send:
- From: my.email@gmail.com  
- To: colleague@company.com
- Subject: Project Update
- Content: A markdown report about our progress

I'll provide my app password when prompted.
```

## 📊 Function Schema

### OpenAI Function Calling Format

```json
{
  "name": "gmail_send",
  "description": "Send email via Gmail using App Password authentication with Markdown support",
  "parameters": {
    "type": "object", 
    "properties": {
      "username": {
        "type": "string",
        "description": "Gmail address for authentication"
      },
      "app_password": {
        "type": "string", 
        "description": "16-character Gmail App Password"
      },
      "content": {
        "type": "string",
        "description": "Email content in Markdown format"
      },
      "to_email": {
        "type": "string",
        "description": "Recipient email address"
      },
      "subject": {
        "type": "string",
        "description": "Email subject line",
        "default": "Email from Gmail Send Skill"
      },
      "from_name": {
        "type": "string", 
        "description": "Display name for sender",
        "default": null
      }
    },
    "required": ["username", "app_password", "content", "to_email"]
  }
}
```

## 📋 Project Structure

```
mcp-server-gmail-send/
├── 📄 gmail_send_skill.py      # Main skill implementation
├── 🔧 skill_compat.py          # Framework compatibility layer  
├── 🖥️  mcp_server.py           # MCP server with stdio transport
├── 📊 version.py               # Version management
├── 🧪 test_gmail_skill.py      # Comprehensive test suite
├── ⚙️  mcp_config.json         # MCP client configuration
├── 🔌 claude_desktop_config.json # Claude Desktop integration
├── 📦 requirements.txt         # Python dependencies
├── 🛠️ install.sh               # Automated installation script
├── 📖 GMAIL_SEND_USAGE.md      # Detailed usage guide
├── 🚀 MCP_DEPLOYMENT.md        # MCP deployment instructions
└── 📝 README.md                # This file
```

## 🔧 Configuration

### MCP Server Configuration

Update paths in `mcp_config.json`:

```json
{
  "mcpServers": {
    "gmail-send": {
      "command": "python",
      "args": ["/absolute/path/to/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/project"
      }
    }
  }
}
```

### Claude Desktop Configuration  

Update `claude_desktop_config.json` with your installation path and copy to:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json` 
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

## 🧪 Testing

### Automated Testing

```bash
# Run all tests
python3 test_gmail_skill.py

# Test specific components
python3 test_gmail_skill.py --test TestGmailSendSkill

# Verbose output
python3 test_gmail_skill.py --verbose
```

### Manual Testing

```bash
# Test skill directly
python3 gmail_send_skill.py

# Test MCP server
python3 mcp_server.py --test

# Check version and info
python3 version.py --info
```

## ⚙️ Technical Details

### Dependencies and Licensing

#### Core Dependencies (Built-in Python)
- `smtplib` - SMTP email sending
- `email.mime` - Email composition
- `ssl` - TLS encryption
- `json` - Configuration handling
- `re` - Regular expressions for fallback conversion

#### Optional Enhancement (Commercial-Friendly)
- **markdown** library (BSD 3-Clause License)
  - ✅ Commercial use allowed
  - ✅ Distribution allowed  
  - ✅ Modification allowed
  - 🔧 Graceful fallback when unavailable

#### System Requirements
- Python 3.7+ (tested up to 3.12)
- Internet connection for Gmail SMTP
- Gmail account with 2FA enabled

### Architecture

```
Gmail Send Skill Architecture
├── gmail_send_skill.py      # Core skill implementation
├── skill_compat.py          # Framework compatibility layer
├── mcp_server.py           # MCP Protocol server
└── version.py              # Version management

HTML Conversion Pipeline:
Markdown Content → Advanced/Basic Converter → CSS Styling → Email HTML
```

### Conversion System Details

#### Advanced Mode (with markdown library)
- Full CommonMark specification support
- Extensions: tables, strikethrough, task lists
- Professional syntax highlighting
- Advanced table rendering

#### Fallback Mode (built-in)
- Regex-based Markdown parsing
- Core element support (headers, lists, formatting)
- Email-safe HTML generation
- Professional CSS styling maintained

## 📚 Documentation

- 📖 **[Usage Guide](GMAIL_SEND_USAGE.md)** - Comprehensive usage instructions and examples
- 🚀 **[MCP Deployment](MCP_DEPLOYMENT.md)** - Complete MCP integration guide  
- 🔧 **[Installation Script](install.sh)** - Automated setup and configuration
- 🧪 **[Test Suite](test_gmail_skill.py)** - Comprehensive testing framework

## 🔒 Security

### Best Practices

- ✅ **Use App Passwords** - Never use regular Gmail passwords
- ✅ **Enable 2FA** - Required for App Password generation
- ✅ **Secure Storage** - Never commit credentials to version control
- ✅ **Input Validation** - All parameters are validated before use
- ✅ **Error Handling** - Sensitive information is not exposed in errors

### Supported Authentication

- **Gmail App Passwords** (recommended)
- **G Suite/Workspace** accounts with App Passwords
- **2-Factor Authentication** required

## 📊 Response Format

### Success Response
```json
{
  "success": true,
  "function_name": "gmail_send",
  "result": {
    "message": "Email sent successfully to recipient@example.com",
    "timestamp": "2026-02-14T10:30:00",
    "from": "sender@gmail.com",
    "to": "recipient@example.com",
    "subject": "Email Subject"
  }
}
```

### Error Response  
```json
{
  "success": false,
  "function_name": "gmail_send", 
  "error": {
    "message": "Authentication failed. Please check your credentials.",
    "type": "authentication_error",
    "details": "SMTP Authentication Error: (535, 'Incorrect password')"
  }
}
```

## 🔄 Version Information

Current Version: **1.0.0** (2026-02-14)

```bash
# Check version
python3 version.py --version

# Full version info  
python3 version.py --info

# View changelog
python3 version.py --changelog
```

## 🛠️ Requirements

### System Requirements
- **Python 3.7+** (required)
- **Internet connection** for SMTP access
- **Gmail account** with 2FA enabled

### Dependencies
- **Built-in Python libraries**: `smtplib`, `email`, `json`, `logging`
- **Optional**: `markdown>=3.4.0` (for rich formatting)

### Compatibility
- ✅ **MCP Protocol** 2024-11-05
- ✅ **OpenAI Function Calling** compatible
- ✅ **Claude Desktop** integration
- ✅ **Cross-platform** (macOS, Linux, Windows)

## 🆘 Troubleshooting

### Common Issues

#### Authentication Errors
```bash
# Verify App Password format (16 characters)
# Check 2FA is enabled
# Generate new App Password
```

#### Module Import Errors
```bash
# Check Python path
export PYTHONPATH=/path/to/mcp-server-gmail-send

# Verify file permissions
chmod 644 gmail_send_skill.py
```

#### MCP Connection Issues
```bash
# Test MCP server
python3 mcp_server.py --test

# Check Claude Desktop logs
tail -f ~/Library/Logs/Claude/claude-desktop.log
```

### Support Resources

- 📋 **[Usage Guide](GMAIL_SEND_USAGE.md)** - Detailed troubleshooting
- 🔧 **[Deployment Guide](MCP_DEPLOYMENT.md)** - MCP-specific issues
- 🧪 **Test Suite** - `python3 test_gmail_skill.py`
- 📊 **Logs** - Check `gmail_send_mcp.log`

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open Pull Request**

### Development Setup

```bash
# Clone for development
git clone <repository-url>
cd mcp-server-gmail-send

# Install development dependencies
pip3 install -r requirements.txt
pip3 install pytest pytest-asyncio  # For testing

# Run tests
python3 test_gmail_skill.py

# Check code style
python3 -m flake8 gmail_send_skill.py
```

## � Version History

### v1.1.0 (2024-12-19) - Enhanced Markdown Support
- ✨ **Advanced Markdown Conversion** - Full markdown library support with extensions
- 🎨 **Professional Email Styling** - Responsive CSS for email clients
- 🔧 **Graceful Fallback System** - Basic converter when external library unavailable  
- ⚖️ **Commercial License Compliance** - BSD-licensed dependencies
- 📧 **Email Client Optimization** - Improved compatibility across platforms
- 🧪 **Enhanced Testing** - Comprehensive conversion and styling tests

### v1.0.0 (2024-12-19) - Initial Release
- 📧 **Gmail SMTP Integration** - Secure email sending via Gmail
- 🔐 **App Password Authentication** - Secure credential handling
- 🤖 **MCP Protocol Support** - Full Model Context Protocol implementation
- 📝 **Basic Markdown Support** - Simple markdown to HTML conversion
- ✅ **Comprehensive Testing** - 18 unit tests with edge case coverage
- 🛠️ **Local Development Tools** - Configuration templates and testing utilities

## �📄 License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

### Third-Party License Compliance
- **markdown library** (Optional) - BSD 3-Clause License - Commercial use allowed
- **Python Standard Library** - Python Software Foundation License

## 🙏 Acknowledgments

- **Model Context Protocol** - For the standardized AI agent integration
- **OpenAI Function Calling** - For the function schema standard  
- **Gmail SMTP** - For reliable email delivery infrastructure
- **Python Community** - For the excellent libraries and tools
- **Markdown Community** - For the BSD-licensed markdown processing library

---

**Built for AI-Powered Applications** 🤖 | **MCP Compatible** 🔌 | **Production Ready** 🚀

*Gmail Send Skill v1.1.0 - Enhanced Markdown conversion with professional email styling*
Send mail through gmail.
