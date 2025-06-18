# Search Module API Endpoints

## Search Configurations

### GET /api/search/configurations
**Description:** Get list of search configurations with filtering
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `page` (number, default: 1) - Page number
- `limit` (number, default: 25) - Items per page
- `is_template` (boolean, optional) - Filter by template status
- `is_public` (boolean, optional) - Filter by public visibility
- `created_by` (UUID, optional) - Filter by creator
- `search` (string, optional) - Search by name or description

**Response:**
```json
{
  "configurations": [
    {
      "id": "uuid",
      "name": "string",
      "description": "string",
      "client_types": ["array of client types"],
      "locations": ["array of locations"],
      "websites": ["array of website domains"],
      "validate_emails": "boolean",
      "validate_websites": "boolean",
      "validate_phones": "boolean",
      "company_size_min": "number",
      "company_size_max": "number",
      "industries": ["array of industries"],
      "job_titles": ["array of job titles"],
      "keywords": "string",
      "exclude_keywords": "string",
      "is_template": "boolean",
      "is_public": "boolean",
      "usage_count": "number",
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

### GET /api/search/configurations/:id
**Description:** Get specific search configuration details
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Configuration ID

**Response:**
```json
{
  "configuration": {
    "id": "uuid",
    "name": "string",
    "description": "string",
    "client_types": ["array"],
    "locations": ["array"],
    "websites": ["array"],
    "validate_emails": "boolean",
    "validate_websites": "boolean",
    "validate_phones": "boolean",
    "company_size_min": "number",
    "company_size_max": "number",
    "industries": ["array"],
    "job_titles": ["array"],
    "keywords": "string",
    "exclude_keywords": "string",
    "is_template": "boolean",
    "is_public": "boolean",
    "usage_count": "number",
    "metadata": "object",
    "created_by": "uuid",
    "created_by_name": "string",
    "created_at": "timestamp",
    "updated_at": "timestamp",
    "last_used_at": "timestamp"
  },
  "usage_stats": {
    "total_searches": "number",
    "avg_results_per_search": "number",
    "success_rate": "number (percentage)",
    "recent_searches": [
      {
        "id": "uuid",
        "started_at": "timestamp",
        "total_results": "number",
        "status": "string"
      }
    ]
  }
}
```

### POST /api/search/configurations
**Description:** Create new search configuration
**Method:** POST
**Headers:**
- `Authorization: Bearer {access_token}`
**Body:**
```json
{
  "name": "string (required)",
  "description": "string (optional)",
  "client_types": ["array (optional)"],
  "locations": ["array (optional)"],
  "websites": ["array (optional)"],
  "validate_emails": "boolean (default: true)",
  "validate_websites": "boolean (default: true)",
  "validate_phones": "boolean (default: false)",
  "company_size_min": "number (optional)",
  "company_size_max": "number (optional)",
  "industries": ["array (optional)"],
  "job_titles": ["array (optional)"],
  "keywords": "string (optional)",
  "exclude_keywords": "string (optional)",
  "is_template": "boolean (default: false)",
  "is_public": "boolean (default: false)",
  "metadata": "object (optional)"
}
```

**Response:**
```json
{
  "configuration": {
    "id": "uuid",
    "name": "string",
    "description": "string",
    "client_types": "array",
    "locations": "array",
    "websites": "array",
    "validate_emails": "boolean",
    "validate_websites": "boolean",
    "validate_phones": "boolean",
    "is_template": "boolean",
    "is_public": "boolean",
    "created_by": "uuid",
    "created_at": "timestamp"
  },
  "message": "Search configuration created successfully"
}
```

### PUT /api/search/configurations/:id
**Description:** Update search configuration
**Method:** PUT
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Configuration ID
**Body:**
```json
{
  "name": "string (optional)",
  "description": "string (optional)",
  "client_types": ["array (optional)"],
  "locations": ["array (optional)"],
  "websites": ["array (optional)"],
  "validate_emails": "boolean (optional)",
  "validate_websites": "boolean (optional)",
  "validate_phones": "boolean (optional)",
  "company_size_min": "number (optional)",
  "company_size_max": "number (optional)",
  "industries": ["array (optional)"],
  "job_titles": ["array (optional)"],
  "keywords": "string (optional)",
  "exclude_keywords": "string (optional)",
  "is_public": "boolean (optional)"
}
```

**Response:**
```json
{
  "configuration": {
    "id": "uuid",
    "name": "string",
    "updated_at": "timestamp"
  },
  "message": "Search configuration updated successfully"
}
```

### DELETE /api/search/configurations/:id
**Description:** Delete search configuration
**Method:** DELETE
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Configuration ID

**Response:**
```json
{
  "message": "Search configuration deleted successfully"
}
```

### POST /api/search/configurations/:id/duplicate
**Description:** Duplicate search configuration
**Method:** POST
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Configuration ID to duplicate
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
  "configuration": {
    "id": "uuid",
    "name": "string",
    "created_at": "timestamp"
  },
  "message": "Configuration duplicated successfully"
}
```

## Search Execution

### POST /api/search/execute
**Description:** Execute search with configuration
**Method:** POST
**Headers:**
- `Authorization: Bearer {access_token}`
**Body:**
```json
{
  "query_name": "string (optional)",
  "search_config_id": "uuid (optional)",
  "search_parameters": {
    "client_types": ["array (required)"],
    "locations": ["array (required)"],
    "websites": ["array (optional)"],
    "validate_emails": "boolean (default: true)",
    "validate_websites": "boolean (default: true)",
    "validate_phones": "boolean (default: false)",
    "keywords": "string (optional)",
    "exclude_keywords": "string (optional)",
    "max_results": "number (default: 100)"
  },
  "filters_applied": "object (optional)"
}
```

**Response:**
```json
{
  "search": {
    "id": "uuid",
    "query_name": "string",
    "status": "pending",
    "search_parameters": "object",
    "filters_applied": "object",
    "estimated_duration": "number (seconds)",
    "started_at": "timestamp"
  },
  "message": "Search started successfully"
}
```

### GET /api/search/execute/:id/status
**Description:** Get search execution status
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Search ID

**Response:**
```json
{
  "search": {
    "id": "uuid",
    "query_name": "string",
    "status": "pending|in_progress|completed|failed|cancelled",
    "progress": "number (0-100)",
    "total_results": "number",
    "valid_results": "number",
    "duplicate_results": "number",
    "execution_time_ms": "number",
    "pages_scraped": "number",
    "websites_searched": "array",
    "started_at": "timestamp",
    "completed_at": "timestamp",
    "error_message": "string",
    "results_file_url": "string",
    "results_summary": "object"
  }
}
```

### POST /api/search/execute/:id/cancel
**Description:** Cancel running search
**Method:** POST
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Search ID

**Response:**
```json
{
  "search": {
    "id": "uuid",
    "status": "cancelled",
    "cancelled_at": "timestamp"
  },
  "message": "Search cancelled successfully"
}
```

### GET /api/search/execute/:id/results
**Description:** Get search results
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Search ID
**Query Parameters:**
- `page` (number, default: 1) - Page number
- `limit` (number, default: 50) - Items per page
- `quality_filter` (number, optional) - Minimum quality score

**Response:**
```json
{
  "results": [
    {
      "id": "uuid",
      "email": "string",
      "verified_email": "boolean",
      "phone": "string",
      "verified_phone": "boolean",
      "company_name": "string",
      "company_website": "string",
      "verified_website": "boolean",
      "address": "string",
      "state": "string",
      "country": "string",
      "activity": "string",
      "description": "string",
      "category": "string",
      "data_quality_score": "number",
      "source_website": "string",
      "found_at": "timestamp"
    }
  ],
  "pagination": {
    "page": "number",
    "limit": "number",
    "total": "number",
    "total_pages": "number"
  },
  "search_info": {
    "id": "uuid",
    "query_name": "string",
    "status": "string",
    "total_results": "number",
    "completed_at": "timestamp"
  }
}
```

## Search History

### GET /api/search/history
**Description:** Get user's search history
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `page` (number, default: 1) - Page number
- `limit` (number, default: 25) - Items per page
- `status` (string, optional) - Filter by status
- `start_date` (date, optional) - Filter by date range
- `end_date` (date, optional) - Filter by date range

**Response:**
```json
{
  "history": [
    {
      "id": "uuid",
      "query_name": "string",
      "search_config_id": "uuid",
      "config_name": "string",
      "search_parameters": "object",
      "status": "pending|in_progress|completed|failed|cancelled",
      "total_results": "number",
      "valid_results": "number",
      "duplicate_results": "number",
      "execution_time_ms": "number",
      "pages_scraped": "number",
      "websites_searched": "array",
      "started_at": "timestamp",
      "completed_at": "timestamp",
      "results_file_url": "string"
    }
  ],
  "pagination": {
    "page": "number",
    "limit": "number",
    "total": "number",
    "total_pages": "number"
  },
  "statistics": {
    "total_searches": "number",
    "successful_searches": "number",
    "total_results_found": "number",
    "avg_execution_time": "number",
    "most_productive_config": "string"
  }
}
```

### GET /api/search/history/:id
**Description:** Get specific search history details
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Search history ID

**Response:**
```json
{
  "search": {
    "id": "uuid",
    "user_id": "uuid",
    "user_name": "string",
    "query_name": "string",
    "search_config_id": "uuid",
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
    "error_message": "string",
    "results_file_url": "string",
    "results_summary": "object",
    "metadata": "object"
  },
  "performance_details": {
    "avg_page_load_time": "number",
    "requests_per_minute": "number",
    "success_rate_by_website": [
      {
        "website": "string",
        "success_rate": "number",
        "results_found": "number"
      }
    ]
  }
}
```

### DELETE /api/search/history/:id
**Description:** Delete search history entry
**Method:** DELETE
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Search history ID

**Response:**
```json
{
  "message": "Search history deleted successfully"
}
```

## Templates & Popular Configurations

### GET /api/search/templates
**Description:** Get search configuration templates
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `category` (string, optional) - Filter by category
- `industry` (string, optional) - Filter by industry

**Response:**
```json
{
  "templates": [
    {
      "id": "uuid",
      "name": "string",
      "description": "string",
      "category": "string",
      "client_types": "array",
      "locations": "array",
      "validate_emails": "boolean",
      "validate_websites": "boolean",
      "validate_phones": "boolean",
      "keywords": "string",
      "exclude_keywords": "string",
      "usage_count": "number",
      "success_rate": "number",
      "avg_results": "number",
      "created_by_name": "string",
      "created_at": "timestamp",
      "last_used_at": "timestamp"
    }
  ],
  "categories": [
    {
      "name": "string",
      "label": "string",
      "template_count": "number"
    }
  ]
}
```

### GET /api/search/popular
**Description:** Get popular search configurations
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `limit` (number, default: 10) - Number of configurations to return
- `period` (string, default: "30d") - Time period: 7d, 30d, 90d

**Response:**
```json
{
  "popular_configs": [
    {
      "id": "uuid",
      "name": "string",
      "description": "string",
      "usage_count": "number",
      "success_rate": "number",
      "avg_results": "number",
      "created_by_name": "string",
      "last_used_at": "timestamp",
      "is_public": "boolean"
    }
  ],
  "trending_keywords": [
    {
      "keyword": "string",
      "usage_count": "number",
      "growth_rate": "number"
    }
  ],
  "popular_locations": [
    {
      "location": "string",
      "search_count": "number",
      "avg_results": "number"
    }
  ]
}
```

## Search Analytics & Performance

### GET /api/search/analytics/performance
**Description:** Get search performance analytics
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `user_id` (UUID, optional) - Filter by user
- `days` (number, default: 30) - Days to analyze
- `config_id` (UUID, optional) - Filter by configuration

**Response:**
```json
{
  "performance": {
    "total_searches": "number",
    "successful_searches": "number",
    "failed_searches": "number",
    "success_rate": "number (percentage)",
    "avg_execution_time": "number (seconds)",
    "total_results_found": "number",
    "avg_results_per_search": "number",
    "total_pages_scraped": "number"
  },
  "trends": {
    "daily_performance": [
      {
        "date": "date",
        "searches": "number",
        "success_rate": "number",
        "avg_results": "number"
      }
    ]
  },
  "website_performance": [
    {
      "website": "string",
      "searches": "number",
      "success_rate": "number",
      "avg_results": "number",
      "avg_response_time": "number"
    }
  ]
}
```

### GET /api/search/analytics/statistics
**Description:** Get search statistics for user
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `period` (string, default: "30d") - Time period

**Response:**
```json
{
  "statistics": {
    "total_searches": "number",
    "successful_searches": "number",
    "failed_searches": "number",
    "total_results": "number",
    "avg_execution_time_ms": "number",
    "last_search_date": "timestamp",
    "most_used_config": "string",
    "favorite_locations": "array",
    "favorite_client_types": "array"
  },
  "monthly_breakdown": [
    {
      "month": "string",
      "searches": "number",
      "results": "number",
      "success_rate": "number"
    }
  ],
  "quality_distribution": {
    "high_quality": "number",
    "medium_quality": "number",
    "low_quality": "number"
  }
}
```

## Search Options & Configuration

### GET /api/search/options
**Description:** Get available search options and parameters
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`

**Response:**
```json
{
  "options": {
    "client_types": [
      {
        "value": "string",
        "label": "string",
        "description": "string"
      }
    ],
    "locations": [
      {
        "value": "string",
        "label": "string",
        "country": "string",
        "region": "string"
      }
    ],
    "websites": [
      {
        "domain": "string",
        "name": "string",
        "description": "string",
        "is_active": "boolean",
        "success_rate": "number"
      }
    ],
    "industries": [
      {
        "value": "string",
        "label": "string",
        "parent_category": "string"
      }
    ],
    "company_sizes": [
      {
        "range": "string",
        "min": "number",
        "max": "number"
      }
    ]
  },
  "validation_options": {
    "email_validation": {
      "available": "boolean",
      "cost_per_validation": "number",
      "accuracy": "number (percentage)"
    },
    "phone_validation": {
      "available": "boolean",
      "cost_per_validation": "number",
      "accuracy": "number (percentage)"
    },
    "website_validation": {
      "available": "boolean",
      "cost_per_validation": "number",
      "accuracy": "number (percentage)"
    }
  }
}
```
