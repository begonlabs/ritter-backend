# History Module API Endpoints

## Activity History

### GET /api/history/activities
**Description:** Get comprehensive activity history with filtering
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `page` (number, default: 1) - Page number
- `limit` (number, default: 50) - Items per page
- `user_id` (UUID, optional) - Filter by user
- `activity_type` (string, optional) - Filter by activity type
- `resource_type` (string, optional) - Filter by resource type
- `start_date` (date, optional) - Filter by date range
- `end_date` (date, optional) - Filter by date range
- `search` (string, optional) - Search in descriptions

**Response:**
```json
{
  "activities": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "user_name": "string",
      "user_email": "string",
      "activity_type": "string",
      "action": "string",
      "description": "string",
      "resource_type": "string",
      "resource_id": "uuid",
      "ip_address": "string",
      "user_agent": "string",
      "before_data": "object",
      "after_data": "object",
      "changes": "object",
      "execution_time_ms": "number",
      "response_status": "number",
      "timestamp": "timestamp"
    }
  ],
  "pagination": {
    "page": "number",
    "limit": "number",
    "total": "number",
    "total_pages": "number"
  },
  "summary": {
    "total_activities": "number",
    "unique_users": "number",
    "activity_types": "object",
    "date_range": {
      "earliest": "date",
      "latest": "date"
    }
  }
}
```

### GET /api/history/activities/:id
**Description:** Get specific activity details
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Activity ID

**Response:**
```json
{
  "activity": {
    "id": "uuid",
    "user_id": "uuid",
    "user_name": "string",
    "user_email": "string",
    "activity_type": "string",
    "action": "string",
    "description": "string",
    "resource_type": "string",
    "resource_id": "uuid",
    "ip_address": "string",
    "user_agent": "string",
    "browser_info": "object",
    "device_info": "object",
    "location_info": "object",
    "before_data": "object",
    "after_data": "object",
    "changes": "object",
    "execution_time_ms": "number",
    "response_status": "number",
    "timestamp": "timestamp"
  },
  "related_activities": [
    {
      "id": "uuid",
      "activity_type": "string",
      "action": "string",
      "timestamp": "timestamp",
      "relation": "same_session|same_resource|same_user"
    }
  ]
}
```

### GET /api/history/timeline/:user_id
**Description:** Get user activity timeline
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `user_id` (UUID) - User ID
**Query Parameters:**
- `days_back` (number, default: 30) - Days to look back
- `limit` (number, default: 100) - Maximum activities to return

**Response:**
```json
{
  "timeline": [
    {
      "activity_id": "uuid",
      "activity_time": "timestamp",
      "activity_type": "string",
      "action": "string",
      "description": "string",
      "resource_type": "string",
      "resource_name": "string",
      "details": "object"
    }
  ],
  "user_info": {
    "user_id": "uuid",
    "user_name": "string",
    "email": "string",
    "total_activities": "number",
    "period_analyzed": "string"
  },
  "summary": {
    "activities_by_type": "object",
    "activities_by_day": [
      {
        "date": "date",
        "count": "number"
      }
    ],
    "most_active_day": {
      "date": "date",
      "count": "number"
    }
  }
}
```

## Campaign History

### GET /api/history/campaigns
**Description:** Get campaign history with status tracking
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `page` (number, default: 1) - Page number
- `limit` (number, default: 25) - Items per page
- `status` (string, optional) - Filter by campaign status
- `user_id` (UUID, optional) - Filter by creator
- `start_date` (date, optional) - Filter by creation date
- `end_date` (date, optional) - Filter by creation date

**Response:**
```json
{
  "campaigns": [
    {
      "campaign_id": "uuid",
      "campaign_name": "string",
      "status": "string",
      "created_at": "timestamp",
      "started_at": "timestamp",
      "completed_at": "timestamp",
      "total_recipients": "number",
      "emails_sent": "number",
      "emails_delivered": "number",
      "emails_opened": "number",
      "emails_clicked": "number",
      "open_rate": "number",
      "click_rate": "number",
      "created_by_name": "string",
      "template_name": "string",
      "status_type": "success|error|warning|info"
    }
  ],
  "pagination": {
    "page": "number",
    "limit": "number",
    "total": "number",
    "total_pages": "number"
  },
  "statistics": {
    "total_campaigns": "number",
    "successful_campaigns": "number",
    "failed_campaigns": "number",
    "avg_open_rate": "number",
    "total_emails_sent": "number"
  }
}
```

### GET /api/history/campaigns/:id/execution
**Description:** Get detailed campaign execution history
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Campaign ID

**Response:**
```json
{
  "execution_history": [
    {
      "event_time": "timestamp",
      "event_type": "string",
      "event_description": "string",
      "recipient_email": "string",
      "status": "string",
      "details": "object"
    }
  ],
  "campaign_summary": {
    "campaign_id": "uuid",
    "campaign_name": "string",
    "total_events": "number",
    "campaign_created": "timestamp",
    "campaign_started": "timestamp",
    "campaign_completed": "timestamp",
    "duration_minutes": "number"
  },
  "performance_breakdown": {
    "creation_phase": {
      "duration_seconds": "number",
      "events": "number"
    },
    "sending_phase": {
      "duration_seconds": "number",
      "emails_per_minute": "number",
      "success_rate": "number"
    },
    "completion_phase": {
      "final_metrics": "object"
    }
  }
}
```

## Search History

### GET /api/history/searches
**Description:** Get detailed search history with results
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `page` (number, default: 1) - Page number
- `limit` (number, default: 25) - Items per page
- `user_id` (UUID, optional) - Filter by user
- `status` (string, optional) - Filter by search status
- `start_date` (date, optional) - Filter by search date
- `end_date` (date, optional) - Filter by search date

**Response:**
```json
{
  "searches": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "user_name": "string",
      "query_name": "string",
      "search_parameters": "object",
      "filters_applied": "object",
      "status": "string",
      "total_results": "number",
      "valid_results": "number",
      "duplicate_results": "number",
      "execution_time_ms": "number",
      "pages_scraped": "number",
      "websites_searched": "array",
      "started_at": "timestamp",
      "completed_at": "timestamp",
      "config_name": "string",
      "status_type": "success|error|warning|info",
      "duration_seconds": "number"
    }
  ],
  "pagination": {
    "page": "number",
    "limit": "number",
    "total": "number",
    "total_pages": "number"
  },
  "performance_summary": {
    "total_searches": "number",
    "successful_searches": "number",
    "avg_execution_time": "number",
    "total_results_found": "number",
    "avg_success_rate": "number"
  }
}
```

### GET /api/history/searches/performance
**Description:** Get search performance history and trends
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `user_id` (UUID, optional) - Filter by user
- `days_back` (number, default: 30) - Days to analyze

**Response:**
```json
{
  "performance_trends": [
    {
      "search_date": "date",
      "total_searches": "number",
      "successful_searches": "number",
      "failed_searches": "number",
      "avg_results_per_search": "number",
      "avg_execution_time_seconds": "number",
      "success_rate": "number"
    }
  ],
  "summary": {
    "period_analyzed": "string",
    "total_searches": "number",
    "overall_success_rate": "number",
    "best_day": {
      "date": "date",
      "searches": "number",
      "success_rate": "number"
    },
    "trends": {
      "search_volume_trend": "up|down|stable",
      "success_rate_trend": "up|down|stable",
      "performance_trend": "improving|declining|stable"
    }
  }
}
```

## Session History

### GET /api/history/sessions
**Description:** Get user session history
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `page` (number, default: 1) - Page number
- `limit` (number, default: 25) - Items per page
- `user_id` (UUID, optional) - Filter by user (admin only)
- `days_back` (number, default: 30) - Days to look back

**Response:**
```json
{
  "sessions": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "user_name": "string",
      "user_email": "string",
      "login_time": "timestamp",
      "logout_at": "timestamp",
      "logout_reason": "string",
      "ip_address": "string",
      "device_type": "string",
      "browser": "string",
      "os": "string",
      "country": "string",
      "city": "string",
      "is_active": "boolean",
      "session_duration_seconds": "number"
    }
  ],
  "pagination": {
    "page": "number",
    "limit": "number",
    "total": "number",
    "total_pages": "number"
  },
  "session_analytics": {
    "total_sessions": "number",
    "active_sessions": "number",
    "avg_session_duration": "number (minutes)",
    "most_used_device": "string",
    "most_common_location": "string",
    "login_patterns": {
      "peak_hours": "array",
      "peak_days": "array"
    }
  }
}
```

## Authentication History

### GET /api/history/authentication
**Description:** Get authentication event history
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `page` (number, default: 1) - Page number
- `limit` (number, default: 50) - Items per page
- `user_id` (UUID, optional) - Filter by user
- `event_type` (string, optional) - Filter by event type
- `success` (boolean, optional) - Filter by success status
- `days_back` (number, default: 30) - Days to look back
- `risk_threshold` (number, optional) - Filter by risk score

**Response:**
```json
{
  "auth_history": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "user_name": "string",
      "user_email": "string",
      "attempted_email": "string",
      "event_type": "string",
      "success": "boolean",
      "failure_reason": "string",
      "risk_score": "number",
      "ip_address": "string",
      "country": "string",
      "city": "string",
      "created_at": "timestamp",
      "alert_level": "success|warning|danger|info"
    }
  ],
  "pagination": {
    "page": "number",
    "limit": "number",
    "total": "number",
    "total_pages": "number"
  },
  "security_summary": {
    "total_events": "number",
    "successful_logins": "number",
    "failed_attempts": "number",
    "suspicious_activities": "number",
    "unique_ips": "number",
    "high_risk_events": "number"
  }
}
```

## Data Export & Archival

### GET /api/history/export
**Description:** Export historical data
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `type` (string, required) - Export type: activities, campaigns, searches, sessions, auth
- `format` (string, default: "json") - Export format: json, csv, xlsx
- `start_date` (date, required) - Start date for export
- `end_date` (date, required) - End date for export
- `user_id` (UUID, optional) - Filter by user
- `include_details` (boolean, default: false) - Include detailed data

**Response:**
```json
{
  "export": {
    "id": "uuid",
    "type": "string",
    "format": "string",
    "status": "generating|completed|failed",
    "file_url": "string",
    "file_name": "string",
    "file_size": "number (bytes)",
    "total_records": "number",
    "date_range": {
      "start": "date",
      "end": "date"
    },
    "created_at": "timestamp",
    "expires_at": "timestamp"
  },
  "message": "Export started successfully"
}
```

### GET /api/history/export/:id/status
**Description:** Get export job status
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Export job ID

**Response:**
```json
{
  "export": {
    "id": "uuid",
    "type": "string",
    "status": "generating|completed|failed",
    "progress": "number (0-100)",
    "file_url": "string",
    "file_size": "number",
    "total_records": "number",
    "processed_records": "number",
    "error_message": "string",
    "created_at": "timestamp",
    "completed_at": "timestamp",
    "expires_at": "timestamp"
  }
}
```

### POST /api/history/archive
**Description:** Archive old historical data
**Method:** POST
**Headers:**
- `Authorization: Bearer {access_token}` (admin permission required)
**Body:**
```json
{
  "days_to_keep": "number (required)",
  "data_types": ["array of data types to archive"],
  "compress": "boolean (default: true)",
  "delete_after_archive": "boolean (default: false)"
}
```

**Response:**
```json
{
  "archive": {
    "id": "uuid",
    "status": "processing|completed|failed",
    "data_types": "array",
    "days_to_keep": "number",
    "estimated_records": "number",
    "started_at": "timestamp"
  },
  "message": "Archival process started"
}
```

## Analytics & Insights

### GET /api/history/analytics/summary
**Description:** Get historical analytics summary
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `period` (string, default: "30d") - Analysis period
- `user_id` (UUID, optional) - Filter by user

**Response:**
```json
{
  "analytics": {
    "user_activity": {
      "most_active_users": [
        {
          "user_id": "uuid",
          "user_name": "string",
          "activity_count": "number",
          "primary_activities": "array"
        }
      ],
      "activity_patterns": {
        "peak_hours": "array",
        "peak_days": "array",
        "seasonal_trends": "object"
      }
    },
    "performance_insights": {
      "search_effectiveness": {
        "avg_success_rate": "number",
        "improvement_trend": "string",
        "top_performing_configs": "array"
      },
      "campaign_effectiveness": {
        "avg_performance": "number",
        "best_practices": "array",
        "improvement_areas": "array"
      }
    },
    "system_usage": {
      "resource_utilization": "object",
      "feature_adoption": "object",
      "user_engagement": "object"
    }
  }
}
```

### GET /api/history/analytics/trends
**Description:** Get historical trend analysis
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `metric` (string, required) - Metric to analyze
- `period` (string, default: "90d") - Analysis period
- `granularity` (string, default: "day") - Data granularity

**Response:**
```json
{
  "trends": {
    "data_points": [
      {
        "date": "date",
        "value": "number",
        "moving_average": "number",
        "trend_indicator": "up|down|stable"
      }
    ],
    "analysis": {
      "overall_trend": "string",
      "growth_rate": "number",
      "volatility": "string",
      "seasonal_patterns": "object",
      "predictions": {
        "next_7_days": "array",
        "confidence_level": "number"
      }
    }
  }
}
```
