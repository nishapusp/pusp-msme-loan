import re
from datetime import datetime
import pytesseract
from PIL import Image
import io
import fitz  # PyMuPDF
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
GST_STATE_CODES = {
    '01': 'Jammu and Kashmir', '02': 'Himachal Pradesh', '03': 'Punjab', '04': 'Chandigarh',
    '05': 'Uttarakhand', '06': 'Haryana', '07': 'Delhi', '08': 'Rajasthan',
    '09': 'Uttar Pradesh', '10': 'Bihar', '11': 'Sikkim', '12': 'Arunachal Pradesh',
    '13': 'Nagaland', '14': 'Manipur', '15': 'Mizoram', '16': 'Tripura',
    '17': 'Meghalaya', '18': 'Assam', '19': 'West Bengal', '20': 'Jharkhand',
    '21': 'Odisha', '22': 'Chhattisgarh', '23': 'Madhya Pradesh', '24': 'Gujarat',
    '26': 'Dadra and Nagar Haveli and Daman and Diu', '27': 'Maharashtra',
    '28': 'Andhra Pradesh (Before Division)', '29': 'Karnataka', '30': 'Goa',
    '31': 'Lakshadweep', '32': 'Kerala', '33': 'Tamil Nadu', '34': 'Puducherry',
    '35': 'Andaman and Nicobar Isands', '36': 'Telangana', '37': 'Andhra Pradesh', '38': 'Ladakh'

}

# Utility functions
def extract_text_from_image(file):
    image = Image.open(file)
    return pytesseract.image_to_string(image)

def extract_text_from_pdf(file):
    pdf = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in pdf:
        text += page.get_text()
    return text

def clean_text(text):
    return ' '.join(text.split())

def fuzzy_search(text, search_term, threshold=80):
    lines = text.split('\n')
    best_match = max(lines, key=lambda line: fuzz.partial_ratio(line.lower(), search_term.lower()))
    if fuzz.partial_ratio(best_match.lower(), search_term.lower()) > threshold:
        return best_match
    return None

# Validation functions
def validate_pan(pan):
    return re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', pan) is not None

def validate_aadhaar(aadhaar):
    return re.match(r'^\d{12}$', aadhaar) is not None

def validate_gst(gst):
    return re.match(r'^\d{2}[A-Z]{5}\d{4}[A-Z]{1}\d[Z]{1}[A-Z\d]{1}$', gst) is not None

def validate_date(date_string):
    try:
        datetime.strptime(date_string, "%d/%m/%Y")
        return True
    except ValueError:
        return False

# Extraction functions
# Extraction functions
def extract_udyam_data(text):
    data = {}
    
    # Extract Udyam Registration Number
    udyam_match = re.search(r'UDYAM REGISTRATION NUMBER\s*(UDYAM-[A-Z]{2}-\d{2}-\d{7})', text)
    if udyam_match:
        data['udyam_number'] = udyam_match.group(1)

    # Extract Name of Enterprise
    name_match = re.search(r'NAME OF ENTERPRISE\s*(.*)', text)
    if name_match:
        data['enterprise_name'] = name_match.group(1).strip()

    # Extract Type of Enterprise and Classification Date
    type_match = re.search(r'TYPE OF ENTERPRISE.*?\n.*?(\w+)\s+(\d{2}/\d{2}/\d{4})', text, re.DOTALL)
    if type_match:
        data['classification'] = type_match.group(1)
        data['date_of_classification'] = type_match.group(2)

    # Extract Major Activity
    activity_match = re.search(r'MAJOR ACTIVITY\s*(.*)', text)
    if activity_match:
        data['major_activity'] = activity_match.group(1).strip()

    # Extract Social Category
    social_category_match = re.search(r'SOCIAL CATEGORY OF\s*ENTREPRENEUR\s*(.*)', text)
    if social_category_match:
        data['social_category'] = social_category_match.group(1).strip()

    # Extract Address
    address_match = re.search(r'OFFICAL ADDRESS OF ENTERPRISE(.*?)(?=Mobile|DATE OF)', text, re.DOTALL | re.IGNORECASE)
    if address_match:
        address_lines = address_match.group(1).strip().split('\n')
        data['address'] = ', '.join(line.strip() for line in address_lines if line.strip())

    # Extract Mobile and Email
    mobile_match = re.search(r'Mobile\s*(\d+)', text)
    email_match = re.search(r'Email:\s*(\S+@\S+)', text)
    if mobile_match:
        data['mobile'] = mobile_match.group(1)
    if email_match:
        data['email'] = email_match.group(1)

    # Extract Date of Incorporation
    incorporation_match = re.search(r'DATE OF INCORPORATION /\s*REGISTRATION OF ENTERPRISE\s*(\d{2}/\d{2}/\d{4})', text)
    if incorporation_match:
        data['date_of_incorporation'] = incorporation_match.group(1)

    # Extract Date of Commencement
    commencement_match = re.search(r'DATE OF COMMENCEMENT OF\s*PRODUCTION/BUSINESS\s*(\d{2}/\d{2}/\d{4})', text)
    if commencement_match:
        data['date_of_commencement'] = commencement_match.group(1)

    # Extract NIC Code
    nic_match = re.search(r'NATIONAL INDUSTRY\s*CLASSIFICATION CODE.*?(\d+)\s*-\s*(.*?)\s*(\d+)\s*-\s*(.*?)\s*(\d+)\s*-\s*(.*?)\s*(Trading|Activity)', text, re.DOTALL)
    if nic_match:
        data['nic_2_digit'] = f"{nic_match.group(1)} - {nic_match.group(2).strip()}"
        data['nic_4_digit'] = f"{nic_match.group(3)} - {nic_match.group(4).strip()}"
        data['nic_5_digit'] = f"{nic_match.group(5)} - {nic_match.group(6).strip()}"

    logger.info(f"Extracted Udyam data: {data}")
    return data

def extract_gst_data(text):
    data = {}
    
    # Extract GST Registration Number
    gst_match = re.search(r'Registration Number\s*:\s*(\d{2}[A-Z]{5}\d{4}[A-Z]{1}\d[Z]{1}[A-Z\d]{1})', text)
    if gst_match:
        data['gst_number'] = gst_match.group(1)
        data['pan'] = data['gst_number'][2:12]
 
    # Extract Legal Name
    legal_name_match = re.search(r'Legal Name of Business\s*:?\s*(.*)', text)
    if legal_name_match:
        data['legal_name'] = legal_name_match.group(1).strip()

    # Extract Trade Name
    trade_name_match = re.search(r'Trade Name, if any\s*:?\s*(.*)', text)
    if trade_name_match:
        data['trade_name'] = trade_name_match.group(1).strip()

    # Extract Constitution of Business
    constitution_match = re.search(r'Constitution of Business\s*:?\s*(.*)', text)
    if constitution_match:
        data['constitution'] = constitution_match.group(1).strip()

    # Extract Address
    address_match = re.search(r'Address of Principal Place of Business\s*:?\s*(.*?)(?=\n\n|\Z)', text, re.DOTALL)
    if address_match:
        data['address'] = address_match.group(1).strip().replace('\n', ', ')

    # Extract Date of Liability
    liability_match = re.search(r'Date of Liability\s*:?\s*(\d{2}/\d{2}/\d{4})', text)
    if liability_match:
        data['date_of_liability'] = liability_match.group(1)

    # Extract Period of Validity
    validity_match = re.search(r'Period of Validity\s*:?.*?From\s*(\d{2}/\d{2}/\d{4})\s*To\s*(\d{2}/\d{2}/\d{4}|NA)', text)
    if validity_match:
        data['period_of_validity_from'] = validity_match.group(1)
        data['period_of_validity_to'] = validity_match.group(2)

    # Extract Type of Registration
    registration_type_match = re.search(r'Type of Registration\s*:?\s*(.*)', text)
    if registration_type_match:
        data['type_of_registration'] = registration_type_match.group(1).strip()

    # Extract Date of Issue
    issue_date_match = re.search(r'Date of issue of Certificate\s*:?\s*(\d{2}/\d{2}/\d{4})', text)
    if issue_date_match:
        data['date_of_issue'] = issue_date_match.group(1)

    # Extract state from GST number
    if 'gst_number' in data:
        state_code = data['gst_number'][:2]
        data['state'] = GST_STATE_CODES.get(state_code, 'Unknown')

    # Extract proprietor/partner/director details
    data['directors'] = []
    director_pattern = r'(\d+)\s*Name\s*(.*?)\s*Designation/Status\s*(.*?)\s*Resident of State\s*(.*?)(?=\d+\s*Name|\Z)'
    director_matches = re.finditer(director_pattern, text, re.DOTALL)
    
    for i, match in enumerate(director_matches):
        director = {
            f'director_name_{i}': match.group(2).strip(),
            f'director_designation_{i}': match.group(3).strip(),
            f'director_state_{i}': match.group(4).strip()
        }
        data['directors'].append(director)

    return data

def extract_pan_data(text):
    cleaned_text = clean_text(text)
    data = {}
    fields = {
        'name': ['Name', 'Applicant Name'],
        'dob': ['Date of Birth', 'DOB'],
        'pan': ['Permanent Account Number', 'PAN']
    }
    for key, search_terms in fields.items():
        for term in search_terms:
            line = fuzzy_search(cleaned_text, term)
            if line:
                value = line.split(':', 1)[-1].strip() if ':' in line else line
                data[key] = value
                break
    
    if 'pan' in data and not validate_pan(data['pan']):
        data['pan'] = "Invalid PAN"
        logger.warning("Invalid PAN detected")
    
    return data

def extract_aadhaar_data(text):
    cleaned_text = clean_text(text)
    data = {}
    fields = {
        'aadhaar': ['Aadhaar Number', 'UID'],
        'name': ['Name', 'Applicant Name'],
        'address': ['Address', 'Residential Address'],
        'dob': ['DOB', 'Date of Birth']
    }
    for key, search_terms in fields.items():
        for term in search_terms:
            line = fuzzy_search(cleaned_text, term)
            if line:
                value = line.split(':', 1)[-1].strip() if ':' in line else line
                data[key] = value
                break
    
    if 'aadhaar' in data:
        data['aadhaar'] = data['aadhaar'].replace(" ", "")
        if not validate_aadhaar(data['aadhaar']):
            data['aadhaar'] = "Invalid Aadhaar number"
            logger.warning("Invalid Aadhaar number detected")
    
    return data

def extract_bank_data(text):
    cleaned_text = clean_text(text)
    data = {}
    fields = {
        'bank_name': ['Bank Name', 'Name of Bank'],
        'account_number': ['Account Number', 'A/C No'],
        'ifsc_code': ['IFSC Code', 'IFSC'],
        'branch_name': ['Branch Name', 'Branch'],
        'account_type': ['Account Type', 'Type of Account']
    }

    for key, search_terms in fields.items():
        for term in search_terms:
            line = fuzzy_search(cleaned_text, term)
            if line:
                value = line.split(':', 1)[-1].strip() if ':' in line else line
                data[key] = value
                break
        if key not in data:
            logger.warning(f"Could not extract {key} from Bank Statement")

    # Extract credit facilities
    credit_facilities = re.findall(r'(Cash Credit|Term Loan|LC/BG)\s*:\s*Rs\.\s*([\d,.]+)', cleaned_text, re.IGNORECASE)
    if credit_facilities:
        data['credit_facilities'] = credit_facilities
    else:
        logger.warning("Could not extract credit facilities from Bank Statement")

    # Extract security details
    security = fuzzy_search(cleaned_text, 'Security')
    if security:
        data['security'] = security.split(':', 1)[-1].strip() if ':' in security else security
    else:
        logger.warning("Could not extract security details from Bank Statement")

    return data

# Unified mapping function
def map_extracted_data_to_form_fields(data, document_type):
    mapped_data = {}
    
    # Common mappings
    common_fields = ['name', 'dob', 'address', 'pan', 'aadhaar', 'mobile', 'email']
    for field in common_fields:
        if field in data:
            mapped_data[field] = data[field]
    
    if document_type == "Udyam Certificate":
        specific_mappings = {
            'enterprise_name': 'enterprise_name',
            'udyam_number': 'udyam_number',
            'classification': 'classification',
            'date_of_classification': 'date_of_classification',
            'major_activity': 'major_activity',
            'social_category': 'social_category',
            'nic_2_digit': 'nic_2_digit',
            'nic_4_digit': 'nic_4_digit',
            'nic_5_digit': 'nic_5_digit',
            'date_of_incorporation': 'date_of_incorporation',
            'date_of_commencement': 'date_of_commencement'
        }
    elif document_type == "GST Certificate":
        specific_mappings = {
            'legal_name': 'enterprise_name',
            'trade_name': 'trade_name',
            'constitution': 'constitution',
            'gst_number': 'gst_number',
            'date_of_liability': 'date_of_liability',
            'period_of_validity_from': 'period_of_validity_from',
            'period_of_validity_to': 'period_of_validity_to',
            'type_of_registration': 'type_of_registration',
            'date_of_issue': 'date_of_issue',
            'state': 'state'
        }
        for key, value in specific_mappings.items():
            if key in data:
                mapped_data[value] = data[key]
        
        # Map director details
        for director in data.get('directors', []):
            mapped_data.update(director)

        # Map partner/director details
        for i, partner in enumerate(data.get('partners', [])):
            mapped_data[f"director_name_{i}"] = partner['name']
            mapped_data[f"director_designation_{i}"] = partner['designation']
            mapped_data[f"director_state_{i}"] = partner['state']
    elif document_type == "PAN Card":
        specific_mappings = {
            'name': 'director_name_0',
            'pan': 'director_pan_0',
            'dob': 'director_dob_0'
        }
    elif document_type == "Aadhaar Card":
        specific_mappings = {
            'name': 'director_name_0',
            'aadhaar': 'director_aadhaar_0',
            'address': 'director_address_0',
            'dob': 'director_dob_0'
        }
    elif document_type == "Bank Statement":
        specific_mappings = {
            'bank_name': 'existing_bank',
            'account_number': 'account_number',
            'ifsc_code': 'ifsc_code',
            'credit_facilities': 'credit_facilities',
            'security': 'existing_security'
        }
    
    for source_key, target_key in specific_mappings.items():
        if source_key in data:
            mapped_data[target_key] = data[source_key]
    
    return mapped_data

def extract_data_from_document(file, document_type):
    try:
        if file.type.startswith('image'):
            text = extract_text_from_image(file)
        elif file.type == 'application/pdf':
            text = extract_text_from_pdf(file)
        else:
            return {"error": "Unsupported file format"}
    except Exception as e:
        logger.error(f"Error reading file: {str(e)}")
        return {"error": "Unable to read file"}

    extraction_functions = {
        "Udyam Certificate": extract_udyam_data,
        "GST Certificate": extract_gst_data,
        "PAN Card": extract_pan_data,
        "Aadhaar Card": extract_aadhaar_data,
        "Bank Statement": extract_bank_data
    }

    if document_type in extraction_functions:
        try:
            extracted_data = extraction_functions[document_type](text)
            logger.info(f"Successfully extracted data from {document_type}")
            
            mapped_data = map_extracted_data_to_form_fields(extracted_data, document_type)
            logger.info(f"Mapped data: {mapped_data}")
            
            return mapped_data
        except Exception as e:
            logger.error(f"Error extracting data from {document_type}: {str(e)}")
            return {"error": f"Error processing {document_type}"}
    else:
        logger.warning(f"Unsupported document type: {document_type}")
        return {"error": "Unsupported document type"}

# Usage example:
# extracted_data = extract_data_from_document(file, "Udyam Certificate")
# if "error" not in extracted_data:
#     for key, value in extracted_data.items():
#         auto_fill_field(key, value, "Udyam Certificate")
#     st.success("Udyam Certificate data extracted and filled successfully")
# else:
#     st.error(extracted_data["error"])