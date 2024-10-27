import os
from pymongo import MongoClient
import urllib.parse
import streamlit as st
from datetime import datetime
from gridfs import GridFS
from bson import ObjectId

class Database:
    def __init__(self):
        try:
            # Direct connection string - simpler approach
            username = "puspmsme2"
            password = "unionbank"
            
            # Create the connection string
            connection_string = f"mongodb+srv://{username}:{password}@msme-loan-app.a0gwq.mongodb.net/msme_loan_db?authSource=admin"
            
            # Initialize client with minimal settings
            self.client = MongoClient(connection_string)
            
            # Test connection
            self.client.admin.command('ping')
            
            # Initialize database and GridFS
            self.db = self.client['msme_loan_db']
            self.fs = GridFS(self.db)
            print("MongoDB connection successful!")
            
        except Exception as e:
            error_msg = f"Database connection error: {str(e)}"
            print(error_msg)
            st.error(error_msg)
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
