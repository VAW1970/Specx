# Specification — Chemstore (Refined based on Additional Context)

## Overview
The Chemstore system is a Django-based inventory management application designed for laboratory settings. Its primary goal is to manage reagent stock, track expiration dates, manage physical locations, generate automated alerts, and facilitate reporting for laboratory efficiency.

## Requirements
- [x] **Requirement 1 (Inventory Management):** The system must allow users to register, view, add, edit, and delete reagent items, including details such as name, quantity, expiration date, location, and shelf.
- [x] **Requirement 2 (Location Tracking):** Each reagent item must be associated with a specific physical location and shelf within the laboratory.
- [x] **Requirement 3 (Expiration Tracking):** The system must accurately track the expiration dates for all reagents.
- [x] **Requirement 4 (Status Dashboard):** The system must provide a dashboard view categorized by status: 'Vencidos' (Expired), 'Conformes' (Compliant), and 'Alertas' (Reagents expiring within 30 days).
- [x] **Requirement 5 (Alert System):** The system must automatically generate alerts for reagents expiring within the next 30 days.
- [x] **Requirement 6 (Reporting):** The system must support the generation and emission of reports based on the inventory data, capable of being sent to a specified physical printer.

## Constraints
- **Technical Constraints:**
    - The backend must be implemented using the Django framework.
    - The data persistence layer must be suitable for tracking relational inventory data.
    - The reporting mechanism must interface with local printer drivers or system commands.
- **Business Constraints:**
    - Data integrity, especially concerning expiration dates, must be strictly maintained.
    - The system must be usable by laboratory staff in a practical and intuitive manner.

## User Stories
- As a **Laboratory Manager**, I want to manage reagent inventory so that I can keep accurate records of all stock.
- As a **Lab Technician**, I want to track the location and shelf for each reagent so that I can easily locate items.
- As a **Lab Manager**, I want an automated dashboard view of reagent status (Expired, Compliant, Alerts) so that I can quickly identify urgent stock issues.
- As a **Lab Technician**, I want to receive timely alerts about reagents expiring in the next 30 days so that I can proactively manage stock rotation.
- As a **Lab Manager**, I want to generate and print a comprehensive report of the inventory so that I can easily document stock status for external records.

## Acceptance Criteria
- **Criterion 1:** A user must be able to successfully add a new reagent with all required fields (name, quantity, expiration date, location, shelf).
- **Criterion 2:** The system must correctly categorize reagents into 'Vencidos', 'Conformes', or 'Alertas' based on the current date and expiration date.
- **Criterion 3:** If a reagent expires within 30 days, an alert must be generated, and this status must be visible on the dashboard.
- **Criterion 4:** A report generation function must successfully compile the inventory data and output it in a format suitable for printing via a configured printer.
- **Criterion 5:** The system must adhere to Django's established ORM patterns for data interaction.

## Non-Functional Requirements
- **Performance:** Dashboard loading times must be under 3 seconds for typical inventory sizes.
- **Security:** Standard Django authentication/authorization must be enforced. Data access must be restricted based on user roles.
- **Scalability:** The database schema should be designed to support growth in the number of reagents and locations.
- **Usability:** The interface must be intuitive, especially the dashboard and reporting features, requiring minimal training for lab staff.