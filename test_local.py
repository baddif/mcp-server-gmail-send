#!/usr/bin/env python3
"""
Gmail Send Skill - Local Testing Script

This script allows you to test the Gmail Send Skill using local configuration
without hardcoding credentials in the code.
"""

import json
import os
import sys
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gmail_send_skill import GmailSendSkill
from skill_compat import ExecutionContext

def load_config(config_path="config_local.json"):
    """Load configuration from local file"""
    if not os.path.exists(config_path):
        print(f"❌ Configuration file not found: {config_path}")
        print("📝 Please copy config_template.json to config_local.json and fill in your details")
        return None
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"✅ Configuration loaded from: {config_path}")
        return config
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in configuration file: {e}")
        return None
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return None

def validate_config(config):
    """Validate configuration parameters"""
    gmail_config = config.get("gmail_config", {})
    test_config = config.get("test_config", {})
    
    # Check required fields
    required_fields = {
        "gmail_config.username": gmail_config.get("username"),
        "gmail_config.app_password": gmail_config.get("app_password"),
        "test_config.to_email": test_config.get("to_email")
    }
    
    missing_fields = [field for field, value in required_fields.items() if not value or "REPLACE_WITH" in str(value)]
    
    if missing_fields:
        print("❌ Missing or incomplete configuration fields:")
        for field in missing_fields:
            print(f"   • {field}")
        print("📝 Please update config_local.json with your actual values")
        return False
    
    # Check App Password format
    app_password = gmail_config.get("app_password", "")
    clean_password = app_password.replace(" ", "")
    if len(clean_password) != 16 or not clean_password.isalnum():
        print("❌ Invalid App Password format. Should be 16 alphanumeric characters")
        print("📝 Example: 'abcd efgh ijkl mnop' or 'abcdefghijklmnop'")
        return False
    
    print("✅ Configuration validation passed")
    return True

def test_skill_basic():
    """Test basic skill functionality"""
    print("\n🧪 Testing Basic Skill Functionality...")
    
    skill = GmailSendSkill()
    
    # Test schema
    schema = skill.get_openai_schema()
    if schema and schema.get("function", {}).get("name") == "gmail_send":
        print("✅ Schema validation passed")
    else:
        print("❌ Schema validation failed")
        return False
    
    # Test MCP compatibility
    resources = skill.get_mcp_resources()
    if isinstance(resources, list) and len(resources) > 0:
        print("✅ MCP resources available")
    else:
        print("❌ MCP resources test failed")
        return False
    
    return True

def test_email_send(config, dry_run=True):
    """Test email sending (with optional dry run)"""
    print(f"\n📧 Testing Email Send {'(DRY RUN)' if dry_run else '(REAL SEND)'}...")
    
    gmail_config = config["gmail_config"]
    test_config = config["test_config"]
    
    # Initialize skill and context
    skill = GmailSendSkill()
    ctx = ExecutionContext()
    
    # Prepare test content with current date
    content = test_config.get("test_content_markdown", "# Test Email").replace(
        "{{CURRENT_DATE}}", datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    # Prepare parameters
    params = {
        "username": gmail_config["username"],
        "app_password": gmail_config["app_password"],
        "content": content,
        "to_email": test_config["to_email"],
        "subject": test_config.get("test_subject", "Gmail Send Skill Test"),
        "from_name": gmail_config.get("from_name")
    }
    
    if dry_run:
        # Validate parameters without sending
        print("📋 Test Parameters:")
        print(f"   • From: {params['from_name']} <{params['username']}>")
        print(f"   • To: {params['to_email']}")
        print(f"   • Subject: {params['subject']}")
        print(f"   • Content: {len(content)} characters")
        print(f"   • App Password: {'*' * 12}{params['app_password'][-4:]}")
        
        # Test parameter validation
        validation = skill.validate_parameters(**params)
        if validation.get("success"):
            print("✅ Parameter validation passed")
            print("🎯 Ready for real email sending!")
            return True
        else:
            print(f"❌ Parameter validation failed: {validation.get('error')}")
            return False
    else:
        # Actually send email
        print("🚀 Sending email...")
        result = skill.execute(ctx, **params)
        
        if result.get("success"):
            print("✅ Email sent successfully!")
            print(f"📊 Result: {result.get('result', {}).get('message', 'No message')}")
            return True
        else:
            error = result.get("error", {})
            print(f"❌ Email sending failed: {error.get('message', 'Unknown error')}")
            print(f"🔍 Error type: {error.get('type', 'unknown')}")
            if error.get("details"):
                print(f"🔍 Details: {error.get('details')}")
            return False

def interactive_test():
    """Interactive testing menu"""
    print("\n🎮 Interactive Test Menu")
    print("========================")
    print("1. Basic functionality test")
    print("2. Email parameters test (dry run)")
    print("3. Send real email")
    print("4. View configuration")
    print("5. Exit")
    
    while True:
        try:
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == "1":
                if test_skill_basic():
                    print("🎉 Basic functionality test passed!")
                else:
                    print("😞 Basic functionality test failed!")
                    
            elif choice == "2":
                config = load_config()
                if config and validate_config(config):
                    if test_email_send(config, dry_run=True):
                        print("🎉 Parameters test passed!")
                    else:
                        print("😞 Parameters test failed!")
                        
            elif choice == "3":
                config = load_config()
                if config and validate_config(config):
                    if not config.get("testing", {}).get("enable_real_send", False):
                        print("⚠️  Real sending is disabled in configuration")
                        print("📝 Set 'testing.enable_real_send' to true in config_local.json")
                        continue
                    
                    confirm = input("⚠️  This will send a REAL email. Continue? (y/N): ")
                    if confirm.lower() == 'y':
                        if test_email_send(config, dry_run=False):
                            print("🎉 Real email sent successfully!")
                        else:
                            print("😞 Real email sending failed!")
                    else:
                        print("📋 Email sending cancelled")
                        
            elif choice == "4":
                config = load_config()
                if config:
                    # Mask sensitive information
                    safe_config = json.loads(json.dumps(config))
                    if "app_password" in safe_config.get("gmail_config", {}):
                        password = safe_config["gmail_config"]["app_password"]
                        safe_config["gmail_config"]["app_password"] = f"{'*' * 12}{password[-4:] if len(password) >= 4 else '****'}"
                    
                    print("\n📋 Current Configuration:")
                    print(json.dumps(safe_config, indent=2, ensure_ascii=False))
                    
            elif choice == "5":
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid option. Please select 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main entry point"""
    print("🧪 Gmail Send Skill - Local Testing")
    print("====================================")
    
    # Check if config file exists
    if not os.path.exists("config_local.json"):
        print("📝 Setting up configuration...")
        print("Please copy config_template.json to config_local.json and fill in your details:")
        print("")
        print("cp config_template.json config_local.json")
        print("")
        print("Then edit config_local.json with your:")
        print("  • Gmail address")
        print("  • Gmail App Password (16 characters)")
        print("  • Test recipient email")
        print("")
        return
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "--basic":
            test_skill_basic()
        elif command == "--dry-run":
            config = load_config()
            if config and validate_config(config):
                test_email_send(config, dry_run=True)
        elif command == "--send":
            config = load_config()
            if config and validate_config(config):
                if config.get("testing", {}).get("enable_real_send", False):
                    test_email_send(config, dry_run=False)
                else:
                    print("⚠️  Real sending is disabled in configuration")
                    print("📝 Set 'testing.enable_real_send' to true in config_local.json")
        elif command == "--help":
            print("Usage:")
            print("  python3 test_local.py           - Interactive mode")
            print("  python3 test_local.py --basic   - Basic functionality test")
            print("  python3 test_local.py --dry-run - Test parameters without sending")
            print("  python3 test_local.py --send    - Send real email")
            print("  python3 test_local.py --help    - Show this help")
        else:
            print(f"Unknown command: {command}")
            print("Use --help for available commands")
    else:
        # Interactive mode
        interactive_test()

if __name__ == "__main__":
    main()