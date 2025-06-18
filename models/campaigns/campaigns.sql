-- =====================================
-- CAMPAIGNS MODULE - EMAIL CAMPAIGNS & TEMPLATES
-- =====================================
-- Tables: email_templates, template_variables, campaigns, campaign_recipients

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================
-- ENUMS USED BY CAMPAIGNS MODULE
-- =====================================

CREATE TYPE template_status AS ENUM (
  'active',
  'inactive',
  'archived'
);

CREATE TYPE campaign_status AS ENUM (
  'draft',
  'scheduled',
  'sending',
  'sent',
  'completed',
  'cancelled',
  'failed'
);

CREATE TYPE email_status AS ENUM (
  'pending',
  'sent',
  'delivered',
  'opened',
  'clicked',
  'bounced',
  'failed',
  'unsubscribed'
);

-- =====================================
-- EMAIL TEMPLATES SYSTEM
-- =====================================

-- Email templates table
CREATE TABLE email_templates (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  category VARCHAR(100),
  subject VARCHAR(500) NOT NULL,
  body_html TEXT NOT NULL, -- HTML template content
  body_text TEXT, -- Plain text version (optional)
  variables JSONB DEFAULT '[]', -- Available template variables
  preview_text VARCHAR(255),
  status template_status DEFAULT 'active',
  
  -- Usage Statistics
  usage_count INTEGER DEFAULT 0,
  success_rate DECIMAL(5,2) DEFAULT 0.00,
  open_rate DECIMAL(5,2) DEFAULT 0.00,
  click_rate DECIMAL(5,2) DEFAULT 0.00,
  
  -- System Fields
  created_by UUID NOT NULL,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now(),
  last_used_at TIMESTAMP
);

-- Template variables table (for dynamic content)
CREATE TABLE template_variables (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  template_id UUID NOT NULL,
  variable_name VARCHAR(100) NOT NULL,
  variable_type VARCHAR(50) NOT NULL, -- text, number, date, etc.
  default_value TEXT,
  is_required BOOLEAN DEFAULT false,
  description TEXT
);

-- =====================================
-- CAMPAIGNS SYSTEM
-- =====================================

-- Campaigns table
CREATE TABLE campaigns (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  template_id UUID NOT NULL,
  
  -- Campaign Configuration
  subject VARCHAR(500) NOT NULL,
  from_name VARCHAR(255) NOT NULL,
  from_email VARCHAR(255) NOT NULL,
  reply_to VARCHAR(255),
  
  -- Scheduling
  status campaign_status DEFAULT 'draft',
  scheduled_at TIMESTAMP,
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  
  -- Target Audience
  target_leads JSONB DEFAULT '[]', -- Array of lead IDs
  filters JSONB DEFAULT '{}', -- Search filters used
  total_recipients INTEGER DEFAULT 0,
  
  -- Campaign Results
  emails_sent INTEGER DEFAULT 0,
  emails_delivered INTEGER DEFAULT 0,
  emails_opened INTEGER DEFAULT 0,
  emails_clicked INTEGER DEFAULT 0,
  emails_bounced INTEGER DEFAULT 0,
  emails_unsubscribed INTEGER DEFAULT 0,
  
  -- Performance Metrics
  open_rate DECIMAL(5,2) DEFAULT 0.00,
  click_rate DECIMAL(5,2) DEFAULT 0.00,
  bounce_rate DECIMAL(5,2) DEFAULT 0.00,
  unsubscribe_rate DECIMAL(5,2) DEFAULT 0.00,
  conversion_rate DECIMAL(5,2) DEFAULT 0.00,
  
  -- System Fields
  created_by UUID NOT NULL,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now(),
  
  -- Configuration & Settings
  settings JSONB DEFAULT '{}',
  metadata JSONB DEFAULT '{}'
);

-- Campaign recipients table (individual email tracking)
CREATE TABLE campaign_recipients (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  campaign_id UUID NOT NULL,
  lead_id UUID NOT NULL,
  
  -- Email Details
  email_address VARCHAR(255) NOT NULL,
  personalization_data JSONB DEFAULT '{}',
  
  -- Delivery Status
  status email_status DEFAULT 'pending',
  sent_at TIMESTAMP,
  delivered_at TIMESTAMP,
  opened_at TIMESTAMP,
  first_opened_at TIMESTAMP,
  clicked_at TIMESTAMP,
  first_clicked_at TIMESTAMP,
  bounced_at TIMESTAMP,
  unsubscribed_at TIMESTAMP,
  
  -- Engagement Metrics
  open_count INTEGER DEFAULT 0,
  click_count INTEGER DEFAULT 0,
  last_activity_at TIMESTAMP,
  
  -- Error Handling
  error_message TEXT,
  retry_count INTEGER DEFAULT 0,
  max_retries INTEGER DEFAULT 3,
  
  -- Metadata
  metadata JSONB DEFAULT '{}'
);

-- =====================================
-- INDEXES FOR CAMPAIGNS MODULE
-- =====================================

-- Email templates indexes
CREATE INDEX idx_email_templates_name ON email_templates(name);
CREATE INDEX idx_email_templates_category ON email_templates(category);
CREATE INDEX idx_email_templates_status ON email_templates(status);
CREATE INDEX idx_email_templates_created_by ON email_templates(created_by);
CREATE INDEX idx_email_templates_usage_count ON email_templates(usage_count);
CREATE INDEX idx_email_templates_created_at ON email_templates(created_at);

-- Template variables indexes
CREATE INDEX idx_template_variables_template_id ON template_variables(template_id);
CREATE UNIQUE INDEX idx_template_variables_template_name ON template_variables(template_id, variable_name);

-- Campaigns indexes
CREATE INDEX idx_campaigns_name ON campaigns(name);
CREATE INDEX idx_campaigns_status ON campaigns(status);
CREATE INDEX idx_campaigns_template_id ON campaigns(template_id);
CREATE INDEX idx_campaigns_created_by ON campaigns(created_by);
CREATE INDEX idx_campaigns_scheduled_at ON campaigns(scheduled_at);
CREATE INDEX idx_campaigns_created_at ON campaigns(created_at);
CREATE INDEX idx_campaigns_created_by_created_at ON campaigns(created_by, created_at);

-- Campaign recipients indexes
CREATE INDEX idx_campaign_recipients_campaign_id ON campaign_recipients(campaign_id);
CREATE INDEX idx_campaign_recipients_lead_id ON campaign_recipients(lead_id);
CREATE INDEX idx_campaign_recipients_email_address ON campaign_recipients(email_address);
CREATE INDEX idx_campaign_recipients_status ON campaign_recipients(status);
CREATE INDEX idx_campaign_recipients_sent_at ON campaign_recipients(sent_at);
CREATE UNIQUE INDEX idx_campaign_recipients_campaign_lead ON campaign_recipients(campaign_id, lead_id);
CREATE INDEX idx_campaign_recipients_campaign_email ON campaign_recipients(campaign_id, email_address);

-- =====================================
-- FOREIGN KEY CONSTRAINTS
-- =====================================

-- Email templates foreign keys
ALTER TABLE email_templates ADD CONSTRAINT fk_email_templates_created_by FOREIGN KEY (created_by) REFERENCES users(id);

-- Template variables foreign keys
ALTER TABLE template_variables ADD CONSTRAINT fk_template_variables_template_id FOREIGN KEY (template_id) REFERENCES email_templates(id) ON DELETE CASCADE;

-- Campaigns foreign keys
ALTER TABLE campaigns ADD CONSTRAINT fk_campaigns_template_id FOREIGN KEY (template_id) REFERENCES email_templates(id);
ALTER TABLE campaigns ADD CONSTRAINT fk_campaigns_created_by FOREIGN KEY (created_by) REFERENCES users(id);

-- Campaign recipients foreign keys
ALTER TABLE campaign_recipients ADD CONSTRAINT fk_campaign_recipients_campaign_id FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE;
ALTER TABLE campaign_recipients ADD CONSTRAINT fk_campaign_recipients_lead_id FOREIGN KEY (lead_id) REFERENCES leads(id);

-- =====================================
-- TRIGGERS FOR CAMPAIGNS MODULE
-- =====================================

-- Trigger to update updated_at timestamp
CREATE TRIGGER update_email_templates_updated_at 
  BEFORE UPDATE ON email_templates 
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_campaigns_updated_at 
  BEFORE UPDATE ON campaigns 
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to update campaign statistics
CREATE OR REPLACE FUNCTION update_campaign_statistics()
RETURNS TRIGGER AS $$
BEGIN
  -- Update campaign metrics when recipient status changes
  IF TG_OP = 'UPDATE' AND OLD.status != NEW.status THEN
    UPDATE campaigns SET
      emails_sent = (
        SELECT COUNT(*) FROM campaign_recipients 
        WHERE campaign_id = NEW.campaign_id AND status != 'pending'
      ),
      emails_delivered = (
        SELECT COUNT(*) FROM campaign_recipients 
        WHERE campaign_id = NEW.campaign_id AND status IN ('delivered', 'opened', 'clicked')
      ),
      emails_opened = (
        SELECT COUNT(*) FROM campaign_recipients 
        WHERE campaign_id = NEW.campaign_id AND status IN ('opened', 'clicked')
      ),
      emails_clicked = (
        SELECT COUNT(*) FROM campaign_recipients 
        WHERE campaign_id = NEW.campaign_id AND status = 'clicked'
      ),
      emails_bounced = (
        SELECT COUNT(*) FROM campaign_recipients 
        WHERE campaign_id = NEW.campaign_id AND status = 'bounced'
      ),
      emails_unsubscribed = (
        SELECT COUNT(*) FROM campaign_recipients 
        WHERE campaign_id = NEW.campaign_id AND status = 'unsubscribed'
      ),
      updated_at = now()
    WHERE id = NEW.campaign_id;
    
    -- Calculate rates
    UPDATE campaigns SET
      open_rate = CASE WHEN emails_sent > 0 THEN ROUND((emails_opened::DECIMAL / emails_sent) * 100, 2) ELSE 0 END,
      click_rate = CASE WHEN emails_sent > 0 THEN ROUND((emails_clicked::DECIMAL / emails_sent) * 100, 2) ELSE 0 END,
      bounce_rate = CASE WHEN emails_sent > 0 THEN ROUND((emails_bounced::DECIMAL / emails_sent) * 100, 2) ELSE 0 END,
      unsubscribe_rate = CASE WHEN emails_sent > 0 THEN ROUND((emails_unsubscribed::DECIMAL / emails_sent) * 100, 2) ELSE 0 END
    WHERE id = NEW.campaign_id;
  END IF;
  
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to update campaign statistics
CREATE TRIGGER update_campaign_stats_trigger 
  AFTER UPDATE ON campaign_recipients 
  FOR EACH ROW EXECUTE FUNCTION update_campaign_statistics();

-- Function to update template usage statistics
CREATE OR REPLACE FUNCTION update_template_usage()
RETURNS TRIGGER AS $$
BEGIN
  -- Update template usage when campaign is created
  IF TG_OP = 'INSERT' THEN
    UPDATE email_templates SET
      usage_count = usage_count + 1,
      last_used_at = now(),
      updated_at = now()
    WHERE id = NEW.template_id;
  END IF;
  
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to update template usage
CREATE TRIGGER update_template_usage_trigger 
  AFTER INSERT ON campaigns 
  FOR EACH ROW EXECUTE FUNCTION update_template_usage();

-- =====================================
-- FUNCTIONS FOR CAMPAIGNS MODULE
-- =====================================

-- Function to get campaign performance summary
CREATE OR REPLACE FUNCTION get_campaign_performance(p_campaign_id UUID)
RETURNS TABLE (
  campaign_id UUID,
  campaign_name VARCHAR(255),
  total_recipients INTEGER,
  emails_sent INTEGER,
  emails_delivered INTEGER,
  emails_opened INTEGER,
  emails_clicked INTEGER,
  emails_bounced INTEGER,
  emails_unsubscribed INTEGER,
  open_rate DECIMAL(5,2),
  click_rate DECIMAL(5,2),
  bounce_rate DECIMAL(5,2),
  unsubscribe_rate DECIMAL(5,2),
  status campaign_status,
  created_at TIMESTAMP,
  completed_at TIMESTAMP
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    c.id, c.name, c.total_recipients, c.emails_sent, c.emails_delivered,
    c.emails_opened, c.emails_clicked, c.emails_bounced, c.emails_unsubscribed,
    c.open_rate, c.click_rate, c.bounce_rate, c.unsubscribe_rate,
    c.status, c.created_at, c.completed_at
  FROM campaigns c
  WHERE c.id = p_campaign_id;
END;
$$ language 'plpgsql';

-- Function to get template performance
CREATE OR REPLACE FUNCTION get_template_performance(p_template_id UUID)
RETURNS TABLE (
  template_id UUID,
  template_name VARCHAR(255),
  usage_count INTEGER,
  total_campaigns BIGINT,
  total_emails_sent BIGINT,
  avg_open_rate DECIMAL(5,2),
  avg_click_rate DECIMAL(5,2),
  last_used_at TIMESTAMP
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    t.id,
    t.name,
    t.usage_count,
    COUNT(c.id) as total_campaigns,
    COALESCE(SUM(c.emails_sent), 0) as total_emails_sent,
    COALESCE(ROUND(AVG(c.open_rate), 2), 0.00) as avg_open_rate,
    COALESCE(ROUND(AVG(c.click_rate), 2), 0.00) as avg_click_rate,
    t.last_used_at
  FROM email_templates t
  LEFT JOIN campaigns c ON t.id = c.template_id
  WHERE t.id = p_template_id
  GROUP BY t.id, t.name, t.usage_count, t.last_used_at;
END;
$$ language 'plpgsql';

-- Function to get campaign recipients status breakdown
CREATE OR REPLACE FUNCTION get_campaign_recipients_breakdown(p_campaign_id UUID)
RETURNS TABLE (
  status email_status,
  count BIGINT,
  percentage DECIMAL(5,2)
) AS $$
DECLARE
  total_recipients INTEGER;
BEGIN
  -- Get total recipients
  SELECT COUNT(*) INTO total_recipients 
  FROM campaign_recipients 
  WHERE campaign_id = p_campaign_id;
  
  RETURN QUERY
  SELECT 
    cr.status,
    COUNT(*) as count,
    CASE WHEN total_recipients > 0 THEN ROUND((COUNT(*)::DECIMAL / total_recipients) * 100, 2) ELSE 0.00 END as percentage
  FROM campaign_recipients cr
  WHERE cr.campaign_id = p_campaign_id
  GROUP BY cr.status
  ORDER BY count DESC;
END;
$$ language 'plpgsql';

-- Function to add leads to campaign
CREATE OR REPLACE FUNCTION add_leads_to_campaign(
  p_campaign_id UUID,
  p_lead_ids UUID[]
)
RETURNS INTEGER AS $$
DECLARE
  lead_record RECORD;
  added_count INTEGER := 0;
BEGIN
  -- Loop through lead IDs and add to campaign
  FOR lead_record IN 
    SELECT id, email, company_name 
    FROM leads 
    WHERE id = ANY(p_lead_ids) 
      AND email IS NOT NULL 
      AND verified_email = true
  LOOP
    -- Insert recipient record (ignore duplicates)
    INSERT INTO campaign_recipients (campaign_id, lead_id, email_address, personalization_data)
    VALUES (
      p_campaign_id, 
      lead_record.id, 
      lead_record.email,
      json_build_object('company_name', lead_record.company_name)
    )
    ON CONFLICT (campaign_id, lead_id) DO NOTHING;
    
    -- Count successful insertions
    IF FOUND THEN
      added_count := added_count + 1;
    END IF;
  END LOOP;
  
  -- Update campaign total recipients
  UPDATE campaigns SET 
    total_recipients = (
      SELECT COUNT(*) FROM campaign_recipients WHERE campaign_id = p_campaign_id
    ),
    updated_at = now()
  WHERE id = p_campaign_id;
  
  RETURN added_count;
END;
$$ language 'plpgsql';

-- =====================================
-- VIEWS FOR CAMPAIGNS MODULE
-- =====================================

-- View for active templates
CREATE VIEW active_templates AS
SELECT 
  id, name, description, category, subject, 
  body_html, body_text, variables, status,
  usage_count, success_rate, open_rate, click_rate,
  created_by, created_at, updated_at, last_used_at
FROM email_templates 
WHERE status = 'active';

-- View for campaign summary
CREATE VIEW campaign_summary AS
SELECT 
  c.id, c.name, c.description, c.status,
  c.total_recipients, c.emails_sent, c.emails_delivered,
  c.emails_opened, c.emails_clicked, c.emails_bounced,
  c.open_rate, c.click_rate, c.bounce_rate,
  c.created_by, c.created_at, c.scheduled_at, c.completed_at,
  t.name as template_name, t.category as template_category,
  u.full_name as created_by_name
FROM campaigns c
LEFT JOIN email_templates t ON c.template_id = t.id
LEFT JOIN users u ON c.created_by = u.id;

-- View for high-performing campaigns
CREATE VIEW high_performing_campaigns AS
SELECT 
  id, name, open_rate, click_rate, emails_sent,
  status, created_at, completed_at
FROM campaigns 
WHERE status = 'completed' 
  AND emails_sent > 0 
  AND open_rate >= 20.00 -- 20% or higher open rate
ORDER BY open_rate DESC, click_rate DESC;

-- =====================================
-- INITIAL DATA FOR CAMPAIGNS MODULE
-- =====================================

-- Insert default email templates
INSERT INTO email_templates (
  id, name, description, category, subject, body_html, body_text, variables, created_by
) VALUES 
(
  uuid_generate_v4(),
  'Lead Introduction Template',
  'Basic template for introducing our services to new leads',
  'introduction',
  'Hola {{company_name}} - Servicios de Energía Solar',
  '<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{subject}}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2c5aa0;">Hola {{company_name}},</h2>
        
        <p>Nos dirigimos a ustedes desde <strong>RitterFinder</strong> porque hemos identificado que su empresa se dedica a {{activity}}.</p>
        
        <p>Especializamos en ayudar a empresas como la suya a:</p>
        <ul>
            <li>Reducir costos energéticos significativamente</li>
            <li>Implementar soluciones de energía sostenible</li>
            <li>Mejorar la eficiencia operacional</li>
        </ul>
        
        <p>¿Les interesaría conocer más sobre cómo podemos ayudarles?</p>
        
        <p>Saludos cordiales,<br>
        <strong>Equipo RitterFinder</strong></p>
        
        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #666;">
            <p>Si no deseas recibir más emails, puedes <a href="{{unsubscribe_url}}">darte de baja aquí</a>.</p>
        </div>
    </div>
</body>
</html>',
  'Hola {{company_name}},

Nos dirigimos a ustedes desde RitterFinder porque hemos identificado que su empresa se dedica a {{activity}}.

Especializamos en ayudar a empresas como la suya a:
- Reducir costos energéticos significativamente
- Implementar soluciones de energía sostenible
- Mejorar la eficiencia operacional

¿Les interesaría conocer más sobre cómo podemos ayudarles?

Saludos cordiales,
Equipo RitterFinder

---
Si no deseas recibir más emails, puedes darte de baja en: {{unsubscribe_url}}',
  '["company_name", "activity", "unsubscribe_url"]',
  (SELECT id FROM users WHERE email = 'admin@ritterfinder.com' LIMIT 1)
);

-- Insert template variables for the default template
INSERT INTO template_variables (template_id, variable_name, variable_type, default_value, is_required, description)
SELECT 
  t.id,
  var.name,
  var.type,
  var.default_val,
  var.required,
  var.desc
FROM email_templates t,
LATERAL (VALUES 
  ('company_name', 'text', '', true, 'Name of the recipient company'),
  ('activity', 'text', '', true, 'Business activity of the company'),
  ('unsubscribe_url', 'url', '#', true, 'URL for unsubscribing from emails')
) AS var(name, type, default_val, required, desc)
WHERE t.name = 'Lead Introduction Template';

-- Log initialization
INSERT INTO system_logs (level, message, source, metadata) VALUES
('info', 'Campaigns module initialized successfully', 'system', '{"module": "campaigns", "version": "1.0", "tables": ["email_templates", "template_variables", "campaigns", "campaign_recipients"]}');

COMMIT;
