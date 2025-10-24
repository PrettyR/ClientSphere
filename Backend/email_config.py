"""
Email Configuration Helper

This module helps configure email settings for the ClientSphere system.
Run this script to set up email configuration interactively.
"""

import os
import sys

def setup_email_config():
    """Interactive email configuration setup."""
    print("ClientSphere Email Configuration Setup")
    print("=" * 50)
    print()
    
    print("This will help you configure email settings for ClientSphere.")
    print("You can use Gmail, Outlook, or any other SMTP provider.")
    print()
    
    # Get email provider
    print("Select your email provider:")
    print("1. Gmail")
    print("2. Outlook/Hotmail")
    print("3. Custom SMTP")
    
    choice = input("Enter your choice (1-3): ").strip()
    
    if choice == "1":
        setup_gmail()
    elif choice == "2":
        setup_outlook()
    elif choice == "3":
        setup_custom()
    else:
        print("Invalid choice. Please run the script again.")
        return False
    
    print()
    print("Configuration complete!")
    print("You can now test the email functionality with: python test_email.py")
    return True

def setup_gmail():
    """Setup Gmail configuration."""
    print()
    print("Gmail Configuration")
    print("-" * 20)
    print()
    print("For Gmail, you need to:")
    print("1. Enable 2-Factor Authentication")
    print("2. Generate an App Password")
    print("3. Use the App Password (not your regular password)")
    print()
    
    email = input("Enter your Gmail address: ").strip()
    app_password = input("Enter your Gmail App Password (16 characters): ").strip()
    
    config = f"""
# Gmail Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME={email}
SMTP_PASSWORD={app_password}
FROM_EMAIL={email}
FROM_NAME=ClientSphere
"""
    
    save_config(config)

def setup_outlook():
    """Setup Outlook configuration."""
    print()
    print("Outlook Configuration")
    print("-" * 20)
    print()
    
    email = input("Enter your Outlook email address: ").strip()
    password = input("Enter your Outlook password: ").strip()
    
    config = f"""
# Outlook Configuration
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME={email}
SMTP_PASSWORD={password}
FROM_EMAIL={email}
FROM_NAME=ClientSphere
"""
    
    save_config(config)

def setup_custom():
    """Setup custom SMTP configuration."""
    print()
    print("Custom SMTP Configuration")
    print("-" * 25)
    print()
    
    server = input("Enter SMTP server (e.g., smtp.yourdomain.com): ").strip()
    port = input("Enter SMTP port (usually 587): ").strip() or "587"
    username = input("Enter SMTP username: ").strip()
    password = input("Enter SMTP password: ").strip()
    from_email = input("Enter 'from' email address: ").strip()
    
    config = f"""
# Custom SMTP Configuration
SMTP_SERVER={server}
SMTP_PORT={port}
SMTP_USERNAME={username}
SMTP_PASSWORD={password}
FROM_EMAIL={from_email}
FROM_NAME=ClientSphere
"""
    
    save_config(config)

def save_config(config):
    """Save configuration to .env file."""
    env_file = ".env"
    
    # Check if .env already exists
    if os.path.exists(env_file):
        print(f"\n{env_file} already exists.")
        overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Configuration not saved.")
            return
    
    # Save configuration
    try:
        with open(env_file, 'w') as f:
            f.write(config)
        print(f"\nConfiguration saved to {env_file}")
        print("You can now start the server and test email functionality.")
    except Exception as e:
        print(f"Error saving configuration: {e}")

def test_configuration():
    """Test the current email configuration."""
    print("Testing Email Configuration")
    print("=" * 30)
    
    # Check if .env exists
    if not os.path.exists(".env"):
        print("❌ No .env file found. Please run setup first.")
        return False
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️  python-dotenv not installed. Install it with: pip install python-dotenv")
        print("Or set environment variables manually.")
    
    # Check required variables
    required_vars = ["SMTP_SERVER", "SMTP_USERNAME", "SMTP_PASSWORD", "FROM_EMAIL"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All required environment variables are set!")
    print(f"SMTP Server: {os.getenv('SMTP_SERVER')}")
    print(f"From Email: {os.getenv('FROM_EMAIL')}")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_configuration()
    else:
        setup_email_config()
