-- =====================================
-- HISTORY MODULE - ACTIVITY HISTORY & LOGS
-- =====================================
-- This module provides views and functions for historical data

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================
-- HISTORY VIEWS
-- =====================================

-- View for comprehensive activity history
CREATE VIEW comprehensive_activity_history AS
SELECT 
  al.id,
  al.user_id,
  u.full_name as user_name,
  u.email as user_email,
  al.activity_type,
  al.action,
  al.description,
  al.resource_type,
  al.resource_id,
  al.timestamp,
  al.ip_address,
  al.user_agent,
  al.before_data,
  al.after_data,
  al.changes,
  al.execution_time_ms,
  al.response_status
FROM activity_logs al
LEFT JOIN user_profiles u ON al.user_id = u.id
ORDER BY al.timestamp DESC;

-- View for campaign history
CREATE VIEW campaign_history AS
SELECT 
  c.id as campaign_id,
  c.name as campaign_name,
  c.status,
  c.created_at,
  c.started_at,
  c.completed_at,
  c.total_recipients,
  c.emails_sent,
  c.emails_delivered,
  c.emails_opened,
  c.emails_clicked,
  c.open_rate,
  c.click_rate,
  u.full_name as created_by_name,
  t.name as template_name,
  CASE 
    WHEN c.status = 'completed' THEN 'success'
    WHEN c.status = 'failed' THEN 'error' 
    WHEN c.status = 'cancelled' THEN 'warning'
    ELSE 'info'
  END as status_type
FROM campaigns c
LEFT JOIN user_profiles u ON c.created_by = u.id
LEFT JOIN email_templates t ON c.template_id = t.id
ORDER BY c.created_at DESC;

-- View for search history with results
CREATE VIEW search_history_detailed AS
SELECT 
  sh.id,
  sh.user_id,
  u.full_name as user_name,
  sh.query_name,
  sh.search_parameters,
  sh.filters_applied,
  sh.status,
  sh.total_results,
  sh.valid_results,
  sh.duplicate_results,
  sh.execution_time_ms,
  sh.pages_scraped,
  sh.websites_searched,
  sh.started_at,
  sh.completed_at,
  sh.error_message,
  sc.name as config_name,
  CASE 
    WHEN sh.status = 'completed' THEN 'success'
    WHEN sh.status = 'failed' THEN 'error'
    WHEN sh.status = 'cancelled' THEN 'warning'
    ELSE 'info'
  END as status_type,
  CASE 
    WHEN sh.completed_at IS NOT NULL THEN 
      EXTRACT(EPOCH FROM (sh.completed_at - sh.started_at))::INTEGER
    ELSE NULL
  END as duration_seconds
FROM search_history sh
LEFT JOIN user_profiles u ON sh.user_id = u.id
LEFT JOIN search_configurations sc ON sh.search_config_id = sc.id
ORDER BY sh.started_at DESC;

-- =====================================
-- NOTE: Session and authentication history are managed by Supabase Auth
-- These views are not needed with Supabase self-hosted
-- =====================================

-- =====================================
-- HISTORY FUNCTIONS
-- =====================================

-- Function to get user activity timeline
CREATE OR REPLACE FUNCTION get_user_activity_timeline(
  p_user_id UUID,
  p_days_back INTEGER DEFAULT 30,
  p_limit INTEGER DEFAULT 100
)
RETURNS TABLE (
  activity_id UUID,
  activity_time TIMESTAMP,
  activity_type activity_type,
  action VARCHAR(255),
  description TEXT,
  resource_type VARCHAR(100),
  resource_name TEXT,
  details JSONB
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    al.id,
    al.timestamp,
    al.activity_type,
    al.action,
    al.description,
    al.resource_type,
    CASE 
      WHEN al.resource_type = 'campaigns' THEN c.name
      WHEN al.resource_type = 'leads' THEN l.company_name
      WHEN al.resource_type = 'users' THEN u2.full_name
      WHEN al.resource_type = 'email_templates' THEN et.name
      ELSE al.resource_id::TEXT
    END as resource_name,
    jsonb_build_object(
      'ip_address', al.ip_address,
      'execution_time_ms', al.execution_time_ms,
      'changes', al.changes
    ) as details
  FROM activity_logs al
  LEFT JOIN campaigns c ON al.resource_type = 'campaigns' AND al.resource_id = c.id
  LEFT JOIN leads l ON al.resource_type = 'leads' AND al.resource_id = l.id
  LEFT JOIN user_profiles u2 ON al.resource_type = 'users' AND al.resource_id = u2.id
  LEFT JOIN email_templates et ON al.resource_type = 'email_templates' AND al.resource_id = et.id
  WHERE al.user_id = p_user_id
    AND al.timestamp >= CURRENT_DATE - (p_days_back || ' days')::INTERVAL
  ORDER BY al.timestamp DESC
  LIMIT p_limit;
END;
$$ language 'plpgsql';

-- Function to get campaign execution history
CREATE OR REPLACE FUNCTION get_campaign_execution_history(p_campaign_id UUID)
RETURNS TABLE (
  event_time TIMESTAMP,
  event_type VARCHAR(50),
  event_description TEXT,
  recipient_email VARCHAR(255),
  status email_status,
  details JSONB
) AS $$
BEGIN
  RETURN QUERY
  -- Campaign level events
  SELECT 
    c.created_at,
    'campaign_created'::VARCHAR(50),
    'Campaign was created'::TEXT,
    NULL::VARCHAR(255),
    NULL::email_status,
    jsonb_build_object('template', t.name, 'created_by', u.full_name)
  FROM campaigns c
  LEFT JOIN email_templates t ON c.template_id = t.id
  LEFT JOIN user_profiles u ON c.created_by = u.id
  WHERE c.id = p_campaign_id
  
  UNION ALL
  
  SELECT 
    c.started_at,
    'campaign_started'::VARCHAR(50),
    'Campaign execution started'::TEXT,
    NULL::VARCHAR(255),
    NULL::email_status,
    jsonb_build_object('total_recipients', c.total_recipients)
  FROM campaigns c
  WHERE c.id = p_campaign_id AND c.started_at IS NOT NULL
  
  UNION ALL
  
  SELECT 
    c.completed_at,
    'campaign_completed'::VARCHAR(50),
    'Campaign execution completed'::TEXT,
    NULL::VARCHAR(255),
    NULL::email_status,
    jsonb_build_object(
      'emails_sent', c.emails_sent,
      'open_rate', c.open_rate,
      'click_rate', c.click_rate
    )
  FROM campaigns c
  WHERE c.id = p_campaign_id AND c.completed_at IS NOT NULL
  
  UNION ALL
  
  -- Recipient level events
  SELECT 
    cr.sent_at,
    'email_sent'::VARCHAR(50),
    'Email sent to recipient'::TEXT,
    cr.email_address,
    cr.status,
    jsonb_build_object('retry_count', cr.retry_count)
  FROM campaign_recipients cr
  WHERE cr.campaign_id = p_campaign_id AND cr.sent_at IS NOT NULL
  
  ORDER BY event_time;
END;
$$ language 'plpgsql';

-- Function to get search performance history
CREATE OR REPLACE FUNCTION get_search_performance_history(
  p_user_id UUID DEFAULT NULL,
  p_days_back INTEGER DEFAULT 30
)
RETURNS TABLE (
  search_date DATE,
  total_searches INTEGER,
  successful_searches INTEGER,
  failed_searches INTEGER,
  avg_results_per_search DECIMAL(8,2),
  avg_execution_time_seconds DECIMAL(8,2),
  success_rate DECIMAL(5,2)
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    DATE(sh.started_at) as search_date,
    COUNT(*)::INTEGER as total_searches,
    COUNT(*) FILTER (WHERE sh.status = 'completed')::INTEGER as successful_searches,
    COUNT(*) FILTER (WHERE sh.status = 'failed')::INTEGER as failed_searches,
    ROUND(AVG(sh.total_results), 2) as avg_results_per_search,
    ROUND(AVG(sh.execution_time_ms / 1000.0), 2) as avg_execution_time_seconds,
    ROUND(
      COUNT(*) FILTER (WHERE sh.status = 'completed')::DECIMAL / COUNT(*) * 100, 
      2
    ) as success_rate
  FROM search_history sh
  WHERE sh.started_at >= CURRENT_DATE - (p_days_back || ' days')::INTERVAL
    AND (p_user_id IS NULL OR sh.user_id = p_user_id)
  GROUP BY DATE(sh.started_at)
  ORDER BY search_date DESC;
END;
$$ language 'plpgsql';

-- Function to export activity history as JSON
CREATE OR REPLACE FUNCTION export_user_history_json(
  p_user_id UUID,
  p_start_date DATE DEFAULT CURRENT_DATE - INTERVAL '90 days',
  p_end_date DATE DEFAULT CURRENT_DATE
)
RETURNS JSON AS $$
DECLARE
  result JSON;
BEGIN
  SELECT json_build_object(
    'user_id', p_user_id,
    'export_period', json_build_object(
      'start_date', p_start_date,
      'end_date', p_end_date
    ),
    'activities', json_agg(
      json_build_object(
        'timestamp', al.timestamp,
        'activity_type', al.activity_type,
        'action', al.action,
        'description', al.description,
        'resource_type', al.resource_type,
        'resource_id', al.resource_id,
        'ip_address', al.ip_address,
        'changes', al.changes
      ) ORDER BY al.timestamp DESC
    ),
    'summary', json_build_object(
      'total_activities', COUNT(*),
      'activity_types', json_object_agg(
        al.activity_type, 
        COUNT(*)
      )
    )
  ) INTO result
  FROM activity_logs al
  WHERE al.user_id = p_user_id
    AND DATE(al.timestamp) BETWEEN p_start_date AND p_end_date;
  
  RETURN result;
END;
$$ language 'plpgsql';

-- =====================================
-- HISTORY CLEANUP FUNCTIONS
-- =====================================

-- Function to archive old history data
CREATE OR REPLACE FUNCTION archive_old_history(p_days_to_keep INTEGER DEFAULT 365)
RETURNS TABLE (
  table_name TEXT,
  archived_records INTEGER
) AS $$
DECLARE
  cutoff_date DATE;
BEGIN
  cutoff_date := CURRENT_DATE - (p_days_to_keep || ' days')::INTERVAL;
  
  -- Archive old activity logs (could be moved to separate archive table)
  -- For now, just return counts without deleting
  RETURN QUERY
  SELECT 
    'activity_logs'::TEXT,
    COUNT(*)::INTEGER
  FROM activity_logs 
  WHERE DATE(timestamp) < cutoff_date;
  
  -- Note: auth_logs are managed by Supabase and don't need archiving
  
  RETURN QUERY
  SELECT 
    'search_history'::TEXT,
    COUNT(*)::INTEGER
  FROM search_history 
  WHERE DATE(started_at) < cutoff_date;
  
  -- Note: In production, you might want to move old data to archive tables
  -- instead of deleting it completely
END;
$$ language 'plpgsql';

-- =====================================
-- HISTORY MATERIALIZED VIEWS
-- =====================================

-- Materialized view for monthly activity summary
CREATE MATERIALIZED VIEW monthly_activity_summary AS
SELECT 
  DATE_TRUNC('month', timestamp) as month,
  user_id,
  activity_type,
  COUNT(*) as activity_count,
  COUNT(DISTINCT DATE(timestamp)) as active_days
FROM activity_logs 
WHERE timestamp >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY DATE_TRUNC('month', timestamp), user_id, activity_type;

-- Create index on materialized view
CREATE INDEX idx_monthly_activity_summary_month_user ON monthly_activity_summary(month, user_id);

-- Function to refresh history materialized views
CREATE OR REPLACE FUNCTION refresh_history_views()
RETURNS VOID AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_activity_summary;
  
  -- Log the refresh
  INSERT INTO system_logs (level, message, source, metadata)
  VALUES ('info', 'History views refreshed', 'history', 
          json_build_object('refreshed_at', now(), 'view', 'monthly_activity_summary'));
END;
$$ language 'plpgsql';

-- Log initialization
INSERT INTO system_logs (level, message, source, metadata) VALUES
('info', 'History module initialized successfully', 'system', '{"module": "history", "version": "1.0", "type": "views_and_functions"}');

COMMIT;
