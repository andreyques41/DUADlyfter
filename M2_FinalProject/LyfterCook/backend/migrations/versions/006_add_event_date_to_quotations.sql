-- Migration: Add event_date column to quotations table
-- Date: 2025-12-18
-- Purpose: Fix schema mismatch between model and database

-- Add event_date column to quotations table
ALTER TABLE core.quotations 
ADD COLUMN IF NOT EXISTS event_date DATE;

-- Add comment to explain the column
COMMENT ON COLUMN core.quotations.event_date IS 'Date of the event for which the quotation is being prepared';

-- Verify the change
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_schema = 'core' 
  AND table_name = 'quotations' 
  AND column_name = 'event_date';
