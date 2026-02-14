"""
Gmail Send Skill - Email Sending with App Password

This skill provides functionality to send emails via Gmail using App Password authentication.
Supports Markdown content conversion to HTML and returns success/failure status.
"""

import smtplib
import json
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from typing import Any, Dict, List
from datetime import datetime

try:
    import markdown
except ImportError:
    markdown = None

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
    
    def _convert_markdown_to_html(self, markdown_content: str) -> str:
        """Convert Markdown content to HTML"""
        if markdown is None:
            self.logger.warning("Markdown library not available, sending as plain text")
            return markdown_content.replace('\n', '<br>')
        
        try:
            html = markdown.markdown(
                markdown_content,
                extensions=['tables', 'fenced_code', 'nl2br']
            )
            return html
        except Exception as e:
            self.logger.error(f"Failed to convert Markdown to HTML: {str(e)}")
            # Fallback: simple newline to BR conversion
            return markdown_content.replace('\n', '<br>')
    
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
                "markdown_support": markdown is not None,
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