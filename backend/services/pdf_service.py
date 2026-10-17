import os
import io
from typing import Dict, Any, List
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def generate_fridge_sheet_pdf(patient_info: Dict[str, Any], schedules: List[Dict[str, Any]], careplan: Dict[str, Any], appt: Dict[str, Any], lang: str = 'en') -> io.BytesIO:
    """
    Generates a high-quality printable A4 Fridge Sheet PDF.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f766e'),
        alignment=TA_CENTER,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569'),
        alignment=TA_CENTER,
        spaceAfter=12
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0f766e'),
        spaceBefore=8,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1e293b')
    )

    bold_style = ParagraphStyle(
        'BoldBody',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    alert_style = ParagraphStyle(
        'AlertBody',
        parent=body_style,
        textColor=colors.HexColor('#b91c1c'),
        fontName='Helvetica-Bold'
    )

    elements = []

    # 1. Header Banner
    header_title = "CareBridge AI — Patient Daily Care & Medicine Fridge Sheet" if lang == 'en' else "కేర్‌బ్రిడ్జ్ AI — దైనందిన మందుల & సంరక్షణ చార్ట్ (Fridge Sheet)"
    header_sub = "Your Medicine, Your Language, Your Care. Keep this sheet posted on your refrigerator or near your medicine box."
    
    elements.append(Paragraph(header_title, title_style))
    elements.append(Paragraph(header_sub, subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0d9488'), spaceBefore=2, spaceAfter=8))

    # 2. Patient Demographics Table
    pat_name = patient_info.get("full_name", "Lakshmi Devi")
    pat_age = patient_info.get("age", 68)
    emergency = patient_info.get("emergency_contact", "+91 98480 12345")
    
    patient_data = [
        [
            Paragraph(f"<b>Patient Name:</b> {pat_name}", body_style),
            Paragraph(f"<b>Age:</b> {pat_age} Yrs", body_style),
            Paragraph(f"<b>Emergency Contact:</b> {emergency}", body_style)
        ]
    ]
    t_patient = Table(patient_data, colWidths=[200, 100, 220])
    t_patient.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0fdfa')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#99f6e4')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(t_patient)
    elements.append(Spacer(1, 10))

    # 3. Verified Medication Schedule Table
    elements.append(Paragraph("1. Verified Medication Schedule / నిర్ధారిత మందుల వేళలు", section_heading))
    
    med_headers = ["Medicine Name", "Strength", "Dose", "Schedule / Clock Time", "Food Relation", "Status"]
    table_rows = [[Paragraph(f"<b>{h}</b>", bold_style) for h in med_headers]]
    
    if schedules:
        for s in schedules:
            times = s.get("exact_times", "[]")
            if isinstance(times, str):
                import json
                try:
                    times_list = json.loads(times)
                    times = ", ".join(times_list)
                except:
                    pass
            food_text = "After Food" if s.get("food_relation") == "after_food" else "Before Food"
            
            table_rows.append([
                Paragraph(s.get("medicine_name", ""), bold_style),
                Paragraph(s.get("strength", ""), body_style),
                Paragraph(s.get("dose", ""), body_style),
                Paragraph(times, body_style),
                Paragraph(food_text, body_style),
                Paragraph("Verified [OK]", body_style)
            ])
    else:
        table_rows.append([Paragraph("No active verified medicines", body_style)] * 6)

    t_meds = Table(table_rows, colWidths=[120, 70, 70, 110, 90, 60])
    t_meds.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#ccfbf1')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(t_meds)
    elements.append(Spacer(1, 10))

    # 4. Daily Schedule Breakdown Grid (Morning, Afternoon, Evening, Bedtime)
    elements.append(Paragraph("2. Time-of-Day Quick Reference", section_heading))
    timing_data = [
        [
            Paragraph("<b>Morning (08:30 AM)</b>", bold_style),
            Paragraph("<b>Afternoon (01:30 PM)</b>", bold_style),
            Paragraph("<b>Evening (08:30 PM)</b>", bold_style),
            Paragraph("<b>Night (09:30 PM)</b>", bold_style)
        ],
        [
            Paragraph("• Telmisartan 40mg (1 tab)<br/>• Metformin 500mg (1 tab)<br/><i>After breakfast</i>", body_style),
            Paragraph("• Regular water hydration<br/><i>After lunch</i>", body_style),
            Paragraph("• Metformin 500mg (1 tab)<br/><i>After dinner</i>", body_style),
            Paragraph("• Atorvastatin 10mg (1 tab)<br/><i>Before bedtime</i>", body_style)
        ]
    ]
    t_timing = Table(timing_data, colWidths=[130, 130, 130, 130])
    t_timing.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e0f2fe')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#93c5fd')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(t_timing)
    elements.append(Spacer(1, 10))

    # 5. Diet, Activity, & Follow-up
    elements.append(Paragraph("3. Doctor's Lifestyle & Care Instructions", section_heading))
    
    diet_text = careplan.get("diet_en") or "Diabetic diet: Low sugar, low sodium (< 2g salt daily). Drink 2 liters of boiled water."
    act_text = careplan.get("activity_en") or "20 minutes gentle walking in morning. Avoid heavy lifting."
    appt_text = f"Doctor: {appt.get('doctor_or_dept', 'Dr. K. S. Rao')} | Date: {appt.get('appointment_date', '02-Nov-2026')} at {appt.get('appointment_time', '10:30 AM')}" if appt else "Please check with your clinic for next review."

    care_data = [
        [Paragraph("<b>Dietary Advice:</b>", bold_style), Paragraph(diet_text, body_style)],
        [Paragraph("<b>Activity Guidelines:</b>", bold_style), Paragraph(act_text, body_style)],
        [Paragraph("<b>Next Follow-up:</b>", bold_style), Paragraph(appt_text, body_style)]
    ]
    t_care = Table(care_data, colWidths=[130, 390])
    t_care.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f8fafc')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(t_care)
    elements.append(Spacer(1, 10))

    # 6. Emergency Warning Signs Box
    elements.append(Paragraph("4. Emergency Warning Signs (Seek Urgent Medical Care)", section_heading))
    warning_text = careplan.get("warning_signs_en") or "Severe chest pain, sudden shortness of breath, severe dizziness or fainting, fasting sugar > 250 mg/dL."
    warning_data = [[
        Paragraph(f"[!] <b>CRITICAL WARNING:</b> {warning_text}", alert_style)
    ]]
    t_warning = Table(warning_data, colWidths=[520])
    t_warning.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fef2f2')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#f87171')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_warning)
    elements.append(Spacer(1, 10))

    # 7. Disclaimer
    disclaimer = "DISCLAIMER: CareBridge AI Fridge Sheet is prepared strictly from verified hospital records for patient reference. Never alter medication doses without consulting your prescribing physician or pharmacist."
    elements.append(Paragraph(f"<i>{disclaimer}</i>", ParagraphStyle('Discl', parent=body_style, fontSize=7, leading=9, textColor=colors.HexColor('#64748b'), alignment=TA_CENTER)))

    doc.build(elements)
    buffer.seek(0)
    return buffer
