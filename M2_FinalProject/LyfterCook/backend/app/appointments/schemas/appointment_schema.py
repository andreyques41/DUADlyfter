"""
Appointment schemas for validation and serialization
"""
from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime, timedelta


class AppointmentCreateSchema(Schema):
    """Schema for creating a new appointment"""
    client_id = fields.Int(required=False, allow_none=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str(required=False, allow_none=True, validate=validate.Length(max=2000))
    scheduled_at = fields.DateTime(required=True)
    duration_minutes = fields.Int(required=False, load_default=60, validate=validate.Range(min=15, max=480))
    location = fields.Str(required=False, allow_none=True, validate=validate.Length(max=500))
    meeting_url = fields.Str(required=False, allow_none=True, validate=validate.Length(max=500))
    notes = fields.Str(required=False, allow_none=True, validate=validate.Length(max=2000))
    
    # External calendar fields (readonly for now, manual appointments don't use these)
    external_calendar_id = fields.Str(required=False, allow_none=True)
    external_calendar_provider = fields.Str(required=False, allow_none=True, validate=validate.OneOf(['calendly', 'google_calendar']))
    
    @validates('scheduled_at')
    def validate_scheduled_at(self, value):
        """Validate scheduled time is in the future"""
        if value < datetime.utcnow():
            raise ValidationError('Appointment must be scheduled in the future')


class AppointmentUpdateSchema(Schema):
    """Schema for updating appointment"""
    client_id = fields.Int(required=False, allow_none=True)
    title = fields.Str(required=False, validate=validate.Length(min=1, max=200))
    description = fields.Str(required=False, allow_none=True, validate=validate.Length(max=2000))
    scheduled_at = fields.DateTime(required=False)
    duration_minutes = fields.Int(required=False, validate=validate.Range(min=15, max=480))
    location = fields.Str(required=False, allow_none=True, validate=validate.Length(max=500))
    meeting_url = fields.Str(required=False, allow_none=True, validate=validate.Length(max=500))
    notes = fields.Str(required=False, allow_none=True, validate=validate.Length(max=2000))
    
    @validates('scheduled_at')
    def validate_scheduled_at(self, value):
        """Validate scheduled time is in the future"""
        if value and value < datetime.utcnow():
            raise ValidationError('Appointment must be scheduled in the future')


class AppointmentStatusUpdateSchema(Schema):
    """Schema for updating appointment status"""
    status = fields.Str(required=True, validate=validate.OneOf(['scheduled', 'confirmed', 'cancelled', 'completed', 'no_show']))
    cancellation_reason = fields.Str(required=False, allow_none=True, validate=validate.Length(max=500))


class AppointmentClientSchema(Schema):
    """Client info in appointment"""
    id = fields.Int()
    name = fields.Str()
    email = fields.Str(allow_none=True)
    phone = fields.Str(allow_none=True)
    company = fields.Str(allow_none=True)


class AppointmentResponseSchema(Schema):
    """Schema for appointment response"""
    id = fields.Int(dump_only=True)
    chef_id = fields.Int(dump_only=True)
    client_id = fields.Int(allow_none=True)
    title = fields.Str()
    description = fields.Str(allow_none=True)
    scheduled_at = fields.DateTime()
    duration_minutes = fields.Int()
    location = fields.Str(allow_none=True)
    external_calendar_id = fields.Str(allow_none=True, dump_only=True)
    external_calendar_provider = fields.Str(allow_none=True, dump_only=True)
    meeting_url = fields.Str(allow_none=True)
    status = fields.Str()
    notes = fields.Str(allow_none=True)
    cancellation_reason = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    cancelled_at = fields.DateTime(dump_only=True, allow_none=True)
    completed_at = fields.DateTime(dump_only=True, allow_none=True)
    
    # Nested and calculated fields
    client = fields.Method("get_client")
    end_time = fields.Method("get_end_time")
    
    def get_client(self, obj):
        """Serialize client if exists"""
        if not obj.client:
            return None
        return {
            'id': obj.client.id,
            'name': obj.client.name,
            'email': obj.client.email,
            'phone': obj.client.phone,
            'company': obj.client.company
        }
    
    def get_end_time(self, obj):
        """Calculate end time based on scheduled_at + duration_minutes"""
        if obj.scheduled_at and obj.duration_minutes:
            from datetime import timedelta
            return obj.scheduled_at + timedelta(minutes=obj.duration_minutes)
        return None
