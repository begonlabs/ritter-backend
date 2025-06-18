-- =====================================
-- SEARCH MODULE - SEARCH CONFIGURATIONS & HISTORY
-- =====================================
-- Tables: search_configurations, search_history

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================
-- ENUMS USED BY SEARCH MODULE
-- =====================================

CREATE TYPE search_status AS ENUM (
  'pending',
  'in_progress',
  'completed',
  'failed',
  'cancelled'
);

CREATE TYPE validation_status AS ENUM (
  'pending',
  'valid',
  'invalid',
  'risky',
  'unknown'
);

-- =====================================
-- SEARCH CONFIGURATIONS
-- =====================================

-- Search configurations table
CREATE TABLE search_configurations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  
  -- Search Parameters
  client_types JSONB DEFAULT '[]', -- Array of client types
  locations JSONB DEFAULT '[]', -- Array of locations
  websites JSONB DEFAULT '[]', -- Array of selected websites
  
  -- Validation Options
  validate_emails BOOLEAN DEFAULT true,
  validate_websites BOOLEAN DEFAULT true,
  validate_phones BOOLEAN DEFAULT false,
  
  -- Advanced Filters
  company_size_min INTEGER,
  company_size_max INTEGER,
  industries JSONB DEFAULT '[]',
  job_titles JSONB DEFAULT '[]',
  keywords VARCHAR(500),
  exclude_keywords VARCHAR(500),
  
  -- System Fields
  created_by UUID NOT NULL,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now(),
  last_used_at TIMESTAMP,
  usage_count INTEGER DEFAULT 0,
  
  -- Configuration
  is_template BOOLEAN DEFAULT false,
  is_public BOOLEAN DEFAULT false,
  metadata JSONB DEFAULT '{}'
);

-- =====================================
-- SEARCH HISTORY
-- =====================================

-- Search history table
CREATE TABLE search_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,
  search_config_id UUID,
  
  -- Search Details
  query_name VARCHAR(255),
  search_parameters JSONB NOT NULL,
  filters_applied JSONB DEFAULT '{}',
  
  -- Results
  status search_status DEFAULT 'pending',
  total_results INTEGER DEFAULT 0,
  valid_results INTEGER DEFAULT 0,
  duplicate_results INTEGER DEFAULT 0,
  
  -- Performance
  execution_time_ms INTEGER,
  pages_scraped INTEGER DEFAULT 0,
  websites_searched JSONB DEFAULT '[]',
  
  -- System Fields
  started_at TIMESTAMP DEFAULT now(),
  completed_at TIMESTAMP,
  error_message TEXT,
  
  -- Result Storage
  results_file_url VARCHAR(500),
  results_summary JSONB DEFAULT '{}',
  metadata JSONB DEFAULT '{}'
);

-- =====================================
-- INDEXES FOR SEARCH MODULE
-- =====================================

-- Search configurations indexes
CREATE INDEX idx_search_configurations_name ON search_configurations(name);
CREATE INDEX idx_search_configurations_created_by ON search_configurations(created_by);
CREATE INDEX idx_search_configurations_is_template ON search_configurations(is_template);
CREATE INDEX idx_search_configurations_is_public ON search_configurations(is_public);
CREATE INDEX idx_search_configurations_last_used_at ON search_configurations(last_used_at);
CREATE INDEX idx_search_configurations_usage_count ON search_configurations(usage_count);

-- Search history indexes
CREATE INDEX idx_search_history_user_id ON search_history(user_id);
CREATE INDEX idx_search_history_search_config_id ON search_history(search_config_id);
CREATE INDEX idx_search_history_status ON search_history(status);
CREATE INDEX idx_search_history_started_at ON search_history(started_at);
CREATE INDEX idx_search_history_total_results ON search_history(total_results);
CREATE INDEX idx_search_history_user_started ON search_history(user_id, started_at);

-- =====================================
-- FOREIGN KEY CONSTRAINTS
-- =====================================

-- Search configurations foreign keys
ALTER TABLE search_configurations ADD CONSTRAINT fk_search_configurations_created_by FOREIGN KEY (created_by) REFERENCES users(id);

-- Search history foreign keys
ALTER TABLE search_history ADD CONSTRAINT fk_search_history_user_id FOREIGN KEY (user_id) REFERENCES users(id);
ALTER TABLE search_history ADD CONSTRAINT fk_search_history_search_config_id FOREIGN KEY (search_config_id) REFERENCES search_configurations(id);

-- =====================================
-- TRIGGERS FOR SEARCH MODULE
-- =====================================

-- Trigger to update updated_at timestamp
CREATE TRIGGER update_search_configurations_updated_at 
  BEFORE UPDATE ON search_configurations 
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to update search configuration usage
CREATE OR REPLACE FUNCTION update_search_config_usage()
RETURNS TRIGGER AS $$
BEGIN
  -- Update usage when search is started with a configuration
  IF TG_OP = 'INSERT' AND NEW.search_config_id IS NOT NULL THEN
    UPDATE search_configurations SET
      usage_count = usage_count + 1,
      last_used_at = now(),
      updated_at = now()
    WHERE id = NEW.search_config_id;
  END IF;
  
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to update configuration usage
CREATE TRIGGER update_search_config_usage_trigger 
  AFTER INSERT ON search_history 
  FOR EACH ROW EXECUTE FUNCTION update_search_config_usage();

-- =====================================
-- FUNCTIONS FOR SEARCH MODULE
-- =====================================

-- Function to get search statistics for a user
CREATE OR REPLACE FUNCTION get_user_search_statistics(p_user_id UUID)
RETURNS TABLE (
  total_searches BIGINT,
  successful_searches BIGINT,
  failed_searches BIGINT,
  total_results BIGINT,
  avg_execution_time_ms NUMERIC,
  last_search_date TIMESTAMP,
  most_used_config VARCHAR(255)
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    COUNT(*) as total_searches,
    COUNT(*) FILTER (WHERE status = 'completed') as successful_searches,
    COUNT(*) FILTER (WHERE status = 'failed') as failed_searches,
    COALESCE(SUM(total_results), 0) as total_results,
    COALESCE(ROUND(AVG(execution_time_ms), 2), 0) as avg_execution_time_ms,
    MAX(started_at) as last_search_date,
    (
      SELECT sc.name 
      FROM search_configurations sc 
      WHERE sc.id = (
        SELECT search_config_id 
        FROM search_history sh2 
        WHERE sh2.user_id = p_user_id 
          AND sh2.search_config_id IS NOT NULL
        GROUP BY search_config_id 
        ORDER BY COUNT(*) DESC 
        LIMIT 1
      )
    ) as most_used_config
  FROM search_history sh
  WHERE sh.user_id = p_user_id;
END;
$$ language 'plpgsql';

-- Function to get popular search configurations
CREATE OR REPLACE FUNCTION get_popular_search_configurations(p_limit INTEGER DEFAULT 10)
RETURNS TABLE (
  id UUID,
  name VARCHAR(255),
  description TEXT,
  usage_count INTEGER,
  last_used_at TIMESTAMP,
  created_by_name VARCHAR(255),
  is_template BOOLEAN,
  is_public BOOLEAN
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    sc.id, sc.name, sc.description, sc.usage_count, sc.last_used_at,
    u.full_name as created_by_name, sc.is_template, sc.is_public
  FROM search_configurations sc
  LEFT JOIN users u ON sc.created_by = u.id
  WHERE sc.is_public = true OR sc.is_template = true
  ORDER BY sc.usage_count DESC, sc.last_used_at DESC
  LIMIT p_limit;
END;
$$ language 'plpgsql';

-- Function to get search performance trends
CREATE OR REPLACE FUNCTION get_search_performance_trends(
  p_user_id UUID DEFAULT NULL,
  p_days_back INTEGER DEFAULT 30
)
RETURNS TABLE (
  search_date DATE,
  total_searches BIGINT,
  successful_searches BIGINT,
  total_results BIGINT,
  avg_execution_time_ms NUMERIC
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    DATE(started_at) as search_date,
    COUNT(*) as total_searches,
    COUNT(*) FILTER (WHERE status = 'completed') as successful_searches,
    COALESCE(SUM(total_results), 0) as total_results,
    COALESCE(ROUND(AVG(execution_time_ms), 2), 0) as avg_execution_time_ms
  FROM search_history
  WHERE started_at >= CURRENT_DATE - INTERVAL '%s days' 
    AND (p_user_id IS NULL OR user_id = p_user_id)
  GROUP BY DATE(started_at)
  ORDER BY search_date DESC;
END;
$$ language 'plpgsql';

-- Function to clean up old search history
CREATE OR REPLACE FUNCTION cleanup_old_search_history(p_days_to_keep INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
  deleted_count INTEGER;
BEGIN
  DELETE FROM search_history 
  WHERE started_at < CURRENT_DATE - INTERVAL '%s days'
    AND status IN ('completed', 'failed', 'cancelled');
  
  GET DIAGNOSTICS deleted_count = ROW_COUNT;
  
  -- Log cleanup activity
  INSERT INTO system_logs (level, message, source, metadata)
  VALUES ('info', 'Cleaned up old search history', 'search', 
          json_build_object('deleted_count', deleted_count, 'days_kept', p_days_to_keep));
  
  RETURN deleted_count;
END;
$$ language 'plpgsql';

-- =====================================
-- VIEWS FOR SEARCH MODULE
-- =====================================

-- View for recent searches
CREATE VIEW recent_searches AS
SELECT 
  sh.id, sh.query_name, sh.status, sh.total_results, sh.valid_results,
  sh.execution_time_ms, sh.started_at, sh.completed_at,
  u.full_name as user_name, sc.name as config_name
FROM search_history sh
LEFT JOIN users u ON sh.user_id = u.id
LEFT JOIN search_configurations sc ON sh.search_config_id = sc.id
ORDER BY sh.started_at DESC;

-- View for search configuration templates
CREATE VIEW search_templates AS
SELECT 
  id, name, description, client_types, locations, 
  validate_emails, validate_websites, validate_phones,
  keywords, exclude_keywords, usage_count, last_used_at,
  created_by, created_at
FROM search_configurations 
WHERE is_template = true
ORDER BY usage_count DESC, name;

-- View for public search configurations
CREATE VIEW public_search_configs AS
SELECT 
  sc.id, sc.name, sc.description, sc.client_types, sc.locations,
  sc.validate_emails, sc.validate_websites, sc.validate_phones,
  sc.keywords, sc.exclude_keywords, sc.usage_count, sc.last_used_at,
  u.full_name as created_by_name, sc.created_at
FROM search_configurations sc
LEFT JOIN users u ON sc.created_by = u.id
WHERE sc.is_public = true
ORDER BY sc.usage_count DESC, sc.name;

-- =====================================
-- INITIAL DATA FOR SEARCH MODULE
-- =====================================

-- Insert default search configuration templates
INSERT INTO search_configurations (
  id, name, description, client_types, locations, 
  validate_emails, validate_websites, validate_phones,
  keywords, is_template, is_public, created_by
) VALUES 
(
  uuid_generate_v4(),
  'Empresas Solares Madrid',
  'Configuración para buscar empresas de energía solar en Madrid',
  '["solar", "energy"]',
  '["Madrid"]',
  true, true, false,
  'energía solar, paneles solares, instalación solar',
  true, true,
  (SELECT id FROM users WHERE email LIKE '%admin%' LIMIT 1)
),
(
  uuid_generate_v4(),
  'Constructoras Barcelona',
  'Configuración para buscar empresas constructoras en Barcelona',
  '["construction", "commercial"]',
  '["Barcelona"]',
  true, true, false,
  'construcción, edificios, obras',
  true, true,
  (SELECT id FROM users WHERE email LIKE '%admin%' LIMIT 1)
),
(
  uuid_generate_v4(),
  'Industrias Valencia',
  'Configuración para buscar empresas industriales en Valencia',
  '["industrial"]',
  '["Valencia"]',
  true, false, true,
  'industria, manufactura, producción',
  true, true,
  (SELECT id FROM users WHERE email LIKE '%admin%' LIMIT 1)
);

-- Log initialization
INSERT INTO system_logs (level, message, source, metadata) VALUES
('info', 'Search module initialized successfully', 'system', '{"module": "search", "version": "1.0", "tables": ["search_configurations", "search_history"]}');

COMMIT;
