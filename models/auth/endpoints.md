# Auth Module API Endpoints

## Authentication

### POST /api/auth/login
**Description:** User login with email and password
**Method:** POST
**Body:**
```json
{
  "email": "string (required)",
  "password": "string (required)",
  "remember_me": "boolean (optional, default: false)"
}
```

**Response:**
```json
{
  "user": {
    "id": "uuid",
    "email": "string",
    "full_name": "string",
    "role": {
      "id": "uuid",
      "name": "string",
      "permissions": ["array of permission names"]
    },
    "status": "string",
    "last_login_at": "timestamp",
    "two_factor_enabled": "boolean"
  },
  "tokens": {
    "access_token": "string",
    "refresh_token": "string",
    "expires_at": "timestamp",
    "token_type": "Bearer"
  },
  "session": {
    "id": "uuid",
    "expires_at": "timestamp"
  }
}
```

### POST /api/auth/logout
**Description:** User logout (invalidate session)
**Method:** POST
**Headers:**
- `Authorization: Bearer {access_token}`

**Body:**
```json
{
  "logout_all_devices": "boolean (optional, default: false)"
}
```

**Response:**
```json
{
  "message": "Logged out successfully"
}
```

### POST /api/auth/refresh
**Description:** Refresh access token using refresh token
**Method:** POST
**Body:**
```json
{
  "refresh_token": "string (required)"
}
```

**Response:**
```json
{
  "tokens": {
    "access_token": "string",
    "refresh_token": "string",
    "expires_at": "timestamp",
    "token_type": "Bearer"
  }
}
```

### GET /api/auth/me
**Description:** Get current user information
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`

**Response:**
```json
{
  "user": {
    "id": "uuid",
    "email": "string",
    "full_name": "string",
    "role": {
      "id": "uuid",
      "name": "string",
      "permissions": ["array of permission names"]
    },
    "status": "string",
    "last_login_at": "timestamp",
    "email_verified_at": "timestamp",
    "two_factor_enabled": "boolean",
    "created_at": "timestamp"
  }
}
```

## Password Management

### POST /api/auth/set-password
**Description:** Set password using invitation token (first-time setup)
**Method:** POST
**Body:**
```json
{
  "token": "string (required)",
  "password": "string (required)",
  "password_confirmation": "string (required)"
}
```

**Response:**
```json
{
  "message": "Password set successfully",
  "user": {
    "id": "uuid",
    "email": "string",
    "full_name": "string",
    "status": "active",
    "password_set_at": "timestamp"
  },
  "tokens": {
    "access_token": "string",
    "refresh_token": "string",
    "expires_at": "timestamp",
    "token_type": "Bearer"
  }
}
```

### POST /api/auth/forgot-password
**Description:** Request password reset email
**Method:** POST
**Body:**
```json
{
  "email": "string (required)"
}
```

**Response:**
```json
{
  "message": "Password reset email sent if account exists"
}
```

### POST /api/auth/reset-password
**Description:** Reset password using reset token
**Method:** POST
**Body:**
```json
{
  "token": "string (required)",
  "password": "string (required)",
  "password_confirmation": "string (required)"
}
```

**Response:**
```json
{
  "message": "Password reset successfully",
  "user": {
    "id": "uuid",
    "email": "string"
  }
}
```

### POST /api/auth/change-password
**Description:** Change password for authenticated user
**Method:** POST
**Headers:**
- `Authorization: Bearer {access_token}`

**Body:**
```json
{
  "current_password": "string (required)",
  "new_password": "string (required)",
  "new_password_confirmation": "string (required)"
}
```

**Response:**
```json
{
  "message": "Password changed successfully"
}
```

## Token Management

### GET /api/auth/tokens/validate
**Description:** Validate invitation or reset token
**Method:** GET
**Query Parameters:**
- `token` (string, required) - Token to validate
- `type` (string, required) - Token type (invitation, password_reset)

**Response:**
```json
{
  "valid": "boolean",
  "token_info": {
    "type": "string",
    "expires_at": "timestamp",
    "user": {
      "id": "uuid",
      "email": "string",
      "full_name": "string"
    }
  }
}
```

### POST /api/auth/tokens/resend-invitation
**Description:** Resend invitation email
**Method:** POST
**Headers:**
- `Authorization: Bearer {access_token}` (admin only)

**Body:**
```json
{
  "user_id": "uuid (required)"
}
```

**Response:**
```json
{
  "message": "Invitation email sent successfully",
  "invitation": {
    "user_id": "uuid",
    "expires_at": "timestamp"
  }
}
```

## Session Management

### GET /api/auth/sessions
**Description:** Get user's active sessions
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`

**Response:**
```json
{
  "sessions": [
    {
      "id": "uuid",
      "created_at": "timestamp",
      "last_accessed_at": "timestamp",
      "expires_at": "timestamp",
      "ip_address": "string",
      "device_type": "string",
      "browser": "string",
      "os": "string",
      "country": "string",
      "city": "string",
      "is_current": "boolean",
      "is_active": "boolean"
    }
  ],
  "total_sessions": "number"
}
```

### DELETE /api/auth/sessions/:id
**Description:** Terminate specific session
**Method:** DELETE
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Session ID

**Response:**
```json
{
  "message": "Session terminated successfully"
}
```

### DELETE /api/auth/sessions/all
**Description:** Terminate all sessions except current
**Method:** DELETE
**Headers:**
- `Authorization: Bearer {access_token}`

**Response:**
```json
{
  "message": "All other sessions terminated successfully",
  "terminated_count": "number"
}
```

## Two-Factor Authentication

### POST /api/auth/2fa/enable
**Description:** Enable two-factor authentication
**Method:** POST
**Headers:**
- `Authorization: Bearer {access_token}`

**Response:**
```json
{
  "qr_code": "string (base64 image)",
  "backup_codes": ["array of backup codes"],
  "secret": "string"
}
```

### POST /api/auth/2fa/verify
**Description:** Verify and confirm 2FA setup
**Method:** POST
**Headers:**
- `Authorization: Bearer {access_token}`

**Body:**
```json
{
  "code": "string (required, 6-digit code)"
}
```

**Response:**
```json
{
  "message": "Two-factor authentication enabled successfully",
  "backup_codes": ["array of backup codes"]
}
```

### POST /api/auth/2fa/disable
**Description:** Disable two-factor authentication
**Method:** POST
**Headers:**
- `Authorization: Bearer {access_token}`

**Body:**
```json
{
  "password": "string (required)",
  "code": "string (required, 6-digit code or backup code)"
}
```

**Response:**
```json
{
  "message": "Two-factor authentication disabled successfully"
}
```

### POST /api/auth/2fa/verify-login
**Description:** Verify 2FA code during login
**Method:** POST
**Body:**
```json
{
  "email": "string (required)",
  "password": "string (required)",
  "code": "string (required, 6-digit code or backup code)"
}
```

**Response:**
```json
{
  "user": {
    "id": "uuid",
    "email": "string",
    "full_name": "string",
    "role": {
      "id": "uuid",
      "name": "string",
      "permissions": ["array"]
    }
  },
  "tokens": {
    "access_token": "string",
    "refresh_token": "string",
    "expires_at": "timestamp",
    "token_type": "Bearer"
  }
}
```

## Security & Monitoring

### GET /api/auth/security/login-history
**Description:** Get user's login history
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `page` (number, default: 1)
- `limit` (number, default: 20)
- `days` (number, default: 30) - Number of days to look back

**Response:**
```json
{
  "login_history": [
    {
      "id": "uuid",
      "event_type": "string",
      "success": "boolean",
      "ip_address": "string",
      "country": "string",
      "city": "string",
      "user_agent": "string",
      "risk_score": "number",
      "failure_reason": "string",
      "created_at": "timestamp"
    }
  ],
  "pagination": {
    "page": "number",
    "limit": "number",
    "total": "number",
    "total_pages": "number"
  },
  "security_summary": {
    "successful_logins": "number",
    "failed_attempts": "number",
    "unique_locations": "number",
    "suspicious_activities": "number"
  }
}
```

### GET /api/auth/security/risk-assessment
**Description:** Get current security risk assessment
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`

**Response:**
```json
{
  "risk_score": "number (0-100)",
  "risk_level": "low|medium|high|critical",
  "factors": [
    {
      "type": "string",
      "description": "string",
      "impact": "number",
      "recommendation": "string"
    }
  ],
  "recommendations": [
    {
      "action": "string",
      "priority": "low|medium|high",
      "description": "string"
    }
  ]
}
```

### POST /api/auth/security/report-suspicious
**Description:** Report suspicious activity
**Method:** POST
**Headers:**
- `Authorization: Bearer {access_token}`

**Body:**
```json
{
  "activity_type": "string (required)",
  "description": "string (required)",
  "additional_info": "object (optional)"
}
```

**Response:**
```json
{
  "message": "Suspicious activity reported successfully",
  "report_id": "uuid"
}
```

## Account Verification

### POST /api/auth/verify-email
**Description:** Verify email address using verification token
**Method:** POST
**Body:**
```json
{
  "token": "string (required)"
}
```

**Response:**
```json
{
  "message": "Email verified successfully",
  "user": {
    "id": "uuid",
    "email": "string",
    "email_verified_at": "timestamp"
  }
}
```

### POST /api/auth/resend-verification
**Description:** Resend email verification
**Method:** POST
**Headers:**
- `Authorization: Bearer {access_token}`

**Response:**
```json
{
  "message": "Verification email sent successfully"
}
```

## System Logs & Audit

### GET /api/auth/logs
**Description:** Get authentication logs (admin only)
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}` (admin permission required)
**Query Parameters:**
- `page` (number, default: 1)
- `limit` (number, default: 50)
- `user_id` (UUID, optional) - Filter by user
- `event_type` (string, optional) - Filter by event type
- `success` (boolean, optional) - Filter by success status
- `start_date` (date, optional) - Filter by date range
- `end_date` (date, optional) - Filter by date range
- `ip_address` (string, optional) - Filter by IP address

**Response:**
```json
{
  "logs": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "user_email": "string",
      "event_type": "string",
      "success": "boolean",
      "ip_address": "string",
      "user_agent": "string",
      "country": "string",
      "city": "string",
      "risk_score": "number",
      "failure_reason": "string",
      "session_id": "uuid",
      "created_at": "timestamp"
    }
  ],
  "pagination": {
    "page": "number",
    "limit": "number",
    "total": "number",
    "total_pages": "number"
  },
  "summary": {
    "total_events": "number",
    "successful_events": "number",
    "failed_events": "number",
    "unique_users": "number",
    "unique_ips": "number"
  }
}
```
