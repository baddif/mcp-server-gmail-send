# Gmail Send Skill - Usage Guide

## 📧 Overview

The Gmail Send Skill provides email sending functionality through Gmail's SMTP server using App Password authentication. It supports Markdown content conversion to HTML and provides comprehensive error reporting.

## 🔧 Prerequisites

### 1. Python Environment
- **Python 3.7+** (required)
- **markdown** library (optional, for rich formatting)

### 2. Gmail Setup
1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to [Google Account Settings](https://myaccount.google.com/)
   - Security → 2-Step Verification → App Passwords
   - Select "Mail" and generate password
   - Save the 16-character password (e.g., `abcd efgh ijkl mnop`)

### 3. Installation
```bash
# Clone or download the skill files
cd mcp-server-gmail-send

# Install dependencies
pip install -r requirements.txt

# Run installation script (optional)
chmod +x install.sh
./install.sh
```

## 📋 Function Schema

### OpenAI Function Calling Format

```json
{
  "type": "function",
  "function": {
    "name": "gmail_send",
    "description": "Send email via Gmail using App Password authentication. Supports Markdown content conversion to HTML and provides detailed success/failure feedback.",
    "parameters": {
      "type": "object",
      "properties": {
        "username": {
          "type": "string",
          "description": "Gmail username (email address) for authentication. Must be a valid Gmail address."
        },
        "app_password": {
          "type": "string", 
          "description": "Gmail App Password for authentication (not the regular password). Must be a 16-character App Password generated from Google Account settings."
        },
        "content": {
          "type": "string",
          "description": "Email content in Markdown format. Will be converted to HTML for rich formatting. Supports standard Markdown syntax including headers, lists, links, etc."
        },
        "to_email": {
          "type": "string",
          "description": "Recipient email address. Must be a valid email address."
        },
        "subject": {
          "type": "string",
          "description": "Email subject line.",
          "default": "Email from Gmail Send Skill"
        },
        "from_name": {
          "type": "string",
          "description": "Display name for the sender. If not provided, uses the username.",
          "default": null
        }
      },
      "required": ["username", "app_password", "content", "to_email"]
    }
  }
}
```

## 🚀 Usage Examples

### Basic Email Sending

```python
from gmail_send_skill import GmailSendSkill
from skill_compat import ExecutionContext

# Initialize skill and context
skill = GmailSendSkill()
ctx = ExecutionContext()

# Send basic email
result = skill.execute(ctx,
    username="your.email@gmail.com",
    app_password="abcd efgh ijkl mnop",
    content="Hello from Gmail Send Skill!",
    to_email="recipient@example.com",
    subject="Test Email"
)

print(result)
```

### Markdown Content Email

```python
# Send email with Markdown content
markdown_content = """
# Project Update

## Completed Tasks ✅
- Database optimization
- User authentication
- Email notifications

## Next Steps 📋
1. **Testing Phase**
   - Unit tests
   - Integration tests
2. **Deployment**
   - Staging environment
   - Production rollout

## Resources 🔗
- [Documentation](https://example.com/docs)
- [Project Board](https://example.com/board)

Best regards,  
**The Development Team**
"""

result = skill.execute(ctx,
    username="team@company.com",
    app_password="your_app_password",
    content=markdown_content,
    to_email="stakeholders@company.com",
    subject="Weekly Project Update",
    from_name="Development Team"
)
```

### Error Handling

```python
result = skill.execute(ctx,
    username="invalid-email",  # Invalid email format
    app_password="too-short",  # Invalid app password
    content="Test content",
    to_email="recipient@example.com"
)

if not result["success"]:
    error_type = result["error"]["type"]
    error_message = result["error"]["message"]
    print(f"Error ({error_type}): {error_message}")
```

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
    "subject": "Test Subject"
  }
}
```

### Error Response

```json
{
  "success": false,
  "function_name": "gmail_send",
  "error": {
    "message": "Authentication failed. Please check your username and App Password.",
    "type": "authentication_error",
    "details": "SMTP Authentication Error details..."
  }
}
```

## 🔍 Error Types

| Error Type | Description | Common Causes |
|------------|-------------|---------------|
| `validation_error` | Invalid parameters | Wrong email format, invalid app password |
| `authentication_error` | SMTP authentication failed | Wrong credentials, app password expired |
| `recipient_error` | Recipient email rejected | Invalid recipient address |
| `connection_error` | Network/SMTP connection issues | Network problems, server unavailable |
| `execution_error` | General execution failure | Unexpected errors, missing dependencies |

## 🎨 Markdown Support

The skill automatically converts Markdown to HTML for rich email formatting:

### Supported Markdown Features

| Markdown | HTML Output | Description |
|----------|-------------|-------------|
| `# Header` | `<h1>Header</h1>` | Headers (H1-H6) |
| `**bold**` | `<strong>bold</strong>` | Bold text |
| `*italic*` | `<em>italic</em>` | Italic text |
| `[link](url)` | `<a href="url">link</a>` | Links |
| `- item` | `<ul><li>item</li></ul>` | Unordered lists |
| `1. item` | `<ol><li>item</li></ol>` | Ordered lists |
| `` `code` `` | `<code>code</code>` | Inline code |
| `> quote` | `<blockquote>quote</blockquote>` | Blockquotes |

### Example Markdown Email

```markdown
# Welcome to Our Service! 🎉

Dear **Customer Name**,

Thank you for joining us! Here's what you can do next:

## Getting Started 📋
1. **Verify your email** - Check your inbox
2. **Complete your profile** - Add your details
3. **Explore features** - Try our tools

## Support Resources 🔗
- [Documentation](https://docs.example.com)
- [Support Center](https://support.example.com)
- [Community Forum](https://forum.example.com)

> Need help? Reply to this email or contact support@example.com

Best regards,  
*The Team*
```

## 🔗 MCP Integration

### MCP Server Usage

```bash
# Start MCP server
python mcp_server.py

# Test MCP server
python mcp_server.py --test
```

### Claude Desktop Integration

1. **Update configuration path** in `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "gmail-send": {
         "command": "python",
         "args": ["/path/to/your/mcp-server-gmail-send/mcp_server.py"]
       }
     }
   }
   ```

2. **Copy to Claude Desktop**:
   ```bash
   cp claude_desktop_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

3. **Restart Claude Desktop**

### MCP Resources

The skill provides these MCP resources:

| URI | Description |
|-----|-------------|
| `skill://gmail_send/status` | Current skill status and configuration |
| `skill://gmail_send/last_result` | Last email sending result |

### MCP Prompts

| Prompt | Description |
|--------|-------------|
| `gmail_send_help` | Usage help and instructions |

## 🧪 Testing

### Run Tests

```bash
# Run all tests
python test_gmail_skill.py

# Run specific test class
python test_gmail_skill.py --test TestGmailSendSkill

# Verbose output
python test_gmail_skill.py --verbose
```

### Manual Testing

```python
# Test skill directly
python gmail_send_skill.py

# Test MCP server
python mcp_server.py --test

# Check version
python version.py --info
```

## 🔒 Security Best Practices

### 1. App Password Security
- ✅ **Use App Passwords**, not regular account passwords
- ✅ **Enable 2FA** before generating App Passwords
- ✅ **Store passwords securely**, never in code
- ✅ **Rotate passwords** regularly
- ❌ **Never commit** passwords to version control

### 2. Email Content
- ✅ **Validate recipient** addresses
- ✅ **Sanitize content** from user input
- ✅ **Use plain text** for sensitive information
- ❌ **Don't include** sensitive data in subject lines

### 3. Error Handling
- ✅ **Log errors** for debugging
- ✅ **Provide helpful** error messages
- ❌ **Don't expose** sensitive information in errors

## 🛠️ Troubleshooting

### Common Issues

#### Authentication Errors
```
Error: Authentication failed
```
**Solutions:**
- Verify App Password is correct (16 characters)
- Check if 2FA is enabled
- Try generating a new App Password
- Ensure no extra spaces in password

#### Connection Errors
```
Error: Connection timeout
```
**Solutions:**
- Check internet connection
- Verify SMTP settings (smtp.gmail.com:587)
- Check firewall/proxy settings

#### Markdown Not Converting
```
Warning: Markdown library not available
```
**Solutions:**
- Install markdown: `pip install markdown`
- Content will be sent as plain text with basic formatting

### Log Analysis

Check logs for detailed error information:
```bash
# View MCP server logs
tail -f gmail_send_mcp.log

# Enable debug logging
export PYTHONPATH=. && python -m logging.config -c DEBUG mcp_server.py
```

## 📚 Advanced Usage

### Custom SMTP Configuration

For advanced use cases, you can modify the skill to support different SMTP servers:

```python
# In gmail_send_skill.py, modify these settings:
def __init__(self):
    self.smtp_server = "smtp.gmail.com"  # Change for other providers
    self.smtp_port = 587                 # 465 for SSL, 587 for TLS
```

### Batch Email Sending

```python
recipients = ["user1@example.com", "user2@example.com", "user3@example.com"]

for recipient in recipients:
    result = skill.execute(ctx,
        username="sender@gmail.com",
        app_password="app_password",
        content=f"Hello {recipient.split('@')[0]}!",
        to_email=recipient,
        subject="Batch Email"
    )
    print(f"Sent to {recipient}: {result['success']}")
```

### Template System

```python
# Email templates
templates = {
    "welcome": """
    # Welcome {name}! 🎉
    
    Thanks for joining **{company}**.
    
    Your account: `{email}`
    """,
    "reminder": """
    # Reminder: {task} ⏰
    
    Don't forget about: **{task}**
    Due: {due_date}
    """
}

# Send templated email
content = templates["welcome"].format(
    name="John Doe",
    company="Example Corp",
    email="john@example.com"
)

result = skill.execute(ctx, content=content, ...)
```

## 🆘 Support

### Documentation
- **Function Schema**: See OpenAI schema above
- **MCP Protocol**: [Model Context Protocol](https://modelcontextprotocol.io/)
- **Gmail App Passwords**: [Google Support](https://support.google.com/accounts/answer/185833)

### Troubleshooting
1. **Check logs**: `tail -f gmail_send_mcp.log`
2. **Test skill**: `python gmail_send_skill.py`
3. **Validate setup**: `python mcp_server.py --test`
4. **Version info**: `python version.py --info`

### Community
- **Issues**: Report bugs in the project repository
- **Discussions**: Join community discussions
- **Contributions**: Submit pull requests with improvements

---

**Gmail Send Skill v1.0.0** - Built for AI-powered applications with MCP support