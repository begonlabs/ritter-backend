# Analytics Module API Endpoints

## Dashboard Metrics

### GET /api/analytics/dashboard/stats
**Description:** Get dashboard statistics for overview widget
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `period` (string, default: "daily") - Period type: daily, weekly, monthly
- `days` (number, default: 30) - Number of days to analyze

**Response:**
```json
{
  "stats": {
    "total_leads": "number",
    "total_campaigns": "number", 
    "total_searches": "number",
    "average_open_rate": "number (percentage)",
    "leads_quality_score": "number (1-5)",
    "campaign_success_rate": "number (percentage)",
    "search_efficiency": "number (percentage)",
    "cost_per_lead": "number",
    "roi_percentage": "number",
    "estimated_money_saved": "number",
    "cost_savings_percentage": "number"
  },
  "trends": {
    "leads_trend_percentage": "number",
    "campaigns_trend_percentage": "number", 
    "searches_trend_percentage": "number",
    "open_rate_trend_percentage": "number"
  },
  "period_info": {
    "current_period": "string",
    "previous_period": "string",
    "days_analyzed": "number"
  }
}
```

### GET /api/analytics/dashboard/recent-activity
**Description:** Get recent activity for dashboard widget
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `limit` (number, default: 10) - Number of activities to return

**Response:**
```json
{
  "activities": [
    {
      "id": "uuid",
      "user_name": "string",
      "activity_type": "string",
      "action": "string", 
      "description": "string",
      "resource_type": "string",
      "timestamp": "timestamp",
      "icon": "string",
      "color": "string"
    }
  ]
}
```

### GET /api/analytics/dashboard/trends
**Description:** Get trend data for dashboard charts
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `metric` (string, required) - Metric type: leads, campaigns, searches, open_rate
- `period` (string, default: "daily") - daily, weekly, monthly
- `days` (number, default: 30) - Days to analyze

**Response:**
```json
{
  "trends": [
    {
      "date": "date",
      "value": "number",
      "change": "number",
      "change_percentage": "number"
    }
  ],
  "summary": {
    "total": "number",
    "average": "number",
    "growth_rate": "number",
    "trend_direction": "up|down|stable"
  }
}
```

## Scraping Analytics

### GET /api/analytics/scraping/stats
**Description:** Get scraping performance statistics
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `user_id` (UUID, optional) - Filter by user
- `days` (number, default: 30) - Days to analyze
- `website` (string, optional) - Filter by website domain

**Response:**
```json
{
  "stats": {
    "total_sessions": "number",
    "total_leads_found": "number",
    "total_valid_leads": "number",
    "average_success_rate": "number (percentage)",
    "average_duration_minutes": "number",
    "total_pages_scraped": "number",
    "average_leads_per_session": "number",
    "money_saved": "number",
    "cost_savings_percentage": "number"
  },
  "performance": {
    "avg_page_load_time": "number (milliseconds)",
    "avg_requests_per_minute": "number",
    "total_bandwidth_mb": "number",
    "error_rate": "number (percentage)"
  },
  "trends": {
    "daily_sessions": [
      {
        "date": "date",
        "sessions": "number",
        "leads_found": "number",
        "success_rate": "number"
      }
    ]
  }
}
```

### GET /api/analytics/scraping/sources
**Description:** Get website sources performance rankings
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `limit` (number, default: 10) - Number of sources to return
- `sort_by` (string, default: "leads_found") - Sort by: leads_found, success_rate, usage_count

**Response:**
```json
{
  "sources": [
    {
      "id": "uuid",
      "website_name": "string",
      "domain": "string", 
      "total_leads_found": "number",
      "total_searches": "number",
      "success_rate": "number (percentage)",
      "average_leads_per_search": "number",
      "lead_quality_score": "number (1-5)",
      "validation_success_rate": "number (percentage)",
      "average_response_time_ms": "number",
      "last_used_at": "timestamp",
      "is_active": "boolean"
    }
  ],
  "summary": {
    "total_sources": "number",
    "active_sources": "number",
    "best_performing_source": "string",
    "total_leads_from_all_sources": "number"
  }
}
```

### POST /api/analytics/scraping/session
**Description:** Record scraping session statistics
**Method:** POST
**Headers:**
- `Authorization: Bearer {access_token}`
**Body:**
```json
{
  "search_history_id": "uuid (required)",
  "session_start": "timestamp (required)",
  "session_end": "timestamp (required)",
  "pages_visited": "number (required)",
  "leads_found": "number (required)",
  "leads_extracted": "number (required)", 
  "valid_leads": "number (required)",
  "duplicate_leads": "number (required)",
  "errors_encountered": "number (optional, default: 0)",
  "warnings_count": "number (optional, default: 0)",
  "error_details": "array (optional)",
  "avg_page_load_time": "number (optional)",
  "bandwidth_used_mb": "number (optional)"
}
```

**Response:**
```json
{
  "session": {
    "id": "uuid",
    "duration_minutes": "number",
    "success_rate": "number",
    "extraction_rate": "number",
    "validation_rate": "number",
    "created_at": "timestamp"
  },
  "message": "Scraping session recorded successfully"
}
```

## Performance Analytics

### GET /api/analytics/performance/summary
**Description:** Get overall performance analytics summary
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
    "leads": {
      "total": "number",
      "quality_distribution": {
        "score_1": "number",
        "score_2": "number", 
        "score_3": "number",
        "score_4": "number",
        "score_5": "number"
      },
      "verification_rates": {
        "email": "number (percentage)",
        "phone": "number (percentage)", 
        "website": "number (percentage)"
      }
    },
    "campaigns": {
      "total": "number",
      "avg_open_rate": "number (percentage)",
      "avg_click_rate": "number (percentage)",
      "avg_bounce_rate": "number (percentage)",
      "total_emails_sent": "number"
    },
    "searches": {
      "total": "number",
      "success_rate": "number (percentage)",
      "avg_results_per_search": "number",
      "avg_execution_time_seconds": "number"
    }
  },
  "top_performers": {
    "best_campaign": {
      "id": "uuid",
      "name": "string",
      "open_rate": "number"
    },
    "most_productive_user": {
      "id": "uuid", 
      "name": "string",
      "total_leads": "number"
    },
    "best_search_config": {
      "id": "uuid",
      "name": "string",
      "avg_results": "number"
    }
  }
}
```

### GET /api/analytics/performance/users
**Description:** Get user performance analytics
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}` (admin permission required)
**Query Parameters:**
- `days` (number, default: 30) - Days to analyze
- `sort_by` (string, default: "total_activity") - Sort by metric

**Response:**
```json
{
  "users": [
    {
      "user_id": "uuid",
      "user_name": "string",
      "email": "string",
      "role": "string",
      "total_searches": "number",
      "total_campaigns": "number", 
      "total_leads_found": "number",
      "avg_search_success_rate": "number",
      "avg_campaign_performance": "number",
      "last_activity": "timestamp",
      "activity_score": "number (0-100)"
    }
  ],
  "summary": {
    "total_users": "number",
    "active_users": "number",
    "most_active_user": "string",
    "avg_activity_score": "number"
  }
}
```

## Data Export & Reports

### GET /api/analytics/export/summary
**Description:** Export analytics summary as CSV/Excel
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `format` (string, default: "csv") - Export format: csv, xlsx, json
- `start_date` (date, optional) - Start date for export
- `end_date` (date, optional) - End date for export
- `include_details` (boolean, default: false) - Include detailed data

**Response:**
```json
{
  "export": {
    "file_url": "string",
    "file_name": "string",
    "file_size": "number (bytes)",
    "format": "string",
    "expires_at": "timestamp"
  },
  "summary": {
    "total_records": "number",
    "date_range": {
      "start": "date",
      "end": "date"
    }
  }
}
```

### POST /api/analytics/reports/custom
**Description:** Generate custom analytics report
**Method:** POST
**Headers:**
- `Authorization: Bearer {access_token}`
**Body:**
```json
{
  "report_name": "string (required)",
  "metrics": ["array of metric names (required)"],
  "filters": {
    "start_date": "date",
    "end_date": "date",
    "user_ids": ["array of UUIDs"],
    "campaign_ids": ["array of UUIDs"],
    "categories": ["array of strings"]
  },
  "grouping": "string (optional)", 
  "format": "string (default: json)"
}
```

**Response:**
```json
{
  "report": {
    "id": "uuid",
    "name": "string",
    "status": "generating|completed|failed",
    "file_url": "string",
    "created_at": "timestamp",
    "expires_at": "timestamp"
  },
  "message": "Custom report generation started"
}
```

### GET /api/analytics/reports/:id
**Description:** Get custom report status and download
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Report ID

**Response:**
```json
{
  "report": {
    "id": "uuid",
    "name": "string",
    "status": "generating|completed|failed",
    "file_url": "string",
    "file_size": "number",
    "progress": "number (0-100)",
    "error_message": "string",
    "created_at": "timestamp",
    "completed_at": "timestamp",
    "expires_at": "timestamp"
  }
}
```

## Real-time Analytics

### GET /api/analytics/realtime/activity
**Description:** Get real-time activity feed
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `limit` (number, default: 20) - Number of activities

**Response:**
```json
{
  "activities": [
    {
      "id": "uuid",
      "user_name": "string",
      "activity_type": "string",
      "description": "string",
      "timestamp": "timestamp",
      "metadata": "object"
    }
  ],
  "live_stats": {
    "active_users": "number",
    "ongoing_searches": "number",
    "campaigns_sending": "number",
    "system_load": "number (percentage)"
  }
}
```

### GET /api/analytics/realtime/metrics
**Description:** Get real-time metrics for dashboard
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`

**Response:**
```json
{
  "metrics": {
    "leads_today": "number",
    "campaigns_today": "number",
    "searches_today": "number",
    "active_sessions": "number",
    "avg_response_time": "number (milliseconds)",
    "error_rate": "number (percentage)"
  },
  "alerts": [
    {
      "type": "warning|error|info",
      "message": "string",
      "timestamp": "timestamp"
    }
  ],
  "timestamp": "timestamp"
}
```
