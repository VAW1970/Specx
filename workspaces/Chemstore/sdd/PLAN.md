## Plan — Chemstore (Refined)

Based on the requirements in `SPEC.md`, this plan outlines the architecture, data model, technology choices, and implementation steps necessary to build the Chemstore inventory management system.

### Architecture
The system will follow the standard Django MVC (Model-View-Template) pattern, emphasizing separation of concerns as required by the non-functional requirements.

*   **Backend:** Django (handling business logic, ORM, and API endpoints).
*   **Data Layer:** PostgreSQL or SQLite (relational database suitable for inventory tracking).
*   **Presentation Layer:** Standard Django templates for the dashboard and reporting views.

### Data Model
The data model focuses on accurately tracking reagents, their locations, and their expiration status to satisfy Requirements 1, 2, and 3.

| Entity | Fields | Relationships | Purpose |
| :--- | :--- | :--- | :--- |
| **Reagent** | `name` (CharField), `quantity` (IntegerField), `expiration_date` (DateField), `status` (CharField) | Foreign Key to Location, Shelf | Core inventory item. |
| **Location** | `name` (CharField), `shelf_designation` (CharField) | One-to-Many with Reagent | Defines physical storage areas. |
| **InventoryItem** (Optional/Refinement) | `reagent` (ForeignKey to Reagent), `location` (ForeignKey to Location) | Many-to-One | Links specific stock to a physical location. |
| **ReportLog** (For Reporting) | `report_type` (CharField), `generated_at` (DateTimeField), `output_data` (JSON/Text) | Many-to-One with User (implied for security) | Stores generated report details. |

### Implementation Steps
The implementation will be phased to ensure data integrity and critical features are developed sequentially.

1.  **Step one: Database Setup and Core Model Definition:**
    *   Define the core Django models for `Location`, `Reagent`, and `InventoryItem`.
    *   Set up the initial database structure and migration.
2.  **Step two: Inventory Management Endpoints (CRUD):**
    *   Implement the API/View logic for creating, reading, updating, and deleting (CRUD) reagents, ensuring strict validation on input data (Criterion 1).
3.  **Step three: Status Calculation and Alert System:**
    *   Implement the logic to calculate the status ('Vencidos', 'Conformes', 'Alertas') based on the current date and expiration dates (Criterion 2 & 3).
    *   Implement the automated alert generation mechanism for reagents expiring within 30 days (Requirement 5).
4.  **Step four: Reporting and Output:**
    *   Develop the reporting function to compile inventory data.
    *   Implement the mechanism to format the report output for printing (Criterion 4).

### Tech Stack
*   **Backend:** Django (Python)
*   **Database:** PostgreSQL (Recommended for robust relational integrity) or SQLite (for initial development).
*   **Deployment:** Standard WSGI deployment environment.
*   **Reporting Interface:** Backend processing combined with potential system calls or direct library integration for printer interaction (Constraint adherence).

### Milestones
| Milestone | Focus | Target Date | Criteria Met |
| :--- | :--- | :--- | :--- |
| **MVP (Data Foundation)** | Step 1: Data Models and Database Setup | 2024-01-01 | Data persistence established. |
| **Feature Complete (Inventory)** | Step 2: CRUD operations for Reagents and Locations | 2024-01-15 | Requirement 1 & 2 met. |
| **Alert & Status Logic** | Step 3: Expiration tracking, Status calculation, and Alerts | 2024-01-30 | Requirement 3, 4, & 5 met. |
| **Reporting Finalization** | Step 4: Report generation and printing mechanism | 2024-02-10 | Requirement 6 met. |