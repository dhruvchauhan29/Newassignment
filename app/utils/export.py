"""Export utilities for generating PDFs and other formats."""
from datetime import datetime
from io import BytesIO
from typing import Any, Dict

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer


def generate_pdf_report(data: Dict[str, Any]) -> BytesIO:
    """Generate a PDF report from data.

    Args:
        data: Report data

    Returns:
        PDF file as BytesIO
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title = data.get("title", "Project Report")
    story.append(Paragraph(title, styles["Title"]))
    story.append(Spacer(1, 12))

    # Date
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    story.append(Paragraph(f"Generated: {date_str}", styles["Normal"]))
    story.append(Spacer(1, 24))

    # Content sections
    sections = data.get("sections", [])
    for section in sections:
        section_title = section.get("title", "")
        section_content = section.get("content", "")

        story.append(Paragraph(section_title, styles["Heading1"]))
        story.append(Spacer(1, 12))
        story.append(Paragraph(section_content, styles["Normal"]))
        story.append(Spacer(1, 24))

    doc.build(story)
    buffer.seek(0)
    return buffer


def export_to_markdown(data: Dict[str, Any]) -> str:
    """Export data to Markdown format.

    Args:
        data: Data to export

    Returns:
        Markdown string
    """
    md = []

    # Title
    title = data.get("title", "Project Report")
    md.append(f"# {title}\n")

    # Date
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    md.append(f"**Generated:** {date_str}\n")

    # Content sections
    sections = data.get("sections", [])
    for section in sections:
        section_title = section.get("title", "")
        section_content = section.get("content", "")

        md.append(f"\n## {section_title}\n")
        md.append(f"{section_content}\n")

    return "\n".join(md)
