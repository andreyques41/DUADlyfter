-- Migration: Expand menustatus enum with additional states
-- Author: System
-- Date: 2025-12-21
-- Description: 
--   Adds new status values to menustatus enum:
--   - draft: Menu under construction
--   - published: Publicly available (replaces ACTIVE)
--   - archived: Historical/inactive menu
--   - seasonal: Only available during certain dates
--
-- Note: PostgreSQL doesn't support removing enum values, so ACTIVE and INACTIVE 
--       will remain for backward compatibility but should be deprecated.

BEGIN;

DO $$
BEGIN
    -- Add new enum values if they don't exist
    -- Note: ALTER TYPE ADD VALUE cannot be in a transaction block if combined with other operations,
    -- but we can check if value exists first
    
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'draft' AND enumtypid = (
        SELECT oid FROM pg_type WHERE typname = 'menustatus'
    )) THEN
        ALTER TYPE menustatus ADD VALUE 'draft';
        RAISE NOTICE 'Added enum value: draft';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'published' AND enumtypid = (
        SELECT oid FROM pg_type WHERE typname = 'menustatus'
    )) THEN
        ALTER TYPE menustatus ADD VALUE 'published';
        RAISE NOTICE 'Added enum value: published';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'archived' AND enumtypid = (
        SELECT oid FROM pg_type WHERE typname = 'menustatus'
    )) THEN
        ALTER TYPE menustatus ADD VALUE 'archived';
        RAISE NOTICE 'Added enum value: archived';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'seasonal' AND enumtypid = (
        SELECT oid FROM pg_type WHERE typname = 'menustatus'
    )) THEN
        ALTER TYPE menustatus ADD VALUE 'seasonal';
        RAISE NOTICE 'Added enum value: seasonal';
    END IF;
END $$;

-- Update existing menus to use new values
-- ACTIVE -> published (publicly available menus)
-- INACTIVE -> archived (inactive menus)
UPDATE core.menus SET status = 'published' WHERE status = 'ACTIVE';
UPDATE core.menus SET status = 'archived' WHERE status = 'INACTIVE';

-- Verification: Show all enum values
DO $$
DECLARE
    enum_values TEXT;
BEGIN
    SELECT string_agg(enumlabel, ', ' ORDER BY enumsortorder) INTO enum_values
    FROM pg_enum 
    WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'menustatus');
    
    RAISE NOTICE '✅ SUCCESS: menustatus enum now has values: %', enum_values;
END $$;

COMMIT;
