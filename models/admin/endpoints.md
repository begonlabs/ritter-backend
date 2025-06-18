# Admin Module API Endpoints

## User Management

### GET /api/admin/users
**Description:** Get list of all users with pagination and filtering
**Method:** GET
**Query Parameters:**
- `page` (number, default: 1) - Page number
- `limit` (number, default: 25) - Items per page
- `status` (string, optional) - Filter by user status (invited, active, inactive, suspended, banned, locked)
- `role_id` (UUID, optional) - Filter by role
- `search` (string, optional) - Search by name or email

**Response:**
```json
{
  "users": [
    {
      "id": "uuid",
      "email": "string",
      "full_name": "string",
      "role_id": "uuid",
      "role_name": "string",
      "status": "active|inactive|invited|suspended|banned|locked",
      "last_login_at": "timestamp",
      "email_verified_at": "timestamp",
      "two_factor_enabled": "boolean",
      "invited_by": "uuid",
      "invited_at": "timestamp",
      "created_at": "timestamp",
      "updated_at": "timestamp"
    }
  ],
  "pagination": {
    "page": "number",
    "limit": "number",
    "total": "number",
    "total_pages": "number"
  }
}
```

### GET /api/admin/users/:id
**Description:** Get specific user details
**Method:** GET
**Parameters:**
- `id` (UUID) - User ID

**Response:**
```json
{
  "id": "uuid",
  "email": "string",
  "full_name": "string",
  "role_id": "uuid",
  "role": {
    "id": "uuid",
    "name": "string",
    "description": "string",
    "permissions": ["array of permission names"]
  },
  "status": "string",
  "last_login_at": "timestamp",
  "email_verified_at": "timestamp",
  "two_factor_enabled": "boolean",
  "invited_by": "uuid",
  "invited_at": "timestamp",
  "password_set_at": "timestamp",
  "failed_login_attempts": "number",
  "locked_until": "timestamp",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### POST /api/admin/users
**Description:** Create new user (invitation)
**Method:** POST
**Body:**
```json
{
  "email": "string (required)",
  "full_name": "string (required)",
  "role_id": "uuid (required)"
}
```

**Response:**
```json
{
  "user": {
    "id": "uuid",
    "email": "string",
    "full_name": "string",
    "role_id": "uuid",
    "status": "invited",
    "invited_at": "timestamp",
    "invited_by": "uuid"
  },
  "invitation_token": "string"
}
```

### PUT /api/admin/users/:id
**Description:** Update user information
**Method:** PUT
**Parameters:**
- `id` (UUID) - User ID

**Body:**
```json
{
  "full_name": "string (optional)",
  "role_id": "uuid (optional)",
  "status": "string (optional)"
}
```

**Response:**
```json
{
  "user": {
    "id": "uuid",
    "email": "string",
    "full_name": "string",
    "role_id": "uuid",
    "status": "string",
    "updated_at": "timestamp"
  }
}
```

### DELETE /api/admin/users/:id
**Description:** Delete user (soft delete - set status to inactive)
**Method:** DELETE
**Parameters:**
- `id` (UUID) - User ID

**Response:**
```json
{
  "message": "User deleted successfully"
}
```

### POST /api/admin/users/:id/activate
**Description:** Activate user account
**Method:** POST
**Parameters:**
- `id` (UUID) - User ID

**Response:**
```json
{
  "message": "User activated successfully",
  "user": {
    "id": "uuid",
    "status": "active",
    "updated_at": "timestamp"
  }
}
```

### POST /api/admin/users/:id/deactivate
**Description:** Deactivate user account
**Method:** POST
**Parameters:**
- `id` (UUID) - User ID

**Response:**
```json
{
  "message": "User deactivated successfully",
  "user": {
    "id": "uuid",
    "status": "inactive",
    "updated_at": "timestamp"
  }
}
```

### POST /api/admin/users/:id/reset-password
**Description:** Send password reset email to user
**Method:** POST
**Parameters:**
- `id` (UUID) - User ID

**Response:**
```json
{
  "message": "Password reset email sent successfully"
}
```

## Role Management

### GET /api/admin/roles
**Description:** Get list of all roles
**Method:** GET

**Response:**
```json
{
  "roles": [
    {
      "id": "uuid",
      "name": "string",
      "description": "string",
      "is_system_role": "boolean",
      "permissions": ["array of permission names"],
      "user_count": "number",
      "created_at": "timestamp",
      "updated_at": "timestamp"
    }
  ]
}
```

### GET /api/admin/roles/:id
**Description:** Get specific role details
**Method:** GET
**Parameters:**
- `id` (UUID) - Role ID

**Response:**
```json
{
  "id": "uuid",
  "name": "string",
  "description": "string",
  "is_system_role": "boolean",
  "permissions": [
    {
      "id": "uuid",
      "name": "string",
      "description": "string",
      "category": "string",
      "resource": "string",
      "action": "string"
    }
  ],
  "user_count": "number",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### POST /api/admin/roles
**Description:** Create new role
**Method:** POST
**Body:**
```json
{
  "name": "string (required)",
  "description": "string (optional)",
  "permissions": ["array of permission names (required)"]
}
```

**Response:**
```json
{
  "role": {
    "id": "uuid",
    "name": "string",
    "description": "string",
    "permissions": ["array"],
    "created_at": "timestamp"
  }
}
```

### PUT /api/admin/roles/:id
**Description:** Update role
**Method:** PUT
**Parameters:**
- `id` (UUID) - Role ID

**Body:**
```json
{
  "name": "string (optional)",
  "description": "string (optional)",
  "permissions": ["array of permission names (optional)"]
}
```

**Response:**
```json
{
  "role": {
    "id": "uuid",
    "name": "string",
    "description": "string",
    "permissions": ["array"],
    "updated_at": "timestamp"
  }
}
```

### DELETE /api/admin/roles/:id
**Description:** Delete role (only if no users assigned)
**Method:** DELETE
**Parameters:**
- `id` (UUID) - Role ID

**Response:**
```json
{
  "message": "Role deleted successfully"
}
```

## Permission Management

### GET /api/admin/permissions
**Description:** Get list of all permissions grouped by category
**Method:** GET

**Response:**
```json
{
  "permissions": {
    "leads": [
      {
        "id": "uuid",
        "name": "string",
        "description": "string",
        "resource": "string",
        "action": "string"
      }
    ],
    "campaigns": [...],
    "analytics": [...],
    "admin": [...],
    "export": [...],
    "settings": [...]
  }
}
```

### GET /api/admin/permissions/categories
**Description:** Get permission categories
**Method:** GET

**Response:**
```json
{
  "categories": [
    {
      "name": "leads",
      "label": "Gestión de Leads",
      "permission_count": "number"
    },
    {
      "name": "campaigns",
      "label": "Campañas",
      "permission_count": "number"
    }
  ]
}
```

## System Settings

### GET /api/admin/settings
**Description:** Get system settings grouped by category
**Method:** GET
**Query Parameters:**
- `category` (string, optional) - Filter by category
- `is_public` (boolean, optional) - Filter by public visibility

**Response:**
```json
{
  "settings": {
    "email": [
      {
        "id": "uuid",
        "key": "string",
        "value": "string",
        "value_type": "string|number|boolean|json",
        "description": "string",
        "is_public": "boolean",
        "is_encrypted": "boolean",
        "validation_rules": "object",
        "default_value": "string"
      }
    ],
    "scraping": [...],
    "system": [...],
    "security": [...]
  }
}
```

### GET /api/admin/settings/:id
**Description:** Get specific setting
**Method:** GET
**Parameters:**
- `id` (UUID) - Setting ID

**Response:**
```json
{
  "id": "uuid",
  "category": "string",
  "key": "string",
  "value": "string",
  "value_type": "string",
  "description": "string",
  "is_public": "boolean",
  "is_encrypted": "boolean",
  "validation_rules": "object",
  "default_value": "string",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### PUT /api/admin/settings/:id
**Description:** Update system setting
**Method:** PUT
**Parameters:**
- `id` (UUID) - Setting ID

**Body:**
```json
{
  "value": "string (required)",
  "description": "string (optional)"
}
```

**Response:**
```json
{
  "setting": {
    "id": "uuid",
    "key": "string",
    "value": "string",
    "updated_at": "timestamp",
    "updated_by": "uuid"
  }
}
```

## Notifications

### GET /api/admin/notifications
**Description:** Get notifications for current user
**Method:** GET
**Query Parameters:**
- `page` (number, default: 1)
- `limit` (number, default: 20)
- `is_read` (boolean, optional) - Filter by read status
- `type` (string, optional) - Filter by notification type
- `priority` (number, optional) - Filter by priority

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
      "read_at": "timestamp",
      "action_url": "string",
      "action_text": "string",
      "action_data": "object",
      "related_type": "string",
      "related_id": "uuid",
      "created_at": "timestamp",
      "expires_at": "timestamp"
    }
  ],
  "unread_count": "number",
  "pagination": {
    "page": "number",
    "limit": "number",
    "total": "number",
    "total_pages": "number"
  }
}
```

### PUT /api/admin/notifications/:id/read
**Description:** Mark notification as read
**Method:** PUT
**Parameters:**
- `id` (UUID) - Notification ID

**Response:**
```json
{
  "message": "Notification marked as read",
  "notification": {
    "id": "uuid",
    "is_read": true,
    "read_at": "timestamp"
  }
}
```

### PUT /api/admin/notifications/read-all
**Description:** Mark all notifications as read for current user
**Method:** PUT

**Response:**
```json
{
  "message": "All notifications marked as read",
  "updated_count": "number"
}
```

### DELETE /api/admin/notifications/:id
**Description:** Archive notification
**Method:** DELETE
**Parameters:**
- `id` (UUID) - Notification ID

**Response:**
```json
{
  "message": "Notification archived successfully"
}
```

## Activity Logs

### GET /api/admin/activity-logs
**Description:** Get activity logs with filtering
**Method:** GET
**Query Parameters:**
- `page` (number, default: 1)
- `limit` (number, default: 50)
- `user_id` (UUID, optional) - Filter by user
- `activity_type` (string, optional) - Filter by activity type
- `resource_type` (string, optional) - Filter by resource type
- `start_date` (date, optional) - Filter by date range
- `end_date` (date, optional) - Filter by date range

**Response:**
```json
{
  "activities": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "user_name": "string",
      "activity_type": "string",
      "action": "string",
      "description": "string",
      "resource_type": "string",
      "resource_id": "uuid",
      "ip_address": "string",
      "user_agent": "string",
      "changes": "object",
      "execution_time_ms": "number",
      "timestamp": "timestamp"
    }
  ],
  "pagination": {
    "page": "number",
    "limit": "number",
    "total": "number",
    "total_pages": "number"
  }
}
```

### GET /api/admin/activity-logs/summary
**Description:** Get activity summary statistics
**Method:** GET
**Query Parameters:**
- `days` (number, default: 30) - Number of days to analyze

**Response:**
```json
{
  "summary": {
    "total_activities": "number",
    "unique_users": "number",
    "most_active_user": {
      "user_id": "uuid",
      "user_name": "string",
      "activity_count": "number"
    },
    "activity_types": {
      "user_login": "number",
      "campaign_created": "number",
      "leads_searched": "number"
    },
    "daily_activity": [
      {
        "date": "date",
        "count": "number"
      }
    ]
  }
}
```
