"""
GitHub Sentinel Email Notifier

This module provides email notification functionality for GitHub Sentinel reports.

SECURE CONFIGURATION using Environment Variables:

Required Environment Variables (for security):
- EMAIL_ADDRESS: Your sender email address (e.g., your_email@gmail.com)
- EMAIL_PASSWORD: Your email password or app password
- RECIPIENT_EMAIL: Recipient email address (optional, defaults to sender email)

Example .env file:
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_16_character_app_password
RECIPIENT_EMAIL=recipient@example.com

SMTP Configuration in config.json:
{
    "notification_settings": {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587
    }
}

For Gmail users:
1. Enable 2-factor authentication in your Google Account
2. Generate an App Password: https://support.google.com/accounts/answer/185833
3. Use the 16-character App Password (not your regular password) in EMAIL_PASSWORD
4. Set EMAIL_ADDRESS to your Gmail address

This approach keeps sensitive credentials out of your repository while maintaining functionality.
"""

import smtplib
import markdown2
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from logger import LOG


class Notifier:
    def __init__(self, settings):
        self.settings = settings
    
    def notify(self, report, repo_name=None):
        """
        Send notification via email
        
        Args:
            report: The report content (can be markdown or plain text)
            repo_name: Optional repository name for the email subject
        """
        if not self.settings or not self.settings.get('email'):
            LOG.warning("No email configuration found, skipping notification")
            return
            
        try:
            self._send_email(report, repo_name)
            LOG.info("Email notification sent successfully")
        except Exception as e:
            LOG.error(f"Failed to send email notification: {e}")
    
    def _send_email(self, report, repo_name=None):
        """Send email notification"""
        # Email configuration
        smtp_server = self.settings.get('smtp_server', 'smtp.gmail.com')
        smtp_port = self.settings.get('smtp_port', 587)
        email_address = self.settings.get('email')
        email_password = self.settings.get('email_password')
        recipient_email = self.settings.get('recipient_email', email_address)
        
        if not email_address or not email_password:
            raise ValueError("Email address and password are required in notification settings")
        
        # Create message
        msg = MIMEMultipart('alternative')
        
        # Set subject
        if repo_name:
            subject = f"GitHub Sentinel Report - {repo_name}"
        else:
            subject = "GitHub Sentinel Report"
        msg['Subject'] = subject
        msg['From'] = email_address
        msg['To'] = recipient_email
        
        # Convert markdown to HTML if the report looks like markdown
        if self._is_markdown(report):
            try:
                html_content = markdown2.markdown(report)
                html_part = MIMEText(html_content, 'html')
                msg.attach(html_part)
                LOG.debug("Report converted from markdown to HTML")
            except Exception as e:
                LOG.warning(f"Failed to convert markdown to HTML: {e}")
                # Fallback to plain text
                text_part = MIMEText(report, 'plain')
                msg.attach(text_part)
        else:
            # Send as plain text
            text_part = MIMEText(report, 'plain')
            msg.attach(text_part)
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_address, email_password)
            server.send_message(msg)
    
    def _is_markdown(self, text):
        """Simple heuristic to detect if text contains markdown"""
        markdown_indicators = ['#', '*', '**', '```', '[', '](', '|']
        return any(indicator in text for indicator in markdown_indicators)
