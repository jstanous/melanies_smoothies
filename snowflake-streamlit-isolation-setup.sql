-- Commentary:
  -- name: Melanie's Smoothie App Isolation
  -- domain: Snowflake
  -- scope: WH, RBAC, GRANTS
  -- rationale: Enforces scoped access for Streamlit app within Snowflake
  -- exposure: Public repo, cert-prep aligned
  -- password:
    -- rationale: Password placeholder defers to external secrets management
    -- exposure: No hardcoded credentials; aligns with security best practices
    -- notes:
      -- Replace with vault-managed secret or environment variable
      -- Commentary flags credential hygiene for cert-prep and repo exposure
  -- notes:
    -- Resource monitor enforces budget discipline
    -- Role grants scoped to app-specific tables and sequences
    -- Commentary flags password placeholder and SYSADMIN exposure

-- Switch to SYSADMIN role for warehouse creation and ownership
USE ROLE SYSADMIN;

-- Create dedicated Warehouse for Streamlit hosted applications.
CREATE WAREHOUSE IF NOT EXISTS STREAMLIT_WH
  WITH WAREHOUSE_SIZE = 'XSMALL'
       AUTO_SUSPEND = 300                   -- suspend after 60 seconds of inactivity
       AUTO_RESUME = TRUE
       SCALING_POLICY = 'STANDARD'         -- disables multi-cluster scaling
       COMMENT = 'Used by Streamlit hosted apps'

-- Switch to ACCOUNTADMIN role for Resource Monitor creation and ownership
USE ROLE ACCOUNTADMIN;

-- Create ultra-low budget Resource Monitor to preserve Trial Credits for cert-prep
CREATE RESOURCE MONITOR IF NOT EXISTS STREAMLIT_WH_MONITOR
  WITH CREDIT_QUOTA = 1                     -- adjust based on your monthly budget
       TRIGGERS ON 80 PERCENT DO NOTIFY
                ON 100 PERCENT DO SUSPEND;

-- Assign Resource Monitor to Warehouse
ALTER WAREHOUSE STREAMLIT_WH
  SET RESOURCE_MONITOR = STREAMLIT_WH_MONITOR;

-- Create dedicated USER for Streamlit integration
CREATE USER IF NOT EXISTS STREAMLIT_USER
       PASSWORD = '<<EXTERNAL_SECRET>>'
       DEFAULT_ROLE = STREAMLIT_ROLE
       MUST_CHANGE_PASSWORD = FALSE
       COMMENT = 'Used by Streamlit apps';

-- Create dedicated ROLE for Streamlit integration
CREATE ROLE IF NOT EXISTS STREAMLIT_ROLE
       COMMENT = 'Used by Streamlit apps';

-- Switch to SECURITYADMIN for ROLE GRANTS
USE ROLE SECURITYADMIN;
-- GRANT USAGE on objects supporting Smoothie Shop App to STREAMLIT_ROLE
GRANT USAGE ON WAREHOUSE STREAMLIT_WH TO ROLE STREAMLIT_ROLE;
GRANT USAGE ON DATABASE SMOOTHIES TO ROLE STREAMLIT_ROLE;
GRANT USAGE ON SCHEMA SMOOTHIES.PUBLIC TO ROLE STREAMLIT_ROLE;

-- GRANT least required permissions on objects supporting Smoothie Shop App to STREAMLIT_ROLE
GRANT SELECT, INSERT ON TABLE SMOOTHIES.PUBLIC.ORDERS TO ROLE STREAMLIT_ROLE;
GRANT SELECT ON TABLE SMOOTHIES.PUBLIC.FRUIT_OPTIONS TO ROLE STREAMLIT_ROLE;
GRANT USAGE ON SEQUENCE SMOOTHIES.PUBLIC.ORDER_SEQ TO ROLE STREAMLIT_ROLE;

-- Assign STREAMLIT_USER to STREAMLIT_ROLE for inherited permissions
GRANT ROLE STREAMLIT_ROLE TO USER STREAMLIT_USER;
-- Assign STREAMLIT_ROLE to SYSADMIN to preserve system wide control for SYSADMINs
GRANT ROLE STREAMLIT_ROLE TO ROLE SYSADMIN;
