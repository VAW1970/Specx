Based on the goals, constraints, and implementation steps outlined in `SPEC.md` and `PLAN.md`, here is the refined, atomic, and prioritized task list for the Chemstore project.

This structure follows the phased implementation plan defined in the `PLAN.md` to ensure data integrity and feature completion sequentially.

---

# Tasks — Chemstore (Refined & Atomic)

## Phase 1: MVP (Data Foundation)
*(Goal: Establish the core data models and persistence.)*

### Task 1: Define Data Models and Initial Migration (High Priority)
**Description:** Define the Django models for `Location`, `Reagent`, and the linking model `InventoryItem`. Create and apply the initial database migrations.
**Steps:**
1. Define `Location` model (name, shelf_designation).
2. Define `Reagent` model (name, quantity, expiration_date, status).
3. Define `InventoryItem` model linking `Reagent` and `Location`.
4. Create and apply database migrations.
**Definition of Done:**
- [ ] All three models are defined in `models.py`.
- [ ] Migrations are successfully applied to the database.

## Phase 2: Inventory Management Endpoints (CRUD)
*(Goal: Implement the ability to manage reagent stock.)*

### Task 2: Implement Reagent and Location CRUD Views (High Priority)
**Description:** Implement the Django views (using Django REST Framework or standard class-based views) to handle the full CRUD operations for `Reagent` and `Location` entities.
**Steps:**
1. Implement views for creating, reading, updating, and deleting `Location` records.
2. Implement views for creating, reading, updating, and deleting `Reagent` records.
3. Implement logic to handle data validation (especially for date/quantity inputs).
**Definition of Done:**
- [ ] All CRUD operations for Locations and Reagents are functional via the backend.
- [ ] Input validation prevents invalid data insertion.

## Phase 3: Status Calculation and Alert System
*(Goal: Implement the core business logic for tracking status and generating alerts.)*

### Task 3: Implement Expiration Status Calculation Logic (High Priority)
**Description:** Develop the backend logic (likely in the Model or a service layer) to calculate the status ('Vencidos', 'Conformes', 'Alertas') for every reagent based on the current date and its `expiration_date`.
**Steps:**
1. Write a function/method to determine the status based on the expiration date.
2. Ensure the status is updated automatically upon saving a reagent record.
**Definition of Done:**
- [ ] Reagent status is accurately calculated upon data entry or record retrieval.

### Task 4: Implement Automated Alert Generation (High Priority)
**Description:** Implement the mechanism to identify and flag reagents that are expiring within the next 30 days.
**Steps:**
1. Write a query or loop to identify reagents where `expiration_date` is within the next 30 days.
2. Implement a system (e.g., a custom manager method or signal) to flag these items for display on the dashboard.
**Definition of Done:**
- [ ] Reagents expiring within 30 days are flagged correctly.
- [ ] These alerts are accessible for the dashboard view (Requirement 5).

## Phase 4: Reporting and Finalization
*(Goal: Fulfill the reporting requirement.)*

### Task 5: Develop Inventory Reporting Function (Medium Priority)
**Description:** Create the backend function that compiles the entire inventory data, categorized by status, suitable for report generation.
**Steps:**
1. Write a query to aggregate reagents by 'Vencidos', 'Conformes', and 'Alertas'.
2. Develop a function to compile all necessary details (Name, Location, Expiration Date) for a full inventory list.
**Definition of Done:**
- [ ] A function exists to generate the required aggregated inventory data.

### Task 6: Implement Report Generation and Output (Medium Priority)
**Description:** Implement the functionality to generate the report data and format it for physical printing.
**Steps:**
1. Design the output format (e.g., plain text or PDF structure).
2. Implement the mechanism to interface with the required printing method (e.g., generating a print-friendly PDF or using system commands as per constraints).
3. Log the report generation in `ReportLog` (if applicable).
**Definition of Done:**
- [ ] A report can be generated from the aggregated data.
- [ ] The report output is correctly formatted for printing (Requirement 6).