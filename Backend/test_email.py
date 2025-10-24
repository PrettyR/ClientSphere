"""
Test script for email functionality

This script tests the email service to ensure verification codes
and other emails are being sent correctly.
"""

import os
from utils.email_service import send_verification_code_email, send_welcome_email, send_account_approved_email

def test_email_configuration():
    """Test if email configuration is properly set up."""
    print("Testing Email Configuration")
    print("=" * 40)
    
    # Check environment variables
    smtp_server = os.getenv("SMTP_SERVER", "Not set")
    smtp_username = os.getenv("SMTP_USERNAME", "Not set")
    smtp_password = os.getenv("SMTP_PASSWORD", "Not set")
    from_email = os.getenv("FROM_EMAIL", "Not set")
    
    print(f"SMTP Server: {smtp_server}")
    print(f"SMTP Username: {smtp_username}")
    print(f"SMTP Password: {'Set' if smtp_password != 'Not set' else 'Not set'}")
    print(f"From Email: {from_email}")
    print()
    
    if smtp_server == "Not set" or smtp_username == "Not set":
        print("❌ Email configuration is incomplete!")
        print("Please set the following environment variables:")
        print("- SMTP_SERVER")
        print("- SMTP_USERNAME") 
        print("- SMTP_PASSWORD")
        print("- FROM_EMAIL")
        print()
        print("See EMAIL_SETUP_GUIDE.md for detailed instructions.")
        return False
    
    print("✅ Email configuration looks good!")
    return True

def test_verification_email():
    """Test sending a verification code email."""
    print("Testing Verification Code Email")
    print("=" * 40)
    
    test_email = input("Enter test email address (or press Enter to skip): ").strip()
    if not test_email:
        print("Skipping email test.")
        return True
    
    test_code = "123456"
    test_name = "Test User"
    
    print(f"Sending verification code to {test_email}...")
    
    success = send_verification_code_email(
        email=test_email,
        code=test_code,
        user_name=test_name
    )
    
    if success:
        print("✅ Verification email sent successfully!")
        print(f"Check {test_email} for the email with code: {test_code}")
    else:
        print("❌ Failed to send verification email")
        print("Check your SMTP configuration and try again.")
    
    return success

def test_welcome_email():
    """Test sending a welcome email."""
    print("Testing Welcome Email")
    print("=" * 40)
    
    test_email = input("Enter test email address (or press Enter to skip): ").strip()
    if not test_email:
        print("Skipping welcome email test.")
        return True
    
    test_name = "Test User"
    
    print(f"Sending welcome email to {test_email}...")
    
    success = send_welcome_email(
        email=test_email,
        user_name=test_name
    )
    
    if success:
        print("✅ Welcome email sent successfully!")
        print(f"Check {test_email} for the welcome email")
    else:
        print("❌ Failed to send welcome email")
        print("Check your SMTP configuration and try again.")
    
    return success

def test_approval_email():
    """Test sending an account approval email."""
    print("Testing Account Approval Email")
    print("=" * 40)
    
    test_email = input("Enter test email address (or press Enter to skip): ").strip()
    if not test_email:
        print("Skipping approval email test.")
        return True
    
    test_name = "Test User"
    
    print(f"Sending approval email to {test_email}...")
    
    success = send_account_approved_email(
        email=test_email,
        user_name=test_name
    )
    
    if success:
        print("✅ Approval email sent successfully!")
        print(f"Check {test_email} for the approval email")
    else:
        print("❌ Failed to send approval email")
        print("Check your SMTP configuration and try again.")
    
    return success

def run_all_tests():
    """Run all email tests."""
    print("Email Service Test Suite")
    print("=" * 50)
    print()
    
    # Test configuration
    if not test_email_configuration():
        print("❌ Email configuration test failed. Please fix configuration first.")
        return False
    
    print()
    
    # Test verification email
    verification_success = test_verification_email()
    print()
    
    # Test welcome email
    welcome_success = test_welcome_email()
    print()
    
    # Test approval email
    approval_success = test_approval_email()
    print()
    
    # Summary
    print("Test Results Summary")
    print("=" * 30)
    print(f"Configuration: {'✅ Pass' if True else '❌ Fail'}")
    print(f"Verification Email: {'✅ Pass' if verification_success else '❌ Fail'}")
    print(f"Welcome Email: {'✅ Pass' if welcome_success else '❌ Fail'}")
    print(f"Approval Email: {'✅ Pass' if approval_success else '❌ Fail'}")
    
    all_passed = verification_success and welcome_success and approval_success
    print()
    
    if all_passed:
        print("🎉 All email tests passed! Email service is working correctly.")
    else:
        print("❌ Some email tests failed. Check the configuration and try again.")
        print("See EMAIL_SETUP_GUIDE.md for troubleshooting help.")
    
    return all_passed

if __name__ == "__main__":
    run_all_tests()
