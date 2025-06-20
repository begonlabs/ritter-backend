-- =====================================
-- ADMIN MODULE - SUPABASE ADAPTED VERSION
-- =====================================
-- Aprovechamos auth.users de Supabase y solo mantenemos lo necesario

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================
-- ENUMS - MANTENER SOLO LOS NECESARIOS
-- =====================================

CREATE TYPE permission_category AS ENUM (
  'leads',
  'campaigns', 
  'analytics',
  'admin',
  'export',
  'settings'
);

CREATE TYPE activity_type AS ENUM (
  -- User Management (simplificado)
  'user_created',
  'user_updated',
  'user_role_changed',
  
  -- Role & Permission Management
  'role_created',
  'role_updated',
  'role_deleted',
  'role_assigned',
  'permission_granted',
  'permission_revoked',
  
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
-- USER PROFILES - EXTIENDE auth.users DE SUPABASE
-- =====================================

-- Tabla de perfiles que complementa auth.users de Supabase
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  full_name VARCHAR(255) NOT NULL,
  role_id UUID,
  
  -- Campos adicionales que no están en auth.users
  invited_by UUID REFERENCES auth.users(id),
  invited_at TIMESTAMP DEFAULT now(),
  last_activity_at TIMESTAMP,
  
  -- Metadatos adicionales
  metadata JSONB DEFAULT '{}',
  
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

-- =====================================
-- ROLES Y PERMISOS - MANTENER IGUAL
-- =====================================

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
  granted_by UUID REFERENCES auth.users(id)
);

-- User permissions (overrides/additions to role permissions)
CREATE TABLE user_permissions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  permission_id UUID NOT NULL,
  granted BOOLEAN DEFAULT true,
  granted_at TIMESTAMP DEFAULT now(),
  granted_by UUID REFERENCES auth.users(id),
  expires_at TIMESTAMP
);

-- =====================================
-- SYSTEM SETTINGS - MANTENER IGUAL
-- =====================================

CREATE TABLE system_settings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  category VARCHAR(100) NOT NULL,
  key VARCHAR(255) NOT NULL,
  value TEXT,
  value_type VARCHAR(50) DEFAULT 'string',
  description TEXT,
  is_public BOOLEAN DEFAULT false,
  is_encrypted BOOLEAN DEFAULT false,
  
  validation_rules JSONB DEFAULT '{}',
  default_value TEXT,
  
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now(),
  updated_by UUID REFERENCES auth.users(id)
);

-- =====================================  
-- NOTIFICATIONS - MANTENER IGUAL
-- =====================================

CREATE TABLE notifications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  type VARCHAR(100) NOT NULL,
  title VARCHAR(255) NOT NULL,
  message TEXT NOT NULL,
  priority INTEGER DEFAULT 0,
  
  is_read BOOLEAN DEFAULT false,
  read_at TIMESTAMP,
  is_archived BOOLEAN DEFAULT false,
  archived_at TIMESTAMP,
  
  action_url VARCHAR(500),
  action_text VARCHAR(100),
  action_data JSONB DEFAULT '{}',
  
  related_type VARCHAR(100),
  related_id UUID,
  
  created_at TIMESTAMP DEFAULT now(),
  expires_at TIMESTAMP
);

-- =====================================
-- ACTIVITY TRACKING - SIMPLIFICADO
-- =====================================

CREATE TABLE activity_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id),
  
  activity_type activity_type NOT NULL,
  action VARCHAR(255) NOT NULL,
  description TEXT,
  resource_type VARCHAR(100),
  resource_id UUID,
  
  -- Información de contexto simplificada
  ip_address INET,
  user_agent TEXT,
  
  -- Datos de la actividad
  before_data JSONB DEFAULT '{}',
  after_data JSONB DEFAULT '{}',
  changes JSONB DEFAULT '{}',
  
  timestamp TIMESTAMP DEFAULT now()
);

-- =====================================
-- SYSTEM LOGS - MANTENER
-- =====================================

CREATE TABLE system_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  level VARCHAR(20) NOT NULL CHECK (level IN ('debug', 'info', 'warning', 'error', 'critical')),
  message TEXT NOT NULL,
  source VARCHAR(50) NOT NULL,
  
  user_id UUID REFERENCES auth.users(id),
  ip_address INET,
  
  request_id VARCHAR(255),
  execution_time_ms INTEGER,
  response_status INTEGER,
  
  resource_type VARCHAR(100),
  resource_id UUID,
  
  error_code VARCHAR(100),
  error_details JSONB DEFAULT '{}',
  stack_trace TEXT,
  
  metadata JSONB DEFAULT '{}',
  
  created_at TIMESTAMP DEFAULT now()
);

-- =====================================
-- INDEXES
-- =====================================

-- User profiles indexes
CREATE INDEX idx_user_profiles_role_id ON user_profiles(role_id);
CREATE INDEX idx_user_profiles_invited_by ON user_profiles(invited_by);

-- Roles indexes
CREATE UNIQUE INDEX idx_roles_name ON roles(name);
CREATE INDEX idx_roles_is_system_role ON roles(is_system_role);

-- Permissions indexes
CREATE UNIQUE INDEX idx_permissions_name ON permissions(name);
CREATE INDEX idx_permissions_category ON permissions(category);
CREATE UNIQUE INDEX idx_permissions_resource_action ON permissions(resource, action);

-- Role permissions indexes
CREATE UNIQUE INDEX idx_role_permissions_role_permission ON role_permissions(role_id, permission_id);

-- User permissions indexes
CREATE UNIQUE INDEX idx_user_permissions_user_permission ON user_permissions(user_id, permission_id);

-- System settings indexes
CREATE UNIQUE INDEX idx_system_settings_category_key ON system_settings(category, key);

-- Notifications indexes
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
CREATE INDEX idx_notifications_user_read_created ON notifications(user_id, is_read, created_at);

-- Activity logs indexes
CREATE INDEX idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX idx_activity_logs_activity_type ON activity_logs(activity_type);
CREATE INDEX idx_activity_logs_timestamp ON activity_logs(timestamp);

-- System logs indexes
CREATE INDEX idx_system_logs_level ON system_logs(level);
CREATE INDEX idx_system_logs_created_at ON system_logs(created_at);

-- =====================================
-- FOREIGN KEY CONSTRAINTS
-- =====================================

-- User profiles foreign keys
ALTER TABLE user_profiles ADD CONSTRAINT fk_user_profiles_role_id FOREIGN KEY (role_id) REFERENCES roles(id);

-- Role permissions foreign keys
ALTER TABLE role_permissions ADD CONSTRAINT fk_role_permissions_role_id FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE;
ALTER TABLE role_permissions ADD CONSTRAINT fk_role_permissions_permission_id FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE;

-- User permissions foreign keys
ALTER TABLE user_permissions ADD CONSTRAINT fk_user_permissions_permission_id FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE;

-- System settings foreign keys
ALTER TABLE system_settings ADD CONSTRAINT fk_system_settings_updated_by FOREIGN KEY (updated_by) REFERENCES auth.users(id);

-- =====================================
-- TRIGGERS
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
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_roles_updated_at BEFORE UPDATE ON roles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_system_settings_updated_at BEFORE UPDATE ON system_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================
-- RLS (Row Level Security) - MUY IMPORTANTE CON SUPABASE
-- =====================================

-- Habilitar RLS en todas las tablas
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE role_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_logs ENABLE ROW LEVEL SECURITY;

-- Políticas básicas (se pueden refinar más)
CREATE POLICY "Users can view their own profile" ON user_profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update their own profile" ON user_profiles FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can view their own notifications" ON notifications FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update their own notifications" ON notifications FOR UPDATE USING (auth.uid() = user_id);

-- =====================================
-- FUNCIONES SUPABASE-ESPECÍFICAS
-- =====================================

-- Función para crear perfil automáticamente cuando se crea usuario en auth.users
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.user_profiles (id, full_name, metadata)
  VALUES (NEW.id, COALESCE(NEW.raw_user_meta_data->>'full_name', ''), '{}');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger que se ejecuta cuando se crea un usuario en auth.users
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- =====================================
-- DATOS INICIALES
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