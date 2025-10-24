"""
Email Service for ClientSphere

This module handles email sending functionality including verification codes,
notifications, and other system emails.
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import logging
from typing import Optional, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails through various providers."""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@clientsphere.local")
        self.from_name = os.getenv("FROM_NAME", "ClientSphere")
        
    def send_email(
        self, 
        to_email: str, 
        subject: str, 
        body: str, 
        is_html: bool = False,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None
    ) -> bool:
        """
        Send an email to the specified recipient.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            is_html: Whether the body is HTML format
            cc_emails: List of CC email addresses
            bcc_emails: List of BCC email addresses
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add CC and BCC if provided
            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)
            if bcc_emails:
                msg['Bcc'] = ', '.join(bcc_emails)
            
            # Create email body
            if is_html:
                html_part = MIMEText(body, 'html')
                msg.attach(html_part)
            else:
                text_part = MIMEText(body, 'plain')
                msg.attach(text_part)
            
            # Connect to SMTP server
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            
            # Login if credentials are provided
            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)
            
            # Send email
            all_recipients = [to_email]
            if cc_emails:
                all_recipients.extend(cc_emails)
            if bcc_emails:
                all_recipients.extend(bcc_emails)
                
            server.sendmail(self.from_email, all_recipients, msg.as_string())
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_verification_code(self, email: str, code: str, user_name: str = None, verify_link: str = None) -> bool:
        """
        Send email verification code to user.
        
        Args:
            email: User's email address
            code: Verification code
            user_name: User's name (optional)
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        subject = "ClientSphere - Verify your email"
        
        # Create HTML email template
        link_html = f"<p><a href=\"{verify_link}\" style=\"background:#667eea;color:#fff;padding:12px 20px;text-decoration:none;border-radius:6px\">Verify Email</a></p>" if verify_link else ""
        link_text = f"Verify Link: {verify_link}\n\n" if verify_link else ""

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Email Verification</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .code {{
                    background: #fff;
                    border: 2px solid #667eea;
                    border-radius: 8px;
                    padding: 20px;
                    text-align: center;
                    font-size: 24px;
                    font-weight: bold;
                    color: #667eea;
                    margin: 20px 0;
                    letter-spacing: 3px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 20px;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>ClientSphere</h1>
                <p>Email Verification</p>
            </div>
            <div class="content">
                <h2>Hello{f' {user_name}' if user_name else ''}!</h2>
                <p>Thank you for registering with ClientSphere. To complete your registration, please use the verification code below:</p>
                
                <div class=\"code\">{code}</div>
                {link_html}
                
                <p><strong>Important:</strong></p>
                <ul>
                    <li>This code will expire in 10 minutes</li>
                    <li>Do not share this code with anyone</li>
                    <li>If you didn't request this code, please ignore this email</li>
                </ul>
                
                <p>If you have any questions, please contact our support team.</p>
                
                <p>Best regards,<br>The ClientSphere Team</p>
            </div>
            <div class="footer">
                <p>This is an automated message. Please do not reply to this email.</p>
            </div>
        </body>
        </html>
        """
        
        # Create plain text version
        text_body = f"""
        ClientSphere - Email Verification
        
        Hello{f' {user_name}' if user_name else ''}!
        
        Thank you for registering with ClientSphere. To complete your registration, please use the verification code below:
        
        Verification Code: {code}
        {link_text}
        
        Important:
        - This code will expire in 10 minutes
        - Do not share this code with anyone
        - If you didn't request this code, please ignore this email
        
        If you have any questions, please contact our support team.
        
        Best regards,
        The ClientSphere Team
        
        ---
        This is an automated message. Please do not reply to this email.
        """
        
        # Try HTML first, fallback to plain text
        success = self.send_email(email, subject, html_body, is_html=True)
        if not success:
            success = self.send_email(email, subject, text_body, is_html=False)
            
        return success
    
    def send_welcome_email(self, email: str, user_name: str = None) -> bool:
        """
        Send welcome email to newly registered user.
        
        Args:
            email: User's email address
            user_name: User's name (optional)
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        subject = "Welcome to ClientSphere!"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Welcome to ClientSphere</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .button {{
                    background: #667eea;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 5px;
                    display: inline-block;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Welcome to ClientSphere!</h1>
            </div>
            <div class="content">
                <h2>Hello{f' {user_name}' if user_name else ''}!</h2>
                <p>Welcome to ClientSphere - your comprehensive client segmentation and analytics platform!</p>
                
                <p>Your account has been successfully created and is now ready to use. Here's what you can do:</p>
                
                <ul>
                    <li>Upload and analyze client data</li>
                    <li>Generate client segments using machine learning</li>
                    <li>Create personalized client strategies</li>
                    <li>Track and monitor client engagement</li>
                </ul>
                
                <p>Get started by logging into your account and exploring the dashboard.</p>
                
                <p>If you have any questions or need assistance, our support team is here to help.</p>
                
                <p>Best regards,<br>The ClientSphere Team</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(email, subject, html_body, is_html=True)
    
    def send_account_approved_email(self, email: str, user_name: str = None) -> bool:
        """
        Send account approval notification email.
        
        Args:
            email: User's email address
            user_name: User's name (optional)
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        subject = "ClientSphere - Account Approved!"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Account Approved</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Account Approved!</h1>
            </div>
            <div class="content">
                <h2>Hello{f' {user_name}' if user_name else ''}!</h2>
                <p>Great news! Your ClientSphere account has been approved by an administrator.</p>
                
                <p>You can now:</p>
                <ul>
                    <li>Log in to your account</li>
                    <li>Access all platform features</li>
                    <li>Start analyzing your client data</li>
                </ul>
                
                <p>Welcome to the ClientSphere community!</p>
                
                <p>Best regards,<br>The ClientSphere Team</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(email, subject, html_body, is_html=True)


# Global email service instance
email_service = EmailService()


def send_verification_code_email(email: str, code: str, user_name: str = None) -> bool:
    """
    Convenience function to send verification code email.
    
    Args:
        email: User's email address
        code: Verification code
        user_name: User's name (optional)
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    return email_service.send_verification_code(email, code, user_name)


def send_welcome_email(email: str, user_name: str = None) -> bool:
    """
    Convenience function to send welcome email.
    
    Args:
        email: User's email address
        user_name: User's name (optional)
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    return email_service.send_welcome_email(email, user_name)


def send_account_approved_email(email: str, user_name: str = None) -> bool:
    """
    Convenience function to send account approval email.
    
    Args:
        email: User's email address
        user_name: User's name (optional)
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    return email_service.send_account_approved_email(email, user_name)
