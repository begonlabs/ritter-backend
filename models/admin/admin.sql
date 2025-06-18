-- =====================================
-- ADMIN MODULE - USER & ROLE MANAGEMENT
-- =====================================
-- Tables: users, roles, permissions, role_permissions, user_permissions, system_settings, notifications

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================
-- ENUMS USED BY ADMIN MODULE
-- =====================================

CREATE TYPE user_status AS ENUM (
  'invited',      -- User created but hasn't set password yet
  'active',       -- User has set password and can login
  'inactive',     -- User deactivated by admin
  'suspended',    -- Temporarily suspended
  'banned',       -- Permanently banned
  'locked'        -- Temporarily locked due to failed attempts
);

CREATE TYPE permission_category AS ENUM (
  'leads',
  'campaigns', 
  'analytics',
  'admin',
  'export',
  'settings'
);

CREATE TYPE activity_type AS ENUM (
  -- User Management
  'user_created',
  'user_updated',
  'user_deleted',
  'user_activated',
  'user_deactivated',
  'user_login',
  'user_logout',
  
  -- Role & Permission Management
  'role_created',
  'role_updated',
  'role_deleted',
  'role_assigned',
  'permission_granted',
  'permission_revoked',
  'permission_created',
  
  -- Campaign Management
  'campaign_created',
  'campaign_updated',
  'campaign_deleted',
  'campaign_sent',
  'template_created',
  'template_updated',
  'template_deleted',
  
  -- Lead Management
  'leads_searched',
  'leads_exported',
  'leads_imported',
  
  -- System Management
  'settings_updated',
  'system_updated',
  
  -- General Actions
  'resource_viewed',
  'resource_exported',
  'resource_shared'
);

-- =====================================
-- USER MANAGEMENT TABLES
-- =====================================

-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255), -- Nullable until password is set
  full_name VARCHAR(255) NOT NULL,
  role_id UUID,
  status user_status DEFAULT 'invited',
  last_login_at TIMESTAMP,
  email_verified_at TIMESTAMP,
  two_factor_enabled BOOLEAN DEFAULT false,
  two_factor_secret VARCHAR(255),
  
  -- Invitation and auth fields
  invited_by UUID,
  invited_at TIMESTAMP DEFAULT now(),
  password_set_at TIMESTAMP,
  failed_login_attempts INTEGER DEFAULT 0,
  locked_until TIMESTAMP,
  
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

-- Roles table
CREATE TABLE roles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(100) UNIQUE NOT NULL,
  description TEXT,
  is_system_role BOOLEAN DEFAULT false,
  permissions JSONB DEFAULT '[]',
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

-- Permissions table
CREATE TABLE permissions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(100) UNIQUE NOT NULL,
  description TEXT,
  category permission_category NOT NULL,
  resource VARCHAR(100) NOT NULL,
  action VARCHAR(100) NOT NULL,
  conditions JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT now()
);

-- Role permissions junction table
CREATE TABLE role_permissions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  role_id UUID NOT NULL,
  permission_id UUID NOT NULL,
  granted_at TIMESTAMP DEFAULT now(),
  granted_by UUID
);

-- User permissions (overrides/additions to role permissions)
CREATE TABLE user_permissions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,
  permission_id UUID NOT NULL,
  granted BOOLEAN DEFAULT true,
  granted_at TIMESTAMP DEFAULT now(),
  granted_by UUID,
  expires_at TIMESTAMP
);

-- =====================================
-- SYSTEM CONFIGURATION
-- =====================================

-- System settings table
CREATE TABLE system_settings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  category VARCHAR(100) NOT NULL,
  key VARCHAR(255) NOT NULL,
  value TEXT,
  value_type VARCHAR(50) DEFAULT 'string', -- string, number, boolean, json
  description TEXT,
  is_public BOOLEAN DEFAULT false,
  is_encrypted BOOLEAN DEFAULT false,
  
  -- Validation
  validation_rules JSONB DEFAULT '{}',
  default_value TEXT,
  
  -- System Fields
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now(),
  updated_by UUID
);

-- =====================================
-- NOTIFICATIONS SYSTEM
-- =====================================

-- Notifications table
CREATE TABLE notifications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,
  
  -- Notification Details
  type VARCHAR(100) NOT NULL, -- campaign_complete, search_finished, system_alert, etc.
  title VARCHAR(255) NOT NULL,
  message TEXT NOT NULL,
  priority INTEGER DEFAULT 0, -- 0=low, 1=medium, 2=high, 3=urgent
  
  -- Status
  is_read BOOLEAN DEFAULT false,
  read_at TIMESTAMP,
  is_archived BOOLEAN DEFAULT false,
  archived_at TIMESTAMP,
  
  -- Actions
  action_url VARCHAR(500),
  action_text VARCHAR(100),
  action_data JSONB DEFAULT '{}',
  
  -- Related Resources
  related_type VARCHAR(100), -- campaign, search, user, etc.
  related_id UUID,
  
  -- System Fields
  created_at TIMESTAMP DEFAULT now(),
  expires_at TIMESTAMP
);

-- =====================================
-- ACTIVITY TRACKING (for admin monitoring)
-- =====================================

-- Activity logs table
CREATE TABLE activity_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID,
  
  -- Activity Details
  activity_type activity_type NOT NULL,
  action VARCHAR(255) NOT NULL,
  description TEXT,
  resource_type VARCHAR(100), -- leads, campaigns, users, etc.
  resource_id UUID,
  
  -- Context Information
  ip_address INET,
  user_agent TEXT,
  browser_info JSONB DEFAULT '{}',
  device_info JSONB DEFAULT '{}',
  location_info JSONB DEFAULT '{}',
  
  -- Activity Data
  before_data JSONB DEFAULT '{}',
  after_data JSONB DEFAULT '{}',
  changes JSONB DEFAULT '{}',
  
  -- Performance
  execution_time_ms INTEGER,
  response_status INTEGER,
  
  -- System Fields
  timestamp TIMESTAMP DEFAULT now()
);

-- =====================================
-- INDEXES FOR ADMIN MODULE
-- =====================================

-- Users indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role_id ON users(role_id);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_invited_by ON users(invited_by);

-- Roles indexes
CREATE UNIQUE INDEX idx_roles_name ON roles(name);
CREATE INDEX idx_roles_is_system_role ON roles(is_system_role);

-- Permissions indexes
CREATE UNIQUE INDEX idx_permissions_name ON permissions(name);
CREATE INDEX idx_permissions_category ON permissions(category);
CREATE UNIQUE INDEX idx_permissions_resource_action ON permissions(resource, action);

-- Role permissions indexes
CREATE UNIQUE INDEX idx_role_permissions_role_permission ON role_permissions(role_id, permission_id);
CREATE INDEX idx_role_permissions_role_id ON role_permissions(role_id);
CREATE INDEX idx_role_permissions_permission_id ON role_permissions(permission_id);

-- User permissions indexes
CREATE UNIQUE INDEX idx_user_permissions_user_permission ON user_permissions(user_id, permission_id);
CREATE INDEX idx_user_permissions_user_id ON user_permissions(user_id);
CREATE INDEX idx_user_permissions_permission_id ON user_permissions(permission_id);
CREATE INDEX idx_user_permissions_expires_at ON user_permissions(expires_at);

-- System settings indexes
CREATE INDEX idx_system_settings_category ON system_settings(category);
CREATE INDEX idx_system_settings_key ON system_settings(key);
CREATE UNIQUE INDEX idx_system_settings_category_key ON system_settings(category, key);
CREATE INDEX idx_system_settings_is_public ON system_settings(is_public);

-- Notifications indexes
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_type ON notifications(type);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
CREATE INDEX idx_notifications_priority ON notifications(priority);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);
CREATE INDEX idx_notifications_expires_at ON notifications(expires_at);
CREATE INDEX idx_notifications_user_read_created ON notifications(user_id, is_read, created_at);

-- Activity logs indexes
CREATE INDEX idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX idx_activity_logs_activity_type ON activity_logs(activity_type);
CREATE INDEX idx_activity_logs_action ON activity_logs(action);
CREATE INDEX idx_activity_logs_resource_type ON activity_logs(resource_type);
CREATE INDEX idx_activity_logs_resource_id ON activity_logs(resource_id);
CREATE INDEX idx_activity_logs_timestamp ON activity_logs(timestamp);
CREATE INDEX idx_activity_logs_user_timestamp ON activity_logs(user_id, timestamp);
CREATE INDEX idx_activity_logs_type_timestamp ON activity_logs(activity_type, timestamp);

-- =====================================
-- FOREIGN KEY CONSTRAINTS
-- =====================================

-- Users foreign keys
ALTER TABLE users ADD CONSTRAINT fk_users_role_id FOREIGN KEY (role_id) REFERENCES roles(id);
ALTER TABLE users ADD CONSTRAINT fk_users_invited_by FOREIGN KEY (invited_by) REFERENCES users(id);

-- Role permissions foreign keys
ALTER TABLE role_permissions ADD CONSTRAINT fk_role_permissions_role_id FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE;
ALTER TABLE role_permissions ADD CONSTRAINT fk_role_permissions_permission_id FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE;
ALTER TABLE role_permissions ADD CONSTRAINT fk_role_permissions_granted_by FOREIGN KEY (granted_by) REFERENCES users(id);

-- User permissions foreign keys
ALTER TABLE user_permissions ADD CONSTRAINT fk_user_permissions_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
ALTER TABLE user_permissions ADD CONSTRAINT fk_user_permissions_permission_id FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE;
ALTER TABLE user_permissions ADD CONSTRAINT fk_user_permissions_granted_by FOREIGN KEY (granted_by) REFERENCES users(id);

-- System settings foreign keys
ALTER TABLE system_settings ADD CONSTRAINT fk_system_settings_updated_by FOREIGN KEY (updated_by) REFERENCES users(id);

-- Notifications foreign keys
ALTER TABLE notifications ADD CONSTRAINT fk_notifications_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Activity logs foreign keys
ALTER TABLE activity_logs ADD CONSTRAINT fk_activity_logs_user_id FOREIGN KEY (user_id) REFERENCES users(id);

-- =====================================
-- TRIGGER FOR UPDATED_AT TIMESTAMP
-- =====================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_roles_updated_at BEFORE UPDATE ON roles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_system_settings_updated_at BEFORE UPDATE ON system_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================
-- INITIAL DATA FOR ADMIN MODULE
-- =====================================

-- Insert default roles
INSERT INTO roles (id, name, description, is_system_role, permissions) VALUES
(uuid_generate_v4(), 'admin', 'Administrator with full system access', true, '["admin:*", "users:*", "campaigns:*", "leads:*", "analytics:*", "export:*", "settings:*"]'),
(uuid_generate_v4(), 'supervisor', 'Supervisor with limited admin access', true, '["users:read", "campaigns:*", "leads:*", "analytics:read", "export:limited"]'),
(uuid_generate_v4(), 'comercial', 'Commercial user with campaign and lead access', true, '["campaigns:*", "leads:*", "analytics:read", "export:limited"]');

-- Insert default permissions
INSERT INTO permissions (id, name, description, category, resource, action) VALUES
-- Admin permissions
(uuid_generate_v4(), 'admin.users.create', 'Create new users', 'admin', 'users', 'create'),
(uuid_generate_v4(), 'admin.users.read', 'View users', 'admin', 'users', 'read'),
(uuid_generate_v4(), 'admin.users.update', 'Update users', 'admin', 'users', 'update'),
(uuid_generate_v4(), 'admin.users.delete', 'Delete users', 'admin', 'users', 'delete'),
(uuid_generate_v4(), 'admin.roles.manage', 'Manage roles and permissions', 'admin', 'roles', 'manage'),
(uuid_generate_v4(), 'admin.settings.manage', 'Manage system settings', 'admin', 'settings', 'manage'),

-- Campaign permissions
(uuid_generate_v4(), 'campaigns.create', 'Create campaigns', 'campaigns', 'campaigns', 'create'),
(uuid_generate_v4(), 'campaigns.read', 'View campaigns', 'campaigns', 'campaigns', 'read'),
(uuid_generate_v4(), 'campaigns.update', 'Update campaigns', 'campaigns', 'campaigns', 'update'),
(uuid_generate_v4(), 'campaigns.delete', 'Delete campaigns', 'campaigns', 'campaigns', 'delete'),
(uuid_generate_v4(), 'campaigns.send', 'Send campaigns', 'campaigns', 'campaigns', 'send'),

-- Leads permissions
(uuid_generate_v4(), 'leads.search', 'Search for leads', 'leads', 'leads', 'search'),
(uuid_generate_v4(), 'leads.read', 'View leads', 'leads', 'leads', 'read'),
(uuid_generate_v4(), 'leads.export', 'Export leads', 'leads', 'leads', 'export'),
(uuid_generate_v4(), 'leads.import', 'Import leads', 'leads', 'leads', 'import'),

-- Analytics permissions
(uuid_generate_v4(), 'analytics.view', 'View analytics', 'analytics', 'analytics', 'view'),
(uuid_generate_v4(), 'analytics.export', 'Export analytics', 'analytics', 'analytics', 'export'),

-- Export permissions
(uuid_generate_v4(), 'export.unlimited', 'Unlimited exports', 'export', 'export', 'unlimited'),
(uuid_generate_v4(), 'export.limited', 'Limited exports', 'export', 'export', 'limited');

-- Insert default system settings
INSERT INTO system_settings (category, key, value, value_type, description, is_public) VALUES
('email', 'smtp_host', '', 'string', 'SMTP server hostname', false),
('email', 'smtp_port', '587', 'number', 'SMTP server port', false),
('email', 'smtp_username', '', 'string', 'SMTP username', false),
('email', 'smtp_password', '', 'string', 'SMTP password', false),
('email', 'from_email', 'noreply@ritterfinder.com', 'string', 'Default from email address', true),
('email', 'from_name', 'RitterFinder', 'string', 'Default from name', true),

('scraping', 'max_concurrent_requests', '10', 'number', 'Maximum concurrent scraping requests', false),
('scraping', 'request_delay_ms', '1000', 'number', 'Delay between requests in milliseconds', false),
('scraping', 'max_results_per_search', '1000', 'number', 'Maximum results per search session', true),

('system', 'maintenance_mode', 'false', 'boolean', 'Enable maintenance mode', false),
('system', 'registration_enabled', 'false', 'boolean', 'Allow new user registration', true),
('system', 'max_users', '100', 'number', 'Maximum number of users', false),

('security', 'session_timeout_hours', '24', 'number', 'Session timeout in hours', false),
('security', 'max_login_attempts', '5', 'number', 'Maximum login attempts before lockout', false),
('security', 'lockout_duration_minutes', '30', 'number', 'Account lockout duration in minutes', false);

COMMIT;
