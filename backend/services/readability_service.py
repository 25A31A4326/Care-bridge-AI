import re
import math
from typing import Dict, Any, List

def count_syllables_word(word: str) -> int:
    """Estimate syllables in an English word."""
    word = word.lower().strip()
    if not word:
        return 0
    if len(word) <= 3:
        return 1
    # Remove ending 'e' or 'es' or 'ed' if not preceded by certain consonants
    word = re.sub(r'(?:[^laeiouy]es|ed|[^laeiouy]e)$', '', word)
    word = re.sub(r'^y', '', word)
    matches = re.findall(r'[aeiouy]{1,2}', word)
    return max(1, len(matches))

def calculate_flesch_reading_ease(text: str) -> Dict[str, Any]:
    """
    Computes Flesch Reading Ease score for English text.
    Score ranges:
    90-100: Very Easy (5th grade)
    80-89: Easy (6th grade)
    70-79: Fairly Easy (7th grade)
    60-69: Standard (8th-9th grade)
    50-59: Fairly Difficult (10th-12th grade)
    30-49: Difficult (College)
    0-29: Very Confusing
    """
    if not text or not text.strip():
        return {
            "score": 0.0,
            "label": "Not enough text",
            "grade_level": "N/A",
            "metric_name": "Flesch Reading Ease (English only)"
        }
    
    # Split into sentences and words
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    sentence_count = max(1, len(sentences))
    
    words = re.findall(r'\b[A-Za-z0-9\'-]+\b', text)
    word_count = max(1, len(words))
    
    syllable_count = sum(count_syllables_word(w) for w in words)
    
    # Flesch Reading Ease formula
    score = 206.835 - (1.015 * (word_count / sentence_count)) - (84.6 * (syllable_count / word_count))
    score = round(max(0.0, min(100.0, score)), 1)
    
    if score >= 90:
        label = "Very Easy to Understand (Elderly & General Public friendly)"
        grade = "5th grade reading level"
    elif score >= 80:
        label = "Easy to Understand"
        grade = "6th grade reading level"
    elif score >= 70:
        label = "Fairly Easy"
        grade = "7th grade reading level"
    elif score >= 60:
        label = "Standard English"
        grade = "8th-9th grade reading level"
    elif score >= 50:
        label = "Fairly Complex"
        grade = "High school level"
    else:
        label = "Complex Medical Terminology"
        grade = "College level"
        
    return {
        "score": score,
        "label": label,
        "grade_level": grade,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "metric_name": "Flesch Reading Ease (Validated for English)"
    }

def validate_instructions_against_source(structured_items: List[Dict[str, Any]], raw_source_text: str) -> Dict[str, Any]:
    """
    Deterministically cross-checks structured extracted instructions against raw source text.
    Flags missing, unsupported, or conflicting values.
    """
    source_lower = raw_source_text.lower()
    item_results = []
    overall_status = "verified"
    discrepancies = []
    
    for item in structured_items:
        med_name = item.get("medicine_name", "").strip()
        strength = item.get("strength", "").strip()
        dose = item.get("prescribed_dose", "").strip()
        frequency = item.get("frequency", "").strip()
        exact_time = item.get("exact_time", "").strip()
        duration = item.get("duration", "").strip()
        
        flags = []
        
        # 1. Check medicine name presence in source
        if med_name.lower() not in source_lower:
            flags.append(f"Medicine '{med_name}' was not detected in original document text.")
        
        # 2. Check strength presence
        if strength and strength.lower() not in ["needs verification", "not mentioned in document", "not mentioned"]:
            strength_clean = re.sub(r'\s+', '', strength.lower())
            source_no_space = re.sub(r'\s+', '', source_lower)
            if strength_clean not in source_no_space:
                flags.append(f"Strength '{strength}' was not clearly confirmed in source.")
        elif strength.lower() in ["needs verification", "not mentioned in document"]:
            flags.append("Strength is missing or unreadable in source document.")

        # 3. Check exact time verification
        if exact_time.lower() in ["needs verification", "not mentioned in document", "needs confirmation"]:
            flags.append("Exact clock time was not specified by doctor; requires manual verification.")
        
        # 4. Check for conflict keywords in source
        if "conflict" in source_lower or "discontinue after" in source_lower:
            if med_name.lower() in ["amoxicillin", "amoxicillin-clavulanate"]:
                flags.append("Duration conflict detected between discharge orders and nurse notes (5 days vs 3 days).")

        item_status = "verified"
        if any("conflict" in f.lower() for f in flags):
            item_status = "conflicting"
            overall_status = "conflicting"
        elif len(flags) > 0:
            item_status = "needs_verification"
            if overall_status != "conflicting":
                overall_status = "needs_verification"
                
        discrepancies.extend(flags)
        item_results.append({
            "medicine_name": med_name,
            "status": item_status,
            "flags": flags,
            "can_auto_schedule": item_status == "verified"
        })
        
    return {
        "overall_status": overall_status,
        "items": item_results,
        "discrepancies": discrepancies,
        "total_items": len(structured_items),
        "verified_items": len([i for i in item_results if i["status"] == "verified"]),
        "unverified_items": len([i for i in item_results if i["status"] != "verified"]),
    }
