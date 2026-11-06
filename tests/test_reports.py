"""
RR TalentIQ - Unit Tests for Strategy Reporting Engines (PDF & PPTX)
Validates that PDF strategy briefs and 16-slide PowerPoint presentations
generate successfully with non-empty content and correct binary headers.
"""

import pytest
from reports.executive_summary import ExecutiveSummaryPDFGenerator
from reports.presentation_export import PresentationDeckGenerator


def test_pdf_report_generation():
    """Verifies that the PDF strategy report compiles cleanly and begins with %PDF."""
    pdf_bytes = ExecutiveSummaryPDFGenerator.generate_pdf()
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 1000
    # Standard PDF magic header
    assert pdf_bytes.startswith(b"%PDF")


def test_pptx_deck_generation():
    """Verifies that the 16-slide PowerPoint deck generates cleanly and starts with ZIP header."""
    pptx_bytes = PresentationDeckGenerator.generate_presentation_deck()
    assert pptx_bytes is not None
    assert len(pptx_bytes) > 5000
    # Standard PK ZIP header for PPTX (OpenXML)
    assert pptx_bytes.startswith(b"PK")

