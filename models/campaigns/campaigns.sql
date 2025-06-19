-- =====================================
-- CAMPAIGNS MODULE - SUPABASE ADAPTED VERSION
-- =====================================
-- Adaptado para usar auth.users de Supabase

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
  body_html TEXT NOT NULL,
  body_text TEXT,
  variables JSONB DEFAULT '[]',
  preview_text VARCHAR(255),
  status template_status DEFAULT 'active',
  
  -- Usage Statistics
  usage_count INTEGER DEFAULT 0,
  success_rate DECIMAL(5,2) DEFAULT 0.00,
  open_rate DECIMAL(5,2) DEFAULT 0.00,
  click_rate DECIMAL(5,2) DEFAULT 0.00,
  
  -- System Fields - ADAPTADO PARA SUPABASE
  created_by UUID NOT NULL REFERENCES auth.users(id),
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now(),
  last_used_at TIMESTAMP
);

-- Template variables table (for dynamic content)
CREATE TABLE template_variables (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  template_id UUID NOT NULL,
  variable_name VARCHAR(100) NOT NULL,
  variable_type VARCHAR(50) NOT NULL,
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
  target_leads JSONB DEFAULT '[]',
  filters JSONB DEFAULT '{}',
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
  
  -- System Fields - ADAPTADO PARA SUPABASE
  created_by UUID NOT NULL REFERENCES auth.users(id),
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

-- =====================================
-- FOREIGN KEY CONSTRAINTS - ADAPTADO
-- =====================================

-- Template variables foreign keys
ALTER TABLE template_variables ADD CONSTRAINT fk_template_variables_template_id FOREIGN KEY (template_id) REFERENCES email_templates(id) ON DELETE CASCADE;

-- Campaigns foreign keys
ALTER TABLE campaigns ADD CONSTRAINT fk_campaigns_template_id FOREIGN KEY (template_id) REFERENCES email_templates(id);

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

-- Function to update campaign statistics - SIN CAMBIOS
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
-- RLS POLICIES - NUEVO PARA SUPABASE
-- =====================================

-- Habilitar RLS
ALTER TABLE email_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE template_variables ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaign_recipients ENABLE ROW LEVEL SECURITY;

-- Políticas básicas de RLS
CREATE POLICY "Users can view their own templates" ON email_templates FOR SELECT USING (auth.uid() = created_by);
CREATE POLICY "Users can create templates" ON email_templates FOR INSERT WITH CHECK (auth.uid() = created_by);
CREATE POLICY "Users can update their own templates" ON email_templates FOR UPDATE USING (auth.uid() = created_by);

CREATE POLICY "Users can view their own campaigns" ON campaigns FOR SELECT USING (auth.uid() = created_by);
CREATE POLICY "Users can create campaigns" ON campaigns FOR INSERT WITH CHECK (auth.uid() = created_by);
CREATE POLICY "Users can update their own campaigns" ON campaigns FOR UPDATE USING (auth.uid() = created_by);

COMMIT; 