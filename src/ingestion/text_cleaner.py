"""
Text cleaning utilities for PDF extraction.
Fixes common issues like excessive newlines.
"""

import re


def clean_extracted_text(text: str) -> str:
    """
    Clean extracted text by fixing common PDF extraction issues.
    
    Args:
        text: Raw extracted text
        
    Returns:
        Cleaned text
    """
    if not text:
        return text
    
    # Remove gibberish lines from scanned pages (high punctuation/noise ratio)
    def is_gibberish_line(line):
        if not line or len(line) < 10:
            return False
        special_chars = sum(1 for c in line if c in '-;><,.:!?/\\|()[]{}')
        letter_chars = sum(1 for c in line if c.isalpha())
        if letter_chars == 0:
            return True
        noise_ratio = special_chars / len(line)
        return noise_ratio > 0.4  # More than 40% special characters
    
    lines = text.split('\n')
    lines = [line for line in lines if not is_gibberish_line(line)]
    text = '\n'.join(lines)
    
    # Fix 1: Replace newlines between words with spaces
    # This handles: "word\nword\nword" -> "word word word"
    text = re.sub(r'(\w)\n(\w)', r'\1 \2', text)
    
    # Fix 2: Remove newlines after single characters (like "Dr\n.")
    text = re.sub(r'(\w)\n(\W)', r'\1\2', text)
    
    # Fix 3: Handle hyphenated words at line breaks
    # This handles: "Sekundär-\nschulen" -> "Sekundarschulen"
    text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)
    
    # Fix 3.5: Remove soft hyphens (¬) - common in old PDFs
    # This handles: "vor¬\nzüglich" -> "vorzüglich"
    text = text.replace('¬\n', '').replace('¬ ', '').replace('¬', '')
    
    # Fix 4: Remove newlines after punctuation (commas, periods) if followed by lowercase
    # This handles: "sentence,\nnext word" -> "sentence, next word"
    text = re.sub(r'([,;])\n([a-zäöüß])', r'\1 \2', text)
    
    # Fix 5: Remove newlines after quotes
    text = re.sub(r'([""])\n', r'\1 ', text)
    
    # Fix 6: Join lines that don't end with sentence-ending punctuation
    # This is aggressive: removes newlines unless preceded by . ! ? or :
    text = re.sub(r'([^.!?:\n])\n([a-zäöüßA-ZÄÖÜ])', r'\1 \2', text)
    
    # Fix 7: Replace multiple newlines with double newline (paragraph break)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Fix 8: Remove newlines after common abbreviations
    text = re.sub(r'(Dr|Prof|Co|A\.G|L\.)\.\n', r'\1. ', text)
    
    # Fix 9: Remove newlines before punctuation
    text = re.sub(r'\n([,;.!?])', r'\1', text)
    
    # Fix 10: Clean up multiple spaces
    text = re.sub(r' {2,}', ' ', text)
    
    # Fix 11: Remove leading/trailing whitespace per line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    # Fix 12: Remove empty lines
    lines = [line for line in text.split('\n') if line.strip()]
    text = '\n'.join(lines)
    
    # Fix 13: Add paragraph breaks after sentence-ending punctuation followed by capital
    text = re.sub(r'([.!?])\s+([A-ZÄÖÜ])', r'\1\n\n\2', text)
    
    # Fix 14: Remove remaining single newlines (keep only paragraph breaks)
    # This is very aggressive - only keeps \n\n for paragraphs
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
    
    # Fix 15: Clean up to exactly one or two newlines
    text = re.sub(r'\n{2,}', '\n\n', text)
    
    # Fix 16: Remove leading/trailing whitespace
    text = text.strip()
    
    return text


def clean_german_text(text: str) -> str:
    """
    Additional cleaning specific to German text.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    text = clean_extracted_text(text)
    
    # Fix German-specific issues
    # Fix quotes
    text = text.replace('„', '"').replace('"', '"')
    
    # Fix umlauts if they got corrupted (uncommon but possible)
    # Add more replacements if you notice specific issues
    
    return text


if __name__ == "__main__":
    # Test the cleaner
    test_text = """Vorwort\nVorliegendes\nBuch\nbaut\nauf\ndie\n„\nSchweizer\nGeschichte\n"\nvon\nDr\n.\nLudwig\nSuter"""
    
    print("BEFORE:")
    print(test_text[:200])
    print("\n" + "="*60 + "\n")
    
    cleaned = clean_german_text(test_text)
    print("AFTER:")
    print(cleaned[:200])
