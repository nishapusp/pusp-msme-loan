# sections.py

import streamlit as st
import pandas as pd

def basic_information_section(auto_fill_field, create_input_field, colorful_document_upload, extract_data_from_document):
    st.subheader("Basic Information")

    col1, col2 = st.columns(2)
    with col1:
        udyam_file = colorful_document_upload("Udyam Certificate", "udyam", "#3498db")
        if udyam_file:
            with st.spinner("Extracting data from Udyam Certificate..."):
                extracted_data = extract_data_from_document(udyam_file, "Udyam Certificate")
                if "error" not in extracted_data:
                    for key, value in extracted_data.items():
                        auto_fill_field(key, value, "Udyam Certificate")
                    st.success("Udyam Certificate data extracted and filled successfully")
                else:
                    st.error(f"Error extracting data: {extracted_data['error']}")
    
    with col2:
        gst_file = colorful_document_upload("GST Certificate", "gst", "#2ecc71")
        if gst_file:
            with st.spinner("Extracting data from GST Certificate..."):
                extracted_data = extract_data_from_document(gst_file, "GST Certificate")
                if "error" not in extracted_data:
                    for key, value in extracted_data.items():
                        auto_fill_field(key, value, "GST Certificate")
                    st.success("GST Certificate data extracted and filled successfully")
                else:
                    st.error(f"Error extracting data: {extracted_data['error']}")

    col1, col2 = st.columns(2)
    with col1:
        create_input_field("Name of the Enterprise", "enterprise_name")
        create_input_field("UDYAM Registration No.", "udyam_number")
        create_input_field("Classification", "classification")
        create_input_field("Date of Classification", "date_of_classification")
        create_input_field("Social Category", "social_category")
        create_input_field("Address", "address")
        create_input_field("State", "state")
    
    with col2:
        create_input_field("Major Activity", "major_activity")
        create_input_field("NIC 5 Digit Code", "nic_5_digit")
        create_input_field("Mobile No.", "mobile")
        create_input_field("Email Address", "email")
        create_input_field("Date of Incorporation", "date_of_incorporation")
        create_input_field("Date of Commencement", "date_of_commencement")
        create_input_field("GST Registration No.", "gst_number")

    # Option to add another GST number
    if st.button("Add Another GST Number"):
        if 'additional_gst_numbers' not in st.session_state:
            st.session_state.additional_gst_numbers = 1
        else:
            st.session_state.additional_gst_numbers += 1
    
    for i in range(st.session_state.get('additional_gst_numbers', 0)):
        create_input_field(f"Additional GST Registration No. {i+1}", f"additional_gst_number_{i}")

    create_input_field("PAN Card No.", "pan")
    create_input_field("Constitution", "constitution")

    premises_type = st.selectbox("Details of Premises", ["Owned", "Rented", "Leased"])
    if premises_type in ["Rented", "Leased"]:
        create_input_field("Tenant/Lessor Details", "premises_details")
    
    create_input_field("Telephone No. (Office)", "telephone_office")
    
    gem_registered = st.radio("Registered on GeM", ["Yes", "No"])
    if gem_registered == "Yes":
        create_input_field("GeM Registration No.", "gem_registration")
    
    create_input_field("Importer-Exporter Code (IEC), if applicable", "iec_code")
    create_input_field("City/District where loan is required", "loan_city")
    create_input_field("Branch where loan is required, if any", "loan_branch")

    # Hidden fields in an expander
    with st.expander("Additional Details"):
        create_input_field("NIC 2 Digit Code", "nic_2_digit")
        create_input_field("NIC 4 Digit Code", "nic_4_digit")
        create_input_field("Date of Liability", "date_of_liability")
        create_input_field("Period of Validity From", "period_of_validity_from")
        create_input_field("Period of Validity To", "period_of_validity_to")
        create_input_field("Registered Office Address", "regd_office_address")
        create_input_field("Factory/Shop/Admin Office Address", "factory_address")
        create_input_field("Trade Name", "trade_name")
        create_input_field("Type of Registration", "type_of_registration")
        create_input_field("Date of Issue", "date_of_issue")

       
def proprietor_partners_directors_section(auto_fill_field, create_input_field, colorful_document_upload, extract_data_from_document):
    st.subheader("Proprietor / Partners / Directors Information")
    
    constitution = st.session_state.get('constitution', '')
    gst_data = st.session_state.get('gst_data', {})
    
    if constitution == 'Proprietorship':
        st.write("Proprietor Information")
        num_directors = 1
        # Auto-fill proprietor information from GST data
        if gst_data and 'directors' in gst_data and gst_data['directors']:
            for key, value in gst_data['directors'][0].items():
                auto_fill_field(f"director_{key}_0", value, "GST Certificate")
    else:
        st.write("Partners/Directors Information")
        num_directors = max(1, len(gst_data.get('directors', [])))

    for i in range(num_directors):
        with st.expander(f"{'Proprietor' if constitution == 'Proprietorship' else 'Partner/Director'} {i+1}"):
            col1, col2 = st.columns(2)
            
            with col1:
                create_input_field("Name", f"director_name_{i}")
                create_input_field("Designation", f"director_designation_{i}")
                create_input_field("Date of Birth", f"director_dob_{i}")
                create_input_field("Father/Spouse", f"director_father_spouse_{i}")
                create_input_field("Academic Qualifications", f"director_qualifications_{i}")
            
            with col2:
                create_input_field("PAN No.", f"director_pan_{i}")
                create_input_field("Aadhaar No.", f"director_aadhaar_{i}")
                create_input_field("DIN No. (if applicable)", f"director_din_{i}")
                create_input_field("Net Worth (Rs. in lacs)", f"director_networth_{i}")
                create_input_field("Mobile No.", f"director_mobile_{i}")

            create_input_field("Residential Address", f"director_address_{i}")
            create_input_field("State", f"director_state_{i}")
            create_input_field("Category (SC/ST/OBC/Minority/Women)", f"director_category_{i}")
            create_input_field("Experience in the line of activity (Years)", f"director_experience_{i}")

            col1, col2 = st.columns(2)
            with col1:
                pan_file = colorful_document_upload(f"Upload PAN Card", f"pan_upload_{i}", "#9b59b6")
                if pan_file:
                    pan_data = extract_data_from_document(pan_file, "PAN Card")
                    if "error" not in pan_data:
                        for key, value in pan_data.items():
                            auto_fill_field(f"director_{key}_{i}", value, "PAN Card")
                        st.success(f"PAN Card data extracted and filled successfully")
                    else:
                        st.error(pan_data["error"])
            
            with col2:
                aadhaar_file = colorful_document_upload(f"Upload Aadhaar Card", f"aadhaar_upload_{i}", "#34495e")
                if aadhaar_file:
                    aadhaar_data = extract_data_from_document(aadhaar_file, "Aadhaar Card")
                    if "error" not in aadhaar_data:
                        for key, value in aadhaar_data.items():
                            auto_fill_field(f"director_{key}_{i}", value, "Aadhaar Card")
                        st.success(f"Aadhaar Card data extracted and filled successfully")
                    else:
                        st.error(aadhaar_data["error"])

    if st.button("Add Another Partner/Director", key="add_director") and constitution != 'Proprietorship':
        num_directors += 1
        st.experimental_rerun()

    #if st.button("Save Progress", key="save_proprietor_partners_directors"):
        #save_progress("proprietor_partners_directors", {f"director_{key}_{i}": st.session_state.get(f"director_{key}_{i}", "") for i in #range(num_directors) for key in ["name", "designation", "dob", "pan", "aadhaar", "address", "state", "mobile", "networth"]})
        #st.success("Progress saved successfully!")

    # Add proprietor/partners/directors to guarantors
    if 'guarantors' not in st.session_state:
        st.session_state.guarantors = []
    
    st.session_state.guarantors = [
        {
            'name': st.session_state.get(f'director_name_{i}', ''),
            'pan': st.session_state.get(f'director_pan_{i}', ''),
            'aadhaar': st.session_state.get(f'director_aadhaar_{i}', ''),
            'address': st.session_state.get(f'director_address_{i}', ''),
            'mobile': st.session_state.get(f'director_mobile_{i}', '')
        } for i in range(num_directors)
    ]

    st.write("Note: The information provided here will be automatically added to the Guarantors section.")

    # Validation
    if constitution not in ['Individual', 'Proprietorship'] and num_directors < 2:
        st.error("For partnerships or companies, at least two partners/directors are required.")

    # Display current guarantors (for debugging, can be removed in production)
    if st.checkbox("Show current guarantors"):
        st.write(st.session_state.guarantors)

def credit_facilities_section(auto_fill_field, create_input_field, colorful_document_upload, extract_data_from_document):
    st.header("Credit Facilities")

    facility_types = ["Cash Credit", "Overdraft", "Term Loan", "LC/BG", "Other"]

    is_takeover = st.radio("Is this a takeover?", ["No", "Yes"])
    
    if is_takeover == "Yes":
        col1, col2 = st.columns(2)
        with col1:
            sanction_letter = colorful_document_upload("Upload Sanction Letter", "sanction_letter", "#3498db")
        with col2:
            account_statement = colorful_document_upload("Upload Account Statement (Last 1 Year)", "account_statement", "#2ecc71")

        if sanction_letter:
            with st.spinner("Extracting data from Sanction Letter..."):
                sanction_data = extract_data_from_document(sanction_letter, "Sanction Letter")
                if "error" not in sanction_data:
                    for key, value in sanction_data.items():
                        auto_fill_field(key, value, "Sanction Letter")
                    st.success("Sanction Letter data extracted and filled successfully")
                else:
                    st.error(sanction_data["error"])

        st.subheader("Existing Credit Facilities to be Taken Over")
    else:
        has_existing_facilities = st.radio("Do you have existing credit facilities?", ["No", "Yes"])
        if has_existing_facilities == "Yes":
            st.subheader("Existing Credit Facilities")

    if is_takeover == "Yes" or (is_takeover == "No" and has_existing_facilities == "Yes"):
        num_facilities = st.number_input("Number of existing facilities", min_value=1, value=1)
        for i in range(num_facilities):
            st.write(f"Facility {i+1}")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                facility_type = st.selectbox(f"Facility Type {i+1}", facility_types, key=f"existing_facility_type_{i}")
            with col2:
                create_input_field("Limit (in lacs)", f"existing_facility_limit_{i}")
            with col3:
                create_input_field("Outstanding", f"existing_facility_outstanding_{i}")
            with col4:
                create_input_field("Bank", f"existing_facility_bank_{i}")
            create_input_field("Security", f"existing_facility_security_{i}")
            st.write("---")

    # Proposed Credit Facilities
    st.subheader("Proposed Credit Facilities")
    num_proposed_facilities = st.number_input("Number of proposed facilities", min_value=1, value=1)
    for i in range(num_proposed_facilities):
        st.write(f"Proposed Facility {i+1}")
        col1, col2, col3 = st.columns(3)
        with col1:
            facility_type = st.selectbox(f"Facility Type {i+1}", facility_types, key=f"proposed_facility_type_{i}")
        with col2:
            create_input_field(f"Amount (in lacs)", f"proposed_facility_amount_{i}")
        with col3:
            create_input_field(f"Purpose", f"proposed_facility_purpose_{i}")
        create_input_field(f"Security", f"proposed_facility_security_{i}")
        st.write("---")

    #if st.button("Save Progress", key="credit_facilities_save_progress"):
        #save_progress("credit_facilities", {
            #"is_takeover": is_takeover,
            # Add all other fields here
        #})
        st.success("Progress saved successfully!")
         
def collateral_and_guarantor_section(auto_fill_field, create_input_field, colorful_document_upload, extract_data_from_document):
    st.subheader("Collateral Security and Guarantors")

    col1, col2 = st.columns(2)

    with col1:
        st.write("### Collateral Security")
        is_collateral_offered = st.radio("Is collateral security offered?", ["Yes", "No"])

        if is_collateral_offered == "Yes":
            num_collaterals = st.number_input("Number of Collateral Securities", min_value=1, value=1)
            for i in range(num_collaterals):
                with st.expander(f"Collateral Security {i+1}"):
                    create_input_field("Name of owner", f"collateral_owner_{i}")
                    collateral_type = st.selectbox("Nature of Collateral", ["Property", "Machinery", "Vehicles", "Stocks", "Other"], key=f"collateral_type_{i}")
                    create_input_field("Details", f"collateral_details_{i}")
                    create_input_field("Value (Rs. in lacs)", f"collateral_value_{i}")

    with col2:
        st.write("### Guarantors")
        # Automatically add partners/directors as guarantors
        guarantors = [st.session_state.get(f"director_name_{i}", "") for i in range(10) if st.session_state.get(f"director_name_{i}")]
        
        # Add collateral owners as guarantors
        if is_collateral_offered == "Yes":
            for i in range(num_collaterals):
                collateral_owner = st.session_state.get(f"collateral_owner_{i}", "")
                if collateral_owner and collateral_owner not in guarantors:
                    guarantors.append(collateral_owner)

        st.write("Existing Guarantors:")
        for i, guarantor in enumerate(guarantors):
            st.write(f"{i+1}. {guarantor}")

        additional_guarantors = st.number_input("Number of additional guarantors", min_value=0, value=0)
        for i in range(additional_guarantors):
            with st.expander(f"Additional Guarantor {i+1}"):
                create_input_field("Name", f"additional_guarantor_name_{i}")
                create_input_field("PAN No.", f"additional_guarantor_pan_{i}")
                create_input_field("Aadhaar No.", f"additional_guarantor_aadhaar_{i}")
                create_input_field("Net Worth (Rs. in lacs)", f"additional_guarantor_networth_{i}")

        if not guarantors and additional_guarantors == 0:
            is_cgtmse_proposed = st.radio("Is CGTMSE guarantee proposed?", ["Yes", "No"])

    #if st.button("Save Progress", key="save_collateral_and_guarantor"):
        #save_progress("collateral_and_guarantor", {
            #"is_collateral_offered": is_collateral_offered,
            #"guarantors": guarantors,
            #"additional_guarantors": additional_guarantors,
            # Add other relevant fields here
        #})
        st.success("Progress saved successfully!")

def past_performance_and_business_relations_section(auto_fill_field, create_input_field, colorful_document_upload, extract_data_from_document):
    st.subheader("Past Performance and Business Relations")

    col1, col2 = st.columns(2)

    with col1:
        st.write("### Past Performance")
        years = ["Past Year-II", "Past Year-I", "Present Year", "Next Year"]
        parameters = ["Net Sales", "Net Profit", "Capital"]

        df = pd.DataFrame(index=parameters, columns=years)
        for param in parameters:
            for year in years:
                df.at[param, year] = st.text_input(f"{param} - {year}", key=f"{param}_{year}")

        st.table(df)

    with col2:
        st.write("### Suppliers and Customers")
        
        st.write("Top Suppliers")
        num_suppliers = st.number_input("Number of Suppliers", min_value=3, value=3)
        suppliers_df = pd.DataFrame(columns=["Name", "Contact", "Associated Since", "Business %"])
        for i in range(num_suppliers):
            suppliers_df.loc[i] = [
                st.text_input(f"Supplier {i+1} Name", key=f"supplier_name_{i}"),
                st.text_input(f"Supplier {i+1} Contact", key=f"supplier_contact_{i}"),
                st.text_input(f"Supplier {i+1} Associated Since", key=f"supplier_association_{i}"),
                st.text_input(f"Supplier {i+1} Business %", key=f"supplier_business_{i}")
            ]
        st.table(suppliers_df)

        st.write("Top Customers")
        num_customers = st.number_input("Number of Customers", min_value=3, value=3)
        customers_df = pd.DataFrame(columns=["Name", "Contact", "Associated Since", "Business %"])
        for i in range(num_customers):
            customers_df.loc[i] = [
                st.text_input(f"Customer {i+1} Name", key=f"customer_name_{i}"),
                st.text_input(f"Customer {i+1} Contact", key=f"customer_contact_{i}"),
                st.text_input(f"Customer {i+1} Associated Since", key=f"customer_association_{i}"),
                st.text_input(f"Customer {i+1} Business %", key=f"customer_business_{i}")
            ]
        st.table(customers_df)

    #if st.button("Save Progress", key="past_performance_and_business_relations_save_progress"):
        #save_progress("past_performance_and_business_relations", {
            #"performance_data": df.to_dict(),
            #"suppliers_data": suppliers_df.to_dict(),
           # "customers_data": customers_df.to_dict()
        #})
        #st.success("Progress saved successfully!")

def associate_concerns_and_statutory_obligations_section(auto_fill_field, create_input_field, colorful_document_upload, extract_data_from_document):
    st.subheader("Associate Concerns and Statutory Obligations")

    col1, col2 = st.columns(2)

    with col1:
        st.write("### Associate Concerns")
        num_concerns = st.number_input("Number of Associate Concerns", min_value=0, value=1)
        concerns_df = pd.DataFrame(columns=["Name", "Address", "Banking With", "Nature of Association", "Extent of Interest"])
        for i in range(num_concerns):
            concerns_df.loc[i] = [
                st.text_input(f"Concern {i+1} Name", key=f"concern_name_{i}"),
                st.text_input(f"Concern {i+1} Address", key=f"concern_address_{i}"),
                st.text_input(f"Concern {i+1} Banking With", key=f"concern_bank_{i}"),
                st.text_input(f"Concern {i+1} Nature of Association", key=f"concern_association_{i}"),
                st.text_input(f"Concern {i+1} Extent of Interest", key=f"concern_interest_{i}")
            ]
        st.table(concerns_df)

    with col2:
        st.write("### Statutory Obligations")
        obligations = [
            "Registration under Shops and Establishment Act",
            "Registration under MSME (Provisional/Final)",
            "Drug License",
            "Latest Sales Tax Return Filed",
            "Latest Income Tax Returns Filed",
            "Any other Statutory Dues remaining outstanding"
        ]
        for obligation in obligations:
            create_input_field(obligation, f"statutory_{obligation.lower().replace(' ', '_')}")

    #if st.button("Save Progress", key="associate_concerns_and_statutory_obligations_save_progress"):
        #save_progress("associate_concerns_and_statutory_obligations", {
            #"concerns_data": concerns_df.to_dict(),
            #"statutory_obligations": {f"statutory_{obligation.lower().replace(' ', '_')}": st.session_state.get(f"statutory_{obligation.lower().replace(' #', '_')}", "") for obligation in obligations}
       #})
        #st.success("Progress saved successfully!")

def undertakings_and_document_upload_section(auto_fill_field, create_input_field, colorful_document_upload, extract_data_from_document):
    st.subheader("Undertakings and Document Upload")

    col1, col2 = st.columns(2)

    with col1:
        st.write("### Undertakings")
        undertakings = [
            "I/We hereby certify that all information furnished by me/us is true, correct and complete.",
            "I/We have no borrowing arrangements for the unit except as indicated in the application.",
            "There is no overdue/statutory dues against me/us/promoters except as indicated in the application.",
            "No legal action has been/is being taken against me/us/promoters by any Bank/FIs.",
            "I/We shall furnish all other information that may be required in connection with my/our application.",
            "This information may be exchanged by you with any agency you may deem fit.",
            "You, your representatives or Reserve Bank of India or any other agency as authorized by you, may, at any time, inspect/verify my/our assets, books of accounts etc. in our factory/business premises as given above.",
            "You may take appropriate safeguards/action for recovery of bank's dues."
        ]
        for undertaking in undertakings:
            st.checkbox(undertaking, key=f"undertaking_{undertakings.index(undertaking)}")

    with col2:
        st.write("### Document Upload")
        documents = [
            "Proof of Identity",
            "Proof of Residence",
            "Proof of Business Address",
            "MSME Registration",
            "Last three years Balance Sheets",
            "GST Returns",
            "Income Tax Returns"
        ]
        for doc in documents:
            colorful_document_upload(doc, f"upload_{doc.lower().replace(' ', '_')}", "#3498db")

    #if st.button("Save Progress", key="undertakings_and_document_upload_save_progress"):
        #save_progress("undertakings_and_document_upload", {
            #"undertakings": {f"undertaking_{undertakings.index(u)}": st.session_state.get(f"undertaking_{undertakings.index(u)}", False) for u in #undertakings},
            #"uploaded_documents": [doc for doc in documents if st.session_state.get(f"upload_{doc.lower().replace(' ', '_')}")]
        #})
        #st.success("Progress saved successfully!")

def document_upload_section(auto_fill_field, create_input_field, colorful_document_upload, extract_data_from_document):
    st.subheader("Document Upload")
    st.write("Please upload the following documents:")
    st.file_uploader("Proof of Identity", type=["pdf", "jpg", "jpeg", "png"])
    st.file_uploader("Proof of Residence", type=["pdf", "jpg", "jpeg", "png"])
    st.file_uploader("Proof of Business Address", type=["pdf", "jpg", "jpeg", "png"])
    st.file_uploader("MSME Registration", type=["pdf", "jpg", "jpeg", "png"])
    st.file_uploader("Last three years Balance Sheets", type=["pdf", "xlsx", "xls"])
    st.file_uploader("GST Returns", type=["pdf", "xlsx", "xls"])
    st.file_uploader("Income Tax Returns", type=["pdf", "xlsx", "xls"])

def review_section(auto_fill_field, create_input_field, colorful_document_upload, extract_data_from_document):
    st.subheader("Review Your Application")
    st.write("Please review all the information you've provided before submitting your application.")

    sections = [
        ("Basic Information", ["enterprise_name", "regd_office_address", "factory_address", "date_of_establishment", "state", "premises_type", "telephone_office", "mobile", "email", "pan", "constitution", "udyam_number", "gst_number", "gst_registration_date", "gem_registration", "iec_code", "loan_city", "loan_branch"]),
        ("Business Details", ["activity", "existing_since"]),
        ("Proprietor/Partners/Directors", [f"director_name_{i}" for i in range(5)]),
        ("Associate Concerns", ["associate_concern_name", "associate_concern_address"]),
        ("Existing Credit Facilities", ["existing_credit_type", "existing_credit_limit", "existing_credit_outstanding"]),
        ("Proposed Credit Facilities", ["proposed_credit_type", "proposed_credit_amount", "proposed_credit_purpose"]),
        ("Collateral Security", [f"collateral_owner_{i}" for i in range(3)]),
        ("Guarantors", [f"guarantor_name_{i}" for i in range(3)]),
        ("Past Performance", ["past_year_sales", "past_year_profit"]),
        ("Suppliers and Customers", [f"supplier_name_{i}" for i in range(5)] + [f"customer_name_{i}" for i in range(5)]),
        ("Statutory Obligations", ["statutory_registration_shop_act", "statutory_registration_msme", "statutory_gst_return", "statutory_income_tax_return"]),
    ]

    for section_name, fields in sections:
        st.write(f"### {section_name}")
        for field in fields:
            value = st.session_state.get(field, "")
            st.write(f"**{field.replace('_', ' ').title()}:** {value}")
        st.write("---")

    st.write("### Undertakings")
    st.write("You have agreed to the following undertakings:")
    for undertaking in st.session_state.get("undertakings", []):
        st.write(f"- {undertaking}")

    st.write("### Uploaded Documents")
    for doc in st.session_state.get("uploaded_documents", []):
        st.write(f"- {doc}")

    st.write("Please ensure all information is correct before submitting your application.")
    if st.button("Edit Application"):
        st.session_state.page = 0  # Return to the first page for editing
        st.experimental_rerun()