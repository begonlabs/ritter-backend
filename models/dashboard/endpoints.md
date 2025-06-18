# Dashboard Module API Endpoints

## Dashboard Overview

### GET /api/dashboard/overview
**Description:** Get dashboard overview statistics
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `period` (string, default: "30d") - Time period: 7d, 30d, 90d, 1y
- `user_id` (UUID, optional) - Filter by specific user (admin only)

**Response:**
```json
{
  "overview": {
    "total_leads": "number",
    "total_campaigns": "number",
    "total_searches": "number",
    "total_users": "number",
    "avg_open_rate": "number (percentage)",
    "avg_click_rate": "number (percentage)",
    "avg_lead_quality": "number (1-5)"
  },
  "growth_metrics": {
    "leads_growth": "number (percentage)",
    "campaigns_growth": "number (percentage)",
    "searches_growth": "number (percentage)",
    "users_growth": "number (percentage)"
  },
  "period_comparison": {
    "current_period": {
      "start_date": "date",
      "end_date": "date",
      "leads": "number",
      "campaigns": "number",
      "searches": "number"
    },
    "previous_period": {
      "start_date": "date",
      "end_date": "date",
      "leads": "number",
      "campaigns": "number",
      "searches": "number"
    }
  },
  "timestamp": "timestamp"
}
```

### GET /api/dashboard/summary
**Description:** Get comprehensive dashboard summary
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `start_date` (date, optional) - Start date for analysis
- `end_date` (date, optional) - End date for analysis

**Response:**
```json
{
  "summary": {
    "total_leads": "number",
    "total_campaigns": "number",
    "total_searches": "number",
    "active_users": "number",
    "avg_open_rate": "number",
    "avg_click_rate": "number",
    "avg_lead_quality": "number",
    "leads_growth_rate": "number",
    "campaigns_growth_rate": "number",
    "searches_growth_rate": "number"
  },
  "quick_stats": {
    "today": {
      "leads_created": "number",
      "campaigns_sent": "number",
      "searches_completed": "number",
      "active_sessions": "number"
    },
    "this_week": {
      "leads_created": "number",
      "campaigns_sent": "number",
      "searches_completed": "number",
      "new_users": "number"
    },
    "this_month": {
      "leads_created": "number",
      "campaigns_sent": "number",
      "searches_completed": "number",
      "total_revenue": "number"
    }
  }
}
```

## Activity Feed

### GET /api/dashboard/activity
**Description:** Get recent activity feed for dashboard
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `limit` (number, default: 20) - Number of activities to return
- `types` (array, optional) - Filter by activity types
- `user_id` (UUID, optional) - Filter by user

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
      "timestamp": "timestamp",
      "icon": "string",
      "color": "string",
      "priority": "low|medium|high"
    }
  ],
  "activity_summary": {
    "total_activities": "number",
    "activity_types": {
      "searches": "number",
      "campaigns": "number",
      "user_actions": "number",
      "system_events": "number"
    },
    "most_active_user": {
      "user_id": "uuid",
      "user_name": "string",
      "activity_count": "number"
    }
  }
}
```

### GET /api/dashboard/activity/timeline
**Description:** Get activity timeline for charts
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `period` (string, default: "24h") - Time period: 24h, 7d, 30d
- `granularity` (string, default: "hour") - Data granularity: minute, hour, day
- `activity_types` (array, optional) - Filter by activity types

**Response:**
```json
{
  "timeline": [
    {
      "timestamp": "timestamp",
      "activities": "number",
      "searches": "number",
      "campaigns": "number",
      "leads_created": "number"
    }
  ],
  "summary": {
    "period": "string",
    "granularity": "string",
    "total_data_points": "number",
    "peak_activity": {
      "timestamp": "timestamp",
      "count": "number"
    },
    "trends": {
      "searches_trend": "up|down|stable",
      "campaigns_trend": "up|down|stable",
      "overall_trend": "up|down|stable"
    }
  }
}
```

## Performance Metrics

### GET /api/dashboard/performance
**Description:** Get performance metrics for dashboard widgets
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `metrics` (array, optional) - Specific metrics to retrieve
- `period` (string, default: "30d") - Time period for analysis

**Response:**
```json
{
  "performance": {
    "lead_generation": {
      "total_leads": "number",
      "avg_quality_score": "number",
      "quality_distribution": {
        "high_quality": "number",
        "medium_quality": "number",
        "low_quality": "number"
      },
      "verification_rates": {
        "email": "number (percentage)",
        "phone": "number (percentage)",
        "website": "number (percentage)"
      }
    },
    "campaign_performance": {
      "total_campaigns": "number",
      "avg_open_rate": "number",
      "avg_click_rate": "number",
      "best_performing_campaign": {
        "id": "uuid",
        "name": "string",
        "open_rate": "number"
      },
      "campaign_status_breakdown": {
        "completed": "number",
        "in_progress": "number",
        "failed": "number"
      }
    },
    "search_performance": {
      "total_searches": "number",
      "success_rate": "number",
      "avg_results_per_search": "number",
      "avg_execution_time": "number",
      "top_performing_sources": [
        {
          "source": "string",
          "results": "number",
          "success_rate": "number"
        }
      ]
    }
  }
}
```

### GET /api/dashboard/metrics/trends
**Description:** Get trending metrics for dashboard charts
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `metric` (string, required) - Metric type: leads, campaigns, searches, quality
- `period` (string, default: "30d") - Time period
- `granularity` (string, default: "day") - Data granularity

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
  "analysis": {
    "metric": "string",
    "period": "string",
    "total": "number",
    "average": "number",
    "peak_value": "number",
    "peak_date": "date",
    "trend_direction": "up|down|stable",
    "growth_rate": "number (percentage)",
    "volatility": "low|medium|high"
  }
}
```

## User Activity Analysis

### GET /api/dashboard/users/activity
**Description:** Get user activity summary for dashboard
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}` (admin permission required)
**Query Parameters:**
- `period` (string, default: "30d") - Time period
- `limit` (number, default: 10) - Number of users to return
- `sort_by` (string, default: "activity") - Sort by: activity, searches, campaigns, leads

**Response:**
```json
{
  "user_activity": [
    {
      "user_id": "uuid",
      "user_name": "string",
      "email": "string",
      "role": "string",
      "total_searches": "number",
      "total_campaigns": "number",
      "total_leads_found": "number",
      "last_activity": "timestamp",
      "activity_score": "number (0-100)",
      "favorite_activity": "string"
    }
  ],
  "summary": {
    "total_active_users": "number",
    "avg_activity_score": "number",
    "most_productive_user": {
      "user_id": "uuid",
      "user_name": "string",
      "total_leads": "number"
    },
    "activity_distribution": {
      "highly_active": "number",
      "moderately_active": "number",
      "low_activity": "number",
      "inactive": "number"
    }
  }
}
```

### GET /api/dashboard/users/performance
**Description:** Get user performance metrics
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}` (admin permission required)
**Query Parameters:**
- `user_id` (UUID, optional) - Specific user analysis
- `days` (number, default: 30) - Days to analyze

**Response:**
```json
{
  "performance": {
    "search_efficiency": {
      "avg_search_time": "number (seconds)",
      "success_rate": "number (percentage)",
      "avg_results_per_search": "number"
    },
    "campaign_effectiveness": {
      "avg_open_rate": "number (percentage)",
      "avg_click_rate": "number (percentage)",
      "campaigns_completed": "number"
    },
    "productivity_metrics": {
      "leads_per_day": "number",
      "searches_per_day": "number",
      "active_hours_per_day": "number"
    }
  },
  "trends": {
    "daily_productivity": [
      {
        "date": "date",
        "searches": "number",
        "leads_found": "number",
        "campaigns_sent": "number"
      }
    ]
  }
}
```

## System Health & Status

### GET /api/dashboard/system/health
**Description:** Get system health metrics for admin dashboard
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}` (admin permission required)

**Response:**
```json
{
  "system_health": {
    "status": "healthy|warning|critical",
    "uptime": "number (seconds)",
    "response_time": "number (milliseconds)",
    "error_rate": "number (percentage)",
    "active_sessions": "number",
    "database_status": "healthy|slow|error",
    "external_services": {
      "email_service": "online|offline|degraded",
      "scraping_service": "online|offline|degraded",
      "storage_service": "online|offline|degraded"
    }
  },
  "performance_metrics": {
    "avg_api_response_time": "number (ms)",
    "requests_per_minute": "number",
    "memory_usage": "number (MB)",
    "cpu_usage": "number (percentage)",
    "disk_usage": "number (percentage)"
  },
  "alerts": [
    {
      "type": "error|warning|info",
      "message": "string",
      "timestamp": "timestamp",
      "resolved": "boolean"
    }
  ]
}
```

### GET /api/dashboard/system/usage
**Description:** Get system usage statistics
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}` (admin permission required)
**Query Parameters:**
- `period` (string, default: "24h") - Time period for usage data

**Response:**
```json
{
  "usage": {
    "api_calls": {
      "total": "number",
      "by_endpoint": {
        "/api/search/*": "number",
        "/api/campaigns/*": "number",
        "/api/results/*": "number",
        "/api/auth/*": "number"
      },
      "by_hour": [
        {
          "hour": "string",
          "calls": "number"
        }
      ]
    },
    "resource_consumption": {
      "bandwidth_used": "number (MB)",
      "storage_used": "number (GB)",
      "emails_sent": "number",
      "searches_executed": "number"
    },
    "user_activity": {
      "concurrent_users": "number",
      "peak_concurrent": "number",
      "total_sessions": "number",
      "avg_session_duration": "number (minutes)"
    }
  }
}
```

## Real-time Dashboard Data

### GET /api/dashboard/realtime
**Description:** Get real-time dashboard data
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`

**Response:**
```json
{
  "realtime": {
    "active_users": "number",
    "ongoing_searches": "number",
    "campaigns_sending": "number",
    "recent_activities": [
      {
        "type": "string",
        "description": "string",
        "timestamp": "timestamp"
      }
    ],
    "live_metrics": {
      "searches_last_hour": "number",
      "leads_created_today": "number",
      "campaigns_sent_today": "number",
      "avg_response_time": "number (ms)"
    }
  },
  "timestamp": "timestamp",
  "next_update": "timestamp"
}
```

## Widget Configuration

### GET /api/dashboard/widgets
**Description:** Get available dashboard widgets configuration
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`

**Response:**
```json
{
  "widgets": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "type": "chart|stat|table|activity",
      "category": "overview|performance|activity|system",
      "default_size": "small|medium|large",
      "configurable": "boolean",
      "required_permissions": ["array"],
      "data_source": "string",
      "refresh_interval": "number (seconds)"
    }
  ],
  "layouts": {
    "default": [
      {
        "widget_id": "string",
        "position": {
          "x": "number",
          "y": "number",
          "width": "number",
          "height": "number"
        }
      }
    ],
    "admin": [...],
    "user": [...]
  }
}
```

### GET /api/dashboard/widgets/:id/data
**Description:** Get data for specific dashboard widget
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (string) - Widget ID
**Query Parameters:**
- `period` (string, optional) - Time period for widget data
- `refresh` (boolean, default: false) - Force refresh data

**Response:**
```json
{
  "widget_data": {
    "id": "string",
    "type": "string",
    "data": "object (structure depends on widget type)",
    "last_updated": "timestamp",
    "cache_expires": "timestamp"
  },
  "metadata": {
    "total_records": "number",
    "data_range": {
      "start": "timestamp",
      "end": "timestamp"
    },
    "refresh_rate": "number (seconds)"
  }
}
```
