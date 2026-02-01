import os
from pptx import Presentation
from pptx.util import Inches
from openpyxl import Workbook
from .config import config

def generate_excel_report(study_id: int):
    """Generates a summary Excel file with Data Checks and Pre-analysis."""
    wb = Workbook()
    
    # Sheet 1: Data Checks
    ws1 = wb.active
    ws1.title = "Data Checks"
    ws1.append(["Category", "Item", "Status", "Details"])
    
    from .database import SessionLocal, DataCheck
    db = SessionLocal()
    checks = db.query(DataCheck).all() # Should filter by study_id if column existed on checks
    
    for c in checks:
        ws1.append([c.check_category, c.check_item, c.status, c.details])
        
    # Sheet 2: Pre-Analysis Means
    ws2 = wb.create_sheet("Brand Means")
    ws2.append(["Brand ID", "Metric ID", "Mean Score"])
    
    from .models import PreAnalysisResult
    means = db.query(PreAnalysisResult).filter_by(study_id=study_id).all()
    for m in means:
        ws2.append([m.brand_id, m.metric_id, m.mean_score])
        
    filename = os.path.join(config.OUTPUT_DIR, f"Report_Study_{study_id}.xlsx")
    wb.save(filename)
    print(f"Excel report saved: {filename}")
    db.close()

def generate_ppt_presentation(study_id: int):
    """Creates a PPT with the generated charts."""
    prs = Presentation()
    
    # Title Slide
    slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    title.text = f"AMRAP Analysis - Study {study_id}"
    subtitle.text = "Automated generated report"
    
    # Chart Slide
    chart_path = os.path.join(config.CHARTS_DIR, f"correlation_heatmap_{study_id}.png")
    if os.path.exists(chart_path):
        slide_layout = prs.slide_layouts[5] # Blank
        slide = prs.slides.add_slide(slide_layout)
        title = slide.shapes.title
        title.text = "Correlation Heatmap"
        
        # Add image
        left = Inches(1)
        top = Inches(2)
        height = Inches(5)
        slide.shapes.add_picture(chart_path, left, top, height=height)
        
    output_path = os.path.join(config.OUTPUT_DIR, f"Presentation_Study_{study_id}.pptx")
    prs.save(output_path)
    print(f"PPT saved: {output_path}")
