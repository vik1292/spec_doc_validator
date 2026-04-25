# Customer Data Specification

Version: 1.0  
Initiative: Customer Data Platform

## Description

This specification defines the expected schema for the customer extract CSV files delivered weekly by the source system.

## Naming Convention

All column names must use snake_case (lowercase letters, digits, and underscores only). No spaces, hyphens, or mixed-case allowed.

## File Naming

Files must match the pattern: `customers_YYYYMMDD.csv`

## Field Definitions

| Field | Type | Nullable | Allowed Values | Pattern | Description |
|-------|------|----------|----------------|---------|-------------|
| customer_id | integer | no | | | Unique customer identifier. Must be positive. |
| first_name | string | no | | | Customer first name. |
| last_name | string | no | | | Customer last name. |
| email | email | no | | | Primary contact email address. Must be unique per customer. |
| status | enum | no | active,inactive,suspended | | Account status. |
| country_code | string | no | | ^[A-Z]{2}$ | ISO 3166-1 alpha-2 country code (uppercase). |
| date_of_birth | date | yes | | | Customer date of birth. Format: YYYY-MM-DD. |
| annual_revenue | float | yes | | | Estimated annual revenue in USD. Must be >= 0 if provided. |
| is_verified | boolean | no | | | Whether the customer has completed identity verification. |
| created_at | datetime | no | | | Record creation timestamp. ISO 8601 format. |

## Business Rules

- `customer_id` must be a positive integer greater than 0.
- `email` must be unique across all rows in the file.
- `annual_revenue` must be >= 0 when provided.
- `country_code` must be a valid ISO 3166-1 alpha-2 code (two uppercase letters).
- `created_at` must not be a future date relative to the file delivery date.
- Rows where `status` is `suspended` should have a non-null `date_of_birth` (required for compliance).
