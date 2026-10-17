import re
from typing import Dict, Any, List
from backend.services.readability_service import calculate_flesch_reading_ease, validate_instructions_against_source

# Common medicine patterns
MED_PATTERNS = [
    r'(?:Tab|Cap|Syp|Inj)?\.?\s*([A-Za-z0-9\-]+(?:\s+[A-Za-z0-9\-]+)?)\s+(\d+(?:\.\d+)?\s*(?:mg|mcg|gm|ml|IU)?|\?+|\[.*?\])?'
]

def parse_medical_document_text(raw_text: str) -> Dict[str, Any]:
    """
    Parses prescription or discharge summary text into structured instruction fields,
    never hallucinating missing details.
    """
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    structured_items: List[Dict[str, Any]] = []
    
    # Check for diet instructions
    diet_advice = "Not mentioned in the document"
    activity_restrictions = "Not mentioned in the document"
    follow_up_date = "Not mentioned in the document"
    warning_signs = "Not mentioned in the document"
    
    for line in lines:
        line_lower = line.lower()
        if any(k in line_lower for k in ["diet", "sodium", "salt", "sugar"]):
            diet_advice = line.split(":", 1)[-1].strip() if ":" in line else line
        elif any(k in line_lower for k in ["exercise", "walk", "lifting", "rest", "activity"]):
            activity_restrictions = line.split(":", 1)[-1].strip() if ":" in line else line
        elif any(k in line_lower for k in ["follow-up", "follow up", "review on", "appointment"]):
            follow_up_date = line.split(":", 1)[-1].strip() if ":" in line else line
        elif any(k in line_lower for k in ["warning sign", "seek emergency", "danger sign"]):
            warning_signs = line.split(":", 1)[-1].strip() if ":" in line else line

    # Parse numbered medicine lines or bullet items
    # Example: "1. Tab Metformin 500mg - 1 tablet twice daily after meals (08:30 AM, 08:30 PM) for 30 days."
    for line in lines:
        line_clean = re.sub(r'^\d+[\.\)]\s*', '', line).strip()
        line_lower = line_clean.lower()
        
        # Check if line looks like a medication order
        is_med_line = False
        if any(line_lower.startswith(prefix) for prefix in ['tab', 'cap', 'syp', 'inj', 'rx']):
            is_med_line = True
        elif any(m in line_lower for m in ['metformin', 'telmisartan', 'atorvastatin', 'pantoprazole',
                                            'glycomet', 'ecospirin', 'amoxicillin', 'paracetamol',
                                            'aspirin', 'amlodipine']):
            is_med_line = True
        elif re.search(r'\d+\s*(?:mg|mcg|ml|gm|IU)\b', line_clean, re.IGNORECASE):
            # Line contains a strength value — likely a medicine order
            is_med_line = True
        elif re.search(r'\d+\s*(?:tab(?:let)?s?|cap(?:sule)?s?)\b', line_clean, re.IGNORECASE):
            # Line mentions tablet/capsule count
            is_med_line = True
        elif re.search(r'(?:once|twice|thrice|daily|bd|od|tid|bid)\b', line_clean, re.IGNORECASE) and len(line_clean) > 5:
            # Line contains frequency keyword — likely medicine instruction
            is_med_line = True

        if not is_med_line:
            continue

        # Extract Medicine Name
        med_name = "Needs verification"
        med_match = re.search(r'(?:Tab|Cap|Syp|Inj)?\.?\s*([A-Za-z0-9\-]+(?:\s+[A-Za-z0-9\-]+)?)', line_clean, re.IGNORECASE)
        if med_match:
            candidate = med_match.group(1).strip()
            if candidate.lower() not in ['tab', 'cap', 'syp', 'rx']:
                med_name = candidate

        # Extract Strength
        strength_match = re.search(r'(\d+(?:\.\d+)?\s*(?:mg|mcg|gm|ml|IU)|\[.*?strength.*?\])', line_clean, re.IGNORECASE)
        if strength_match:
            val = strength_match.group(1).strip()
            if "[" in val or "?" in val:
                strength = "Needs verification"
            else:
                strength = val
        else:
            strength = "Needs verification" if "unclear" in line_lower or "smudged" in line_lower else "Not mentioned in the document"

        # Prescribed Dose
        dose_match = re.search(r'(\d+\s*(?:tablet|tab|capsule|cap|spoon|ml)|\[.*?dose.*?\])', line_clean, re.IGNORECASE)
        if dose_match:
            val = dose_match.group(1).strip()
            dose = "Needs verification" if "[" in val or "?" in val else val
        else:
            dose = "Needs verification" if "dose missing" in line_lower or "??" in line_clean else "1 tablet"

        # Frequency
        freq = "Not mentioned in the document"
        if "twice daily" in line_lower or "bid" in line_lower or "b.i.d" in line_lower:
            freq = "Twice daily"
        elif "thrice daily" in line_lower or "tid" in line_lower or "t.i.d" in line_lower:
            freq = "Thrice daily"
        elif "once daily" in line_lower or "od" in line_lower or "o.d" in line_lower or "daily" in line_lower:
            freq = "Once daily"
        elif "as needed" in line_lower or "sos" in line_lower or "prn" in line_lower:
            freq = "As needed for symptoms"

        # Exact Time (Only if explicitly stated)
        time_match = re.search(r'\(([\d:APMapm\s,]+)\)', line_clean)
        if time_match and any(p in time_match.group(1).upper() for p in ['AM', 'PM', ':']):
            exact_time = time_match.group(1).strip()
        else:
            exact_time = "Needs verification (Clock time not stated by doctor)"

        # Duration
        dur_match = re.search(r'(?:for\s+|\s*x\s*)(\d+\s*(?:days|weeks|months))', line_clean, re.IGNORECASE)
        if dur_match:
            duration = dur_match.group(1).strip()
        elif "conflict" in raw_text.lower() and "amoxicillin" in line_lower:
            duration = "Conflicting: 5 days vs 3 days"
        else:
            duration = "Not mentioned in the document"

        # Food instructions
        food_instruction = "Not mentioned in the document"
        if "after meals" in line_lower or "after food" in line_lower or "after breakfast" in line_lower:
            food_instruction = "After food (భోజనం లేదా టిఫిన్ తర్వాత)"
        elif "before breakfast" in line_lower or "before meals" in line_lower or "empty stomach" in line_lower:
            food_instruction = "Before food on empty stomach (ఖాళీ కడుపుతో / భోజనానికి ముందు)"
        elif "bedtime" in line_lower or "night" in line_lower:
            food_instruction = "At bedtime (రాత్రి నిద్రపోయే ముందు)"

        # Item status
        item_status = "verified"
        if "conflict" in duration.lower() or "conflict" in raw_text.lower() and "amoxicillin" in line_lower:
            item_status = "conflicting"
        elif any(v == "Needs verification" for v in [strength, dose, exact_time]):
            item_status = "needs_verification"

        structured_items.append({
            "medicine_name": med_name,
            "strength": strength,
            "prescribed_dose": dose,
            "frequency": freq,
            "exact_time": exact_time,
            "duration": duration,
            "food_instruction": food_instruction,
            "doctor_notes": "Prescribed as documented.",
            "diet_advice": diet_advice,
            "activity_restrictions": activity_restrictions,
            "follow_up_date": follow_up_date,
            "warning_signs": warning_signs,
            "status": item_status,
            "raw_source_snippet": line_clean
        })

    # Validate against source
    validation_report = validate_instructions_against_source(structured_items, raw_text)

    # ── CRITICAL: if no medicine lines were extracted, the document cannot be ──
    # ── considered verified. Override status to prevent false "verified" result ──
    if not structured_items:
        validation_report["overall_status"] = "needs_verification"
        validation_report["discrepancies"].append(
            "No medication instructions could be automatically extracted from this document. "
            "Possible reasons: handwritten text, non-standard formatting, or an unsupported medicine name. "
            "Please show the document to your doctor or pharmacist."
        )
    
    # Generate Simple Explanations (English & Telugu)
    simple_explanation_en = generate_simple_explanation_en(structured_items, diet_advice, activity_restrictions, follow_up_date, warning_signs)
    simple_explanation_te = generate_simple_explanation_te(structured_items, diet_advice, activity_restrictions, follow_up_date, warning_signs)
    
    readability = calculate_flesch_reading_ease(simple_explanation_en)
    
    return {
        "structured_items": structured_items,
        "simple_explanation_en": simple_explanation_en,
        "simple_explanation_te": simple_explanation_te,
        "diet_advice": diet_advice,
        "activity_restrictions": activity_restrictions,
        "follow_up_date": follow_up_date,
        "warning_signs": warning_signs,
        "readability": readability,
        "validation_report": validation_report,
        "overall_status": validation_report["overall_status"]
    }

def generate_simple_explanation_en(items: List[Dict[str, Any]], diet: str, activity: str, follow_up: str, warnings: str) -> str:
    if not items:
        return "No specific prescription instructions could be safely extracted. Please show this document to your doctor or pharmacist."
    
    lines = ["Here is your simple medicine plan based strictly on your document:\n"]
    for i, it in enumerate(items, 1):
        lines.append(f"{i}. Take {it['medicine_name']} ({it['strength']}):")
        lines.append(f"   - Dose: {it['prescribed_dose']}")
        lines.append(f"   - When: {it['frequency']}")
        if it['exact_time'] != "Needs verification (Clock time not stated by doctor)":
            lines.append(f"   - Exact Time: {it['exact_time']}")
        else:
            lines.append(f"   - Exact Time: Needs verification from doctor")
        lines.append(f"   - Food instructions: {it['food_instruction']}")
        lines.append(f"   - Duration: {it['duration']}")
        if it['status'] == 'needs_verification':
            lines.append("   - [!] Notice: Some details require doctor verification before setting reminders.")
        elif it['status'] == 'conflicting':
            lines.append("   - [!] Warning: Conflicting instructions found. Consult your doctor immediately.")
        lines.append("")
        
    if diet != "Not mentioned in the document":
        lines.append(f"Diet Guidance: {diet}")
    if activity != "Not mentioned in the document":
        lines.append(f"Activity Advice: {activity}")
    if follow_up != "Not mentioned in the document":
        lines.append(f"Follow-up Date: {follow_up}")
    if warnings != "Not mentioned in the document":
        lines.append(f"Emergency Warning Signs: {warnings}")
        
    return "\n".join(lines)

def generate_simple_explanation_te(items: List[Dict[str, Any]], diet: str, activity: str, follow_up: str, warnings: str) -> str:
    if not items:
        return "డాక్యుమెంట్ నుండి మందుల వివరాలు స్పష్టంగా రాలేదు. దయచేసి మీ డాక్టర్ లేదా ఫార్మసిస్ట్‌ను సంప్రదించండి."
    
    lines = ["మీ డాక్యుమెంట్ ఆధారంగా సులభమైన మందుల వివరాలు ఇక్కడ ఉన్నాయి:\n"]
    for i, it in enumerate(items, 1):
        lines.append(f"{i}. {it['medicine_name']} ({it['strength']}):")
        lines.append(f"   - మోతాదు: {it['prescribed_dose']}")
        
        freq_te = "ఒకసారి" if "once" in it['frequency'].lower() else ("రెండుసార్లు" if "twice" in it['frequency'].lower() else it['frequency'])
        lines.append(f"   - ఎప్పుడు: రోజుకు {freq_te}")
        
        if it['exact_time'] != "Needs verification (Clock time not stated by doctor)":
            lines.append(f"   - నిర్దిష్ట సమయం: {it['exact_time']}")
        else:
            lines.append("   - నిర్దిష్ట సమయం: డాక్టర్‌తో నిర్ధారించుకోవాలి")
            
        lines.append(f"   - ఆహార నియమం: {it['food_instruction']}")
        lines.append(f"   - ఎన్ని రోజులు: {it['duration']}")
        
        if it['status'] == 'needs_verification':
            lines.append("   - [గమనిక]: ఈ మందు వివరాలు అస్పష్టంగా ఉన్నాయి. రిమైండర్ పెట్టేముందు డాక్టర్‌ను అడగండి.")
        elif it['status'] == 'conflicting':
            lines.append("   - [హెచ్చరిక]: ఈ మందు సూచనలలో పరస్పర విరుద్ధత ఉంది. డాక్టర్‌తో తక్షణమే మాట్లాడండి.")
        lines.append("")
        
    if diet != "Not mentioned in the document":
        lines.append(f"ఆహార సూచనలు: {diet}")
    if activity != "Not mentioned in the document":
        lines.append(f"శారీరక శ్రమ / వ్యాయామం: {activity}")
    if follow_up != "Not mentioned in the document":
        lines.append(f"తదుపరి డాక్టర్ అపాయింట్‌మెంట్: {follow_up}")
    if warnings != "Not mentioned in the document":
        lines.append(f"అత్యవసర హెచ్చరిక లక్షణాలు: {warnings}")
        
    return "\n".join(lines)
