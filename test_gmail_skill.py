#!/usr/bin/env python3
"""
Test Suite for Gmail Send Skill

Comprehensive tests for the Gmail Send Skill including schema validation,
parameter validation, MCP compatibility, and mock execution tests.
"""

import json
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gmail_send_skill import GmailSendSkill
from skill_compat import ExecutionContext, McpResource, McpPrompt
from mcp_server import GmailSendMcpServer

class TestGmailSendSkill(unittest.TestCase):
    """Test cases for Gmail Send Skill"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.skill = GmailSendSkill()
        self.context = ExecutionContext()
        
        # Valid test parameters
        self.valid_params = {
            "username": "test@gmail.com",
            "app_password": "abcd efgh ijkl mnop",
            "content": "# Test Email\n\nThis is a **test** email.",
            "to_email": "recipient@example.com",
            "subject": "Test Subject",
            "from_name": "Test Sender"
        }
        
        # Invalid test parameters
        self.invalid_params = {
            "bad_email": {
                "username": "invalid-email",
                "app_password": "abcdefghijklmnop",
                "content": "Test content",
                "to_email": "recipient@example.com"
            },
            "bad_app_password": {
                "username": "test@gmail.com",
                "app_password": "too-short",
                "content": "Test content", 
                "to_email": "recipient@example.com"
            },
            "missing_required": {
                "username": "test@gmail.com"
                # Missing app_password, content, to_email
            }
        }
    
    def test_schema_validity(self):
        """Test that the OpenAI schema is valid"""
        schema = self.skill.get_openai_schema()
        
        # Check basic structure
        self.assertIn("type", schema)
        self.assertEqual(schema["type"], "function")
        self.assertIn("function", schema)
        
        function_def = schema["function"]
        self.assertIn("name", function_def)
        self.assertIn("description", function_def)
        self.assertIn("parameters", function_def)
        
        # Check function name
        self.assertEqual(function_def["name"], "gmail_send")
        
        # Check parameters structure
        params = function_def["parameters"]
        self.assertIn("type", params)
        self.assertEqual(params["type"], "object")
        self.assertIn("properties", params)
        self.assertIn("required", params)
        
        # Check required parameters
        required = params["required"]
        expected_required = ["username", "app_password", "content", "to_email"]
        for param in expected_required:
            self.assertIn(param, required)
        
        # Check parameter definitions
        properties = params["properties"]
        for param in expected_required:
            self.assertIn(param, properties)
            self.assertIn("type", properties[param])
            self.assertIn("description", properties[param])
    
    def test_email_validation(self):
        """Test email address validation"""
        valid_emails = [
            "test@gmail.com",
            "user.name@example.org",
            "test+tag@domain.co.uk"
        ]
        
        invalid_emails = [
            "invalid-email",
            "@gmail.com",
            "test@",
            "test.gmail.com",
            ""
        ]
        
        for email in valid_emails:
            self.assertTrue(self.skill._validate_email(email), f"Should be valid: {email}")
        
        for email in invalid_emails:
            self.assertFalse(self.skill._validate_email(email), f"Should be invalid: {email}")
    
    def test_app_password_validation(self):
        """Test App Password validation"""
        valid_passwords = [
            "abcdefghijklmnop",
            "1234567890123456",
            "abcd efgh ijkl mnop",  # With spaces
            "ABCD1234EFGH5678"
        ]
        
        invalid_passwords = [
            "too-short",
            "abcdefghijklmnopq",  # Too long
            "abcd-efgh-ijkl-mnop",  # Special characters
            ""
        ]
        
        for password in valid_passwords:
            self.assertTrue(self.skill._validate_app_password(password), f"Should be valid: {password}")
        
        for password in invalid_passwords:
            self.assertFalse(self.skill._validate_app_password(password), f"Should be invalid: {password}")
    
    def test_markdown_conversion(self):
        """Test Markdown to HTML conversion"""
        markdown_content = "# Header\n\nThis is **bold** and *italic* text.\n\n- Item 1\n- Item 2"
        
        html_content = self.skill._convert_markdown_to_html(markdown_content)
        
        # Check that conversion happened (should contain HTML tags)
        self.assertIn("<", html_content)
        self.assertIn(">", html_content)
        
        # If markdown library is available, check for specific tags
        try:
            import markdown
            self.assertIn("<h1>", html_content)
            self.assertIn("<strong>", html_content)
            self.assertIn("<em>", html_content)
            self.assertIn("<ul>", html_content)
        except ImportError:
            # Fallback conversion should at least convert newlines
            self.assertIn("<br>", html_content)
    
    def test_parameter_validation_success(self):
        """Test successful parameter validation"""
        result = self.skill.execute(self.context, **self.valid_params)
        
        # Should not fail due to validation errors
        if not result.get("success"):
            error_type = result.get("error", {}).get("type", "")
            self.assertNotEqual(error_type, "validation_error", 
                              f"Validation should pass, but got: {result.get('error', {}).get('message')}")
    
    def test_parameter_validation_failures(self):
        """Test parameter validation error cases"""
        for case_name, params in self.invalid_params.items():
            with self.subTest(case=case_name):
                result = self.skill.execute(self.context, **params)
                
                self.assertFalse(result.get("success"), f"Should fail for {case_name}")
                self.assertEqual(result.get("error", {}).get("type"), "validation_error")
    
    @patch('smtplib.SMTP')
    def test_successful_email_send(self, mock_smtp_class):
        """Test successful email sending with mocked SMTP"""
        # Mock SMTP server
        mock_smtp = MagicMock()
        mock_smtp_class.return_value = mock_smtp
        
        result = self.skill.execute(self.context, **self.valid_params)
        
        # Check result
        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("function_name"), "gmail_send")
        self.assertIn("result", result)
        
        # Check SMTP interactions
        mock_smtp_class.assert_called_once_with("smtp.gmail.com", 587)
        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_once_with("test@gmail.com", "abcdefghijklmnop")
        mock_smtp.sendmail.assert_called_once()
        mock_smtp.quit.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_smtp_authentication_error(self, mock_smtp_class):
        """Test SMTP authentication error handling"""
        import smtplib
        
        mock_smtp = MagicMock()
        mock_smtp.login.side_effect = smtplib.SMTPAuthenticationError(535, "Authentication failed")
        mock_smtp_class.return_value = mock_smtp
        
        result = self.skill.execute(self.context, **self.valid_params)
        
        self.assertFalse(result.get("success"))
        self.assertEqual(result.get("error", {}).get("type"), "authentication_error")
    
    def test_context_storage(self):
        """Test that results are stored in context"""
        with patch('smtplib.SMTP'):
            result = self.skill.execute(self.context, **self.valid_params)
            
            # Check context storage
            stored_result = self.context.get("skill:gmail_send:result")
            self.assertIsNotNone(stored_result)
            
            last_result = self.context.get("skill:gmail_send:last_result")
            self.assertIsNotNone(last_result)


class TestMcpCompatibility(unittest.TestCase):
    """Test MCP compatibility features"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.skill = GmailSendSkill()
    
    def test_mcp_resources(self):
        """Test MCP resource definitions"""
        resources = self.skill.get_mcp_resources()
        
        self.assertIsInstance(resources, list)
        self.assertGreater(len(resources), 0)
        
        for resource in resources:
            self.assertIsInstance(resource, McpResource)
            self.assertTrue(hasattr(resource, 'uri'))
            self.assertTrue(hasattr(resource, 'name'))
            self.assertTrue(hasattr(resource, 'description'))
    
    def test_mcp_prompts(self):
        """Test MCP prompt definitions"""
        prompts = self.skill.get_mcp_prompts()
        
        self.assertIsInstance(prompts, list)
        self.assertGreater(len(prompts), 0)
        
        for prompt in prompts:
            self.assertIsInstance(prompt, McpPrompt)
            self.assertTrue(hasattr(prompt, 'name'))
            self.assertTrue(hasattr(prompt, 'description'))
    
    def test_resource_reading(self):
        """Test MCP resource reading"""
        # Test status resource
        result = self.skill.read_resource("skill://gmail_send/status")
        self.assertIn("contents", result)
        
        contents = result["contents"][0]
        self.assertIn("text", contents)
        self.assertIn("mimeType", contents)
        
        # Parse JSON content
        status_data = json.loads(contents["text"])
        self.assertIn("skill_name", status_data)
        self.assertEqual(status_data["skill_name"], "gmail_send")
    
    def test_prompt_retrieval(self):
        """Test MCP prompt retrieval"""
        result = self.skill.get_prompt("gmail_send_help")
        
        self.assertIn("description", result)
        self.assertIn("messages", result)
        self.assertIsInstance(result["messages"], list)


class TestMcpServer(unittest.TestCase):
    """Test MCP Server functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.server = GmailSendMcpServer()
    
    def test_server_info(self):
        """Test server information"""
        info = self.server.get_server_info()
        
        self.assertIn("name", info)
        self.assertIn("version", info)
        self.assertIn("description", info)
        self.assertIn("capabilities", info)
        
        capabilities = info["capabilities"]
        self.assertTrue(capabilities.get("tools"))
        self.assertTrue(capabilities.get("resources"))
        self.assertTrue(capabilities.get("prompts"))
    
    def test_tool_listing(self):
        """Test tool listing"""
        tools = self.server.list_tools()
        
        self.assertIsInstance(tools, list)
        self.assertEqual(len(tools), 1)
        
        tool = tools[0]
        self.assertEqual(tool["name"], "gmail_send")
        self.assertIn("description", tool)
        self.assertIn("inputSchema", tool)
    
    def test_resource_listing(self):
        """Test resource listing"""
        resources = self.server.list_resources()
        
        self.assertIsInstance(resources, list)
        self.assertGreater(len(resources), 0)
        
        for resource in resources:
            self.assertIn("uri", resource)
            self.assertIn("name", resource)
            self.assertIn("description", resource)
    
    def test_prompt_listing(self):
        """Test prompt listing"""
        prompts = self.server.list_prompts()
        
        self.assertIsInstance(prompts, list)
        self.assertGreater(len(prompts), 0)
        
        for prompt in prompts:
            self.assertIn("name", prompt)
            self.assertIn("description", prompt)
    
    @patch('smtplib.SMTP')
    def test_tool_execution(self, mock_smtp_class):
        """Test tool execution through MCP server"""
        mock_smtp = MagicMock()
        mock_smtp_class.return_value = mock_smtp
        
        test_args = {
            "username": "test@gmail.com",
            "app_password": "abcdefghijklmnop",
            "content": "Test email",
            "to_email": "recipient@example.com"
        }
        
        result = self.server.call_tool("gmail_send", test_args)
        
        self.assertIn("content", result)
        self.assertIsInstance(result["content"], list)
        
        content_text = result["content"][0]["text"]
        result_data = json.loads(content_text)
        
        self.assertIn("tool_result", result_data)
        self.assertTrue(result_data["tool_result"].get("success"))


def run_tests():
    """Run all tests"""
    # Create test suite
    test_classes = [
        TestGmailSendSkill,
        TestMcpCompatibility, 
        TestMcpServer
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success status
    return result.wasSuccessful()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Gmail Send Skill Test Suite")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--test", "-t", help="Run specific test class or method")
    
    args = parser.parse_args()
    
    if args.test:
        # Run specific test
        unittest.main(argv=[''], module=args.test, verbosity=2 if args.verbose else 1)
    else:
        # Run all tests
        print("🧪 Gmail Send Skill - Test Suite")
        print("================================")
        print()
        
        success = run_tests()
        
        print()
        if success:
            print("✅ All tests passed!")
            sys.exit(0)
        else:
            print("❌ Some tests failed!")
            sys.exit(1)