-- Migration: Create Admin Audit Logs Table
-- Date: 2024
-- Description: Tabla para tracking de acciones administrativas

-- Create table
CREATE TABLE IF NOT EXISTS core.admin_audit_logs (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    action VARCHAR(100) NOT NULL,
    target_type VARCHAR(50),
    target_id INTEGER,
    reason TEXT,
    metadata JSONB,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_admin_logs_admin_id 
    ON core.admin_audit_logs(admin_id);

CREATE INDEX IF NOT EXISTS idx_admin_logs_action 
    ON core.admin_audit_logs(action);

CREATE INDEX IF NOT EXISTS idx_admin_logs_created_at 
    ON core.admin_audit_logs(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_admin_logs_target 
    ON core.admin_audit_logs(target_type, target_id);

-- Add comments
COMMENT ON TABLE core.admin_audit_logs IS 
    'Audit trail for all administrative actions';

COMMENT ON COLUMN core.admin_audit_logs.admin_id IS 
    'ID of the admin user who performed the action';

COMMENT ON COLUMN core.admin_audit_logs.action IS 
    'Type of action performed (e.g., activate_chef, deactivate_chef)';

COMMENT ON COLUMN core.admin_audit_logs.target_type IS 
    'Type of entity affected (e.g., chef, user, dish)';

COMMENT ON COLUMN core.admin_audit_logs.target_id IS 
    'ID of the affected entity';

COMMENT ON COLUMN core.admin_audit_logs.reason IS 
    'Optional reason provided by admin for the action';

COMMENT ON COLUMN core.admin_audit_logs.metadata IS 
    'Additional JSON data related to the action';

COMMENT ON COLUMN core.admin_audit_logs.ip_address IS 
    'IP address from which the action was performed';
