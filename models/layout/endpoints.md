# Layout Module API Endpoints

**SIMPLIFICADO:** Este módulo solo maneja lo mínimo indispensable que requiere backend. Tema, idioma, sidebar, etc. se manejan en frontend con localStorage.

## Notificaciones (Único que realmente necesita backend)

### GET /api/layout/notifications
**Description:** Get user notifications
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `unread_only` (boolean, default: false) - Only unread notifications
- `limit` (number, default: 10) - Number of notifications

**Response:**
```json
{
  "notifications": [
    {
      "id": "uuid",
      "type": "string",
      "title": "string",
      "message": "string",
      "priority": "number",
      "is_read": "boolean",
      "created_at": "timestamp",
      "action_url": "string",
      "action_text": "string"
    }
  ],
  "unread_count": "number"
}
```

### PUT /api/layout/notifications/:id/read
**Description:** Mark notification as read
**Method:** PUT
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Notification ID

**Response:**
```json
{
  "success": "boolean",
  "message": "Notification marked as read"
}
```

### POST /api/layout/notifications/mark-all-read
**Description:** Mark all user notifications as read
**Method:** POST
**Headers:**
- `Authorization: Bearer {access_token}`

**Response:**
```json
{
  "marked_count": "number",
  "message": "All notifications marked as read"
}
```

## Datos de Usuario (Para header/profile)

### GET /api/layout/user-info
**Description:** Get minimal user info for layout header
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`

**Response:**
```json
{
  "user": {
    "id": "uuid",
    "full_name": "string",
    "email": "string",
    "role_name": "string",
    "last_login_at": "timestamp"
  },
  "session": {
    "expires_at": "timestamp",
    "time_remaining_minutes": "number"
  }
}
```

---

## Notas Técnicas

**Lo que SÍ maneja backend:**
- ✅ Notificaciones (tabla `notifications`)
- ✅ Info básica de usuario (tabla `users`)
- ✅ Info de sesión (tabla `user_sessions`)

**Lo que NO necesita backend (se maneja en frontend):**
- ❌ Tema (light/dark) - localStorage
- ❌ Idioma - localStorage  
- ❌ Sidebar collapsed/expanded - localStorage
- ❌ Preferencias de tabla - localStorage
- ❌ Layout de dashboard - localStorage
- ❌ Configuración de widgets - localStorage

**Frontend maneja todo con:**
- `localStorage` para persistencia
- `useLayout` hook para estado
- No requiere sincronización con servidor
