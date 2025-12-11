# Agencyzoom API - Summary

## Overview
**Version:** 1.0.0  
**Base URL:** `/v1/api`  
**Contact:** support@agencyzoom.com

Agencyzoom API enables third-party applications to integrate with Agencyzoom to manage leads, customers, policies, and tasks. The management operations include creation, retrieval, updating, and deletion.

## Rate Limits
- **Day (Standard):** 30 calls per minute
- **Night (10PM CT - 4AM CT):** 60 calls per minute

## Authentication
- **Type:** JWT Bearer Token
- **Header:** `Authorization: Bearer <token>`
- **Login Endpoint:** `POST /v1/api/auth/login`
- **Logout Endpoint:** `POST /v1/api/auth/logout`

## API Categories

### 1. **Authentication** (3 endpoints)
Authentication and session management using JWT tokens.
- Login (standard and V4 SSO)
- Logout
- Get V4 SSO auth parameters

### 2. **Contact Management** (1 endpoint)
- Batch create contacts (max 5 per call)

### 3. **Customer Management** (11 endpoints)
Complete CRUD operations for customers including:
- Search customers with advanced filters
- Get/Update/Delete customer details
- Customer tasks, files, notes
- Customer policies (AMS and regular)
- Create new customers

### 4. **Policy Management** (5 endpoints)
Comprehensive policy lifecycle management:
- Create and update policies
- Tag management
- Status updates (Active, Cancelled, Renewed, etc.)
- Policy endorsements

### 5. **Thread Management** (10 endpoints)
Email and SMS thread operations:
- Search email/SMS threads
- Thread details and messages
- Mark as read/unread
- Delete threads and messages
- Get list of producers

### 6. **Lead Management** (28 endpoints)
Extensive lead management capabilities:
- **Search & Filtering:** Search leads with multiple filters, pipeline counts
- **CRUD Operations:** Create (personal/commercial/batch), update, delete leads
- **Opportunities:** Add, update, delete opportunities for leads
- **Quotes:** Manage quote lifecycle
- **Files:** Upload, rename, delete lead files
- **Status Management:** Change status, move stages, mark as sold
- **Notes & Tasks:** Add notes and view tasks

### 7. **Life & Health Lead Management** (1 endpoint)
- Search life and health leads with specialized filters

### 8. **Opportunity Management** (20 endpoints)
Advanced opportunity management with:
- **Drivers:** Create, update, delete, link/unlink drivers
- **Vehicles:** Create, update, delete, link/unlink vehicles
- **Opportunities:** Full CRUD operations
- Support for auto insurance with driver/vehicle details

### 9. **User Management** (1 endpoint)
- Update user profile

### 10. **Configuration & Settings** (13 endpoints)
Retrieve system configuration data:
- Product categories and lines (policy types)
- Employees and life professionals
- Lead sources and categories
- Assignment groups and locations
- Carriers and loss reasons
- Custom fields and CSRs
- Recycle events

### 11. **Department & Groups** (1 endpoint)
- Get departments and groups by agency

### 12. **Pipeline** (2 endpoints)
- Get pipelines with stages
- Get end stages

### 13. **Business Classifications** (1 endpoint)
- Search business classifications

### 14. **Task Management** (8 endpoints)
Complete task lifecycle:
- Search/filter tasks
- Create, update, delete tasks
- Complete and reopen tasks
- Batch delete operations
- Task types: To Do, Email, Call, Meeting

### 15. **Service Center** (1 endpoint)
- Search and filter service tickets

## Key Features

### Pagination
Most list endpoints support pagination:
- `pageSize`: Number of results (default: 20, max varies by endpoint)
- `page`: Page number (starts at 0)

### Sorting & Filtering
- `sort`: Field name for sorting
- `order`: `asc` or `desc`
- Various filters specific to each resource type

### Standard Codes
Enterprise users can use standard codes instead of internal IDs:
- `standardProductLineCode`: Standard policy type code
- `standardCarrierCode`: Standard carrier code

### Custom Fields
Many resources support custom fields for extended data storage.

### Tags
Support for tagging on multiple resource types (leads, customers, policies).

## Common Response Codes
- **200:** Success
- **400:** Invalid request parameters
- **500:** Internal processing error

## Important Notes

1. **Permissions:** API calls inherit the permissions of the logged-in user. Use agency owner credentials for full access.

2. **Batch Operations:** 
   - Contact batch create: max 5 contacts
   - Lead batch create: max 5 leads

3. **Date Formats:**
   - ISO 8601 for filters: `YYYY-MM-DD`
   - US format for data: `MM/dd/YYYY`

4. **Money Values:**
   - Premium amounts in cents (e.g., $100.00 = 10000)

5. **Lead Status Codes:**
   - 0: NEW
   - 1: QUOTED
   - 2: WON
   - 3: LOST
   - 4: CONTACTED
   - 5: EXPIRED

6. **Policy Status Codes:**
   - 0: Cancelled
   - 1: Active
   - 10: Active-New
   - 11: Active-Renewed
   - 12: Active-Reinstated
   - 13: Active-Rewritten

## Getting Started

1. Authenticate using `/v1/api/auth/login` with username (email) and password
2. Receive JWT token in response
3. Include token in all subsequent requests: `Authorization: Bearer <token>`
4. Use configuration endpoints to get IDs for pipelines, stages, carriers, etc.
5. Start creating and managing leads, customers, and policies

## Change Log Highlights

- **2024.03.10:** Added `licenseNumber` and `stateLicensed` fields for drivers
- **2024.01.18:** New customer policies endpoints, policy tag updates
- **2024.01.10:** Batch contact creation, additional customer fields
- **2023.11.21:** Increased daily rate limit to 30 per minute
- **2023.11.07:** Fixed sort by `lastActivityDate`, added activity date filters

## Total Endpoints: 105+

The API provides comprehensive access to all major Agencyzoom functionality for seamless third-party integrations.


