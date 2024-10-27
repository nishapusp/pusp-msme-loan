import streamlit as st
from database import Database
import uuid
from datetime import datetime
from utils import colorful_document_upload
from document_extraction import extract_data_from_document
from sections import (
    basic_information_section,
    proprietor_partners_directors_section,
    credit_facilities_section,
    collateral_and_guarantor_section,
    past_performance_and_business_relations_section,
    associate_concerns_and_statutory_obligations_section,
    undertakings_and_document_upload_section,
    review_section
)

# Initialize database
db = Database()

# Page config
st.set_page_config(
    layout="wide", 
    page_title="UBI MSME Loan Application",
    initial_sidebar_state="expanded"
)

def generate_application_number():
    """Generate unique application number"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M')
    unique_id = str(uuid.uuid4().hex)[:6]
    return f"MSME{timestamp}{unique_id}"

def initialize_session_state():
    """Initialize session state variables"""
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = 0
    if 'application_number' not in st.session_state:
        st.session_state.application_number = generate_application_number()
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}
    if 'documents' not in st.session_state:
        st.session_state.documents = {}
    if 'status' not in st.session_state:
        st.session_state.status = "Draft"

def auto_fill_field(key, value, source):
    """Auto-fill form fields and track the source"""
    if value and (key not in st.session_state or not st.session_state[key]):
        st.session_state[key] = value
        st.session_state[f"{key}_source"] = source
        st.session_state.form_data[key] = value

def create_input_field(label, key, value="", help=""):
    """Create input field and track changes"""
    input_value = st.text_input(
        label, 
        value=st.session_state.get(key, value), 
        key=key, 
        help=help
    )
    if input_value:
        st.session_state.form_data[key] = input_value
    return input_value

def save_application_data():
    """Save all application data to database"""
    try:
        application_data = {
            'application_number': st.session_state.application_number,
            'submission_date': datetime.now().isoformat(),
            'status': st.session_state.status,
            'basic_info': {
                'enterprise_name': st.session_state.get('enterprise_name'),
                'udyam_number': st.session_state.get('udyam_number'),
                'classification': st.session_state.get('classification'),
                'date_of_classification': st.session_state.get('date_of_classification'),
                'social_category': st.session_state.get('social_category'),
                'address': st.session_state.get('address'),
                'state': st.session_state.get('state'),
                'major_activity': st.session_state.get('major_activity'),
                'nic_5_digit': st.session_state.get('nic_5_digit'),
                'mobile': st.session_state.get('mobile'),
                'email': st.session_state.get('email'),
                'date_of_incorporation': st.session_state.get('date_of_incorporation'),
                'date_of_commencement': st.session_state.get('date_of_commencement'),
                'gst_number': st.session_state.get('gst_number'),
                'pan': st.session_state.get('pan')
            },
            'directors': [
                {
                    'name': st.session_state.get(f'director_name_{i}'),
                    'designation': st.session_state.get(f'director_designation_{i}'),
                    'dob': st.session_state.get(f'director_dob_{i}'),
                    'pan': st.session_state.get(f'director_pan_{i}'),
                    'aadhaar': st.session_state.get(f'director_aadhaar_{i}'),
                    'address': st.session_state.get(f'director_address_{i}'),
                    'mobile': st.session_state.get(f'director_mobile_{i}')
                }
                for i in range(st.session_state.get('num_directors', 1))
            ],
            'form_data': st.session_state.get('form_data', {})
        }
        
        if st.session_state.get('application_id'):
            result = db.update_application(st.session_state.application_id, application_data)
        else:
            result = db.save_application(application_data)
            st.session_state.application_id = result.inserted_id
        
        return True
    except Exception as e:
        st.error(f"Error saving application: {str(e)}")
        return False

def main():
    initialize_session_state()

    # User/Admin Switch in sidebar
    user_type = st.sidebar.radio("Select User Type", ["Applicant", "Bank Official"])
    
    if user_type == "Bank Official":
        main_official_view()
    else:
        main_applicant_view()

def main_applicant_view():
    st.title("MSME Loan Application")
    
    # Application number and status display in sidebar
    st.sidebar.success(f"Application Number: {st.session_state.application_number}")
    st.sidebar.info(f"Status: {st.session_state.status}")

    # Define sections
    sections = [
        ("Basic Information", basic_information_section),
        ("Proprietor/Partners/Directors", proprietor_partners_directors_section),
        ("Credit Facilities", credit_facilities_section),
        ("Collateral and Guarantors", collateral_and_guarantor_section),
        ("Past Performance and Business Relations", past_performance_and_business_relations_section),
        ("Associate Concerns and Statutory Obligations", associate_concerns_and_statutory_obligations_section),
        ("Undertakings and Document Upload", undertakings_and_document_upload_section),
        ("Review Application", review_section)
    ]

    # Create tabs with keys
    tab_keys = [f"tab_{i}" for i in range(len(sections))]
    tabs = st.tabs([section[0] for section in sections])

    # Handle tab selection
    for i, tab in enumerate(tabs):
        with tab:
            if i == st.session_state.current_tab:
                sections[i][1](
                    auto_fill_field=auto_fill_field,
                    create_input_field=create_input_field,
                    colorful_document_upload=colorful_document_upload,
                    extract_data_from_document=extract_data_from_document
                )

    # Navigation and Progress
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("← Previous", key="prev_button", disabled=st.session_state.current_tab == 0):
            save_application_data()
            st.session_state.current_tab = max(0, st.session_state.current_tab - 1)
            st.rerun()
            
    with col2:
        # Progress indicator
        progress = (st.session_state.current_tab + 1) / len(sections)
        st.progress(progress)
        st.write(f"Section {st.session_state.current_tab + 1} of {len(sections)}")

    with col3:
        if st.session_state.current_tab < len(sections) - 1:
            if st.button("Next →", key="next_button"):
                save_application_data()
                st.session_state.current_tab = min(len(sections) - 1, st.session_state.current_tab + 1)
                st.rerun()
        else:
            if st.button("Submit Application", type="primary", key="submit_button"):
                if save_application_data():
                    st.session_state.status = "Submitted"
                    st.balloons()
                    st.success(f"""
                    ### Application Submitted Successfully! 🎉
                    Your Application Number: **{st.session_state.application_number}**
                    
                    Please save this number for future reference.""")
                    st.info("A confirmation email will be sent to your registered email address.")

def main_official_view():
    st.title("Bank Official Dashboard")
    
    # Search functionality
    search_col1, search_col2 = st.columns(2)
    with search_col1:
        search_application = st.text_input("Enter Application Number")
    with search_col2:
        if st.button("Search"):
            if search_application:
                application_data = db.get_application({"application_number": search_application})
                if application_data:
                    display_application_details(application_data)
                else:
                    st.error("Application not found")
    
    # Show all applications
    if st.checkbox("Show All Applications"):
        display_all_applications()

def display_application_details(application_data):
    try:
        if not application_data:
            st.error("No application data available")
            return

        st.subheader("Application Details")
        
        # Basic Information
        st.write("### Basic Information")
        basic_info = application_data.get('basic_info', {})
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Enterprise Details**")
            st.write(f"Enterprise Name: {basic_info.get('enterprise_name', 'N/A')}")
            st.write(f"Status: {application_data.get('status', 'N/A')}")
            st.write(f"Application Number: {application_data.get('application_number', 'N/A')}")
            st.write(f"GST Number: {basic_info.get('gst_number', 'N/A')}")
            st.write(f"PAN: {basic_info.get('pan', 'N/A')}")
        
        with col2:
            st.write("**Contact Details**")
            st.write(f"Mobile: {basic_info.get('mobile', 'N/A')}")
            st.write(f"Email: {basic_info.get('email', 'N/A')}")
            st.write(f"Address: {basic_info.get('address', 'N/A')}")
            st.write(f"State: {basic_info.get('state', 'N/A')}")

        # Documents Section
        st.write("### Uploaded Documents")
        documents = db.get_application_documents(application_data.get('application_number'))
        
        if documents:
            for doc in documents:
                with st.expander(f"📄 {doc.get('document_type', 'Document')}"):
                    st.write(f"Filename: {doc.get('filename', 'N/A')}")
                    st.write(f"Upload Date: {doc.get('upload_date', 'N/A')}")
                    if 'data' in doc:
                        st.download_button(
                            label="Download Document",
                            data=doc['data'],
                            file_name=doc.get('filename', 'document.pdf'),
                            mime=doc.get('content_type', 'application/pdf')
                        )
        else:
            st.info("No documents uploaded yet")

        # Status Update
        st.write("### Update Status")
        new_status = st.selectbox(
            "Select New Status",
            ["Under Review", "Additional Documents Required", "Approved", "Rejected"]
        )
        remarks = st.text_area("Add Remarks", height=100)
        
        if st.button("Update Status"):
            update_data = {
                "status": new_status,
                "last_updated": datetime.now().isoformat(),
                "remarks": remarks
            }
            if db.update_application(application_data['_id'], update_data):
                st.success("Status updated successfully!")
                st.rerun()
            else:
                st.error("Failed to update status")

    except Exception as e:
        st.error(f"Error displaying application details: {str(e)}")
        if st.checkbox("Show debug information"):
            st.write(e)
            st.json(application_data)

def display_all_applications():
    applications = db.get_all_applications()
    
    if applications:
        # Create a DataFrame for better visualization
        import pandas as pd
        df = pd.DataFrame([{
            'Application Number': app.get('application_number'),
            'Enterprise Name': app.get('basic_info', {}).get('enterprise_name'),
            'Status': app.get('status'),
            'Submission Date': app.get('submission_date')
        } for app in applications])
        
        st.dataframe(df)
    else:
        st.info("No applications found")

if __name__ == "__main__":
    main()