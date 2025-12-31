-- ============================================================================
-- Migration: Standardize VARCHAR Lengths
-- Date: 2025-12-19
-- Author: Backend Engineering Team
-- 
-- Purpose: Standardize VARCHAR lengths for columns that appear in multiple
--          tables with inconsistent lengths.
--
-- Affected Tables:
--   • core.ingredients.unit (20 → 50)
--   • integrations.scraped_products.ingredient_name (100 → 200)
--   • integrations.scraped_products.product_name (200 → 300)
--
-- Rationale:
--   1. Consistency across database schema
--   2. Accommodate all use cases with single standard
--   3. Prevent data truncation issues
--   4. Improve maintainability
--
-- Risk: LOW - Only affects empty/integration tables
-- Rollback: See rollback section at end of file
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. Standardize 'unit' column to VARCHAR(50)
-- ============================================================================

-- Current state:
--   core.ingredients.unit = VARCHAR(20)
--   integrations.scraped_prices.unit = VARCHAR(50)
-- 
-- Decision: Use VARCHAR(50) to allow for longer unit names like "tablespoons"

COMMENT ON COLUMN core.ingredients.unit IS 
'Measurement unit for ingredient. Standardized to VARCHAR(50) on 2025-12-19 for consistency.';

ALTER TABLE core.ingredients 
  ALTER COLUMN unit TYPE VARCHAR(50);

COMMENT ON COLUMN core.ingredients.unit IS 
'Unit of measurement (e.g., kg, lbs, cups, tablespoons, ml)';

-- ============================================================================
-- 2. Standardize 'ingredient_name' column to VARCHAR(200)
-- ============================================================================

-- Current state:
--   integrations.scraped_prices.ingredient_name = VARCHAR(200) ✓
--   integrations.scraped_products.ingredient_name = VARCHAR(100)
-- 
-- Decision: Use VARCHAR(200) as reasonable balance for ingredient names

COMMENT ON COLUMN integrations.scraped_products.ingredient_name IS 
'Ingredient name from scraper. Standardized to VARCHAR(200) on 2025-12-19 for consistency.';

ALTER TABLE integrations.scraped_products 
  ALTER COLUMN ingredient_name TYPE VARCHAR(200);

COMMENT ON COLUMN integrations.scraped_products.ingredient_name IS 
'Name of ingredient from scraped product data';

-- ============================================================================
-- 3. Standardize 'product_name' column to VARCHAR(300)
-- ============================================================================

-- Current state:
--   integrations.scraped_prices.product_name = VARCHAR(300) ✓
--   integrations.scraped_products.product_name = VARCHAR(200)
-- 
-- Decision: Use VARCHAR(300) to accommodate longer product names from scrapers

COMMENT ON COLUMN integrations.scraped_products.product_name IS 
'Product name from scraper. Standardized to VARCHAR(300) on 2025-12-19 for consistency.';

ALTER TABLE integrations.scraped_products 
  ALTER COLUMN product_name TYPE VARCHAR(300);

COMMENT ON COLUMN integrations.scraped_products.product_name IS 
'Full product name from scraped data';

-- ============================================================================
-- 4. Verification Query
-- ============================================================================

DO $$
DECLARE
    unit_len INTEGER;
    ingredient_name_len INTEGER;
    product_name_len INTEGER;
BEGIN
    -- Check unit length in core.ingredients
    SELECT character_maximum_length INTO unit_len
    FROM information_schema.columns
    WHERE table_schema = 'core' 
      AND table_name = 'ingredients' 
      AND column_name = 'unit';
    
    -- Check ingredient_name length in integrations.scraped_products
    SELECT character_maximum_length INTO ingredient_name_len
    FROM information_schema.columns
    WHERE table_schema = 'integrations' 
      AND table_name = 'scraped_products' 
      AND column_name = 'ingredient_name';
    
    -- Check product_name length in integrations.scraped_products
    SELECT character_maximum_length INTO product_name_len
    FROM information_schema.columns
    WHERE table_schema = 'integrations' 
      AND table_name = 'scraped_products' 
      AND column_name = 'product_name';
    
    -- Verify all are correct
    IF unit_len = 50 AND ingredient_name_len = 200 AND product_name_len = 300 THEN
        RAISE NOTICE '✅ SUCCESS: All VARCHAR lengths standardized';
        RAISE NOTICE '   • core.ingredients.unit → VARCHAR(%)', unit_len;
        RAISE NOTICE '   • integrations.scraped_products.ingredient_name → VARCHAR(%)', ingredient_name_len;
        RAISE NOTICE '   • integrations.scraped_products.product_name → VARCHAR(%)', product_name_len;
    ELSE
        RAISE EXCEPTION '❌ FAILED: VARCHAR standardization incomplete. unit:% ingredient_name:% product_name:%', 
                        unit_len, ingredient_name_len, product_name_len;
    END IF;
END $$;

COMMIT;

-- ============================================================================
-- SUMMARY OF CHANGES
-- ============================================================================
-- 
-- Column Name          | Old Length | New Length | Tables Affected
-- ---------------------|------------|------------|----------------------------------
-- unit                 | 20         | 50         | core.ingredients
-- ingredient_name      | 100        | 200        | integrations.scraped_products
-- product_name         | 200        | 300        | integrations.scraped_products
-- 
-- IMPACT:
-- • LOW risk - no data truncation (tables are empty or have minimal data)
-- • Improves schema consistency
-- • Prevents future data truncation issues
-- • Aligns with scraper requirements
-- 
-- ============================================================================
-- ROLLBACK SCRIPT (in case of issues)
-- ============================================================================
-- Run this only if you need to rollback the migration
-- 
-- BEGIN;
-- 
-- ALTER TABLE core.ingredients 
--   ALTER COLUMN unit TYPE VARCHAR(20);
-- 
-- ALTER TABLE integrations.scraped_products 
--   ALTER COLUMN ingredient_name TYPE VARCHAR(100);
-- 
-- ALTER TABLE integrations.scraped_products 
--   ALTER COLUMN product_name TYPE VARCHAR(200);
-- 
-- COMMIT;
