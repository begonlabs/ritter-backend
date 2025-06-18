# Campaigns Module API Endpoints

## Email Templates

### GET /api/campaigns/templates
**Description:** Get list of email templates with filtering
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `page` (number, default: 1) - Page number
- `limit` (number, default: 25) - Items per page
- `category` (string, optional) - Filter by category
- `status` (string, optional) - Filter by status: active, inactive, archived
- `search` (string, optional) - Search by name or description

**Response:**
```json
{
  "templates": [
    {
      "id": "uuid",
      "name": "string",
      "description": "string",
      "category": "string",
      "subject": "string",
      "body_html": "string",
      "body_text": "string",
      "variables": ["array of variable names"],
      "preview_text": "string",
      "status": "active|inactive|archived",
      "usage_count": "number",
      "success_rate": "number (percentage)",
      "open_rate": "number (percentage)",
      "click_rate": "number (percentage)",
      "created_by": "uuid",
      "created_by_name": "string",
      "created_at": "timestamp",
      "updated_at": "timestamp",
      "last_used_at": "timestamp"
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

### GET /api/campaigns/templates/:id
**Description:** Get specific email template details
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Template ID

**Response:**
```json
{
  "template": {
    "id": "uuid",
    "name": "string",
    "description": "string",
    "category": "string",
    "subject": "string",
    "body_html": "string",
    "body_text": "string",
    "variables": [
      {
        "name": "string",
        "type": "string",
        "default_value": "string",
        "is_required": "boolean",
        "description": "string"
      }
    ],
    "preview_text": "string",
    "status": "string",
    "usage_count": "number",
    "success_rate": "number",
    "open_rate": "number",
    "click_rate": "number",
    "created_by": "uuid",
    "created_by_name": "string",
    "created_at": "timestamp",
    "updated_at": "timestamp",
    "last_used_at": "timestamp"
  },
  "usage_stats": {
    "total_campaigns": "number",
    "total_emails_sent": "number",
    "recent_campaigns": [
      {
        "id": "uuid",
        "name": "string",
        "created_at": "timestamp",
        "open_rate": "number"
      }
    ]
  }
}
```

### POST /api/campaigns/templates
**Description:** Create new email template
**Method:** POST
**Headers:**
- `Authorization: Bearer {access_token}`
**Body:**
```json
{
  "name": "string (required)",
  "description": "string (optional)",
  "category": "string (optional)",
  "subject": "string (required)",
  "body_html": "string (required)",
  "body_text": "string (optional)",
  "variables": [
    {
      "name": "string (required)",
      "type": "string (required)",
      "default_value": "string (optional)",
      "is_required": "boolean (default: false)",
      "description": "string (optional)"
    }
  ],
  "preview_text": "string (optional)"
}
```

**Response:**
```json
{
  "template": {
    "id": "uuid",
    "name": "string",
    "description": "string",
    "category": "string",
    "subject": "string",
    "body_html": "string",
    "body_text": "string",
    "variables": "array",
    "status": "active",
    "created_by": "uuid",
    "created_at": "timestamp"
  },
  "message": "Email template created successfully"
}
```

### PUT /api/campaigns/templates/:id
**Description:** Update email template
**Method:** PUT
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Template ID
**Body:**
```json
{
  "name": "string (optional)",
  "description": "string (optional)",
  "category": "string (optional)",
  "subject": "string (optional)",
  "body_html": "string (optional)",
  "body_text": "string (optional)",
  "variables": "array (optional)",
  "preview_text": "string (optional)",
  "status": "string (optional)"
}
```

**Response:**
```json
{
  "template": {
    "id": "uuid",
    "name": "string",
    "updated_at": "timestamp"
  },
  "message": "Email template updated successfully"
}
```

### DELETE /api/campaigns/templates/:id
**Description:** Delete email template (soft delete - set status to archived)
**Method:** DELETE
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Template ID

**Response:**
```json
{
  "message": "Email template deleted successfully"
}
```

### POST /api/campaigns/templates/:id/duplicate
**Description:** Duplicate email template
**Method:** POST
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Template ID to duplicate
**Body:**
```json
{
  "name": "string (required)",
  "description": "string (optional)"
}
```

**Response:**
```json
{
  "template": {
    "id": "uuid",
    "name": "string",
    "created_at": "timestamp"
  },
  "message": "Template duplicated successfully"
}
```

## Campaigns

### GET /api/campaigns
**Description:** Get list of campaigns with filtering
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `page` (number, default: 1) - Page number
- `limit` (number, default: 25) - Items per page
- `status` (string, optional) - Filter by status
- `template_id` (UUID, optional) - Filter by template
- `created_by` (UUID, optional) - Filter by creator
- `search` (string, optional) - Search by name or description

**Response:**
```json
{
  "campaigns": [
    {
      "id": "uuid",
      "name": "string",
      "description": "string",
      "template_id": "uuid",
      "template_name": "string",
      "subject": "string",
      "from_name": "string",
      "from_email": "string",
      "status": "draft|scheduled|sending|sent|completed|cancelled|failed",
      "scheduled_at": "timestamp",
      "started_at": "timestamp",
      "completed_at": "timestamp",
      "total_recipients": "number",
      "emails_sent": "number",
      "emails_delivered": "number",
      "emails_opened": "number",
      "emails_clicked": "number",
      "emails_bounced": "number",
      "emails_unsubscribed": "number",
      "open_rate": "number (percentage)",
      "click_rate": "number (percentage)",
      "bounce_rate": "number (percentage)",
      "unsubscribe_rate": "number (percentage)",
      "created_by": "uuid",
      "created_by_name": "string",
      "created_at": "timestamp",
      "updated_at": "timestamp"
    }
  ],
  "pagination": {
    "page": "number",
    "limit": "number",
    "total": "number",
    "total_pages": "number"
  },
  "summary": {
    "total_campaigns": "number",
    "active_campaigns": "number",
    "completed_campaigns": "number",
    "avg_open_rate": "number"
  }
}
```

### GET /api/campaigns/:id
**Description:** Get specific campaign details
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Campaign ID

**Response:**
```json
{
  "campaign": {
    "id": "uuid",
    "name": "string",
    "description": "string",
    "template_id": "uuid",
    "template": {
      "id": "uuid",
      "name": "string",
      "subject": "string",
      "body_html": "string"
    },
    "subject": "string",
    "from_name": "string",
    "from_email": "string",
    "reply_to": "string",
    "status": "string",
    "scheduled_at": "timestamp",
    "started_at": "timestamp",
    "completed_at": "timestamp",
    "target_leads": ["array of lead IDs"],
    "filters": "object",
    "total_recipients": "number",
    "emails_sent": "number",
    "emails_delivered": "number",
    "emails_opened": "number",
    "emails_clicked": "number",
    "emails_bounced": "number",
    "emails_unsubscribed": "number",
    "open_rate": "number",
    "click_rate": "number",
    "bounce_rate": "number",
    "unsubscribe_rate": "number",
    "conversion_rate": "number",
    "settings": "object",
    "metadata": "object",
    "created_by": "uuid",
    "created_by_name": "string",
    "created_at": "timestamp",
    "updated_at": "timestamp"
  }
}
```

### POST /api/campaigns
**Description:** Create new campaign
**Method:** POST
**Headers:**
- `Authorization: Bearer {access_token}`
**Body:**
```json
{
  "name": "string (required)",
  "description": "string (optional)",
  "template_id": "uuid (required)",
  "subject": "string (optional, will use template subject if not provided)",
  "from_name": "string (required)",
  "from_email": "string (required)",
  "reply_to": "string (optional)",
  "scheduled_at": "timestamp (optional)",
  "target_leads": ["array of lead IDs (required)"],
  "filters": "object (optional)",
  "settings": "object (optional)"
}
```

**Response:**
```json
{
  "campaign": {
    "id": "uuid",
    "name": "string",
    "status": "draft",
    "total_recipients": "number",
    "created_at": "timestamp"
  },
  "message": "Campaign created successfully"
}
```

### PUT /api/campaigns/:id
**Description:** Update campaign (only if status is draft)
**Method:** PUT
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Campaign ID
**Body:**
```json
{
  "name": "string (optional)",
  "description": "string (optional)",
  "subject": "string (optional)",
  "from_name": "string (optional)",
  "from_email": "string (optional)",
  "reply_to": "string (optional)",
  "scheduled_at": "timestamp (optional)",
  "target_leads": ["array of lead IDs (optional)"],
  "settings": "object (optional)"
}
```

**Response:**
```json
{
  "campaign": {
    "id": "uuid",
    "name": "string",
    "updated_at": "timestamp"
  },
  "message": "Campaign updated successfully"
}
```

### POST /api/campaigns/:id/send
**Description:** Send campaign immediately or schedule for later
**Method:** POST
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Campaign ID
**Body:**
```json
{
  "send_immediately": "boolean (default: true)",
  "scheduled_at": "timestamp (required if send_immediately is false)"
}
```

**Response:**
```json
{
  "campaign": {
    "id": "uuid",
    "status": "scheduled|sending",
    "scheduled_at": "timestamp",
    "started_at": "timestamp"
  },
  "message": "Campaign scheduled successfully" 
}
```

### POST /api/campaigns/:id/cancel
**Description:** Cancel campaign (only if status is scheduled or sending)
**Method:** POST
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Campaign ID

**Response:**
```json
{
  "campaign": {
    "id": "uuid",
    "status": "cancelled"
  },
  "message": "Campaign cancelled successfully"
}
```

### DELETE /api/campaigns/:id
**Description:** Delete campaign (only if status is draft or cancelled)
**Method:** DELETE
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Campaign ID

**Response:**
```json
{
  "message": "Campaign deleted successfully"
}
```

## Campaign Recipients

### GET /api/campaigns/:id/recipients
**Description:** Get campaign recipients with status breakdown
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Campaign ID
**Query Parameters:**
- `page` (number, default: 1) - Page number
- `limit` (number, default: 50) - Items per page
- `status` (string, optional) - Filter by email status
- `search` (string, optional) - Search by email address

**Response:**
```json
{
  "recipients": [
    {
      "id": "uuid",
      "lead_id": "uuid",
      "email_address": "string",
      "personalization_data": "object",
      "status": "pending|sent|delivered|opened|clicked|bounced|failed|unsubscribed",
      "sent_at": "timestamp",
      "delivered_at": "timestamp",
      "opened_at": "timestamp",
      "first_opened_at": "timestamp",
      "clicked_at": "timestamp",
      "first_clicked_at": "timestamp",
      "bounced_at": "timestamp",
      "unsubscribed_at": "timestamp",
      "open_count": "number",
      "click_count": "number",
      "last_activity_at": "timestamp",
      "error_message": "string",
      "retry_count": "number"
    }
  ],
  "pagination": {
    "page": "number",
    "limit": "number",
    "total": "number",
    "total_pages": "number"
  },
  "status_breakdown": {
    "pending": "number",
    "sent": "number",
    "delivered": "number",
    "opened": "number",
    "clicked": "number",
    "bounced": "number",
    "failed": "number",
    "unsubscribed": "number"
  }
}
```

### POST /api/campaigns/:id/recipients
**Description:** Add leads to campaign (only if status is draft)
**Method:** POST
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Campaign ID
**Body:**
```json
{
  "lead_ids": ["array of UUIDs (required)"]
}
```

**Response:**
```json
{
  "added_count": "number",
  "total_recipients": "number",
  "message": "Recipients added successfully"
}
```

### DELETE /api/campaigns/:id/recipients/:recipient_id
**Description:** Remove recipient from campaign (only if status is draft)
**Method:** DELETE
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Campaign ID
- `recipient_id` (UUID) - Recipient ID

**Response:**
```json
{
  "message": "Recipient removed successfully"
}
```

## Campaign Performance

### GET /api/campaigns/:id/performance
**Description:** Get detailed campaign performance metrics
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Campaign ID

**Response:**
```json
{
  "performance": {
    "campaign_id": "uuid",
    "campaign_name": "string",
    "total_recipients": "number",
    "emails_sent": "number",
    "emails_delivered": "number",
    "emails_opened": "number",
    "emails_clicked": "number",
    "emails_bounced": "number",
    "emails_unsubscribed": "number",
    "open_rate": "number",
    "click_rate": "number",
    "bounce_rate": "number",
    "unsubscribe_rate": "number",
    "status": "string",
    "created_at": "timestamp",
    "completed_at": "timestamp"
  },
  "timeline": [
    {
      "date": "date",
      "emails_sent": "number",
      "emails_opened": "number",
      "emails_clicked": "number"
    }
  ],
  "top_links": [
    {
      "url": "string",
      "clicks": "number",
      "unique_clicks": "number"
    }
  ],
  "device_breakdown": {
    "desktop": "number",
    "mobile": "number",
    "tablet": "number"
  },
  "location_breakdown": [
    {
      "country": "string",
      "opens": "number",
      "clicks": "number"
    }
  ]
}
```

### GET /api/campaigns/:id/history
**Description:** Get campaign execution history and events
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Campaign ID

**Response:**
```json
{
  "history": [
    {
      "event_time": "timestamp",
      "event_type": "string",
      "event_description": "string",
      "recipient_email": "string",
      "status": "string",
      "details": "object"
    }
  ],
  "summary": {
    "total_events": "number",
    "campaign_created": "timestamp",
    "campaign_started": "timestamp",
    "campaign_completed": "timestamp",
    "duration_minutes": "number"
  }
}
```

## Template Categories

### GET /api/campaigns/templates/categories
**Description:** Get template categories
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`

**Response:**
```json
{
  "categories": [
    {
      "name": "string",
      "label": "string",
      "description": "string",
      "template_count": "number",
      "usage_count": "number"
    }
  ]
}
```

## Campaign Analytics

### GET /api/campaigns/analytics/summary
**Description:** Get campaigns analytics summary
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `start_date` (date, optional) - Start date for analysis
- `end_date` (date, optional) - End date for analysis
- `user_id` (UUID, optional) - Filter by user

**Response:**
```json
{
  "summary": {
    "total_campaigns": "number",
    "total_emails_sent": "number",
    "avg_open_rate": "number",
    "avg_click_rate": "number",
    "avg_bounce_rate": "number",
    "best_performing_campaign": {
      "id": "uuid",
      "name": "string",
      "open_rate": "number"
    },
    "most_used_template": {
      "id": "uuid",
      "name": "string",
      "usage_count": "number"
    }
  },
  "trends": {
    "monthly_campaigns": [
      {
        "month": "string",
        "campaigns": "number",
        "emails_sent": "number",
        "avg_open_rate": "number"
      }
    ]
  }
}
```
