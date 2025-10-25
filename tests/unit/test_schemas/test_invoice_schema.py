"""
Unit tests for Invoice schemas.

Tests cover:
- InvoiceRegistrationSchema: User/order validation, due date defaults, status validation
- InvoiceUpdateSchema: Partial update validation
- InvoiceStatusUpdateSchema: Status-only updates
- InvoiceResponseSchema: Serialization with status name conversion and overdue calculation
"""

import pytest
from datetime import datetime, timedelta
from marshmallow import ValidationError
from app.sales.schemas.invoice_schema import (
    InvoiceRegistrationSchema,
    InvoiceUpdateSchema,
    InvoiceStatusUpdateSchema,
    InvoiceResponseSchema
)


@pytest.mark.unit
@pytest.mark.sales
class TestInvoiceRegistrationSchema:
    """Test InvoiceRegistrationSchema validation."""
    
    def test_invoice_registration_with_valid_data(self, mocker):
        """Test invoice creation with all fields."""
        mocker.patch(
            'app.sales.schemas.invoice_schema.ReferenceData.is_valid_invoice_status',
            return_value=True
        )
        
        schema = InvoiceRegistrationSchema()
        due_date = datetime.now() + timedelta(days=30)
        data = {
            'user_id': 1,
            'order_id': 1,
            'due_date': due_date,
            'status': 'pending'
        }
        
        result = schema.load(data)
        
        assert result['user_id'] == 1
        assert result['order_id'] == 1
        assert result['due_date'] == due_date
        assert result['status'] == 'pending'
    
    def test_invoice_registration_with_default_due_date(self, mocker):
        """Test invoice creation auto-generates due_date if not provided."""
        mocker.patch(
            'app.sales.schemas.invoice_schema.ReferenceData.is_valid_invoice_status',
            return_value=True
        )
        
        schema = InvoiceRegistrationSchema()
        data = {
            'user_id': 1,
            'order_id': 1,
            'status': 'pending'
        }
        
        before_load = datetime.now()
        result = schema.load(data)
        after_load = datetime.now()
        
        # Should have auto-generated due_date 30 days from now
        assert 'due_date' in result
        expected_min = before_load + timedelta(days=30)
        expected_max = after_load + timedelta(days=30)
        assert expected_min <= result['due_date'] <= expected_max
    
    def test_invoice_registration_with_invalid_status(self, mocker):
        """Test invoice creation with invalid status."""
        mocker.patch(
            'app.sales.schemas.invoice_schema.ReferenceData.is_valid_invoice_status',
            return_value=False
        )
        
        schema = InvoiceRegistrationSchema()
        data = {
            'user_id': 1,
            'order_id': 1,
            'status': 'invalid_status'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'status' in exc_info.value.messages
        assert 'invalid_status' in str(exc_info.value.messages['status'])
    
    def test_invoice_registration_missing_user_id(self):
        """Test invoice creation without user_id."""
        schema = InvoiceRegistrationSchema()
        data = {
            'order_id': 1
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'user_id' in exc_info.value.messages
    
    def test_invoice_registration_missing_order_id(self):
        """Test invoice creation without order_id."""
        schema = InvoiceRegistrationSchema()
        data = {
            'user_id': 1
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'order_id' in exc_info.value.messages
    
    def test_invoice_registration_with_invalid_user_id(self):
        """Test invoice creation with invalid user_id."""
        schema = InvoiceRegistrationSchema()
        data = {
            'user_id': 0,  # Must be >= 1
            'order_id': 1
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'user_id' in exc_info.value.messages
    
    def test_invoice_registration_without_status(self):
        """Test invoice creation without status (should be handled by service layer)."""
        schema = InvoiceRegistrationSchema()
        data = {
            'user_id': 1,
            'order_id': 1
        }
        
        # Should succeed - status is optional
        result = schema.load(data)
        assert result['user_id'] == 1
        assert result['order_id'] == 1
        # Status defaults handled by service layer


@pytest.mark.unit
@pytest.mark.sales
class TestInvoiceUpdateSchema:
    """Test InvoiceUpdateSchema validation."""
    
    def test_invoice_update_with_due_date(self):
        """Test invoice update with new due date."""
        schema = InvoiceUpdateSchema()
        new_due_date = datetime.now() + timedelta(days=45)
        data = {
            'due_date': new_due_date
        }
        
        result = schema.load(data)
        
        assert result['due_date'] == new_due_date
    
    def test_invoice_update_with_status(self, mocker):
        """Test invoice update with new status."""
        mocker.patch(
            'app.sales.schemas.invoice_schema.ReferenceData.is_valid_invoice_status',
            return_value=True
        )
        
        schema = InvoiceUpdateSchema()
        data = {
            'status': 'paid'
        }
        
        result = schema.load(data)
        
        assert result['status'] == 'paid'
    
    def test_invoice_update_with_invalid_status(self, mocker):
        """Test invoice update with invalid status."""
        mocker.patch(
            'app.sales.schemas.invoice_schema.ReferenceData.is_valid_invoice_status',
            return_value=False
        )
        
        schema = InvoiceUpdateSchema()
        data = {
            'status': 'bogus_status'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'status' in exc_info.value.messages
    
    def test_invoice_update_with_empty_data(self):
        """Test invoice update with no fields (partial update)."""
        schema = InvoiceUpdateSchema()
        data = {}
        
        # Should succeed - all fields are optional for updates
        result = schema.load(data)
        assert result == {}


@pytest.mark.unit
@pytest.mark.sales
class TestInvoiceStatusUpdateSchema:
    """Test InvoiceStatusUpdateSchema validation."""
    
    def test_status_update_with_valid_status(self, mocker):
        """Test status-only update with valid status."""
        mocker.patch(
            'app.sales.schemas.invoice_schema.ReferenceData.is_valid_invoice_status',
            return_value=True
        )
        
        schema = InvoiceStatusUpdateSchema()
        data = {'status': 'paid'}
        
        result = schema.load(data)
        
        assert result['status'] == 'paid'
    
    def test_status_update_with_invalid_status(self, mocker):
        """Test status-only update with invalid status."""
        mocker.patch(
            'app.sales.schemas.invoice_schema.ReferenceData.is_valid_invoice_status',
            return_value=False
        )
        
        schema = InvoiceStatusUpdateSchema()
        data = {'status': 'invalid'}
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'status' in exc_info.value.messages
    
    def test_status_update_missing_status(self):
        """Test status-only update without status field."""
        schema = InvoiceStatusUpdateSchema()
        data = {}
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'status' in exc_info.value.messages


@pytest.mark.unit
@pytest.mark.sales
class TestInvoiceResponseSchema:
    """Test InvoiceResponseSchema serialization."""
    
    def test_invoice_response_serialization(self, mocker):
        """Test invoice response with status name conversion."""
        # Create a mock invoice object
        mock_invoice = mocker.Mock()
        mock_invoice.id = 1
        mock_invoice.user_id = 1
        mock_invoice.order_id = 1
        mock_invoice.total_amount = 199.99
        mock_invoice.due_date = datetime.now() + timedelta(days=30)
        mock_invoice.created_at = datetime.now()
        mock_invoice.invoice_status_id = 1
        mock_invoice.is_overdue = mocker.Mock(return_value=False)
        
        mocker.patch(
            'app.sales.schemas.invoice_schema.ReferenceData.get_invoice_status_name',
            return_value='Pending'
        )
        
        schema = InvoiceResponseSchema()
        result = schema.dump(mock_invoice)
        
        # Verify basic fields
        assert result['id'] == 1
        assert result['user_id'] == 1
        assert result['order_id'] == 1
        assert result['total_amount'] == 199.99
        
        # Verify status converted to name
        assert result['status'] == 'Pending'
        
        # Verify overdue calculation
        assert result['is_overdue'] == False
    
    def test_invoice_response_with_overdue_invoice(self, mocker):
        """Test invoice response shows overdue status."""
        mock_invoice = mocker.Mock()
        mock_invoice.id = 2
        mock_invoice.user_id = 1
        mock_invoice.order_id = 2
        mock_invoice.total_amount = 99.99
        mock_invoice.due_date = datetime.now() - timedelta(days=5)  # Past due
        mock_invoice.created_at = datetime.now() - timedelta(days=35)
        mock_invoice.invoice_status_id = 1
        mock_invoice.is_overdue = mocker.Mock(return_value=True)
        
        mocker.patch(
            'app.sales.schemas.invoice_schema.ReferenceData.get_invoice_status_name',
            return_value='Pending'
        )
        
        schema = InvoiceResponseSchema()
        result = schema.dump(mock_invoice)
        
        assert result['is_overdue'] == True
        assert result['status'] == 'Pending'
