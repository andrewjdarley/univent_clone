from datetime import datetime, timedelta
from icalendar import Calendar
import requests
import json, re

def custom_unescape(text):
    # Define a dictionary of common HTML entities and their corresponding characters
    html_entities = {
        '&nbsp;': ' ',
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&#39;': "'",
        '&apos;': "'",
        '&ndash;': '–',
        '&mdash;': '—',
        '&lsquo;': ''',
        '&rsquo;': ''',
        '&ldquo;': '"',
        '&rdquo;': '"',
    }
    
    # Function to replace HTML entities
    def replace_entity(match):
        entity = match.group(0)
        if entity in html_entities:
            return html_entities[entity]
        # Handle numeric entities
        if entity.startswith('&#'):
            try:
                if entity.startswith('&#x'):
                    return chr(int(entity[3:-1], 16))
                return chr(int(entity[2:-1]))
            except ValueError:
                pass
        return entity

    # Replace known HTML entities and numeric entities
    text = re.sub(r'&[a-zA-Z]+;|&#?\w+;', replace_entity, text)
    
    # Replace escape sequences
    escape_sequences = {
        r'\\n': '\n',
        r'\\r': '\r',
        r'\\t': '\t',
        r'\\"': '"',
        r"\\'": "'",
        r'\\\\': '\\'
    }
    for escaped, unescaped in escape_sequences.items():
        text = text.replace(escaped, unescaped)
    
    return text

def clean(text):
    # First, unescape the text
    unescaped_text = custom_unescape(text)
    
    # Then, remove all whitespace
    return ''.join(unescaped_text.split())

def turnInFilter(component):
    trigger = component.get('SUMMARY') == 'Quiz 1'
    # print(component)
    d = clean(component.get('DESCRIPTION'))
    s = clean(component.get('SUMMARY'))
    if len(s) <= 6 and len(d) > 6:

        return True
    
    if not s.isalnum():
        s = s[:-6]
    if d.startswith(s):
        # print(d, s)
        return False

    return True

def parse_course_name(string):
    match = re.search(r'\[(.*?)\]', string)
    
    if match:
        return match.group(1)
    return None

def parse_ical(ical_string, courseInput = None):
    cal = Calendar.from_ical(ical_string)
    events = []
    for component in cal.walk():
        # print(component)
        isCanvas = 'byu.instructure' in ical_string 
        if component.name == "VEVENT" and (isCanvas or turnInFilter(component)):
            if isCanvas:
                course = parse_course_name(component.get('SUMMARY'))
            else:
                course = courseInput
            event_details = {
                'DTSTART': component.get('DTEND').dt.isoformat() if component.get('DTEND') else (component.get('DTSTART').dt.isoformat() if component.get('DTSTART') else None),
                'SUMMARY': re.sub(r'\[.*?\]', '', str(component.get('SUMMARY')).replace('\n', ' ').strip()),
                'DESCRIPTION': str(component.get('DESCRIPTION')).replace('\n', ' ').strip(),
                'COURSE': course
            }
            events.append(event_details)
    return events

def fetch_ical(url):
    response = requests.get(url)
    return response.text

def getAssignments():
    with open('data.txt', 'r') as f:
        all = []
        for line in f.readlines():
            line = line.strip()
            if ' ' in line:
                ical = line.split()[0]
                course = ' '.join(line.split()[1:])
            else:
                ical = line
                course = None
            
            stringy = fetch_ical(ical)
            parsed = parse_ical(stringy, course)

            all.extend(parsed)
        
        return all
