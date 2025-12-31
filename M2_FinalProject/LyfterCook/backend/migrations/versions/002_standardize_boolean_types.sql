-- ============================================================================
-- Migration: Standardize Boolean Types
-- Date: 2025-12-19
-- Author: Backend Engineering Team
-- 
-- Purpose: Convert INTEGER-as-boolean columns to native BOOLEAN type
--          for consistency across the database schema.
--
-- Affected Tables:
--   • core.dishes.is_active (INTEGER → BOOLEAN)
--   • core.ingredients.is_optional (INTEGER → BOOLEAN)
--
-- Rationale:
--   1. PostgreSQL best practice: Use native BOOLEAN type
--   2. Type safety and consistency
--   3. Better query optimization
--   4. Standard SQL compliance
--   5. Seamless SQLAlchemy integration
--
-- Rollback: See rollback section at end of file
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. Convert core.dishes.is_active from INTEGER to BOOLEAN
-- ============================================================================

-- Add comment explaining the change
COMMENT ON COLUMN core.dishes.is_active IS 
'Active status of dish. Migrated from INTEGER to BOOLEAN on 2025-12-19 for type consistency.';

-- Convert the column type
-- USING clause converts: 0 → false, 1 → true, NULL → NULL
ALTER TABLE core.dishes 
  ALTER COLUMN is_active TYPE BOOLEAN 
  USING (
    CASE 
      WHEN is_active IS NULL THEN NULL
      WHEN is_active = 0 THEN FALSE
      ELSE TRUE
    END
  );

-- Set default if it doesn't exist
ALTER TABLE core.dishes 
  ALTER COLUMN is_active SET DEFAULT TRUE;

-- Verify NOT NULL constraint
ALTER TABLE core.dishes 
  ALTER COLUMN is_active SET NOT NULL;

COMMENT ON COLUMN core.dishes.is_active IS 
'Whether the dish is active and available for ordering';


-- ============================================================================
-- 2. Convert core.ingredients.is_optional from INTEGER to BOOLEAN
-- ============================================================================

-- Add comment explaining the change
COMMENT ON COLUMN core.ingredients.is_optional IS 
'Optional status of ingredient. Migrated from INTEGER to BOOLEAN on 2025-12-19 for type consistency.';

-- Convert the column type
ALTER TABLE core.ingredients 
  ALTER COLUMN is_optional TYPE BOOLEAN 
  USING (
    CASE 
      WHEN is_optional IS NULL THEN NULL
      WHEN is_optional = 0 THEN FALSE
      ELSE TRUE
    END
  );

-- Set default if it doesn't exist
ALTER TABLE core.ingredients 
  ALTER COLUMN is_optional SET DEFAULT FALSE;

-- Verify NOT NULL constraint
ALTER TABLE core.ingredients 
  ALTER COLUMN is_optional SET NOT NULL;

COMMENT ON COLUMN core.ingredients.is_optional IS 
'Whether the ingredient is optional in the dish';


-- ============================================================================
-- 3. Verification Query
-- ============================================================================

-- Run this to verify the changes
DO $$
DECLARE
    dishes_type TEXT;
    ingredients_type TEXT;
BEGIN
    -- Check dishes.is_active type
    SELECT data_type INTO dishes_type
    FROM information_schema.columns
    WHERE table_schema = 'core' 
      AND table_name = 'dishes' 
      AND column_name = 'is_active';
    
    -- Check ingredients.is_optional type
    SELECT data_type INTO ingredients_type
    FROM information_schema.columns
    WHERE table_schema = 'core' 
      AND table_name = 'ingredients' 
      AND column_name = 'is_optional';
    
    -- Verify both are boolean
    IF dishes_type = 'boolean' AND ingredients_type = 'boolean' THEN
        RAISE NOTICE '✅ SUCCESS: All boolean columns now use BOOLEAN type';
        RAISE NOTICE '   • core.dishes.is_active → %', dishes_type;
        RAISE NOTICE '   • core.ingredients.is_optional → %', ingredients_type;
    ELSE
        RAISE EXCEPTION '❌ FAILED: Type conversion incomplete. dishes:% ingredients:%', 
                        dishes_type, ingredients_type;
    END IF;
END $$;

COMMIT;

-- ============================================================================
-- ROLLBACK SCRIPT (in case of issues)
-- ============================================================================
-- Run this only if you need to rollback the migration
-- 
-- BEGIN;
-- 
-- ALTER TABLE core.dishes 
--   ALTER COLUMN is_active TYPE INTEGER 
--   USING (is_active::integer);
-- 
-- ALTER TABLE core.dishes 
--   ALTER COLUMN is_active SET DEFAULT 1;
-- 
-- ALTER TABLE core.ingredients 
--   ALTER COLUMN is_optional TYPE INTEGER 
--   USING (is_optional::integer);
-- 
-- ALTER TABLE core.ingredients 
--   ALTER COLUMN is_optional SET DEFAULT 0;
-- 
-- COMMIT;
