# Phase 2.6: Billing Microservice - API Specification

**Authored By:** Manus, Enterprise Architect
**Date:** November 28, 2025
**Status:** DRAFT

## 1.0 Introduction

This document provides the complete API specification for the **Billing** microservice. It defines the set of endpoints that will be used by other TCP services and external clients to manage customers, subscriptions, and payments. This API is the primary interface to the TCP ecosystem's revenue engine.

## 2.0 API Design Principles

The API is designed with the following principles in mind:

*   **RESTful Architecture:** The API follows RESTful conventions, using standard HTTP verbs and status codes.
*   **JSON:API Specification:** All request and response bodies adhere to the JSON:API specification for consistency and clarity.
*   **Statelessness:** Each API request is self-contained and does not rely on server-side session state.
*   **Idempotency:** `POST`, `PUT`, and `PATCH` requests support idempotency keys to prevent duplicate operations.
*   **Authentication:** All endpoints are secured using JWT-based authentication, with role-based access control (RBAC) to enforce authorization.

## 3.0 API Endpoints

This section details each API endpoint, including its HTTP method, URL, request/response schema, and required permissions.

### 3.1 Customer Management

#### 3.1.1 Create a Customer

*   **Method:** `POST`
*   **URL:** `/api/v1/customers`
*   **Description:** Creates a new customer account.
*   **Permissions:** `billing:customers:create`
*   **Request Body:**

```json
{
  "data": {
    "type": "customers",
    "attributes": {
      "name": "John Doe",
      "email": "john.doe@example.com"
    }
  }
}
```

*   **Response Body (201 Created):**

```json
{
  "data": {
    "type": "customers",
    "id": "cus_12345",
    "attributes": {
      "name": "John Doe",
      "email": "john.doe@example.com",
      "created_at": "2025-11-28T10:00:00Z"
    }
  }
}
```

#### 3.1.2 Retrieve a Customer

*   **Method:** `GET`
*   **URL:** `/api/v1/customers/{customerId}`
*   **Description:** Retrieves the details of a specific customer.
*   **Permissions:** `billing:customers:read`
*   **Response Body (200 OK):**

```json
{
  "data": {
    "type": "customers",
    "id": "cus_12345",
    "attributes": {
      "name": "John Doe",
      "email": "john.doe@example.com",
      "created_at": "2025-11-28T10:00:00Z"
    }
  }
}
```

### 3.2 Subscription Management

#### 3.2.1 Create a Subscription

*   **Method:** `POST`
*   **URL:** `/api/v1/subscriptions`
*   **Description:** Creates a new subscription for a customer.
*   **Permissions:** `billing:subscriptions:create`
*   **Request Body:**

```json
{
  "data": {
    "type": "subscriptions",
    "attributes": {
      "customer_id": "cus_12345",
      "plan_id": "plan_abcde"
    }
  }
}
```

*   **Response Body (201 Created):**

```json
{
  "data": {
    "type": "subscriptions",
    "id": "sub_67890",
    "attributes": {
      "customer_id": "cus_12345",
      "plan_id": "plan_abcde",
      "status": "active",
      "start_date": "2025-11-28T10:00:00Z",
      "end_date": null,
      "created_at": "2025-11-28T10:00:00Z"
    }
  }
}
```

#### 3.2.2 Cancel a Subscription

*   **Method:** `PATCH`
*   **URL:** `/api/v1/subscriptions/{subscriptionId}`
*   **Description:** Cancels an active subscription.
*   **Permissions:** `billing:subscriptions:update`
*   **Request Body:**

```json
{
  "data": {
    "type": "subscriptions",
    "id": "sub_67890",
    "attributes": {
      "status": "canceled"
    }
  }
}
```

*   **Response Body (200 OK):**

```json
{
  "data": {
    "type": "subscriptions",
    "id": "sub_67890",
    "attributes": {
      "status": "canceled",
      "end_date": "2025-12-28T10:00:00Z"
    }
  }
}
```

### 3.3 Usage-Based Billing

#### 3.3.1 Report Usage

*   **Method:** `POST`
*   **URL:** `/api/v1/usage-records`
*   **Description:** Reports a usage event for a subscription.
*   **Permissions:** `billing:usage:create`
*   **Request Body:**

```json
{
  "data": {
    "type": "usage-records",
    "attributes": {
      "subscription_id": "sub_67890",
      "metric_name": "attestations",
      "quantity": 100
    }
  }
}
```

*   **Response Body (202 Accepted):**

```json
{
  "meta": {
    "status": "Usage record accepted for processing."
  }
}
```
