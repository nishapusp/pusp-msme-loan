import os
from pymongo import MongoClient, ASCENDING
import urllib.parse
import streamlit as st
from datetime import datetime
from gridfs import GridFS
from bson import ObjectId

class Database:
    def __init__(self):
        try:
            # Get connection parameters
            MONGO_USER = "puspendersharma"
            MONGO_PASSWORD = "unionbank"
            MONGO_CLUSTER = "msme-loan-app.a0gwq.mongodb.net"
            MONGO_DB_NAME = "msme_loan_db"

            # URL encode the credentials
            encoded_username = urllib.parse.quote_plus(MONGO_USER)
            encoded_password = urllib.parse.quote_plus(MONGO_PASSWORD)

            # Build the basic connection string
            basic_uri = (
                f"mongodb+srv://{encoded_username}:{encoded_password}@{MONGO_CLUSTER}/"
            )

            # Create MongoClient with specific options
            self.client = MongoClient(
                basic_uri,
                server_api='1',
                ssl=True,
                tlsAllowInvalidCertificates=True,  # Only for testing
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=20000,
                maxPoolSize=50,
                wtimeout=2500,
                retryWrites=True,
                socketTimeoutMS=20000
            )

            # Access the database
            self.db = self.client[MONGO_DB_NAME]
            
            # Initialize GridFS
            self.fs = GridFS(self.db)

            # Verify connection
            db_list = self.client.list_database_names()
            if MONGO_DB_NAME in db_list:
                print(f"Successfully connected to {MONGO_DB_NAME}")
            else:
                print(f"Database {MONGO_DB_NAME} does not exist")

            # Test write permission
            test_collection = self.db.test_collection
            test_doc = {"test": "connection"}
            test_collection.insert_one(test_doc)
            test_collection.delete_one({"test": "connection"})
            print("Database connection and permissions verified successfully!")

        except Exception as e:
            error_msg = f"Database connection error: {str(e)}"
            print(f"Detailed error: {error_msg}")
            st.error("Failed to connect to database. Please contact support.")
            raise e
            
    def save_application(self, application_data):
        """Save loan application data"""
        try:
            if '_id' in application_data:
                # If updating existing application
                application_id = application_data.pop('_id')
                result = self.db.applications.update_one(
                    {'_id': application_id},
                    {'$set': application_data}
                )
                return result
            else:
                # If new application
                result = self.db.applications.insert_one(application_data)
                return result
        except Exception as e:
            st.error(f"Error saving application: {str(e)}")
            return None

    def update_application(self, application_id, updated_data):
        """Update existing application"""
        try:
            if isinstance(application_id, str):
                application_id = ObjectId(application_id)
            result = self.db.applications.update_one(
                {'_id': application_id},
                {'$set': updated_data}
            )
            return result
        except Exception as e:
            st.error(f"Error updating application: {str(e)}")
            return None

    def get_application(self, criteria):
        """Retrieve specific application"""
        try:
            if isinstance(criteria, ObjectId) or isinstance(criteria, str):
                criteria = {'_id': ObjectId(str(criteria))}
            return self.db.applications.find_one(criteria)
        except Exception as e:
            st.error(f"Error retrieving application: {str(e)}")
            return None

    def get_all_applications(self):
        """Retrieve all applications"""
        try:
            return list(self.db.applications.find())
        except Exception as e:
            st.error(f"Error retrieving applications: {str(e)}")
            return []

    def save_document(self, file_data, metadata):
        """Save uploaded document to GridFS"""
        try:
            if not metadata.get('application_number'):
                metadata['application_number'] = st.session_state.get('application_number')
                
            file_id = self.fs.put(
                file_data,
                filename=metadata['filename'],
                metadata={
                    'application_number': metadata['application_number'],
                    'document_type': metadata['document_type'],
                    'section': metadata.get('section', 'Other'),
                    'upload_date': datetime.now(),
                    'content_type': metadata['content_type']
                }
            )
            return file_id
        except Exception as e:
            st.error(f"Error saving document: {str(e)}")
            return None

    def get_document(self, file_id):
        """Retrieve document from GridFS"""
        try:
            if isinstance(file_id, str):
                file_id = ObjectId(file_id)
            return self.fs.get(file_id)
        except Exception as e:
            st.error(f"Error retrieving document: {str(e)}")
            return None

    def get_application_documents(self, application_number):
        """Get all documents for an application"""
        try:
            documents = []
            for grid_out in self.fs.find({"metadata.application_number": application_number}):
                doc_data = {
                    'file_id': grid_out._id,
                    'filename': grid_out.filename,
                    'document_type': grid_out.metadata.get('document_type'),
                    'section': grid_out.metadata.get('section'),
                    'upload_date': grid_out.metadata.get('upload_date'),
                    'content_type': grid_out.metadata.get('content_type'),
                    'data': grid_out.read()
                }
                documents.append(doc_data)
            return documents
        except Exception as e:
            st.error(f"Error retrieving documents: {str(e)}")
            return []

    def get_documents(self, application_id):
        """Get all documents for an application using ID"""
        try:
            if isinstance(application_id, str):
                application_id = ObjectId(application_id)
            application = self.get_application({'_id': application_id})
            if application and 'application_number' in application:
                return self.get_application_documents(application['application_number'])
            return []
        except Exception as e:
            st.error(f"Error retrieving documents: {str(e)}")
            return []

    def search_applications(self, criteria):
        """Search applications based on various criteria"""
        try:
            return list(self.db.applications.find(criteria))
        except Exception as e:
            st.error(f"Error searching applications: {str(e)}")
            return []

    def delete_application(self, application_id):
        """Delete an application and its documents"""
        try:
            if isinstance(application_id, str):
                application_id = ObjectId(application_id)
            # Get application number first
            application = self.get_application({'_id': application_id})
            if application and 'application_number' in application:
                # Delete all associated documents
                for doc in self.get_application_documents(application['application_number']):
                    self.fs.delete(doc['file_id'])
                # Delete the application
                result = self.db.applications.delete_one({'_id': application_id})
                return result
            return None
        except Exception as e:
            st.error(f"Error deleting application: {str(e)}")
            return None
