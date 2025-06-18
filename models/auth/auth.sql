-- =====================================
-- AUTH MODULE - AUTHENTICATION & SECURITY
-- =====================================
-- Tables: auth_tokens, user_sessions, auth_logs, system_logs

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================
-- ENUMS USED BY AUTH MODULE
-- =====================================

CREATE TYPE token_type AS ENUM (
  'invitation',         -- Initial user invitation to set password
  'password_reset',     -- Password reset request
  'email_verification', -- Email verification
  'two_factor',         -- 2FA token
  'jwt_refresh'         -- JWT refresh token
);

CREATE TYPE auth_event_type AS ENUM (
  'login_attempt',      -- User tried to login
  'login_success',      -- Successful login
  'login_failure',      -- Failed login attempt
  'logout',             -- User logged out
  'password_set',       -- Password was set/changed
  'token_used',         -- Invitation/reset token used
  'session_expired',    -- Session expired
  'forced_logout',      -- Admin forced logout
  'suspicious_activity' -- Suspicious activity detected
);

CREATE TYPE log_level AS ENUM (
  'debug',
  'info',
  'warning',
  'error',
  'critical'
);

CREATE TYPE log_source AS ENUM (
  'auth',         -- Authentication events
  'security',     -- Security-related events
  'database',     -- Database operations
  'api',          -- API requests/responses
  'email',        -- Email operations
  'scraping',     -- Web scraping operations
  'campaign',     -- Campaign operations
  'system',       -- System operations
  'application'   -- General application logs
);

-- =====================================
-- AUTHENTICATION TOKENS
-- =====================================

-- Auth tokens table (invitations, password resets, etc.)
CREATE TABLE auth_tokens (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,
  token_hash VARCHAR(255) UNIQUE NOT NULL, -- Hashed token for security
  token_type token_type NOT NULL,
  
  -- Token lifecycle
  expires_at TIMESTAMP NOT NULL,
  used_at TIMESTAMP, -- When token was used
  created_by UUID, -- Admin who created invitation
  
  -- Security and validation
  ip_address VARCHAR(45), -- IP where token was created
  user_agent TEXT, -- Browser info for security
  is_valid BOOLEAN DEFAULT true,
  attempts_count INTEGER DEFAULT 0, -- Track usage attempts
  max_attempts INTEGER DEFAULT 3, -- Max allowed attempts
  
  -- Metadata
  metadata JSONB DEFAULT '{}', -- Additional data (email content, etc.)
  
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

-- =====================================
-- USER SESSIONS
-- =====================================

-- User sessions table (JWT session management)
CREATE TABLE user_sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,
  
  -- Session Details
  session_token VARCHAR(255) UNIQUE NOT NULL, -- JWT token hash
  refresh_token VARCHAR(255) UNIQUE, -- Refresh token hash
  
  -- Session Lifecycle
  created_at TIMESTAMP DEFAULT now(),
  last_accessed_at TIMESTAMP DEFAULT now(),
  expires_at TIMESTAMP NOT NULL,
  refresh_expires_at TIMESTAMP,
  
  -- Security Information
  ip_address VARCHAR(45),
  user_agent TEXT,
  device_fingerprint VARCHAR(255),
  
  -- Session Status
  is_active BOOLEAN DEFAULT true,
  logout_at TIMESTAMP,
  logout_reason VARCHAR(100), -- manual, expired, security, forced
  
  -- Location & Device Info
  country VARCHAR(100),
  city VARCHAR(255),
  device_type VARCHAR(50), -- desktop, mobile, tablet
  browser VARCHAR(100),
  os VARCHAR(100)
);

-- =====================================
-- AUTHENTICATION LOGS
-- =====================================

-- Auth logs table (comprehensive authentication event logging)
CREATE TABLE auth_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID,
  
  -- Authentication Event
  event_type auth_event_type NOT NULL,
  success BOOLEAN NOT NULL,
  
  -- Request Details
  email VARCHAR(255), -- Email used in attempt
  ip_address VARCHAR(45),
  user_agent TEXT,
  
  -- Security Information
  risk_score INTEGER DEFAULT 0, -- 0-100, higher = more risky
  failure_reason VARCHAR(255), -- Invalid credentials, account locked, etc.
  
  -- Session Information
  session_id UUID,
  token_used UUID, -- For invitation/reset tokens
  
  -- Geolocation
  country VARCHAR(100),
  city VARCHAR(255),
  
  -- Metadata
  metadata JSONB DEFAULT '{}',
  
  created_at TIMESTAMP DEFAULT now()
);

-- =====================================
-- SYSTEM LOGS
-- =====================================

-- System logs table (application-level logging)
CREATE TABLE system_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Log Details
  level log_level NOT NULL,
  message TEXT NOT NULL,
  source log_source NOT NULL,
  
  -- Context Information
  user_id UUID,
  ip_address VARCHAR(45),
  user_agent TEXT,
  
  -- Request/Response Info
  request_id VARCHAR(255), -- For tracing requests
  execution_time_ms INTEGER,
  response_status INTEGER,
  
  -- Resource Information
  resource_type VARCHAR(100), -- users, campaigns, leads, etc.
  resource_id UUID,
  
  -- Error Details (for error logs)
  error_code VARCHAR(100),
  error_details JSONB DEFAULT '{}',
  stack_trace TEXT,
  
  -- Additional Data
  metadata JSONB DEFAULT '{}',
  
  created_at TIMESTAMP DEFAULT now()
);

-- =====================================
-- INDEXES FOR AUTH MODULE
-- =====================================

-- Auth tokens indexes
CREATE UNIQUE INDEX idx_auth_tokens_token_hash ON auth_tokens(token_hash);
CREATE INDEX idx_auth_tokens_user_id ON auth_tokens(user_id);
CREATE INDEX idx_auth_tokens_token_type ON auth_tokens(token_type);
CREATE INDEX idx_auth_tokens_expires_at ON auth_tokens(expires_at);
CREATE INDEX idx_auth_tokens_is_valid ON auth_tokens(is_valid);
CREATE INDEX idx_auth_tokens_created_at ON auth_tokens(created_at);

-- User sessions indexes
CREATE UNIQUE INDEX idx_user_sessions_session_token ON user_sessions(session_token);
CREATE UNIQUE INDEX idx_user_sessions_refresh_token ON user_sessions(refresh_token);
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_is_active ON user_sessions(is_active);
CREATE INDEX idx_user_sessions_created_at ON user_sessions(created_at);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);
CREATE INDEX idx_user_sessions_user_active ON user_sessions(user_id, is_active);

-- Auth logs indexes
CREATE INDEX idx_auth_logs_user_id ON auth_logs(user_id);
CREATE INDEX idx_auth_logs_event_type ON auth_logs(event_type);
CREATE INDEX idx_auth_logs_success ON auth_logs(success);
CREATE INDEX idx_auth_logs_ip_address ON auth_logs(ip_address);
CREATE INDEX idx_auth_logs_created_at ON auth_logs(created_at);
CREATE INDEX idx_auth_logs_risk_score ON auth_logs(risk_score);
CREATE INDEX idx_auth_logs_user_event_created ON auth_logs(user_id, event_type, created_at);

-- System logs indexes
CREATE INDEX idx_system_logs_level ON system_logs(level);
CREATE INDEX idx_system_logs_source ON system_logs(source);
CREATE INDEX idx_system_logs_user_id ON system_logs(user_id);
CREATE INDEX idx_system_logs_created_at ON system_logs(created_at);
CREATE INDEX idx_system_logs_resource_type ON system_logs(resource_type);
CREATE INDEX idx_system_logs_resource_id ON system_logs(resource_id);
CREATE INDEX idx_system_logs_level_source_created ON system_logs(level, source, created_at);
CREATE INDEX idx_system_logs_user_created ON system_logs(user_id, created_at);

-- =====================================
-- FOREIGN KEY CONSTRAINTS
-- =====================================

-- Auth tokens foreign keys
ALTER TABLE auth_tokens ADD CONSTRAINT fk_auth_tokens_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
ALTER TABLE auth_tokens ADD CONSTRAINT fk_auth_tokens_created_by FOREIGN KEY (created_by) REFERENCES users(id);

-- User sessions foreign keys
ALTER TABLE user_sessions ADD CONSTRAINT fk_user_sessions_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Auth logs foreign keys
ALTER TABLE auth_logs ADD CONSTRAINT fk_auth_logs_user_id FOREIGN KEY (user_id) REFERENCES users(id);
ALTER TABLE auth_logs ADD CONSTRAINT fk_auth_logs_session_id FOREIGN KEY (session_id) REFERENCES user_sessions(id);
ALTER TABLE auth_logs ADD CONSTRAINT fk_auth_logs_token_used FOREIGN KEY (token_used) REFERENCES auth_tokens(id);

-- System logs foreign keys
ALTER TABLE system_logs ADD CONSTRAINT fk_system_logs_user_id FOREIGN KEY (user_id) REFERENCES users(id);

-- =====================================
-- TRIGGERS FOR AUTH MODULE
-- =====================================

-- Trigger to update updated_at timestamp on auth_tokens
CREATE TRIGGER update_auth_tokens_updated_at 
  BEFORE UPDATE ON auth_tokens 
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger to automatically log session activity
CREATE OR REPLACE FUNCTION log_session_activity()
RETURNS TRIGGER AS $$
BEGIN
  -- Log session creation
  IF TG_OP = 'INSERT' THEN
    INSERT INTO auth_logs (user_id, event_type, success, ip_address, user_agent, session_id, metadata)
    VALUES (NEW.user_id, 'login_success', true, NEW.ip_address, NEW.user_agent, NEW.id, 
            json_build_object('device_type', NEW.device_type, 'browser', NEW.browser, 'os', NEW.os));
    RETURN NEW;
  END IF;
  
  -- Log session logout
  IF TG_OP = 'UPDATE' AND OLD.is_active = true AND NEW.is_active = false THEN
    INSERT INTO auth_logs (user_id, event_type, success, ip_address, user_agent, session_id, metadata)
    VALUES (NEW.user_id, 'logout', true, NEW.ip_address, NEW.user_agent, NEW.id,
            json_build_object('logout_reason', NEW.logout_reason));
    RETURN NEW;
  END IF;
  
  RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER session_activity_logger 
  AFTER INSERT OR UPDATE ON user_sessions 
  FOR EACH ROW EXECUTE FUNCTION log_session_activity();

-- =====================================
-- FUNCTIONS FOR AUTH MODULE
-- =====================================

-- Function to clean up expired tokens
CREATE OR REPLACE FUNCTION cleanup_expired_tokens()
RETURNS INTEGER AS $$
DECLARE
  deleted_count INTEGER;
BEGIN
  DELETE FROM auth_tokens 
  WHERE expires_at < now() 
    AND (used_at IS NOT NULL OR attempts_count >= max_attempts);
  
  GET DIAGNOSTICS deleted_count = ROW_COUNT;
  
  -- Log cleanup activity
  INSERT INTO system_logs (level, message, source, metadata)
  VALUES ('info', 'Cleaned up expired auth tokens', 'auth', 
          json_build_object('deleted_count', deleted_count));
  
  RETURN deleted_count;
END;
$$ language 'plpgsql';

-- Function to clean up old sessions
CREATE OR REPLACE FUNCTION cleanup_old_sessions()
RETURNS INTEGER AS $$
DECLARE
  deleted_count INTEGER;
BEGIN
  DELETE FROM user_sessions 
  WHERE expires_at < now() 
    AND is_active = false;
  
  GET DIAGNOSTICS deleted_count = ROW_COUNT;
  
  -- Log cleanup activity
  INSERT INTO system_logs (level, message, source, metadata)
  VALUES ('info', 'Cleaned up old user sessions', 'auth', 
          json_build_object('deleted_count', deleted_count));
  
  RETURN deleted_count;
END;
$$ language 'plpgsql';

-- Function to detect suspicious login activity
CREATE OR REPLACE FUNCTION detect_suspicious_activity(
  p_user_id UUID,
  p_ip_address VARCHAR(45),
  p_time_window_minutes INTEGER DEFAULT 30
)
RETURNS INTEGER AS $$
DECLARE
  failed_attempts INTEGER;
  risk_score INTEGER := 0;
BEGIN
  -- Count failed login attempts in time window
  SELECT COUNT(*) INTO failed_attempts
  FROM auth_logs
  WHERE user_id = p_user_id
    AND event_type = 'login_failure'
    AND created_at >= now() - (p_time_window_minutes || ' minutes')::INTERVAL;
  
  -- Calculate risk score
  risk_score := LEAST(failed_attempts * 20, 100);
  
  -- Log if risk is high
  IF risk_score >= 60 THEN
    INSERT INTO auth_logs (user_id, event_type, success, ip_address, risk_score, metadata)
    VALUES (p_user_id, 'suspicious_activity', false, p_ip_address, risk_score,
            json_build_object('failed_attempts', failed_attempts, 'time_window_minutes', p_time_window_minutes));
  END IF;
  
  RETURN risk_score;
END;
$$ language 'plpgsql';

-- =====================================
-- INITIAL DATA FOR AUTH MODULE
-- =====================================

-- Insert default system logs for initialization
INSERT INTO system_logs (level, message, source, metadata) VALUES
('info', 'Auth module initialized successfully', 'system', '{"module": "auth", "version": "1.0"}');

-- =====================================
-- SCHEDULED CLEANUP JOBS (Comments for implementation)
-- =====================================

-- Note: These would typically be implemented as cron jobs or scheduled tasks
-- Example cron expressions:

-- Clean expired tokens daily at 2 AM:
-- 0 2 * * * SELECT cleanup_expired_tokens();

-- Clean old sessions weekly on Sunday at 3 AM:
-- 0 3 * * 0 SELECT cleanup_old_sessions();

-- Clean old auth logs (keep 6 months):
-- 0 4 1 * * DELETE FROM auth_logs WHERE created_at < now() - INTERVAL '6 months';

-- Clean old system logs (keep 3 months):
-- 0 5 1 * * DELETE FROM system_logs WHERE created_at < now() - INTERVAL '3 months';

COMMIT;
