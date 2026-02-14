"""
Gmail Send Skill - Email Sending with App Password

This skill provides functionality to send emails via Gmail using App Password authentication.
Supports Markdown content conversion to HTML and returns success/failure status.
"""

import smtplib
import json
import logging
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from typing import Any, Dict, List
from datetime import datetime

# Markdown processing with fallback and extension support
try:
    import markdown
    MARKDOWN_AVAILABLE = True
    MARKDOWN_VERSION = getattr(markdown, '__version__', 'unknown')
    
    # Try to import common extensions (gracefully handle missing ones)
    AVAILABLE_EXTENSIONS = []
    
    try:
        from markdown.extensions import tables
        AVAILABLE_EXTENSIONS.append('tables')
    except ImportError:
        pass
    
    try:
        from markdown.extensions import fenced_code  
        AVAILABLE_EXTENSIONS.append('fenced_code')
    except ImportError:
        pass
        
    try:
        from markdown.extensions import codehilite
        AVAILABLE_EXTENSIONS.append('codehilite')  
    except ImportError:
        pass
        
    try:
        from markdown.extensions import toc
        AVAILABLE_EXTENSIONS.append('toc')
    except ImportError:
        pass
        
    try:
        from markdown.extensions import nl2br
        AVAILABLE_EXTENSIONS.append('nl2br')
    except ImportError:
        pass
        
    try:
        from markdown.extensions import attr_list
        AVAILABLE_EXTENSIONS.append('attr_list')
    except ImportError:
        pass
        
except ImportError:
    markdown = None
    MARKDOWN_AVAILABLE = False
    MARKDOWN_VERSION = None
    AVAILABLE_EXTENSIONS = []

# Framework compatibility layer
try:
    from framework.mcp.base import McpCompatibleSkill, McpResource, McpPrompt
    from framework.context import ExecutionContext
except ImportError:
    # Fallback to standalone implementation
    from skill_compat import McpCompatibleSkill, McpResource, McpPrompt, ExecutionContext

class GmailSendSkill(McpCompatibleSkill):
    """
    Gmail Send Skill Implementation
    
    Purpose: Send emails via Gmail using App Password authentication
    Category: Communication/Email
    Features:
    - App Password authentication
    - Markdown to HTML conversion
    - Success/failure reporting
    - Detailed error messages
    """
    
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.last_result = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    @staticmethod
    def get_schema() -> Dict[str, Any]:
        """Return OpenAI Function Calling compatible JSON Schema"""
        return {
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
                            "default": None
                        }
                    },
                    "required": ["username", "app_password", "content", "to_email"]
                }
            }
        }
    
    def get_openai_schema(self) -> Dict[str, Any]:
        """Return OpenAI schema"""
        return self.get_schema()
    
    def _validate_email(self, email: str) -> bool:
        """Validate email address format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _validate_app_password(self, app_password: str) -> bool:
        """Validate App Password format (16 characters, alphanumeric)"""
        import re
        # App passwords are typically 16 characters, letters and numbers only
        pattern = r'^[a-zA-Z0-9]{16}$'
        return re.match(pattern, app_password.replace(' ', '')) is not None
    
    def _get_email_css(self) -> str:
        """Generate CSS styles for HTML emails"""
        return """
        <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50;
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
        }
        h1 { font-size: 28px; border-bottom: 2px solid #3498db; padding-bottom: 8px; }
        h2 { font-size: 24px; border-bottom: 1px solid #bdc3c7; padding-bottom: 4px; }
        h3 { font-size: 20px; }
        h4 { font-size: 18px; }
        h5 { font-size: 16px; }
        h6 { font-size: 14px; }
        p {
            margin-bottom: 16px;
        }
        strong {
            font-weight: 600;
            color: #2c3e50;
        }
        em {
            font-style: italic;
            color: #34495e;
        }
        code {
            background-color: #f8f9fa;
            color: #e74c3c;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 0.9em;
        }
        pre {
            background-color: #f8f9fa;
            border: 1px solid #e1e5e8;
            border-radius: 6px;
            padding: 16px;
            overflow-x: auto;
            margin: 16px 0;
        }
        pre code {
            background-color: transparent;
            color: #333;
            padding: 0;
        }
        blockquote {
            border-left: 4px solid #3498db;
            margin: 16px 0;
            padding: 8px 16px;
            background-color: #f8f9fa;
            color: #555;
        }
        ul, ol {
            margin: 16px 0;
            padding-left: 24px;
        }
        li {
            margin-bottom: 8px;
        }
        a {
            color: #3498db;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px 12px;
            text-align: left;
        }
        th {
            background-color: #f8f9fa;
            font-weight: 600;
        }
        tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        hr {
            border: none;
            border-top: 2px solid #bdc3c7;
            margin: 24px 0;
        }
        .highlight {
            background-color: #fff3cd;
            padding: 2px 4px;
            border-radius: 3px;
        }
        </style>
        """

    def _enhance_html_content(self, html_content: str) -> str:
        """Enhance HTML content with better formatting and email-safe styles"""
        # Add CSS styles
        css = self._get_email_css()
        
        # Wrap content in proper HTML structure
        enhanced_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    {css}
</head>
<body>
    {html_content}
</body>
</html>"""
        
        return enhanced_html

    def _convert_markdown_to_html(self, markdown_content: str) -> str:
        """Convert Markdown content to HTML with enhanced styling and features"""
        if not MARKDOWN_AVAILABLE:
            self.logger.warning("Markdown library not available, using basic HTML conversion")
            return self._basic_markdown_to_html(markdown_content)
        
        try:
            # Configure extensions based on what's available
            extensions = []
            extension_configs = {}
            
            # Core extensions for better email formatting
            if 'tables' in AVAILABLE_EXTENSIONS:
                extensions.append('tables')
            if 'fenced_code' in AVAILABLE_EXTENSIONS:
                extensions.append('fenced_code')
            if 'nl2br' in AVAILABLE_EXTENSIONS:
                extensions.append('nl2br')
            if 'attr_list' in AVAILABLE_EXTENSIONS:
                extensions.append('attr_list')
            
            # Add TOC if available (useful for long emails)
            if 'toc' in AVAILABLE_EXTENSIONS:
                extensions.append('toc')
                extension_configs['toc'] = {
                    'title': '目录',
                    'anchorlink': True
                }
            
            # Code highlighting (if available)
            if 'codehilite' in AVAILABLE_EXTENSIONS:
                extensions.append('codehilite')
                extension_configs['codehilite'] = {
                    'use_pygments': False,  # Avoid external dependencies
                    'noclasses': True,      # Inline styles for email compatibility
                }
            
            # Always include these basic extensions
            base_extensions = ['extra', 'smarty', 'meta']
            for ext in base_extensions:
                try:
                    # Test if extension is available
                    test_md = markdown.Markdown(extensions=[ext])
                    extensions.append(ext)
                except Exception:
                    pass  # Skip unavailable extensions
            
            self.logger.info(f"Using Markdown extensions: {extensions}")
            
            # Create markdown instance with configured extensions
            md = markdown.Markdown(
                extensions=extensions,
                extension_configs=extension_configs,
                tab_length=4
            )
            
            # Convert to HTML
            html = md.convert(markdown_content)
            
            # Enhance with email-safe styling
            enhanced_html = self._enhance_html_content(html)
            
            self.logger.info(f"Markdown conversion successful, output length: {len(enhanced_html)} chars")
            return enhanced_html
            
        except Exception as e:
            self.logger.error(f"Advanced Markdown conversion failed: {str(e)}")
            self.logger.info("Falling back to basic HTML conversion")
            return self._basic_markdown_to_html(markdown_content)

    def _basic_markdown_to_html(self, markdown_content: str) -> str:
        """Basic Markdown to HTML conversion when markdown library is not available"""
        html = markdown_content
        
        # Convert headers
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
        html = re.sub(r'^##### (.+)$', r'<h5>\1</h5>', html, flags=re.MULTILINE)
        html = re.sub(r'^###### (.+)$', r'<h6>\1</h6>', html, flags=re.MULTILINE)
        
        # Convert bold and italic
        html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', html)
        html = re.sub(r'__([^_]+)__', r'<strong>\1</strong>', html)
        html = re.sub(r'_([^_]+)_', r'<em>\1</em>', html)
        
        # Convert inline code
        html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
        
        # Convert links
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
        
        # Convert unordered lists
        lines = html.split('\n')
        in_ul = False
        result_lines = []
        
        for line in lines:
            if re.match(r'^[-*+] ', line):
                if not in_ul:
                    result_lines.append('<ul>')
                    in_ul = True
                item_text = re.sub(r'^[-*+] ', '', line)
                result_lines.append(f'<li>{item_text}</li>')
            else:
                if in_ul:
                    result_lines.append('</ul>')
                    in_ul = False
                if line.strip():
                    result_lines.append(f'<p>{line}</p>')
                else:
                    result_lines.append('<br>')
        
        if in_ul:
            result_lines.append('</ul>')
        
        html = '\n'.join(result_lines)
        
        # Convert blockquotes
        html = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)
        
        # Convert horizontal rules
        html = re.sub(r'^---+$', '<hr>', html, flags=re.MULTILINE)
        
        # Enhance with styling
        enhanced_html = self._enhance_html_content(html)
        
        self.logger.info("Basic Markdown conversion completed")
        return enhanced_html
    
    def _send_email(self, username: str, app_password: str, to_email: str, 
                   subject: str, content: str, from_name: str = None) -> Dict[str, Any]:
        """Send email via Gmail SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = formataddr((from_name or username, username))
            msg['To'] = to_email
            
            # Convert Markdown to HTML
            html_content = self._convert_markdown_to_html(content)
            
            # Create both plain text and HTML parts
            text_part = MIMEText(content, 'plain', 'utf-8')
            html_part = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Connect to Gmail SMTP server
            self.logger.info(f"Connecting to {self.smtp_server}:{self.smtp_port}")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            
            # Login with App Password
            self.logger.info(f"Authenticating with username: {username}")
            server.login(username, app_password.replace(' ', ''))
            
            # Send email
            self.logger.info(f"Sending email to: {to_email}")
            text = msg.as_string()
            server.sendmail(username, to_email, text)
            server.quit()
            
            return {
                "success": True,
                "message": f"Email sent successfully to {to_email}",
                "timestamp": datetime.now().isoformat()
            }
            
        except smtplib.SMTPAuthenticationError as e:
            return {
                "success": False,
                "error_type": "authentication_error",
                "message": "Authentication failed. Please check your username and App Password.",
                "details": str(e)
            }
        except smtplib.SMTPRecipientsRefused as e:
            return {
                "success": False,
                "error_type": "recipient_error", 
                "message": f"Recipient email address rejected: {to_email}",
                "details": str(e)
            }
        except smtplib.SMTPServerDisconnected as e:
            return {
                "success": False,
                "error_type": "connection_error",
                "message": "Lost connection to Gmail server",
                "details": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "error_type": "execution_error",
                "message": f"Failed to send email: {str(e)}",
                "details": str(e)
            }
    
    def execute(self, ctx: ExecutionContext, **kwargs) -> Any:
        """
        Execute the Gmail send skill
        
        Args:
            ctx: Execution context
            **kwargs: Skill parameters (username, app_password, content, to_email, subject, from_name)
            
        Returns:
            Result dictionary with success status and details
        """
        try:
            # Extract parameters
            username = kwargs.get('username', '').strip()
            app_password = kwargs.get('app_password', '').strip()
            content = kwargs.get('content', '').strip()
            to_email = kwargs.get('to_email', '').strip()
            subject = kwargs.get('subject', 'Email from Gmail Send Skill').strip()
            from_name = kwargs.get('from_name')
            
            # Validate required parameters
            if not username:
                return {
                    "success": False,
                    "function_name": "gmail_send",
                    "error": {
                        "message": "Username is required",
                        "type": "validation_error"
                    }
                }
            
            if not app_password:
                return {
                    "success": False,
                    "function_name": "gmail_send",
                    "error": {
                        "message": "App Password is required",
                        "type": "validation_error"
                    }
                }
            
            if not content:
                return {
                    "success": False,
                    "function_name": "gmail_send",
                    "error": {
                        "message": "Email content is required",
                        "type": "validation_error"
                    }
                }
            
            if not to_email:
                return {
                    "success": False,
                    "function_name": "gmail_send",
                    "error": {
                        "message": "Recipient email address is required",
                        "type": "validation_error"
                    }
                }
            
            # Validate email formats
            if not self._validate_email(username):
                return {
                    "success": False,
                    "function_name": "gmail_send",
                    "error": {
                        "message": "Invalid username email format",
                        "type": "validation_error"
                    }
                }
            
            if not self._validate_email(to_email):
                return {
                    "success": False,
                    "function_name": "gmail_send",
                    "error": {
                        "message": "Invalid recipient email format",
                        "type": "validation_error"
                    }
                }
            
            # Validate App Password format
            if not self._validate_app_password(app_password):
                return {
                    "success": False,
                    "function_name": "gmail_send",
                    "error": {
                        "message": "Invalid App Password format. Should be 16 alphanumeric characters.",
                        "type": "validation_error"
                    }
                }
            
            # Send email
            self.logger.info(f"Attempting to send email from {username} to {to_email}")
            result = self._send_email(
                username=username,
                app_password=app_password,
                to_email=to_email,
                subject=subject,
                content=content,
                from_name=from_name
            )
            
            # Store result in context
            ctx.set("skill:gmail_send:last_result", result)
            ctx.set(f"skill:gmail_send:result", result)
            
            self.last_result = result
            
            if result["success"]:
                return {
                    "success": True,
                    "function_name": "gmail_send",
                    "result": {
                        "message": result["message"],
                        "timestamp": result["timestamp"],
                        "from": username,
                        "to": to_email,
                        "subject": subject
                    }
                }
            else:
                return {
                    "success": False,
                    "function_name": "gmail_send",
                    "error": {
                        "message": result["message"],
                        "type": result["error_type"],
                        "details": result.get("details")
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Unexpected error in gmail_send: {str(e)}")
            return {
                "success": False,
                "function_name": "gmail_send",
                "error": {
                    "message": f"Unexpected error: {str(e)}",
                    "type": "execution_error"
                }
            }
    
    def get_mcp_resources(self) -> List[McpResource]:
        """Define MCP Resources for Gmail Send skill"""
        return [
            McpResource(
                uri="skill://gmail_send/last_result",
                name="gmail_send_last_result",
                description="Last email sending result with status and details",
                mime_type="application/json"
            ),
            McpResource(
                uri="skill://gmail_send/status",
                name="gmail_send_status",
                description="Current status of Gmail Send skill",
                mime_type="application/json"
            )
        ]
    
    def get_mcp_prompts(self) -> List[McpPrompt]:
        """Define MCP Prompts for Gmail Send skill"""
        return [
            McpPrompt(
                name="gmail_send_help",
                description="Get help and usage instructions for Gmail Send skill",
                arguments=[]
            )
        ]
    
    def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read MCP resource"""
        if uri == "skill://gmail_send/last_result":
            result = self.last_result or {"message": "No emails sent yet"}
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(result, ensure_ascii=False, indent=2)
                    }
                ]
            }
        elif uri == "skill://gmail_send/status":
            status = {
                "skill_name": "gmail_send",
                "status": "ready",
                "smtp_server": self.smtp_server,
                "smtp_port": self.smtp_port,
                "markdown_support": {
                    "available": MARKDOWN_AVAILABLE,
                    "version": MARKDOWN_VERSION,
                    "extensions": AVAILABLE_EXTENSIONS,
                    "enhanced_styling": True,
                    "email_safe_css": True,
                    "fallback_converter": True
                },
                "features": {
                    "html_conversion": True,
                    "css_styling": True,
                    "table_support": 'tables' in AVAILABLE_EXTENSIONS,
                    "code_highlighting": 'codehilite' in AVAILABLE_EXTENSIONS,
                    "toc_generation": 'toc' in AVAILABLE_EXTENSIONS,
                    "advanced_formatting": True
                },
                "last_execution": self.last_result is not None
            }
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(status, ensure_ascii=False, indent=2)
                    }
                ]
            }
        
        return super().read_resource(uri)
    
    def get_prompt(self, name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get MCP prompt"""
        if name == "gmail_send_help":
            help_text = """
# Gmail Send Skill Usage

This skill allows you to send emails via Gmail using App Password authentication.

## Required Parameters:
- **username**: Your Gmail address (e.g., user@gmail.com)
- **app_password**: 16-character App Password from Google Account settings
- **content**: Email content in Markdown format
- **to_email**: Recipient email address

## Optional Parameters:
- **subject**: Email subject line (default: "Email from Gmail Send Skill")
- **from_name**: Display name for sender (default: uses username)

## App Password Setup:
1. Go to Google Account settings
2. Enable 2-Factor Authentication
3. Generate App Password for "Mail"
4. Use the 16-character password (spaces optional)

## Markdown Support:
The skill automatically converts Markdown to HTML for rich formatting:
- Headers: # ## ###
- Lists: - * 1.
- Links: [text](url)
- Bold: **text**
- Italic: *text*
- Code: `code`

## Example:
```json
{
  "username": "sender@gmail.com",
  "app_password": "abcd efgh ijkl mnop",
  "to_email": "recipient@example.com",
  "subject": "Test Email",
  "content": "# Hello\\n\\nThis is a **test** email with *markdown* formatting.\\n\\n- Item 1\\n- Item 2"
}
```
            """
            
            return {
                "description": "Gmail Send Skill usage help",
                "messages": [
                    {
                        "role": "user",
                        "content": {
                            "type": "text",
                            "text": help_text
                        }
                    }
                ]
            }
        
        return {
            "description": f"Prompt {name} not found",
            "messages": []
        }

# Test function for standalone execution
def test_gmail_send():
    """Test function for the Gmail Send skill"""
    skill = GmailSendSkill()
    ctx = ExecutionContext()
    
    print("Testing Gmail Send Skill...")
    print("Schema:", json.dumps(skill.get_openai_schema(), indent=2))
    
    # Note: Don't include real credentials in test
    test_params = {
        "username": "test@gmail.com",
        "app_password": "1234567890123456",
        "content": "# Test Email\n\nThis is a test email with **markdown** formatting.",
        "to_email": "recipient@example.com",
        "subject": "Test Subject"
    }
    
    print("Test parameters (without real credentials):", test_params)
    print("Use real credentials to test actual email sending.")

if __name__ == "__main__":
    test_gmail_send()