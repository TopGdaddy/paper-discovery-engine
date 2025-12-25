"""
notifier.py - Professional email notifications for paper recommendations

Clean, modern email design with accurate statistics.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from typing import List, Optional
from datetime import datetime

from database import DatabaseManager, PaperRecord

load_dotenv()


class EmailNotifier:
    """Sends beautiful, professional email notifications."""
    
    def __init__(self):
        """Initialize email configuration from environment variables."""
        self.email = os.getenv('EMAIL_ADDRESS')
        self.password = os.getenv('EMAIL_PASSWORD')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        
        if not self.email or not self.password:
            print("⚠️  Email credentials not found in .env file!")
            self.is_configured = False
        else:
            self.is_configured = True
            print(f"📧 Email notifier ready: {self.email}")
    
    def create_html_email(self, papers: List[PaperRecord], min_score: float = 0.5) -> str:
        """
        Create a stunning, professional HTML email.
        
        Args:
            papers: List of papers from database
            min_score: Only include papers with score >= this value
            
        Returns:
            HTML string for email body
        """
        
        today = datetime.now().strftime("%A, %B %d, %Y")
        
        # ---------------------------------------------------------------------
        # FILTER AND SORT PAPERS
        # ---------------------------------------------------------------------
        relevant_papers = sorted(
            [p for p in papers if p.relevance_score >= min_score],
            key=lambda p: p.relevance_score,
            reverse=True
        )[:10]  # Top 10 only
        
        # ---------------------------------------------------------------------
        # CALCULATE ACTUAL STATISTICS (BUG FIX!)
        # ---------------------------------------------------------------------
        num_papers = len(relevant_papers)
        
        if relevant_papers:
            # Get ACTUAL min and max from the papers we're showing
            actual_top_score = max(p.relevance_score for p in relevant_papers)
            actual_min_score = min(p.relevance_score for p in relevant_papers)
        else:
            actual_top_score = 0
            actual_min_score = 0
        
        # ---------------------------------------------------------------------
        # BUILD HTML EMAIL
        # ---------------------------------------------------------------------
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Digest</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f5; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
    
    <!-- Wrapper -->
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #f4f4f5;">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                
                <!-- Main Container -->
                <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="background-color: #ffffff; border-radius: 16px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); overflow: hidden;">
                    
                    <!-- Header -->
                    <tr>
                        <td style="padding: 48px 48px 32px 48px;">
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                                <tr>
                                    <td>
                                        <p style="margin: 0; font-size: 13px; font-weight: 600; color: #6366f1; text-transform: uppercase; letter-spacing: 1.5px;">
                                            Research Digest
                                        </p>
                                        <h1 style="margin: 12px 0 0 0; font-size: 26px; font-weight: 700; color: #18181b; line-height: 1.3;">
                                            Your personalized recommendations
                                        </h1>
                                        <p style="margin: 12px 0 0 0; font-size: 15px; color: #71717a;">
                                            {today}
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Divider -->
                    <tr>
                        <td style="padding: 0 48px;">
                            <div style="height: 1px; background-color: #e4e4e7;"></div>
                        </td>
                    </tr>
                    
                    <!-- Stats Bar -->
                    <tr>
                        <td style="padding: 32px 48px;">
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                                <tr>
                                    <td width="33%" style="text-align: center;">
                                        <p style="margin: 0; font-size: 32px; font-weight: 700; color: #18181b;">{num_papers}</p>
                                        <p style="margin: 4px 0 0 0; font-size: 12px; font-weight: 500; color: #a1a1aa; text-transform: uppercase; letter-spacing: 0.5px;">Papers</p>
                                    </td>
                                    <td width="33%" style="text-align: center; border-left: 1px solid #e4e4e7; border-right: 1px solid #e4e4e7;">
                                        <p style="margin: 0; font-size: 32px; font-weight: 700; color: #6366f1;">{actual_top_score:.0%}</p>
                                        <p style="margin: 4px 0 0 0; font-size: 12px; font-weight: 500; color: #a1a1aa; text-transform: uppercase; letter-spacing: 0.5px;">Best Match</p>
                                    </td>
                                    <td width="33%" style="text-align: center;">
                                        <p style="margin: 0; font-size: 32px; font-weight: 700; color: #71717a;">{actual_min_score:.0%}</p>
                                        <p style="margin: 4px 0 0 0; font-size: 12px; font-weight: 500; color: #a1a1aa; text-transform: uppercase; letter-spacing: 0.5px;">Lowest</p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
"""
        
        # ---------------------------------------------------------------------
        # PAPERS SECTION
        # ---------------------------------------------------------------------
        
        if not relevant_papers:
            html += """
                    <!-- Empty State -->
                    <tr>
                        <td style="padding: 48px; text-align: center;">
                            <p style="margin: 0; font-size: 48px;">📭</p>
                            <p style="margin: 16px 0 0 0; font-size: 18px; font-weight: 600; color: #18181b;">No papers today</p>
                            <p style="margin: 8px 0 0 0; font-size: 15px; color: #71717a;">Check back tomorrow for new recommendations.</p>
                        </td>
                    </tr>
"""
        else:
            for i, paper in enumerate(relevant_papers, 1):
                # Prepare content
                summary = paper.summary[:220].strip()
                if len(paper.summary) > 220:
                    last_space = summary.rfind(' ')
                    if last_space > 150:
                        summary = summary[:last_space] + '...'
                    else:
                        summary = summary + '...'
                
                # Format authors nicely
                authors = paper.authors
                if len(authors) > 50:
                    # Try to cut at a comma
                    comma_pos = authors[:50].rfind(',')
                    if comma_pos > 20:
                        authors = authors[:comma_pos] + ' et al.'
                    else:
                        authors = authors[:50] + '...'
                
                # Score styling
                score = paper.relevance_score
                if score >= 0.60:
                    score_color = "#059669"  # Green
                    score_bg = "#ecfdf5"
                elif score >= 0.50:
                    score_color = "#6366f1"  # Purple
                    score_bg = "#eef2ff"
                else:
                    score_color = "#71717a"  # Gray
                    score_bg = "#f4f4f5"
                
                html += f"""
                    <!-- Paper {i} -->
                    <tr>
                        <td style="padding: 0 48px;">
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-top: 1px solid #e4e4e7;">
                                <tr>
                                    <td style="padding: 28px 0;">
                                        <!-- Tags Row -->
                                        <table role="presentation" cellspacing="0" cellpadding="0">
                                            <tr>
                                                <td>
                                                    <span style="display: inline-block; background-color: {score_bg}; color: {score_color}; font-size: 12px; font-weight: 600; padding: 5px 12px; border-radius: 100px;">
                                                        {score:.0%} match
                                                    </span>
                                                </td>
                                                <td style="padding-left: 8px;">
                                                    <span style="display: inline-block; background-color: #f4f4f5; color: #52525b; font-size: 12px; font-weight: 500; padding: 5px 12px; border-radius: 100px;">
                                                        {paper.primary_category}
                                                    </span>
                                                </td>
                                            </tr>
                                        </table>
                                        
                                        <!-- Title -->
                                        <h2 style="margin: 14px 0 0 0; font-size: 17px; font-weight: 600; color: #18181b; line-height: 1.5;">
                                            <a href="{paper.abs_url}" style="color: #18181b; text-decoration: none;">
                                                {paper.title}
                                            </a>
                                        </h2>
                                        
                                        <!-- Authors -->
                                        <p style="margin: 8px 0 0 0; font-size: 14px; color: #71717a;">
                                            {authors}
                                        </p>
                                        
                                        <!-- Summary -->
                                        <p style="margin: 12px 0 0 0; font-size: 14px; color: #52525b; line-height: 1.7;">
                                            {summary}
                                        </p>
                                        
                                        <!-- Buttons -->
                                        <table role="presentation" cellspacing="0" cellpadding="0" style="margin-top: 16px;">
                                            <tr>
                                                <td>
                                                    <a href="{paper.pdf_url}" style="display: inline-block; background-color: #18181b; color: #ffffff; font-size: 13px; font-weight: 500; text-decoration: none; padding: 10px 18px; border-radius: 8px;">
                                                        Read PDF
                                                    </a>
                                                </td>
                                                <td style="padding-left: 10px;">
                                                    <a href="{paper.abs_url}" style="display: inline-block; background-color: #ffffff; color: #18181b; font-size: 13px; font-weight: 500; text-decoration: none; padding: 9px 17px; border-radius: 8px; border: 1px solid #d4d4d8;">
                                                        View on arXiv
                                                    </a>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
"""
        
        # ---------------------------------------------------------------------
        # FOOTER
        # ---------------------------------------------------------------------
        
        html += """
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 36px 48px; background-color: #fafafa; border-top: 1px solid #e4e4e7;">
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                                <tr>
                                    <td style="text-align: center;">
                                        <p style="margin: 0; font-size: 15px; font-weight: 600; color: #18181b;">
                                            Paper Discovery Engine
                                        </p>
                                        <p style="margin: 8px 0 0 0; font-size: 13px; color: #71717a; line-height: 1.5;">
                                            AI-powered research recommendations tailored to your interests
                                        </p>
                                        <p style="margin: 16px 0 0 0; font-size: 11px; color: #a1a1aa;">
                                            Built with Python &amp; Machine Learning
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                </table>
                
            </td>
        </tr>
    </table>
    
</body>
</html>
"""
        
        return html
    
    def create_plain_text(self, papers: List[PaperRecord], min_score: float = 0.5) -> str:
        """Create plain text version for email clients that don't support HTML."""
        
        today = datetime.now().strftime("%A, %B %d, %Y")
        
        relevant_papers = sorted(
            [p for p in papers if p.relevance_score >= min_score],
            key=lambda p: p.relevance_score,
            reverse=True
        )[:10]
        
        # Calculate actual stats
        if relevant_papers:
            top_score = max(p.relevance_score for p in relevant_papers)
            min_displayed = min(p.relevance_score for p in relevant_papers)
        else:
            top_score = 0
            min_displayed = 0
        
        text = f"""
RESEARCH DIGEST
{today}

Your personalized paper recommendations

Papers: {len(relevant_papers)} | Best: {top_score:.0%} | Lowest: {min_displayed:.0%}

{'=' * 55}

"""
        
        if not relevant_papers:
            text += "No papers above threshold today.\n"
        else:
            for i, paper in enumerate(relevant_papers, 1):
                authors = paper.authors[:50]
                if len(paper.authors) > 50:
                    authors += '...'
                
                summary = paper.summary[:120]
                if len(paper.summary) > 120:
                    summary += '...'
                
                text += f"""
{i}. [{paper.relevance_score:.0%}] {paper.title}

   {paper.primary_category} | {authors}
   
   {summary}
   
   PDF: {paper.pdf_url}

{'─' * 55}
"""
        
        text += """

Paper Discovery Engine
AI-powered research recommendations
"""
        
        return text
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send an email via SMTP."""
        
        if not self.is_configured:
            print("❌ Email not configured.")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Attach text version (fallback)
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            # Attach HTML version
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Connect
            print(f"📧 Connecting to {self.smtp_server}...")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            
            # Login
            print(f"🔐 Authenticating...")
            server.login(self.email, self.password)
            
            # Send
            print(f"📤 Sending to {to_email}...")
            server.send_message(msg)
            server.quit()
            
            print("✅ Email sent successfully!")
            return True
            
        except smtplib.SMTPAuthenticationError:
            print("❌ Authentication failed! Check EMAIL_PASSWORD in .env")
            return False
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def send_daily_digest(
        self,
        papers: List[PaperRecord],
        to_email: Optional[str] = None,
        min_score: float = 0.5
    ) -> bool:
        """Send daily digest with top papers."""
        
        if to_email is None:
            to_email = self.email
        
        # Filter papers for counting
        relevant_papers = [p for p in papers if p.relevance_score >= min_score]
        relevant_count = len(relevant_papers)
        
        # Create subject line
        today = datetime.now().strftime("%b %d")
        
        if relevant_count == 0:
            subject = f"Research Digest • {today}"
        elif relevant_count == 1:
            subject = f"Research Digest • {today} • 1 new paper"
        else:
            subject = f"Research Digest • {today} • {min(relevant_count, 10)} papers"
        
        # Create content
        html_content = self.create_html_email(papers, min_score)
        text_content = self.create_plain_text(papers, min_score)
        
        return self.send_email(to_email, subject, html_content, text_content)


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("📧 EMAIL NOTIFIER TEST")
    print("=" * 60)
    
    notifier = EmailNotifier()
    
    if not notifier.is_configured:
        print("\n⚠️  Configure email in .env file first!")
        exit(0)
    
    # Load papers
    print("\n📚 Loading papers...")
    db = DatabaseManager()
    papers = db.get_all_papers(limit=20)
    
    if not papers:
        print("❌ No papers found!")
        db.close()
        exit(1)
    
    # Show what we're sending
    relevant = sorted(
        [p for p in papers if p.relevance_score > 0],
        key=lambda p: p.relevance_score,
        reverse=True
    )[:10]
    
    print(f"\n📊 Papers to include:")
    print("-" * 60)
    
    if relevant:
        top_score = max(p.relevance_score for p in relevant)
        min_score = min(p.relevance_score for p in relevant)
        
        print(f"   Count: {len(relevant)}")
        print(f"   Best Match: {top_score:.0%}")
        print(f"   Lowest: {min_score:.0%}")
        print()
        
        for i, p in enumerate(relevant[:5], 1):
            print(f"   {i}. [{p.relevance_score:.0%}] {p.title[:45]}...")
        
        if len(relevant) > 5:
            print(f"   ... and {len(relevant) - 5} more")
    
    # Send
    print("\n" + "-" * 60)
    print("📤 Sending email...")
    print("-" * 60)
    
    success = notifier.send_daily_digest(
        papers=papers,
        min_score=0.0
    )
    
    db.close()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ Check your inbox!")
        print("=" * 60)