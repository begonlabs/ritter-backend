-- =====================================
-- RESULTS MODULE - LEAD MANAGEMENT
-- =====================================
-- Tables: leads

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================
-- ENUMS USED BY RESULTS MODULE
-- =====================================

CREATE TYPE lead_status AS ENUM (
  'new',
  'contacted',
  'qualified',
  'interested',
  'not_interested',
  'invalid',
  'bounced'
);

-- =====================================
-- LEADS TABLE
-- =====================================

-- Leads table (simplified structure based on frontend requirements)
CREATE TABLE leads (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Contact Information
  email VARCHAR(255),
  verified_email BOOLEAN DEFAULT false,
  phone VARCHAR(50),
  verified_phone BOOLEAN DEFAULT false,
  
  -- Company Information
  company_name VARCHAR(500) NOT NULL,
  company_website VARCHAR(500),
  verified_website BOOLEAN DEFAULT false,
  
  -- Location Information
  address TEXT,
  state VARCHAR(255),
  country VARCHAR(100),
  
  -- Business Information (new fields based on schema)
  activity VARCHAR(255) NOT NULL, -- Required business activity
  description TEXT, -- Business description
  category VARCHAR(255), -- Business category
  
  -- Data Quality Score (1-5 based on verification flags)
  -- Calculation: 1 (base) + verified_email (1) + verified_phone (1) + verified_website (1) + has_phone (1) = max 5
  -- Used ONLY for filtering results, NOT for email campaigns
  data_quality_score INTEGER DEFAULT 1 CHECK (data_quality_score >= 1 AND data_quality_score <= 5),
  
  -- System Fields
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now(),
  last_contacted_at TIMESTAMP
);

-- =====================================
-- INDEXES FOR RESULTS MODULE
-- =====================================

-- Primary search indexes
CREATE INDEX idx_leads_email ON leads(email);
CREATE INDEX idx_leads_company_name ON leads(company_name);
CREATE INDEX idx_leads_activity ON leads(activity);
CREATE INDEX idx_leads_category ON leads(category);

-- Verification status indexes
CREATE INDEX idx_leads_verified_email ON leads(verified_email);
CREATE INDEX idx_leads_verified_phone ON leads(verified_phone);
CREATE INDEX idx_leads_verified_website ON leads(verified_website);

-- Data quality and filtering indexes
CREATE INDEX idx_leads_data_quality_score ON leads(data_quality_score);
CREATE INDEX idx_leads_created_at ON leads(created_at);

-- Compound indexes for common queries
CREATE UNIQUE INDEX idx_leads_email_company ON leads(email, company_name) WHERE email IS NOT NULL;
CREATE INDEX idx_leads_verification_composite ON leads(verified_email, verified_phone, verified_website);
CREATE INDEX idx_leads_quality_activity ON leads(data_quality_score, activity);

-- Location-based indexes
CREATE INDEX idx_leads_state ON leads(state);
CREATE INDEX idx_leads_country ON leads(country);
CREATE INDEX idx_leads_location_composite ON leads(state, country);

-- Full-text search index for company names and activities
CREATE INDEX idx_leads_company_name_gin ON leads USING gin(to_tsvector('english', company_name));
CREATE INDEX idx_leads_activity_gin ON leads USING gin(to_tsvector('english', activity));

-- =====================================
-- TRIGGERS FOR RESULTS MODULE
-- =====================================

-- Trigger to update updated_at timestamp
CREATE TRIGGER update_leads_updated_at 
  BEFORE UPDATE ON leads 
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to automatically calculate data quality score
CREATE OR REPLACE FUNCTION calculate_data_quality_score()
RETURNS TRIGGER AS $$
BEGIN
  -- Calculate quality score based on verification flags
  NEW.data_quality_score := 1; -- Base score
  
  -- Add points for verifications
  IF NEW.verified_email THEN
    NEW.data_quality_score := NEW.data_quality_score + 1;
  END IF;
  
  IF NEW.verified_phone THEN
    NEW.data_quality_score := NEW.data_quality_score + 1;
  END IF;
  
  IF NEW.verified_website THEN
    NEW.data_quality_score := NEW.data_quality_score + 1;
  END IF;
  
  -- Add point for having phone number
  IF NEW.phone IS NOT NULL AND length(trim(NEW.phone)) > 0 THEN
    NEW.data_quality_score := NEW.data_quality_score + 1;
  END IF;
  
  -- Ensure score is within bounds
  NEW.data_quality_score := GREATEST(NEW.data_quality_score, 1);
  NEW.data_quality_score := LEAST(NEW.data_quality_score, 5);
  
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply the quality score calculation trigger
CREATE TRIGGER calculate_lead_quality_score 
  BEFORE INSERT OR UPDATE ON leads 
  FOR EACH ROW EXECUTE FUNCTION calculate_data_quality_score();

-- =====================================
-- FUNCTIONS FOR RESULTS MODULE
-- =====================================

-- Function to search leads with filters
CREATE OR REPLACE FUNCTION search_leads(
  p_search_term TEXT DEFAULT NULL,
  p_min_quality_score INTEGER DEFAULT 1,
  p_verified_email BOOLEAN DEFAULT NULL,
  p_verified_phone BOOLEAN DEFAULT NULL,
  p_verified_website BOOLEAN DEFAULT NULL,
  p_categories TEXT[] DEFAULT NULL,
  p_states TEXT[] DEFAULT NULL,
  p_limit INTEGER DEFAULT 100,
  p_offset INTEGER DEFAULT 0
)
RETURNS TABLE (
  id UUID,
  email VARCHAR(255),
  verified_email BOOLEAN,
  phone VARCHAR(50),
  verified_phone BOOLEAN,
  company_name VARCHAR(500),
  company_website VARCHAR(500),
  verified_website BOOLEAN,
  address TEXT,
  state VARCHAR(255),
  country VARCHAR(100),
  activity VARCHAR(255),
  description TEXT,
  category VARCHAR(255),
  data_quality_score INTEGER,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  last_contacted_at TIMESTAMP
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    l.id, l.email, l.verified_email, l.phone, l.verified_phone,
    l.company_name, l.company_website, l.verified_website,
    l.address, l.state, l.country, l.activity, l.description, l.category,
    l.data_quality_score, l.created_at, l.updated_at, l.last_contacted_at
  FROM leads l
  WHERE 
    -- Quality score filter
    l.data_quality_score >= p_min_quality_score
    
    -- Search term filter (company name or activity)
    AND (p_search_term IS NULL OR 
         l.company_name ILIKE '%' || p_search_term || '%' OR
         l.activity ILIKE '%' || p_search_term || '%')
    
    -- Verification filters
    AND (p_verified_email IS NULL OR l.verified_email = p_verified_email)
    AND (p_verified_phone IS NULL OR l.verified_phone = p_verified_phone)
    AND (p_verified_website IS NULL OR l.verified_website = p_verified_website)
    
    -- Category filter
    AND (p_categories IS NULL OR l.category = ANY(p_categories))
    
    -- State filter
    AND (p_states IS NULL OR l.state = ANY(p_states))
  
  ORDER BY l.data_quality_score DESC, l.created_at DESC
  LIMIT p_limit OFFSET p_offset;
END;
$$ language 'plpgsql';

-- Function to get lead statistics
CREATE OR REPLACE FUNCTION get_lead_statistics()
RETURNS TABLE (
  total_leads BIGINT,
  verified_emails BIGINT,
  verified_phones BIGINT,
  verified_websites BIGINT,
  quality_score_1 BIGINT,
  quality_score_2 BIGINT,
  quality_score_3 BIGINT,
  quality_score_4 BIGINT,
  quality_score_5 BIGINT,
  top_categories JSON,
  top_states JSON
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    COUNT(*) as total_leads,
    COUNT(*) FILTER (WHERE verified_email = true) as verified_emails,
    COUNT(*) FILTER (WHERE verified_phone = true) as verified_phones,
    COUNT(*) FILTER (WHERE verified_website = true) as verified_websites,
    COUNT(*) FILTER (WHERE data_quality_score = 1) as quality_score_1,
    COUNT(*) FILTER (WHERE data_quality_score = 2) as quality_score_2,
    COUNT(*) FILTER (WHERE data_quality_score = 3) as quality_score_3,
    COUNT(*) FILTER (WHERE data_quality_score = 4) as quality_score_4,
    COUNT(*) FILTER (WHERE data_quality_score = 5) as quality_score_5,
    
    -- Top categories
    (SELECT json_agg(json_build_object('category', category, 'count', count))
     FROM (
       SELECT category, COUNT(*) as count
       FROM leads 
       WHERE category IS NOT NULL
       GROUP BY category 
       ORDER BY count DESC 
       LIMIT 10
     ) top_cats) as top_categories,
    
    -- Top states
    (SELECT json_agg(json_build_object('state', state, 'count', count))
     FROM (
       SELECT state, COUNT(*) as count
       FROM leads 
       WHERE state IS NOT NULL
       GROUP BY state 
       ORDER BY count DESC 
       LIMIT 10
     ) top_states_data) as top_states
  
  FROM leads;
END;
$$ language 'plpgsql';

-- Function to validate lead data integrity
CREATE OR REPLACE FUNCTION validate_lead_data()
RETURNS TABLE (
  issue_type TEXT,
  issue_count BIGINT,
  sample_ids UUID[]
) AS $$
BEGIN
  -- Check for leads missing required fields
  RETURN QUERY
  SELECT 
    'missing_company_name' as issue_type,
    COUNT(*) as issue_count,
    array_agg(id) as sample_ids
  FROM leads 
  WHERE company_name IS NULL OR trim(company_name) = ''
  HAVING COUNT(*) > 0;
  
  RETURN QUERY
  SELECT 
    'missing_activity' as issue_type,
    COUNT(*) as issue_count,
    array_agg(id) as sample_ids
  FROM leads 
  WHERE activity IS NULL OR trim(activity) = ''
  HAVING COUNT(*) > 0;
  
  -- Check for invalid email formats
  RETURN QUERY
  SELECT 
    'invalid_email_format' as issue_type,
    COUNT(*) as issue_count,
    array_agg(id) as sample_ids
  FROM leads 
  WHERE email IS NOT NULL 
    AND email !~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
  HAVING COUNT(*) > 0;
  
  -- Check for leads with verification flags but missing data
  RETURN QUERY
  SELECT 
    'verified_email_missing_data' as issue_type,
    COUNT(*) as issue_count,
    array_agg(id) as sample_ids
  FROM leads 
  WHERE verified_email = true AND (email IS NULL OR trim(email) = '')
  HAVING COUNT(*) > 0;
  
  RETURN QUERY
  SELECT 
    'verified_phone_missing_data' as issue_type,
    COUNT(*) as issue_count,
    array_agg(id) as sample_ids
  FROM leads 
  WHERE verified_phone = true AND (phone IS NULL OR trim(phone) = '')
  HAVING COUNT(*) > 0;
  
  RETURN QUERY
  SELECT 
    'verified_website_missing_data' as issue_type,
    COUNT(*) as issue_count,
    array_agg(id) as sample_ids
  FROM leads 
  WHERE verified_website = true AND (company_website IS NULL OR trim(company_website) = '')
  HAVING COUNT(*) > 0;
END;
$$ language 'plpgsql';

-- =====================================
-- VIEWS FOR RESULTS MODULE
-- =====================================

-- View for high-quality leads (quality score 4-5)
CREATE VIEW high_quality_leads AS
SELECT 
  id, email, verified_email, phone, verified_phone,
  company_name, company_website, verified_website,
  address, state, country, activity, description, category,
  data_quality_score, created_at, updated_at, last_contacted_at
FROM leads 
WHERE data_quality_score >= 4;

-- View for leads with contact information
CREATE VIEW contactable_leads AS
SELECT 
  id, email, verified_email, phone, verified_phone,
  company_name, company_website, verified_website,
  address, state, country, activity, description, category,
  data_quality_score, created_at, updated_at, last_contacted_at
FROM leads 
WHERE (email IS NOT NULL AND verified_email = true) 
   OR (phone IS NOT NULL AND verified_phone = true);

-- View for leads summary by category
CREATE VIEW leads_by_category AS
SELECT 
  category,
  COUNT(*) as total_leads,
  COUNT(*) FILTER (WHERE verified_email = true) as verified_emails,
  COUNT(*) FILTER (WHERE verified_phone = true) as verified_phones,
  COUNT(*) FILTER (WHERE verified_website = true) as verified_websites,
  ROUND(AVG(data_quality_score), 2) as avg_quality_score,
  MAX(created_at) as latest_lead_date
FROM leads 
WHERE category IS NOT NULL
GROUP BY category
ORDER BY total_leads DESC;

-- =====================================
-- INITIAL DATA FOR RESULTS MODULE
-- =====================================

-- Insert some sample leads for testing (optional)
-- Uncomment the following lines if you want sample data

/*
INSERT INTO leads (
  email, verified_email, phone, verified_phone, company_name, company_website, verified_website,
  address, state, country, activity, description, category
) VALUES 
(
  'contacto@energiasolar.es', true, '+34 912 345 678', true, 'Energía Solar Madrid', 'energiasolar.es', true,
  'Calle del Sol 123', 'Madrid', 'España', 'Instalación de Paneles Solares', 
  'Empresa especializada en instalación de sistemas de energía solar para hogares y empresas',
  'Energía Renovable'
),
(
  'info@construye.com', true, NULL, false, 'Construcciones del Futuro', 'construye.com', true,
  'Avenida de la Construcción 456', 'Barcelona', 'España', 'Construcción y Desarrollo',
  'Constructora especializada en edificios sostenibles y eficientes energéticamente',
  'Construcción'
),
(
  NULL, false, '+34 933 456 789', true, 'Industrias Mecánicas SA', NULL, false,
  'Polígono Industrial Norte', 'Valencia', 'España', 'Manufactura Industrial',
  'Empresa de manufactura de componentes mecánicos para la industria',
  'Industria'
);
*/

-- Log initialization
INSERT INTO system_logs (level, message, source, metadata) VALUES
('info', 'Results module initialized successfully', 'system', '{"module": "results", "version": "1.0", "table": "leads"}');

COMMIT;
