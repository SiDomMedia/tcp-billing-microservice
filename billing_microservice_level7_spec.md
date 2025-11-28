# Level 7 Specification: Billing Microservice

**Authored By:** Manus, Enterprise Architect
**Date:** November 28, 2025
**Status:** FINAL - Ready for Implementation

## 1.0 Executive Summary

The **Billing Microservice** is the central revenue engine for the entire Trusted Compliance Platform (TCP) ecosystem. It is designed to be the single source of truth for all customer, subscription, and financial data. Its architecture is built for **extensibility, auditability, and high-performance synchronization** with other services, particularly the SmartGateway.

This specification is the complete blueprint for the service, covering the data model, API contract, and event-driven integration strategy.

## 2.0 Architectural Principles

*   **Source of Truth:** The Billing service is the authoritative source for all financial data.
*   **Decoupling:** Services are decoupled via an event-driven architecture to ensure high performance and low latency for critical path operations (e.g., SmartGateway budget checks).
*   **Flexibility:** The design supports a hybrid monetization model: tiered subscriptions, usage-based metering, and one-time purchases.
*   **Auditability:** Every financial transaction is fully traceable and auditable.

## 3.0 Phase 2.5: Data Model (Source of Truth)

The data model is designed to support the full complexity of our monetization strategy.

### 3.1 Entity-Relationship Diagram (ERD)

```mermaid
erDiagram
    CUSTOMER ||--o{ SUBSCRIPTION : has
    CUSTOMER ||--o{ INVOICE : has
    CUSTOMER ||--o{ PAYMENT_METHOD : has

    SUBSCRIPTION ||--|{ PRODUCT : includes
    SUBSCRIPTION ||--o{ INVOICE : generates

    PRODUCT ||--|{ PLAN : has
    PLAN ||--o{ PRICE : has

    INVOICE ||--o{ LINE_ITEM : contains
    INVOICE ||--o{ PAYMENT : receives

    LINE_ITEM }o--|{ USAGE_RECORD : sourced_from

    CUSTOMER {
        UUID id
        String name
        String email
        String stripe_customer_id
        DateTime created_at
    }
    ... (Full Data Dictionary is detailed in the attached Phase 2.5 document)
```

### 3.2 Key Tables

| Table | Purpose | Key Relationships |
| :--- | :--- | :--- |
| `CUSTOMER` | Stores core customer data and external payment provider IDs. | `CUSTOMER` 1:N `SUBSCRIPTION` |
| `PRODUCT` / `PLAN` / `PRICE` | Defines the catalog of sellable items and their pricing. | `PRODUCT` 1:N `PLAN` 1:N `PRICE` |
| `SUBSCRIPTION` | Tracks the customer's active plans and their status. | `SUBSCRIPTION` 1:N `USAGE_RECORD` |
| `USAGE_RECORD` | Stores metered usage events (e.g., attestations, validations). | `USAGE_RECORD` 1:1 `LINE_ITEM` |
| `INVOICE` / `PAYMENT` | Manages billing cycles, line items, and payment reconciliation. | `INVOICE` 1:N `LINE_ITEM` |

## 4.0 Phase 2.6: API Specification (Service Contract)

The API is a RESTful contract for managing the source of truth data.

### 4.1 Core Endpoints

| Resource | Method | URL | Description | Permissions |
| :--- | :--- | :--- | :--- | :--- |
| Customer | `POST` | `/api/v1/customers` | Creates a new customer. | `billing:customers:create` |
| Customer | `GET` | `/api/v1/customers/{id}` | Retrieves customer details. | `billing:customers:read` |
| Subscription | `POST` | `/api/v1/subscriptions` | Creates a new subscription. | `billing:subscriptions:create` |
| Subscription | `PATCH` | `/api/v1/subscriptions/{id}` | Updates/Cancels a subscription. | `billing:subscriptions:update` |
| Usage | `POST` | `/api/v1/usage-records` | Reports metered usage. | `billing:usage:create` |

## 5.0 Phase 2.7: Event-Driven Integration (Synchronization)

This defines the asynchronous mechanism for synchronizing critical budget and routing data to the SmartGateway's local cache for high-performance operations.

### 5.1 SmartGateway Local Schema (Target)

The SmartGateway maintains a local, high-performance `budgets` table, which is updated via events from the Billing service.

| Table | Purpose | Key Fields for Sync |
| :--- | :--- | :--- |
| `budgets` | Local cache for budget enforcement. | `tenant_id`, `subscription_id`, `plan_id`, `total_budget`, `current_spend`, `period_end` |
| `routing_policies` | Local cache for routing decisions. | `priority`, `match_expression`, `strategy`, `targets` |

### 5.2 Key Events Published by Billing Service

| Event Name | Trigger | SmartGateway Action |
| :--- | :--- | :--- |
| `subscription.created` | New subscription is activated. | **INSERT** a new record into the local `budgets` table. |
| `subscription.updated` | Plan change, budget change, or cancellation. | **UPDATE** the corresponding record in the local `budgets` table. |
| `invoice.paid` | Invoice paid, typically resetting the billing cycle. | **UPDATE** the `period_start` and `period_end` columns in the local `budgets` table. |

## 6.0 Conclusion

The Billing Microservice is fully specified and ready for the implementation phase. The design ensures that the TCP ecosystem has a robust, scalable, and auditable revenue engine that supports our complex, hybrid monetization strategy while maintaining the high-performance requirements of the SmartGateway.

---
**Attachments:**
*   `billing_phase2.5_data_model.md`
*   `billing_phase2.6_api_spec.md`
*   `billing_phase2.7_event_spec.md`
