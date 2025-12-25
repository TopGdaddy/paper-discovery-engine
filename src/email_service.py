"""
email_service.py - Email Digest Service with User-Friendly Errors
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List
import re


def clean_text(text):
    """Remove ALL problematic characters"""
    if not text:
        return ""
    text = str(text)
    text = text.replace('\xa0', ' ')
    text = text.replace('\u200b', '')
    text = text.replace('\u200c', '')
    text = text.replace('\u200d', '')
    text = text.replace('\u00a0', ' ')
    text = text.replace('\r', '')
    text = text.replace('\ufeff', '')
    text = ' '.join(text.split())
    return text.strip()


def clean_email(email):
    """Clean email address"""
    if not email:
        return ""
    email = str(email).strip()
    email = re.sub(r'\s+', '', email)
    email = email.replace('\xa0', '')
    email = email.replace('\u200b', '')
    email = email.replace('\u00a0', '')
    email = email.replace('\ufeff', '')
    email = re.sub(r'[^\w.@+-]', '', email)
    return email


def has_hidden_characters(text):
    """Check if text contains hidden/problematic characters"""
    if not text:
        return False
    problematic = ['\xa0', '\u200b', '\u200c', '\u200d', '\u00a0', '\ufeff']
    for char in problematic:
        if char in str(text):
            return True
    # Check for any non-ASCII characters in email/password
    try:
        str(text).encode('ascii')
        return False
    except UnicodeEncodeError:
        return True


def get_friendly_error(error_msg: str) -> str:
    """Convert technical errors to user-friendly messages"""
    error_lower = str(error_msg).lower()
    
    # Encoding/character issues
    if 'ascii' in error_lower and 'encode' in error_lower:
        return ("⚠️ Hidden characters detected!\n\n"
                "This usually happens when you copy-paste from websites or emails.\n\n"
                "**Please try:**\n"
                "1. Clear all fields\n"
                "2. TYPE your email and password manually (don't copy-paste)\n"
                "3. Click Save Settings, then Send Test Email")
    
    if '\\xa0' in error_lower or 'ordinal' in error_lower:
        return ("⚠️ Invalid characters in your input!\n\n"
                "**Fix:** Please TYPE your email and password manually.\n"
                "Don't copy-paste from other sources.")
    
    # Authentication errors
    if 'authentication' in error_lower or 'auth' in error_lower:
        return ("🔐 Authentication Failed!\n\n"
                "**Please check:**\n"
                "1. Is your email address correct?\n"
                "2. Are you using a Gmail App Password (not your regular password)?\n"
                "3. Get an App Password here: https://myaccount.google.com/apppasswords")
    
    if 'username and password not accepted' in error_lower:
        return ("🔐 Gmail rejected the login!\n\n"
                "**You need a Gmail App Password:**\n"
                "1. Go to: myaccount.google.com/apppasswords\n"
                "2. Create a new App Password for 'Mail'\n"
                "3. Use that 16-character password here\n\n"
                "Note: Your regular Gmail password won't work!")
    
    # Connection errors
    if 'connection' in error_lower or 'timeout' in error_lower:
        return ("🌐 Connection Failed!\n\n"
                "Could not connect to the email server.\n"
                "**Please check:**\n"
                "1. Your internet connection\n"
                "2. SMTP Host: smtp.gmail.com\n"
                "3. SMTP Port: 587")
    
    if 'timed out' in error_lower:
        return ("⏱️ Connection Timed Out!\n\n"
                "The email server took too long to respond.\n"
                "Please try again in a few moments.")
    
    # DNS/host errors
    if 'getaddrinfo' in error_lower or 'name or service not known' in error_lower:
        return ("🌐 Invalid SMTP Host!\n\n"
                "**For Gmail, use:**\n"
                "- SMTP Host: smtp.gmail.com\n"
                "- SMTP Port: 587")
    
    # Default - return original with prefix
    return f"❌ Error: {error_msg}"


class EmailDigestService:
    """Email service for sending paper digests"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.smtp_host = 'smtp.gmail.com'
        self.smtp_port = 587
        self.smtp_user = ''
        self.smtp_password = ''
        self.from_email = ''
        self.from_name = 'Paper Discovery AI'
        self._load_config()
    
    def _load_config(self):
        """Load and clean SMTP config from database"""
        try:
            prefs = self.db.get_preferences()
            if prefs.smtp_host:
                self.smtp_host = clean_text(prefs.smtp_host)
            if prefs.smtp_port:
                self.smtp_port = prefs.smtp_port
            if prefs.smtp_user:
                self.smtp_user = clean_email(prefs.smtp_user)
                self.from_email = clean_email(prefs.smtp_user)
            if prefs.smtp_password:
                self.smtp_password = prefs.smtp_password
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def configure(self, smtp_host: str, smtp_port: int, smtp_user: str, smtp_password: str):
        """Configure and save email settings"""
        self.smtp_host = clean_text(smtp_host)
        self.smtp_port = smtp_port
        self.smtp_user = clean_email(smtp_user)
        self.smtp_password = smtp_password
        self.from_email = clean_email(smtp_user)
        
        self.db.update_preferences(
            smtp_host=self.smtp_host,
            smtp_port=self.smtp_port,
            smtp_user=self.smtp_user,
            smtp_password=self.smtp_password
        )
    
    def test_connection(self) -> tuple:
        """Test SMTP connection"""
        try:
            host = clean_text(self.smtp_host)
            with smtplib.SMTP(host, self.smtp_port, timeout=10) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(clean_email(self.smtp_user), self.smtp_password)
                return True, "Connection successful!"
        except Exception as e:
            return False, get_friendly_error(str(e))
    
    def _create_paper_html(self, paper) -> str:
        """Create HTML for a single paper"""
        score = paper.relevance_score or paper.user_score or 0
        score_color = '#10b981' if score >= 0.7 else '#3b82f6' if score >= 0.5 else '#8b5cf6'
        
        title = clean_text(paper.title or 'Untitled')[:150]
        authors = clean_text(paper.authors or 'Unknown')[:80]
        summary = clean_text(paper.summary or '')[:250]
        category = clean_text(paper.primary_category or 'Unknown')
        pdf_url = paper.pdf_url or '#'
        abs_url = paper.abs_url or '#'
        
        return f"""
        <div style="background: #ffffff; border-radius: 16px; padding: 24px; margin: 16px 0; 
                    border-left: 4px solid {score_color}; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <span style="background: {score_color}; color: white; padding: 6px 14px; border-radius: 20px; 
                            font-size: 13px; font-weight: 600;">{score:.0%} Match</span>
                <span style="color: #64748b; font-size: 13px;">{category}</span>
            </div>
            <h3 style="margin: 0 0 12px; color: #1e293b; font-size: 18px; line-height: 1.4;">
                <a href="{abs_url}" style="color: #1e293b; text-decoration: none;">{title}</a>
            </h3>
            <p style="color: #64748b; font-size: 14px; margin: 0 0 12px;">{authors}</p>
            <p style="color: #475569; font-size: 14px; line-height: 1.6; margin: 0 0 16px;">{summary}...</p>
            <div>
                <a href="{pdf_url}" style="background: {score_color}; color: white; padding: 10px 20px; 
                        border-radius: 8px; text-decoration: none; font-size: 14px; font-weight: 600; 
                        margin-right: 10px;">Read PDF</a>
                <a href="{abs_url}" style="background: #f1f5f9; color: #475569; padding: 10px 20px; 
                        border-radius: 8px; text-decoration: none; font-size: 14px; font-weight: 600;">arXiv</a>
            </div>
        </div>
        """
    
    def _create_digest_html(self, papers: List, digest_type: str) -> str:
        """Create full digest HTML email"""
        papers_html = '\n'.join([self._create_paper_html(p) for p in papers])
        
        interests = self.db.get_user_interests()
        top_categories = list(interests['categories'].keys())[:3]
        
        interests_html = ""
        if top_categories:
            cats_text = ', '.join([clean_text(c) for c in top_categories])
            interests_html = f"""
            <div style="background: #f8fafc; border-radius: 12px; padding: 16px; margin: 20px 0;">
                <p style="margin: 0; color: #64748b; font-size: 14px;">
                    Your interests: {cats_text}
                </p>
            </div>
            """
        
        digest_type_clean = clean_text(digest_type)
        
        return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; 
            background: #f1f5f9; margin: 0; padding: 0;">
    <div style="max-width: 680px; margin: 0 auto; padding: 40px 20px;">
        <div style="text-align: center; margin-bottom: 40px;">
            <h1 style="margin: 0; color: #1e293b; font-size: 28px; font-weight: 800;">
                Your {digest_type_clean.title()} Research Digest
            </h1>
            <p style="color: #64748b; font-size: 16px; margin: 12px 0 0;">
                {len(papers)} new papers matching your interests
            </p>
        </div>
        {interests_html}
        <div style="margin: 30px 0;">{papers_html}</div>
        <div style="text-align: center; padding: 30px 0; border-top: 1px solid #e2e8f0; margin-top: 40px;">
            <p style="color: #94a3b8; font-size: 13px; margin: 0;">
                Generated by Paper Discovery AI based on your research interests.
            </p>
        </div>
    </div>
</body>
</html>"""
    
    def send_digest(self, to_email: str, papers: List, digest_type: str = 'daily') -> tuple:
        """Send digest email"""
        if not papers:
            return False, "No papers to send"
        
        self._load_config()
        
        if not self.smtp_user or not self.smtp_password:
            return False, "📧 Email not configured. Please go to Settings and enter your SMTP credentials."
        
        # Check for hidden characters in inputs
        if has_hidden_characters(to_email):
            return False, get_friendly_error("ascii encode \\xa0")
        
        try:
            to_email_clean = clean_email(to_email)
            from_email_clean = clean_email(self.from_email)
            smtp_host_clean = clean_text(self.smtp_host)
            smtp_user_clean = clean_email(self.smtp_user)
            from_name_clean = clean_text(self.from_name)
            digest_type_clean = clean_text(digest_type)
            
            msg = MIMEMultipart('alternative')
            
            msg['Subject'] = f"Your {digest_type_clean.title()} Research Digest - {len(papers)} New Papers"
            msg['From'] = f"{from_name_clean} <{from_email_clean}>"
            msg['To'] = to_email_clean
            
            html_content = self._create_digest_html(papers, digest_type_clean)
            
            plain_text = f"Your {digest_type_clean} research digest\n\n"
            for p in papers:
                title = clean_text(p.title or 'Untitled')
                plain_text += f"- {title}\n  {p.abs_url}\n\n"
            
            part1 = MIMEText(plain_text, 'plain', 'utf-8')
            part2 = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(part1)
            msg.attach(part2)
            
            with smtplib.SMTP(smtp_host_clean, self.smtp_port) as server:
                server.starttls()
                server.login(smtp_user_clean, self.smtp_password)
                server.send_message(msg)
            
            paper_ids = [p.arxiv_id for p in papers]
            self.db.record_digest(paper_ids, digest_type_clean, 'sent')
            
            return True, f"✅ Digest sent to {to_email_clean}"
            
        except Exception as e:
            self.db.record_digest([], digest_type, 'failed')
            return False, get_friendly_error(str(e))
    
    def send_test_email(self, to_email: str) -> tuple:
        """Send a test email"""
        self._load_config()
        
        # Validate inputs first
        if not self.smtp_user or not self.smtp_password:
            return False, ("📧 SMTP not configured!\n\n"
                          "**Please:**\n"
                          "1. Enter your SMTP settings above\n"
                          "2. Click 'Save Settings' first\n"
                          "3. Then click 'Send Test Email'")
        
        # Check for hidden characters
        if has_hidden_characters(to_email):
            return False, ("⚠️ Hidden characters detected in email!\n\n"
                          "**Please:**\n"
                          "1. Clear the email field\n"
                          "2. TYPE your email manually (don't copy-paste)\n"
                          "3. Try again")
        
        if has_hidden_characters(self.smtp_user):
            return False, ("⚠️ Hidden characters in SMTP username!\n\n"
                          "**Please:**\n"
                          "1. Clear the SMTP Username field\n"
                          "2. TYPE your email manually (don't copy-paste)\n"
                          "3. Click Save Settings, then try again")
        
        if has_hidden_characters(self.smtp_password):
            return False, ("⚠️ Hidden characters in password!\n\n"
                          "**Please:**\n"
                          "1. Clear the password field\n"
                          "2. TYPE your App Password manually (don't copy-paste)\n"
                          "3. Click Save Settings, then try again")
        
        try:
            to_email_clean = clean_email(to_email)
            from_email_clean = clean_email(self.from_email)
            smtp_host_clean = clean_text(self.smtp_host)
            smtp_user_clean = clean_email(self.smtp_user)
            from_name_clean = clean_text(self.from_name)
            
            if not to_email_clean:
                return False, "❌ Invalid email address. Please check and try again."
            
            if not smtp_user_clean:
                return False, "❌ Invalid SMTP username. Please check and try again."
            
            msg = MIMEMultipart('alternative')
            
            msg['Subject'] = "Test Email from Paper Discovery"
            msg['From'] = f"{from_name_clean} <{from_email_clean}>"
            msg['To'] = to_email_clean
            
            html = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body>
<div style="font-family: sans-serif; max-width: 500px; margin: 0 auto; padding: 40px;">
    <div style="text-align: center;">
        <div style="font-size: 64px; color: #10b981;">&#10003;</div>
        <h1 style="color: #1e293b;">Email Works!</h1>
        <p style="color: #64748b;">Your Paper Discovery email integration is working correctly.</p>
        <p style="color: #94a3b8; font-size: 12px; margin-top: 30px;">
            You will now receive paper digests at this email address.
        </p>
    </div>
</div>
</body>
</html>"""
            
            plain = "Test email from Paper Discovery - Email integration is working correctly!"
            
            part1 = MIMEText(plain, 'plain', 'utf-8')
            part2 = MIMEText(html, 'html', 'utf-8')
            
            msg.attach(part1)
            msg.attach(part2)
            
            with smtplib.SMTP(smtp_host_clean, self.smtp_port, timeout=30) as server:
                server.starttls()
                server.login(smtp_user_clean, self.smtp_password)
                server.send_message(msg)
            
            return True, f"✅ Test email sent to {to_email_clean}!"
            
        except Exception as e:
            return False, get_friendly_error(str(e))
