-- =====================================
-- DASHBOARD MODULE - DASHBOARD VIEWS & AGGREGATIONS
-- =====================================
-- This module primarily uses data from other modules and provides views and functions

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================
-- DASHBOARD VIEWS
-- =====================================

-- View for dashboard overview stats
CREATE VIEW dashboard_overview AS
SELECT 
  'overview' as section,
  COUNT(DISTINCT l.id) as total_leads,
  COUNT(DISTINCT c.id) as total_campaigns,
  COUNT(DISTINCT sh.id) as total_searches,
  COUNT(DISTINCT u.id) as total_users,
  COALESCE(ROUND(AVG(c.open_rate), 2), 0.00) as avg_open_rate,
  COALESCE(ROUND(AVG(c.click_rate), 2), 0.00) as avg_click_rate,
  COALESCE(ROUND(AVG(l.data_quality_score), 2), 0.00) as avg_lead_quality
FROM leads l
CROSS JOIN campaigns c 
CROSS JOIN search_history sh
CROSS JOIN users u
WHERE u.status = 'active';

-- View for recent activity feed
CREATE VIEW recent_activity_feed AS
SELECT 
  al.id,
  al.user_id,
  u.full_name as user_name,
  al.activity_type,
  al.action,
  al.description,
  al.resource_type,
  al.resource_id,
  al.timestamp,
  al.ip_address
FROM activity_logs al
LEFT JOIN users u ON al.user_id = u.id
ORDER BY al.timestamp DESC
LIMIT 50;

-- View for campaign performance dashboard
CREATE VIEW campaign_performance_dashboard AS
SELECT 
  c.id,
  c.name,
  c.status,
  c.total_recipients,
  c.emails_sent,
  c.emails_delivered,
  c.emails_opened,
  c.emails_clicked,
  c.open_rate,
  c.click_rate,
  c.bounce_rate,
  c.created_at,
  c.completed_at,
  t.name as template_name,
  u.full_name as created_by_name
FROM campaigns c
LEFT JOIN email_templates t ON c.template_id = t.id
LEFT JOIN users u ON c.created_by = u.id
ORDER BY c.created_at DESC;

-- View for lead quality distribution
CREATE VIEW lead_quality_distribution AS
SELECT 
  data_quality_score,
  COUNT(*) as lead_count,
  ROUND(COUNT(*)::DECIMAL / (SELECT COUNT(*) FROM leads) * 100, 2) as percentage
FROM leads 
GROUP BY data_quality_score
ORDER BY data_quality_score;

-- View for search success rates
CREATE VIEW search_success_rates AS
SELECT 
  DATE(started_at) as search_date,
  COUNT(*) as total_searches,
  COUNT(*) FILTER (WHERE status = 'completed') as successful_searches,
  COUNT(*) FILTER (WHERE status = 'failed') as failed_searches,
  ROUND(COUNT(*) FILTER (WHERE status = 'completed')::DECIMAL / COUNT(*) * 100, 2) as success_rate,
  SUM(total_results) as total_leads_found,
  ROUND(AVG(execution_time_ms), 2) as avg_execution_time_ms
FROM search_history
WHERE started_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(started_at)
ORDER BY search_date DESC;

-- =====================================
-- DASHBOARD FUNCTIONS
-- =====================================

-- Function to get dashboard summary for a specific period
CREATE OR REPLACE FUNCTION get_dashboard_summary(
  p_start_date DATE DEFAULT CURRENT_DATE - INTERVAL '30 days',
  p_end_date DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
  total_leads BIGINT,
  total_campaigns BIGINT,
  total_searches BIGINT,
  active_users BIGINT,
  avg_open_rate DECIMAL(5,2),
  avg_click_rate DECIMAL(5,2),
  avg_lead_quality DECIMAL(5,2),
  leads_growth_rate DECIMAL(5,2),
  campaigns_growth_rate DECIMAL(5,2),
  searches_growth_rate DECIMAL(5,2)
) AS $$
DECLARE
  prev_period_start DATE;
  prev_period_end DATE;
  current_period RECORD;
  previous_period RECORD;
BEGIN
  -- Calculate previous period dates
  prev_period_end := p_start_date - INTERVAL '1 day';
  prev_period_start := prev_period_end - (p_end_date - p_start_date);
  
  -- Get current period stats
  SELECT 
    COUNT(DISTINCT l.id) as leads,
    COUNT(DISTINCT c.id) as campaigns,
    COUNT(DISTINCT sh.id) as searches,
    COUNT(DISTINCT u.id) as users,
    COALESCE(ROUND(AVG(c.open_rate), 2), 0.00) as open_rate,
    COALESCE(ROUND(AVG(c.click_rate), 2), 0.00) as click_rate,
    COALESCE(ROUND(AVG(l.data_quality_score), 2), 0.00) as quality
  INTO current_period
  FROM leads l
  FULL OUTER JOIN campaigns c ON DATE(c.created_at) BETWEEN p_start_date AND p_end_date
  FULL OUTER JOIN search_history sh ON DATE(sh.started_at) BETWEEN p_start_date AND p_end_date
  FULL OUTER JOIN users u ON u.status = 'active' AND DATE(u.created_at) BETWEEN p_start_date AND p_end_date
  WHERE DATE(l.created_at) BETWEEN p_start_date AND p_end_date;
  
  -- Get previous period stats for growth calculation
  SELECT 
    COUNT(DISTINCT l.id) as leads,
    COUNT(DISTINCT c.id) as campaigns,
    COUNT(DISTINCT sh.id) as searches
  INTO previous_period
  FROM leads l
  FULL OUTER JOIN campaigns c ON DATE(c.created_at) BETWEEN prev_period_start AND prev_period_end
  FULL OUTER JOIN search_history sh ON DATE(sh.started_at) BETWEEN prev_period_start AND prev_period_end
  WHERE DATE(l.created_at) BETWEEN prev_period_start AND prev_period_end;
  
  RETURN QUERY
  SELECT 
    COALESCE(current_period.leads, 0),
    COALESCE(current_period.campaigns, 0),
    COALESCE(current_period.searches, 0),
    COALESCE(current_period.users, 0),
    COALESCE(current_period.open_rate, 0.00),
    COALESCE(current_period.click_rate, 0.00),
    COALESCE(current_period.quality, 0.00),
    -- Growth rates
    CASE WHEN previous_period.leads > 0 THEN 
      ROUND(((current_period.leads - previous_period.leads)::DECIMAL / previous_period.leads) * 100, 2)
    ELSE 0.00 END,
    CASE WHEN previous_period.campaigns > 0 THEN 
      ROUND(((current_period.campaigns - previous_period.campaigns)::DECIMAL / previous_period.campaigns) * 100, 2)
    ELSE 0.00 END,
    CASE WHEN previous_period.searches > 0 THEN 
      ROUND(((current_period.searches - previous_period.searches)::DECIMAL / previous_period.searches) * 100, 2)
    ELSE 0.00 END;
END;
$$ language 'plpgsql';

-- Function to get user activity summary
CREATE OR REPLACE FUNCTION get_user_activity_summary(p_user_id UUID DEFAULT NULL)
RETURNS TABLE (
  user_id UUID,
  user_name VARCHAR(255),
  total_searches BIGINT,
  total_campaigns BIGINT,
  total_leads_found BIGINT,
  last_activity TIMESTAMP,
  favorite_activity VARCHAR(255)
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    u.id,
    u.full_name,
    COUNT(DISTINCT sh.id) as searches,
    COUNT(DISTINCT c.id) as campaigns,
    COALESCE(SUM(sh.total_results), 0) as leads_found,
    MAX(GREATEST(sh.started_at, c.created_at, al.timestamp)) as last_activity,
    (
      SELECT al2.activity_type::VARCHAR(255)
      FROM activity_logs al2 
      WHERE al2.user_id = u.id 
      GROUP BY al2.activity_type 
      ORDER BY COUNT(*) DESC 
      LIMIT 1
    ) as favorite_activity
  FROM users u
  LEFT JOIN search_history sh ON u.id = sh.user_id
  LEFT JOIN campaigns c ON u.id = c.created_by
  LEFT JOIN activity_logs al ON u.id = al.user_id
  WHERE u.status = 'active'
    AND (p_user_id IS NULL OR u.id = p_user_id)
  GROUP BY u.id, u.full_name
  ORDER BY last_activity DESC;
END;
$$ language 'plpgsql';

-- Function to get top performing content
CREATE OR REPLACE FUNCTION get_top_performing_content()
RETURNS TABLE (
  content_type VARCHAR(50),
  content_name VARCHAR(255),
  performance_metric DECIMAL(10,2),
  usage_count INTEGER,
  last_used TIMESTAMP
) AS $$
BEGIN
  RETURN QUERY
  -- Top email templates
  SELECT 
    'email_template'::VARCHAR(50) as content_type,
    et.name as content_name,
    et.open_rate as performance_metric,
    et.usage_count,
    et.last_used_at as last_used
  FROM email_templates et
  WHERE et.status = 'active' AND et.usage_count > 0
  ORDER BY et.open_rate DESC, et.usage_count DESC
  LIMIT 5
  
  UNION ALL
  
  -- Top search configurations
  SELECT 
    'search_config'::VARCHAR(50) as content_type,
    sc.name as content_name,
    AVG(sh.total_results)::DECIMAL(10,2) as performance_metric,
    sc.usage_count,
    sc.last_used_at as last_used
  FROM search_configurations sc
  LEFT JOIN search_history sh ON sc.id = sh.search_config_id
  WHERE sc.usage_count > 0
  GROUP BY sc.id, sc.name, sc.usage_count, sc.last_used_at
  ORDER BY performance_metric DESC, sc.usage_count DESC
  LIMIT 5;
END;
$$ language 'plpgsql';

-- =====================================
-- DASHBOARD MATERIALIZED VIEWS (for performance)
-- =====================================

-- Materialized view for daily dashboard stats (refresh daily)
CREATE MATERIALIZED VIEW daily_dashboard_stats AS
SELECT 
  CURRENT_DATE as stats_date,
  COUNT(DISTINCT l.id) as total_leads,
  COUNT(DISTINCT c.id) as total_campaigns,
  COUNT(DISTINCT sh.id) as total_searches,
  COUNT(DISTINCT u.id) as active_users,
  COALESCE(ROUND(AVG(c.open_rate), 2), 0.00) as avg_open_rate,
  COALESCE(ROUND(AVG(c.click_rate), 2), 0.00) as avg_click_rate,
  COALESCE(ROUND(AVG(l.data_quality_score), 2), 0.00) as avg_lead_quality
FROM leads l
CROSS JOIN campaigns c 
CROSS JOIN search_history sh
CROSS JOIN users u
WHERE u.status = 'active';

-- Create index on materialized view
CREATE UNIQUE INDEX idx_daily_dashboard_stats_date ON daily_dashboard_stats(stats_date);

-- Function to refresh dashboard materialized views
CREATE OR REPLACE FUNCTION refresh_dashboard_stats()
RETURNS VOID AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY daily_dashboard_stats;
  
  -- Log the refresh
  INSERT INTO system_logs (level, message, source, metadata)
  VALUES ('info', 'Dashboard stats refreshed', 'dashboard', 
          json_build_object('refreshed_at', now(), 'view', 'daily_dashboard_stats'));
END;
$$ language 'plpgsql';

-- =====================================
-- DASHBOARD HELPER FUNCTIONS
-- =====================================

-- Function to get quick stats for dashboard widgets
CREATE OR REPLACE FUNCTION get_dashboard_widgets()
RETURNS TABLE (
  widget_name VARCHAR(50),
  widget_value TEXT,
  widget_change VARCHAR(20),
  widget_trend VARCHAR(10)
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    'total_leads'::VARCHAR(50),
    COUNT(*)::TEXT,
    '+' || COALESCE(
      ROUND(
        (COUNT(*) - LAG(COUNT(*)) OVER (ORDER BY DATE(created_at)))::DECIMAL / 
        NULLIF(LAG(COUNT(*)) OVER (ORDER BY DATE(created_at)), 0) * 100, 1
      ), 0
    )::TEXT || '%',
    CASE WHEN COUNT(*) > LAG(COUNT(*)) OVER (ORDER BY DATE(created_at)) THEN 'up' ELSE 'down' END::VARCHAR(10)
  FROM leads
  WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
  GROUP BY DATE(created_at)
  ORDER BY DATE(created_at) DESC
  LIMIT 1;
END;
$$ language 'plpgsql';

-- Log initialization
INSERT INTO system_logs (level, message, source, metadata) VALUES
('info', 'Dashboard module initialized successfully', 'system', '{"module": "dashboard", "version": "1.0", "type": "views_and_functions"}');

COMMIT;
