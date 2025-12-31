-- ============================================================================
-- Migration: Add Unique Constraints for Duplication Prevention
-- Date: 2025-12-19
-- 
-- Purpose: Add unique constraints to prevent duplicate data
--
-- Affected Tables:
--   • core.dishes - UNIQUE(chef_id, name)
--   • core.clients - UNIQUE(email)
--   • core.menus - UNIQUE(chef_id, name)
--   • core.ingredients - UNIQUE(dish_id, name)
-- ============================================================================

BEGIN;

-- Add constraints (drop first if exists)
DO $$
BEGIN
    ALTER TABLE core.dishes DROP CONSTRAINT IF EXISTS dishes_chef_name_unique;
    ALTER TABLE core.dishes ADD CONSTRAINT dishes_chef_name_unique UNIQUE (chef_id, name);
    
    ALTER TABLE core.clients DROP CONSTRAINT IF EXISTS clients_email_unique;
    ALTER TABLE core.clients ADD CONSTRAINT clients_email_unique UNIQUE (email);
    
    ALTER TABLE core.menus DROP CONSTRAINT IF EXISTS menus_chef_name_unique;
    ALTER TABLE core.menus ADD CONSTRAINT menus_chef_name_unique UNIQUE (chef_id, name);
    
    ALTER TABLE core.ingredients DROP CONSTRAINT IF EXISTS ingredients_dish_name_unique;
    ALTER TABLE core.ingredients ADD CONSTRAINT ingredients_dish_name_unique UNIQUE (dish_id, name);
END $$;

-- Verification
DO $$
DECLARE
    cnt INTEGER;
BEGIN
    SELECT COUNT(*) INTO cnt
    FROM information_schema.table_constraints
    WHERE table_schema = 'core'
    AND constraint_type = 'UNIQUE'
    AND constraint_name IN (
        'dishes_chef_name_unique',
        'clients_email_unique',
        'menus_chef_name_unique',
        'ingredients_dish_name_unique'
    );
    
    IF cnt = 4 THEN
        RAISE NOTICE '✅ SUCCESS: All 4 unique constraints added';
    ELSE
        RAISE EXCEPTION 'Only % of 4 constraints added', cnt;
    END IF;
END $$;

COMMIT;
