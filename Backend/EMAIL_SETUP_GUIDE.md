# Email Configuration Guide for ClientSphere

## Overview

The ClientSphere system now includes a comprehensive email service for sending verification codes, notifications, and other system emails. This guide explains how to configure email functionality.

## Email Service Features

- ✅ **Verification Code Emails**: Beautiful HTML emails with verification codes
- ✅ **Welcome Emails**: Professional welcome messages for new users
- ✅ **Account Approval Notifications**: Email notifications when accounts are approved
- ✅ **Fallback Handling**: Graceful fallback when email delivery fails
- ✅ **Multiple Email Providers**: Support for Gmail, Outlook, and other SMTP providers

## Configuration

### 1. Environment Variables

Create a `.env` file in the Backend directory with the following variables:

```bash
# SMTP Server Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Email Settings
FROM_EMAIL=noreply@clientsphere.local
FROM_NAME=ClientSphere
```

### 2. Gmail Configuration (Recommended)

For Gmail, you'll need to:

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate an App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a password for "Mail"
   - Use this password in `SMTP_PASSWORD`

3. **Update your .env file**:
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-gmail@gmail.com
SMTP_PASSWORD=your-16-character-app-password
FROM_EMAIL=your-gmail@gmail.com
FROM_NAME=ClientSphere
```

### 3. Outlook/Hotmail Configuration

```bash
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-password
FROM_EMAIL=your-email@outlook.com
FROM_NAME=ClientSphere
```

### 4. Custom SMTP Server

```bash
SMTP_SERVER=your-smtp-server.com
SMTP_PORT=587
SMTP_USERNAME=your-username
SMTP_PASSWORD=your-password
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=ClientSphere
```

## Email Templates

### Verification Code Email
- **Subject**: "ClientSphere - Email Verification Code"
- **Content**: Professional HTML template with verification code
- **Features**: 
  - Responsive design
  - Clear code display
  - Security instructions
  - Branded styling

### Welcome Email
- **Subject**: "Welcome to ClientSphere!"
- **Content**: Welcome message with platform features
- **Features**:
  - Platform introduction
  - Feature highlights
  - Getting started guide

### Account Approval Email
- **Subject**: "ClientSphere - Account Approved!"
- **Content**: Notification of account approval
- **Features**:
  - Approval confirmation
  - Next steps
  - Support information

## Fallback Handling

The system includes intelligent fallback mechanisms:

1. **Email Delivery Failure**: If email sending fails, the system will:
   - Log the verification code to console
   - Return the code in the API response
   - Provide clear instructions to the user

2. **No Email Configuration**: If no SMTP settings are provided:
   - System continues to work
   - Codes are logged to console
   - Users receive codes via API response

## Testing Email Functionality

### 1. Test Email Service

```python
from utils.email_service import send_verification_code_email

# Test sending a verification code
success = send_verification_code_email(
    email="test@example.com",
    code="123456",
    user_name="Test User"
)

if success:
    print("Email sent successfully!")
else:
    print("Email sending failed - check SMTP configuration")
```

### 2. Test via API

```bash
# Test verification code sending
curl -X POST http://localhost:5000/api/users/send-code \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

## Troubleshooting

### Common Issues

1. **"Authentication failed"**
   - Check SMTP credentials
   - Ensure 2FA is enabled for Gmail
   - Use App Password instead of regular password

2. **"Connection refused"**
   - Check SMTP server and port
   - Verify firewall settings
   - Test with different SMTP server

3. **"Email not received"**
   - Check spam/junk folder
   - Verify email address is correct
   - Check SMTP server logs

### Debug Mode

Enable debug logging by setting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Security Considerations

1. **Never commit .env files** to version control
2. **Use App Passwords** instead of regular passwords
3. **Rotate credentials** regularly
4. **Monitor email usage** for unusual activity
5. **Use dedicated email accounts** for system emails

## Production Deployment

### 1. Environment Variables
Set environment variables in your production environment:

```bash
export SMTP_SERVER=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USERNAME=production@yourdomain.com
export SMTP_PASSWORD=your-secure-app-password
export FROM_EMAIL=noreply@yourdomain.com
export FROM_NAME=ClientSphere
```

### 2. Email Service Monitoring
- Monitor email delivery rates
- Set up alerts for email failures
- Track bounce rates and spam complaints

### 3. Rate Limiting
Consider implementing rate limiting for email sending to prevent abuse.

## Support

If you encounter issues with email configuration:

1. Check the application logs for error messages
2. Verify SMTP settings with your email provider
3. Test with a simple email client first
4. Contact your system administrator for assistance

## Example .env File

```bash
# Database
DATABASE_URL=mysql+pymysql://username:password@localhost/clientsphere

# JWT
JWT_SECRET_KEY=your-secret-key-here

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=clientsphere@gmail.com
SMTP_PASSWORD=abcd-efgh-ijkl-mnop
FROM_EMAIL=clientsphere@gmail.com
FROM_NAME=ClientSphere

# Default Admin
DEFAULT_ADMIN_EMAIL=prettyraradza@gmail.com
DEFAULT_ADMIN_PASS=Password#
```

This configuration will enable full email functionality in your ClientSphere system.
