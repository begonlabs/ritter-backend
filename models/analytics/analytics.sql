-- =====================================
-- ANALYTICS MODULE - METRICS & PERFORMANCE
-- =====================================
-- Tables: analytics_data, dashboard_metrics, scraping_stats, website_sources

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================
-- ANALYTICS DATA
-- =====================================

-- Analytics data table (general metrics storage)
CREATE TABLE analytics_data (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  date DATE NOT NULL,
  metric_type VARCHAR(100) NOT NULL, -- searches, campaigns, leads, exports, etc.
  metric_name VARCHAR(255) NOT NULL,
  
  -- Metric Values
  count_value INTEGER DEFAULT 0,
  sum_value DECIMAL(15,2) DEFAULT 0.00,
  avg_value DECIMAL(15,2) DEFAULT 0.00,
  min_value DECIMAL(15,2) DEFAULT 0.00,
  max_value DECIMAL(15,2) DEFAULT 0.00,
  
  -- Dimensions
  user_id UUID,
  campaign_id UUID,
  search_history_id UUID,
  
  -- Additional Context
  dimensions JSONB DEFAULT '{}',
  
  -- System Fields
  created_at TIMESTAMP DEFAULT now()
);

-- =====================================
-- DASHBOARD METRICS
-- =====================================

-- Dashboard stats aggregated for performance
CREATE TABLE dashboard_metrics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  date DATE NOT NULL,
  period_type VARCHAR(50) NOT NULL, -- daily, weekly, monthly, yearly
  
  -- Core Stats (matching frontend DashboardStats interface)
  total_leads INTEGER DEFAULT 0,
  total_campaigns INTEGER DEFAULT 0,
  total_searches INTEGER DEFAULT 0,
  average_open_rate DECIMAL(5,2) DEFAULT 0.00,
  
  -- Performance Metrics
  leads_quality_score DECIMAL(5,2) DEFAULT 0.00,
  campaign_success_rate DECIMAL(5,2) DEFAULT 0.00,
  search_efficiency DECIMAL(5,2) DEFAULT 0.00,
  cost_per_lead DECIMAL(10,2) DEFAULT 0.00,
  roi_percentage DECIMAL(8,2) DEFAULT 0.00,
  
  -- Trend data (vs previous period)
  leads_trend_percentage DECIMAL(5,2) DEFAULT 0.00,
  campaigns_trend_percentage DECIMAL(5,2) DEFAULT 0.00,
  searches_trend_percentage DECIMAL(5,2) DEFAULT 0.00,
  open_rate_trend_percentage DECIMAL(5,2) DEFAULT 0.00,
  
  -- Money metrics (for ScrapingStats component)
  estimated_money_saved DECIMAL(12,2) DEFAULT 0.00,
  cost_savings_percentage DECIMAL(5,2) DEFAULT 0.00,
  
  -- System fields
  calculated_at TIMESTAMP DEFAULT now()
);

-- =====================================
-- SCRAPING STATISTICS
-- =====================================

-- Scraping stats table
CREATE TABLE scraping_stats (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,
  search_history_id UUID,
  
  -- Scraping Performance
  session_start TIMESTAMP DEFAULT now(),
  session_end TIMESTAMP,
  duration_minutes INTEGER,
  
  -- Results
  pages_visited INTEGER DEFAULT 0,
  leads_found INTEGER DEFAULT 0,
  leads_extracted INTEGER DEFAULT 0,
  valid_leads INTEGER DEFAULT 0,
  duplicate_leads INTEGER DEFAULT 0,
  
  -- Quality Metrics
  success_rate DECIMAL(5,2) DEFAULT 0.00,
  extraction_rate DECIMAL(5,2) DEFAULT 0.00,
  validation_rate DECIMAL(5,2) DEFAULT 0.00,
  
  -- Error Tracking
  errors_encountered INTEGER DEFAULT 0,
  warnings_count INTEGER DEFAULT 0,
  error_details JSONB DEFAULT '[]',
  
  -- Performance Metrics
  avg_page_load_time INTEGER, -- milliseconds
  requests_per_minute DECIMAL(8,2),
  bandwidth_used_mb DECIMAL(10,2)
);

-- =====================================
-- WEBSITE SOURCES PERFORMANCE
-- =====================================

-- Website sources performance (for ScrapingStats topSources)
CREATE TABLE website_sources (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Website Details
  website_url VARCHAR(500) NOT NULL,
  website_name VARCHAR(255) NOT NULL,
  domain VARCHAR(255) NOT NULL,
  
  -- Performance Metrics
  total_leads_found INTEGER DEFAULT 0,
  total_searches INTEGER DEFAULT 0,
  success_rate DECIMAL(5,2) DEFAULT 0.00,
  average_leads_per_search DECIMAL(8,2) DEFAULT 0.00,
  
  -- Quality Metrics
  lead_quality_score DECIMAL(5,2) DEFAULT 0.00,
  validation_success_rate DECIMAL(5,2) DEFAULT 0.00,
  
  -- Performance Stats
  average_response_time_ms INTEGER DEFAULT 0,
  error_rate DECIMAL(5,2) DEFAULT 0.00,
  last_successful_scrape TIMESTAMP,
  
  -- Status and Configuration
  is_active BOOLEAN DEFAULT true,
  is_blocked BOOLEAN DEFAULT false,
  blocked_reason VARCHAR(255),
  blocked_until TIMESTAMP,
  
  -- Usage Statistics
  last_used_at TIMESTAMP,
  monthly_usage_count INTEGER DEFAULT 0,
  total_usage_count INTEGER DEFAULT 0,
  
  -- System Fields
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

-- =====================================
-- INDEXES FOR ANALYTICS MODULE
-- =====================================

-- Analytics data indexes
CREATE INDEX idx_analytics_data_date ON analytics_data(date);
CREATE INDEX idx_analytics_data_metric_type ON analytics_data(metric_type);
CREATE INDEX idx_analytics_data_metric_name ON analytics_data(metric_name);
CREATE INDEX idx_analytics_data_user_id ON analytics_data(user_id);
CREATE INDEX idx_analytics_data_campaign_id ON analytics_data(campaign_id);
CREATE INDEX idx_analytics_data_search_history_id ON analytics_data(search_history_id);
CREATE INDEX idx_analytics_data_date_metric_type_name ON analytics_data(date, metric_type, metric_name);
CREATE INDEX idx_analytics_data_date_user_metric ON analytics_data(date, user_id, metric_type);

-- Dashboard metrics indexes
CREATE INDEX idx_dashboard_metrics_date ON dashboard_metrics(date);
CREATE INDEX idx_dashboard_metrics_period_type ON dashboard_metrics(period_type);
CREATE UNIQUE INDEX idx_dashboard_metrics_date_period ON dashboard_metrics(date, period_type);
CREATE INDEX idx_dashboard_metrics_calculated_at ON dashboard_metrics(calculated_at);

-- Scraping stats indexes
CREATE INDEX idx_scraping_stats_user_id ON scraping_stats(user_id);
CREATE INDEX idx_scraping_stats_search_history_id ON scraping_stats(search_history_id);
CREATE INDEX idx_scraping_stats_session_start ON scraping_stats(session_start);
CREATE INDEX idx_scraping_stats_success_rate ON scraping_stats(success_rate);

-- Website sources indexes
CREATE UNIQUE INDEX idx_website_sources_domain ON website_sources(domain);
CREATE UNIQUE INDEX idx_website_sources_website_url ON website_sources(website_url);
CREATE INDEX idx_website_sources_is_active ON website_sources(is_active);
CREATE INDEX idx_website_sources_success_rate ON website_sources(success_rate);
CREATE INDEX idx_website_sources_total_leads_found ON website_sources(total_leads_found);
CREATE INDEX idx_website_sources_last_used_at ON website_sources(last_used_at);
CREATE INDEX idx_website_sources_domain_active ON website_sources(domain, is_active);
CREATE INDEX idx_website_sources_success_leads ON website_sources(success_rate, total_leads_found);

-- =====================================
-- FOREIGN KEY CONSTRAINTS
-- =====================================

-- Analytics data foreign keys
ALTER TABLE analytics_data ADD CONSTRAINT fk_analytics_data_user_id FOREIGN KEY (user_id) REFERENCES auth.users(id);
ALTER TABLE analytics_data ADD CONSTRAINT fk_analytics_data_campaign_id FOREIGN KEY (campaign_id) REFERENCES campaigns(id);
ALTER TABLE analytics_data ADD CONSTRAINT fk_analytics_data_search_history_id FOREIGN KEY (search_history_id) REFERENCES search_history(id);

-- Scraping stats foreign keys
ALTER TABLE scraping_stats ADD CONSTRAINT fk_scraping_stats_user_id FOREIGN KEY (user_id) REFERENCES auth.users(id);
ALTER TABLE scraping_stats ADD CONSTRAINT fk_scraping_stats_search_history_id FOREIGN KEY (search_history_id) REFERENCES search_history(id);

-- =====================================
-- TRIGGERS FOR ANALYTICS MODULE
-- =====================================

-- Trigger to update updated_at timestamp
CREATE TRIGGER update_website_sources_updated_at 
  BEFORE UPDATE ON website_sources 
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================
-- FUNCTIONS FOR ANALYTICS MODULE
-- =====================================

-- Function to calculate dashboard metrics for a specific date
CREATE OR REPLACE FUNCTION calculate_dashboard_metrics(p_date DATE DEFAULT CURRENT_DATE)
RETURNS VOID AS $$
DECLARE
  prev_date DATE;
  current_stats RECORD;
  prev_stats RECORD;
BEGIN
  prev_date := p_date - INTERVAL '1 day';
  
  -- Calculate current day stats
  SELECT 
    COALESCE(COUNT(DISTINCT l.id), 0) as total_leads,
    COALESCE(COUNT(DISTINCT c.id), 0) as total_campaigns,
    COALESCE(COUNT(DISTINCT sh.id), 0) as total_searches,
    COALESCE(ROUND(AVG(c.open_rate), 2), 0.00) as average_open_rate,
    COALESCE(ROUND(AVG(l.data_quality_score), 2), 0.00) as leads_quality_score,
    COALESCE(ROUND(AVG(CASE WHEN c.status = 'completed' THEN 100.0 ELSE 0.0 END), 2), 0.00) as campaign_success_rate,
    COALESCE(ROUND(AVG(CASE WHEN sh.status = 'completed' THEN 100.0 ELSE 0.0 END), 2), 0.00) as search_efficiency
  INTO current_stats
  FROM leads l
  FULL OUTER JOIN campaigns c ON DATE(c.created_at) = p_date
  FULL OUTER JOIN search_history sh ON DATE(sh.started_at) = p_date
  WHERE DATE(l.created_at) = p_date OR DATE(c.created_at) = p_date OR DATE(sh.started_at) = p_date;
  
  -- Calculate previous day stats for trends
  SELECT 
    COALESCE(COUNT(DISTINCT l.id), 0) as total_leads,
    COALESCE(COUNT(DISTINCT c.id), 0) as total_campaigns,
    COALESCE(COUNT(DISTINCT sh.id), 0) as total_searches,
    COALESCE(ROUND(AVG(c.open_rate), 2), 0.00) as average_open_rate
  INTO prev_stats
  FROM leads l
  FULL OUTER JOIN campaigns c ON DATE(c.created_at) = prev_date
  FULL OUTER JOIN search_history sh ON DATE(sh.started_at) = prev_date
  WHERE DATE(l.created_at) = prev_date OR DATE(c.created_at) = prev_date OR DATE(sh.started_at) = prev_date;
  
  -- Insert or update dashboard metrics
  INSERT INTO dashboard_metrics (
    date, period_type, total_leads, total_campaigns, total_searches, average_open_rate,
    leads_quality_score, campaign_success_rate, search_efficiency,
    leads_trend_percentage, campaigns_trend_percentage, searches_trend_percentage, open_rate_trend_percentage
  ) VALUES (
    p_date, 'daily',
    COALESCE(current_stats.total_leads, 0),
    COALESCE(current_stats.total_campaigns, 0), 
    COALESCE(current_stats.total_searches, 0),
    COALESCE(current_stats.average_open_rate, 0.00),
    COALESCE(current_stats.leads_quality_score, 0.00),
    COALESCE(current_stats.campaign_success_rate, 0.00),
    COALESCE(current_stats.search_efficiency, 0.00),
    -- Calculate trend percentages
    CASE WHEN prev_stats.total_leads > 0 THEN 
      ROUND(((current_stats.total_leads - prev_stats.total_leads)::DECIMAL / prev_stats.total_leads) * 100, 2)
    ELSE 0.00 END,
    CASE WHEN prev_stats.total_campaigns > 0 THEN 
      ROUND(((current_stats.total_campaigns - prev_stats.total_campaigns)::DECIMAL / prev_stats.total_campaigns) * 100, 2)
    ELSE 0.00 END,
    CASE WHEN prev_stats.total_searches > 0 THEN 
      ROUND(((current_stats.total_searches - prev_stats.total_searches)::DECIMAL / prev_stats.total_searches) * 100, 2)
    ELSE 0.00 END,
    CASE WHEN prev_stats.average_open_rate > 0 THEN 
      ROUND(((current_stats.average_open_rate - prev_stats.average_open_rate) / prev_stats.average_open_rate) * 100, 2)
    ELSE 0.00 END
  )
  ON CONFLICT (date, period_type) 
  DO UPDATE SET
    total_leads = EXCLUDED.total_leads,
    total_campaigns = EXCLUDED.total_campaigns,
    total_searches = EXCLUDED.total_searches,
    average_open_rate = EXCLUDED.average_open_rate,
    leads_quality_score = EXCLUDED.leads_quality_score,
    campaign_success_rate = EXCLUDED.campaign_success_rate,
    search_efficiency = EXCLUDED.search_efficiency,
    leads_trend_percentage = EXCLUDED.leads_trend_percentage,
    campaigns_trend_percentage = EXCLUDED.campaigns_trend_percentage,
    searches_trend_percentage = EXCLUDED.searches_trend_percentage,
    open_rate_trend_percentage = EXCLUDED.open_rate_trend_percentage,
    calculated_at = now();
END;
$$ language 'plpgsql';

-- Function to get analytics summary for a date range
CREATE OR REPLACE FUNCTION get_analytics_summary(
  p_start_date DATE DEFAULT CURRENT_DATE - INTERVAL '30 days',
  p_end_date DATE DEFAULT CURRENT_DATE,
  p_user_id UUID DEFAULT NULL
)
RETURNS TABLE (
  metric_type VARCHAR(100),
  metric_name VARCHAR(255),
  total_count BIGINT,
  total_sum DECIMAL(15,2),
  average_value DECIMAL(15,2),
  trend_direction VARCHAR(10)
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    ad.metric_type,
    ad.metric_name,
    SUM(ad.count_value) as total_count,
    SUM(ad.sum_value) as total_sum,
    ROUND(AVG(ad.avg_value), 2) as average_value,
    CASE 
      WHEN AVG(ad.avg_value) > LAG(AVG(ad.avg_value)) OVER (PARTITION BY ad.metric_type, ad.metric_name ORDER BY ad.date) THEN 'up'
      WHEN AVG(ad.avg_value) < LAG(AVG(ad.avg_value)) OVER (PARTITION BY ad.metric_type, ad.metric_name ORDER BY ad.date) THEN 'down'
      ELSE 'stable'
    END as trend_direction
  FROM analytics_data ad
  WHERE ad.date BETWEEN p_start_date AND p_end_date
    AND (p_user_id IS NULL OR ad.user_id = p_user_id)
  GROUP BY ad.metric_type, ad.metric_name
  ORDER BY ad.metric_type, total_count DESC;
END;
$$ language 'plpgsql';

-- Function to update website source performance
CREATE OR REPLACE FUNCTION update_website_source_stats(
  p_domain VARCHAR(255),
  p_leads_found INTEGER,
  p_session_success BOOLEAN DEFAULT true
)
RETURNS VOID AS $$
BEGIN
  INSERT INTO website_sources (website_url, website_name, domain, total_leads_found, total_searches, last_used_at)
  VALUES (
    'https://' || p_domain,
    p_domain,
    p_domain,
    p_leads_found,
    1,
    now()
  )
  ON CONFLICT (domain) 
  DO UPDATE SET
    total_leads_found = website_sources.total_leads_found + p_leads_found,
    total_searches = website_sources.total_searches + 1,
    success_rate = ROUND(
      (website_sources.total_searches * website_sources.success_rate / 100.0 + 
       CASE WHEN p_session_success THEN 1 ELSE 0 END) / 
      (website_sources.total_searches + 1) * 100, 2
    ),
    average_leads_per_search = ROUND(
      (website_sources.total_leads_found + p_leads_found)::DECIMAL / 
      (website_sources.total_searches + 1), 2
    ),
    last_used_at = now(),
    monthly_usage_count = website_sources.monthly_usage_count + 1,
    total_usage_count = website_sources.total_usage_count + 1,
    updated_at = now();
END;
$$ language 'plpgsql';

-- =====================================
-- VIEWS FOR ANALYTICS MODULE
-- =====================================

-- View for recent dashboard metrics
CREATE VIEW recent_dashboard_metrics AS
SELECT 
  date, period_type, total_leads, total_campaigns, total_searches,
  average_open_rate, leads_quality_score, campaign_success_rate, search_efficiency,
  leads_trend_percentage, campaigns_trend_percentage, searches_trend_percentage,
  estimated_money_saved, cost_savings_percentage, calculated_at
FROM dashboard_metrics 
WHERE period_type = 'daily'
ORDER BY date DESC
LIMIT 30;

-- View for top performing websites
CREATE VIEW top_website_sources AS
SELECT 
  website_name, domain, total_leads_found, total_searches,
  success_rate, average_leads_per_search, lead_quality_score,
  validation_success_rate, last_used_at
FROM website_sources 
WHERE is_active = true
ORDER BY total_leads_found DESC, success_rate DESC
LIMIT 20;

-- View for scraping performance summary
CREATE VIEW scraping_performance_summary AS
SELECT 
  DATE(session_start) as scraping_date,
  COUNT(*) as total_sessions,
  AVG(duration_minutes) as avg_duration_minutes,
  SUM(leads_found) as total_leads_found,
  SUM(valid_leads) as total_valid_leads,
  ROUND(AVG(success_rate), 2) as avg_success_rate,
  ROUND(AVG(extraction_rate), 2) as avg_extraction_rate,
  ROUND(AVG(validation_rate), 2) as avg_validation_rate
FROM scraping_stats 
GROUP BY DATE(session_start)
ORDER BY scraping_date DESC;

-- =====================================
-- INITIAL DATA FOR ANALYTICS MODULE
-- =====================================

-- Insert initial website sources
INSERT INTO website_sources (
  website_url, website_name, domain, total_leads_found, total_searches, 
  success_rate, average_leads_per_search, is_active
) VALUES 
('https://páginas-amarillas.es', 'Páginas Amarillas', 'páginas-amarillas.es', 0, 0, 0.00, 0.00, true),
('https://empresite.eleconomista.es', 'Empresite', 'empresite.eleconomista.es', 0, 0, 0.00, 0.00, true),
('https://directorio.codigocif.es', 'Código CIF', 'directorio.codigocif.es', 0, 0, 0.00, 0.00, true),
('https://guiaempresarial.expansion.com', 'Guía Empresarial', 'guiaempresarial.expansion.com', 0, 0, 0.00, 0.00, true);

-- Calculate initial dashboard metrics for today
SELECT calculate_dashboard_metrics(CURRENT_DATE);

-- Log initialization
INSERT INTO system_logs (level, message, source, metadata) VALUES
('info', 'Analytics module initialized successfully', 'system', '{"module": "analytics", "version": "1.0", "tables": ["analytics_data", "dashboard_metrics", "scraping_stats", "website_sources"]}');

COMMIT;
