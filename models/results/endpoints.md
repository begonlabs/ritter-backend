# Results Module API Endpoints

## Lead Management

### GET /api/results/leads
**Description:** Get leads with advanced filtering and search
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `page` (number, default: 1) - Page number
- `limit` (number, default: 25) - Items per page
- `search` (string, optional) - Search in company name or activity
- `min_quality_score` (number, default: 1) - Minimum quality score (1-5)
- `verified_email` (boolean, optional) - Filter by email verification
- `verified_phone` (boolean, optional) - Filter by phone verification
- `verified_website` (boolean, optional) - Filter by website verification
- `categories` (array, optional) - Filter by business categories
- `states` (array, optional) - Filter by states/regions
- `countries` (array, optional) - Filter by countries
- `sort_by` (string, default: "created_at") - Sort field
- `sort_order` (string, default: "desc") - Sort order: asc, desc

**Response:**
```json
{
  "leads": [
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
      "data_quality_score": "number (1-5)",
      "created_at": "timestamp",
      "updated_at": "timestamp",
      "last_contacted_at": "timestamp"
    }
  ],
  "pagination": {
    "page": "number",
    "limit": "number",
    "total": "number",
    "total_pages": "number"
  },
  "filters_applied": {
    "search": "string",
    "min_quality_score": "number",
    "verified_email": "boolean",
    "verified_phone": "boolean",
    "verified_website": "boolean",
    "categories": "array",
    "states": "array"
  },
  "summary": {
    "total_leads": "number",
    "high_quality_leads": "number (score 4-5)",
    "contactable_leads": "number (with verified contact info)"
  }
}
```

### GET /api/results/leads/:id
**Description:** Get specific lead details
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Lead ID

**Response:**
```json
{
  "lead": {
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
    "created_at": "timestamp",
    "updated_at": "timestamp",
    "last_contacted_at": "timestamp"
  },
  "contact_history": [
    {
      "campaign_id": "uuid",
      "campaign_name": "string",
      "sent_at": "timestamp",
      "status": "string",
      "opened": "boolean",
      "clicked": "boolean"
    }
  ],
  "related_leads": [
    {
      "id": "uuid",
      "company_name": "string",
      "similarity_score": "number"
    }
  ]
}
```

### PUT /api/results/leads/:id
**Description:** Update lead information
**Method:** PUT
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Lead ID
**Body:**
```json
{
  "email": "string (optional)",
  "phone": "string (optional)",
  "company_name": "string (optional)",
  "company_website": "string (optional)",
  "address": "string (optional)",
  "state": "string (optional)",
  "country": "string (optional)",
  "activity": "string (optional)",
  "description": "string (optional)",
  "category": "string (optional)",
  "last_contacted_at": "timestamp (optional)"
}
```

**Response:**
```json
{
  "lead": {
    "id": "uuid",
    "company_name": "string",
    "data_quality_score": "number",
    "updated_at": "timestamp"
  },
  "message": "Lead updated successfully"
}
```

### DELETE /api/results/leads/:id
**Description:** Delete lead
**Method:** DELETE
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Lead ID

**Response:**
```json
{
  "message": "Lead deleted successfully"
}
```

### POST /api/results/leads/bulk-update
**Description:** Bulk update multiple leads
**Method:** POST
**Headers:**
- `Authorization: Bearer {access_token}`
**Body:**
```json
{
  "lead_ids": ["array of UUIDs (required)"],
  "updates": {
    "category": "string (optional)",
    "last_contacted_at": "timestamp (optional)"
  }
}
```

**Response:**
```json
{
  "updated_count": "number",
  "message": "Leads updated successfully"
}
```

### DELETE /api/results/leads/bulk-delete
**Description:** Bulk delete multiple leads
**Method:** DELETE
**Headers:**
- `Authorization: Bearer {access_token}`
**Body:**
```json
{
  "lead_ids": ["array of UUIDs (required)"]
}
```

**Response:**
```json
{
  "deleted_count": "number",
  "message": "Leads deleted successfully"
}
```

## Lead Statistics & Analytics

### GET /api/results/statistics
**Description:** Get lead statistics and distribution
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `period` (string, default: "all") - Time period: all, 30d, 7d, 1d

**Response:**
```json
{
  "statistics": {
    "total_leads": "number",
    "verified_emails": "number",
    "verified_phones": "number",
    "verified_websites": "number",
    "quality_distribution": {
      "score_1": "number",
      "score_2": "number",
      "score_3": "number",
      "score_4": "number",
      "score_5": "number"
    },
    "verification_rates": {
      "email_rate": "number (percentage)",
      "phone_rate": "number (percentage)",
      "website_rate": "number (percentage)"
    }
  },
  "top_categories": [
    {
      "category": "string",
      "count": "number",
      "percentage": "number"
    }
  ],
  "top_states": [
    {
      "state": "string",
      "count": "number",
      "percentage": "number"
    }
  ],
  "trends": {
    "daily_leads": [
      {
        "date": "date",
        "count": "number",
        "quality_avg": "number"
      }
    ]
  }
}
```

### GET /api/results/quality-analysis
**Description:** Get detailed lead quality analysis
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `category` (string, optional) - Filter by category
- `state` (string, optional) - Filter by state

**Response:**
```json
{
  "quality_analysis": {
    "overall_quality": "number (1-5)",
    "quality_factors": {
      "email_verification_impact": "number",
      "phone_verification_impact": "number", 
      "website_verification_impact": "number",
      "completeness_score": "number"
    },
    "recommendations": [
      {
        "type": "string",
        "description": "string",
        "priority": "high|medium|low",
        "affected_leads": "number"
      }
    ]
  },
  "quality_by_source": [
    {
      "source": "string",
      "avg_quality": "number",
      "lead_count": "number"
    }
  ],
  "improvement_opportunities": {
    "low_quality_leads": "number",
    "missing_email": "number",
    "missing_phone": "number",
    "missing_website": "number"
  }
}
```

## Lead Export & Data Management

### GET /api/results/export
**Description:** Export leads to various formats
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `format` (string, default: "csv") - Export format: csv, xlsx, json, vcf
- `filters` (string, optional) - JSON string of filters to apply
- `fields` (array, optional) - Specific fields to export
- `include_contact_history` (boolean, default: false) - Include campaign history

**Response:**
```json
{
  "export": {
    "file_url": "string",
    "file_name": "string",
    "file_size": "number (bytes)",
    "format": "string",
    "total_records": "number",
    "expires_at": "timestamp"
  },
  "filters_applied": "object",
  "fields_exported": "array"
}
```

### POST /api/results/import
**Description:** Import leads from CSV/Excel file
**Method:** POST
**Headers:**
- `Authorization: Bearer {access_token}`
- `Content-Type: multipart/form-data`
**Body:**
- `file` (file, required) - CSV or Excel file
- `mapping` (JSON, required) - Field mapping configuration
- `skip_duplicates` (boolean, default: true) - Skip duplicate entries
- `validate_emails` (boolean, default: true) - Validate email formats
- `validate_phones` (boolean, default: false) - Validate phone formats

**Response:**
```json
{
  "import": {
    "id": "uuid",
    "status": "processing|completed|failed",
    "total_rows": "number",
    "processed_rows": "number",
    "imported_leads": "number",
    "skipped_duplicates": "number",
    "validation_errors": "number",
    "started_at": "timestamp"
  },
  "message": "Import started successfully"
}
```

### GET /api/results/import/:id/status
**Description:** Get import job status
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Import job ID

**Response:**
```json
{
  "import": {
    "id": "uuid",
    "status": "processing|completed|failed",
    "progress": "number (0-100)",
    "total_rows": "number",
    "processed_rows": "number",
    "imported_leads": "number",
    "skipped_duplicates": "number",
    "validation_errors": "number",
    "error_details": "array",
    "started_at": "timestamp",
    "completed_at": "timestamp"
  }
}
```

## Lead Validation & Data Quality

### POST /api/results/validate
**Description:** Validate lead data (emails, phones, websites)
**Method:** POST
**Headers:**
- `Authorization: Bearer {access_token}`
**Body:**
```json
{
  "lead_ids": ["array of UUIDs (required)"],
  "validation_types": ["email", "phone", "website"],
  "update_records": "boolean (default: true)"
}
```

**Response:**
```json
{
  "validation": {
    "id": "uuid",
    "status": "processing|completed|failed",
    "total_leads": "number",
    "processed_leads": "number",
    "validation_types": "array",
    "started_at": "timestamp"
  },
  "message": "Validation started successfully"
}
```

### GET /api/results/validate/:id/status
**Description:** Get validation job status
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Parameters:**
- `id` (UUID) - Validation job ID

**Response:**
```json
{
  "validation": {
    "id": "uuid",
    "status": "processing|completed|failed",
    "progress": "number (0-100)",
    "total_leads": "number",
    "processed_leads": "number",
    "results": {
      "valid_emails": "number",
      "invalid_emails": "number",
      "valid_phones": "number",
      "invalid_phones": "number",
      "valid_websites": "number",
      "invalid_websites": "number"
    },
    "started_at": "timestamp",
    "completed_at": "timestamp"
  }
}
```

### POST /api/results/deduplicate
**Description:** Find and remove duplicate leads
**Method:** POST
**Headers:**
- `Authorization: Bearer {access_token}`
**Body:**
```json
{
  "strategy": "email|company_name|phone|fuzzy_match",
  "auto_merge": "boolean (default: false)",
  "keep_highest_quality": "boolean (default: true)"
}
```

**Response:**
```json
{
  "deduplication": {
    "id": "uuid",
    "status": "processing|completed|failed",
    "strategy": "string",
    "duplicates_found": "number",
    "leads_merged": "number",
    "leads_removed": "number",
    "started_at": "timestamp"
  },
  "message": "Deduplication started successfully"
}
```

## Lead Search & Filtering

### GET /api/results/search
**Description:** Advanced lead search with full-text search
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`
**Query Parameters:**
- `q` (string, required) - Search query
- `fields` (array, optional) - Fields to search in: company_name, activity, description
- `exact_match` (boolean, default: false) - Exact phrase matching
- `page` (number, default: 1) - Page number
- `limit` (number, default: 25) - Items per page

**Response:**
```json
{
  "search_results": [
    {
      "id": "uuid",
      "company_name": "string",
      "activity": "string",
      "description": "string",
      "category": "string",
      "data_quality_score": "number",
      "relevance_score": "number (0-1)",
      "matching_fields": "array",
      "created_at": "timestamp"
    }
  ],
  "pagination": {
    "page": "number",
    "limit": "number",
    "total": "number",
    "total_pages": "number"
  },
  "search_info": {
    "query": "string",
    "execution_time_ms": "number",
    "total_matches": "number"
  }
}
```

### GET /api/results/filters/options
**Description:** Get available filter options for leads
**Method:** GET
**Headers:**
- `Authorization: Bearer {access_token}`

**Response:**
```json
{
  "filter_options": {
    "categories": [
      {
        "value": "string",
        "label": "string",
        "count": "number"
      }
    ],
    "states": [
      {
        "value": "string",
        "label": "string",
        "count": "number"
      }
    ],
    "countries": [
      {
        "value": "string",
        "label": "string", 
        "count": "number"
      }
    ],
    "quality_scores": [
      {
        "score": "number",
        "count": "number",
        "percentage": "number"
      }
    ]
  },
  "summary": {
    "total_categories": "number",
    "total_states": "number",
    "total_countries": "number",
    "date_range": {
      "oldest_lead": "date",
      "newest_lead": "date"
    }
  }
}
```
