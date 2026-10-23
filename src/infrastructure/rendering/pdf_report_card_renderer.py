from fpdf import FPDF
from fpdf.enums import XPos, YPos

from src.academic.application.interfaces.report_card_renderer import ReportCardRenderer
from src.academic.domain.entities.report_card import ReportCard


class PdfReportCardRenderer(ReportCardRenderer):
    """Render only the immutable published snapshot; no database reads occur."""

    def render(self, report_card: ReportCard) -> bytes:
        if report_card.status.value != "ISSUED":
            raise ValueError("Seul un bulletin emis peut etre rendu.")
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, self._text("EduNova - Bulletin officiel"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", size=10)
        pdf.cell(0, 7, self._text(f"Bulletin {report_card.id} - version {report_card.report_version}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 7, self._text(f"Periode: {report_card.snapshot.get('academic_period_id', report_card.academic_period_id)}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 7, self._text(f"Publie le: {report_card.issued_at.isoformat() if report_card.issued_at else 'N/A'}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(5)
        snapshot = report_card.snapshot
        pdf.cell(0, 7, self._text(f"Moyenne generale: {snapshot.get('general_average', 'N/A')}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 7, self._text(f"Matieres echouees: {snapshot.get('failed_subjects', 'N/A')}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 7, self._text(f"Credits: {snapshot.get('credits_obtained', 'N/A')} / {snapshot.get('total_credits', 'N/A')}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(5)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(80, 7, "Matiere", border=1)
        pdf.cell(45, 7, "Moyenne", border=1)
        pdf.cell(45, 7, "Coefficient", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", size=10)
        for result in snapshot.get("subject_results", []):
            pdf.cell(80, 7, self._text(str(result.get("subject_id", ""))), border=1)
            pdf.cell(45, 7, self._text(str(result.get("average", ""))), border=1)
            pdf.cell(45, 7, self._text(str(result.get("coefficient", ""))), border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        output = pdf.output()
        return bytes(output)

    @staticmethod
    def _text(value: str) -> str:
        return value.encode("latin-1", "replace").decode("latin-1")
