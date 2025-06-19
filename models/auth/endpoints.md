# Auth Module API Endpoints - Supabase Adapted

## 🔧 Integración con Supabase Auth

**IMPORTANTE:** La mayoría de endpoints de autenticación los maneja Supabase directamente. FastAPI solo necesita validar tokens y manejar lógica de negocio adicional.

## Endpoints FastAPI - Solo lógica de negocio

### GET /api/auth/profile
**Description:** Get current user profile with role information
**Method:** GET
**Headers:**
- `Authorization: Bearer {supabase_jwt_token}`

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
    "last_activity_at": "timestamp",
    "created_at": "timestamp"
  }
}
```

### PUT /api/auth/profile
**Description:** Update user profile information
**Method:** PUT
**Headers:**
- `Authorization: Bearer {supabase_jwt_token}`

**Body:**
```json
{
  "full_name": "string (optional)",
  "metadata": "object (optional)"
}
```

**Response:**
```json
{
  "message": "Profile updated successfully",
  "user": {
    "id": "uuid",
    "full_name": "string",
    "updated_at": "timestamp"
  }
}
```

### GET /api/auth/permissions
**Description:** Get current user permissions
**Method:** GET
**Headers:**
- `Authorization: Bearer {supabase_jwt_token}`

**Response:**
```json
{
  "permissions": [
    {
      "name": "string",
      "description": "string", 
      "category": "string",
      "resource": "string",
      "action": "string"
    }
  ],
  "role": {
    "id": "uuid",
    "name": "string"
  }
}
```

## 📧 Invitaciones (Admin only)

### POST /api/auth/invite-user
**Description:** Invite new user (uses Supabase Admin API)
**Method:** POST
**Headers:**
- `Authorization: Bearer {supabase_jwt_token}`
**Permissions Required:** `admin.users.create`

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
  "message": "User invited successfully",
  "user": {
    "id": "uuid",
    "email": "string",
    "full_name": "string",
    "invited_at": "timestamp"
  }
}
```

## 🔐 Endpoints manejados directamente por Supabase

### Estos NO necesitan implementarse en FastAPI:

```javascript
// Login
supabase.auth.signInWithPassword({ email, password })

// Logout  
supabase.auth.signOut()

// Password Reset
supabase.auth.resetPasswordForEmail(email)

// Update Password
supabase.auth.updateUser({ password: newPassword })

// 2FA Setup
supabase.auth.mfa.enroll({ factorType: 'totp' })

// 2FA Verify
supabase.auth.mfa.verify({ factorId, challengeId, code })

// Session Management
supabase.auth.getSession()
supabase.auth.refreshSession()
```

## 📝 Logs de Actividad

### POST /api/auth/log-activity
**Description:** Log user activity (internal use)
**Method:** POST
**Headers:**
- `Authorization: Bearer {supabase_jwt_token}`

**Body:**
```json
{
  "activity_type": "string (required)",
  "action": "string (required)", 
  "description": "string (optional)",
  "resource_type": "string (optional)",
  "resource_id": "uuid (optional)"
}
```

**Response:**
```json
{
  "message": "Activity logged successfully"
}
```

## 🛡️ Middleware de Autenticación FastAPI

```python
# Ejemplo de middleware para validar tokens Supabase
from supabase import create_client
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    try:
        # Verificar token con Supabase
        response = supabase.auth.get_user(token.credentials)
        
        if response.user:
            # Obtener perfil y rol del usuario
            profile = await get_user_profile(response.user.id)
            return profile
        else:
            raise HTTPException(status_code=401, detail="Invalid token")
            
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")
``` 