-- =====================================
-- LAYOUT MODULE - MINIMAL BACKEND SUPPORT
-- =====================================
-- Este módulo es SIMPLIFICADO. La mayoría de configuraciones 
-- de layout se manejan en frontend con localStorage.
-- Solo mantenemos funciones auxiliares para datos existentes.

-- =====================================
-- FUNCIONES AUXILIARES PARA LAYOUT
-- =====================================

-- Función para obtener info básica de usuario para el header
CREATE OR REPLACE FUNCTION get_user_layout_info(p_user_id UUID)
RETURNS TABLE (
  user_id UUID,
  full_name VARCHAR,
  email VARCHAR,
  role_name VARCHAR,
  last_login_at TIMESTAMP,
  session_expires_at TIMESTAMP,
  unread_notifications_count BIGINT
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    u.id as user_id,
    u.full_name,
    COALESCE(au.email, '') as email,
    r.name as role_name,
    u.last_activity_at as last_login_at,
    NULL::TIMESTAMP as session_expires_at,
    (
      SELECT COUNT(*)::BIGINT 
      FROM notifications n 
      WHERE n.user_id = u.id AND n.is_read = false
    ) as unread_notifications_count
  FROM user_profiles u
  LEFT JOIN auth.users au ON u.id = au.id
  LEFT JOIN roles r ON u.role_id = r.id
  WHERE u.id = p_user_id
  LIMIT 1;
END;
$$ language 'plpgsql';

-- Función para marcar todas las notificaciones como leídas
CREATE OR REPLACE FUNCTION mark_all_notifications_read(p_user_id UUID)
RETURNS INTEGER AS $$
DECLARE
  affected_count INTEGER;
BEGIN
  UPDATE notifications 
  SET 
    is_read = true,
    read_at = NOW()
  WHERE user_id = p_user_id 
    AND is_read = false;
  
  GET DIAGNOSTICS affected_count = ROW_COUNT;
  
  -- Log la acción
  INSERT INTO activity_logs (
    user_id, 
    activity_type, 
    action, 
    description,
    resource_type
  ) VALUES (
    p_user_id,
    'resource_viewed',
    'mark_all_notifications_read',
    'Usuario marcó todas las notificaciones como leídas',
    'notifications'
  );
  
  RETURN affected_count;
END;
$$ language 'plpgsql';

-- =====================================
-- ÍNDICES PARA MEJORAR RENDIMIENTO
-- =====================================

-- Índice para notificaciones no leídas (si no existe ya)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_indexes 
    WHERE indexname = 'idx_notifications_user_unread'
  ) THEN
    CREATE INDEX idx_notifications_user_unread 
    ON notifications(user_id, is_read, created_at);
  END IF;
END $$;

-- NOTE: User sessions are managed by Supabase Auth, no index needed

-- =====================================
-- LOG DE INICIALIZACIÓN
-- =====================================

-- Log de inicialización simplificada
INSERT INTO system_logs (level, message, source, metadata) 
VALUES (
  'info', 
  'Layout module initialized (simplified version)', 
  'system', 
  '{"module": "layout", "version": "1.0-simplified", "note": "Frontend handles UI preferences"}'
) ON CONFLICT DO NOTHING;

COMMIT;
