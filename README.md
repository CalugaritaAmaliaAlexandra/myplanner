# MyPlanner (Calendar & Appointments) — Flask + SQLite

## Short Description
Local web app (runs on your computer) to manage events in a monthly calendar + day view, with full CRUD, search/filtering, and PDF export (weekly agenda).


## Repository
Girhub repository:
https://github.com/MARIO200518/myplanner

## Install
```bash
python3 -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate

pip install -r requirements.txt
```

## Run
```bash
python run.py
```
Open in browser: http://127.0.0.1:5000

Database is created automatically at `data/events.db`.

## Features
- Monthly calendar (navigate months)
- Days show event counts
- Day view (events for selected day)
- CRUD: Add / Edit / Delete / Details
- Search by keyword + filter by category + date range
- Weekly agenda PDF export (Mon–Sun)

## Tests
```bash
pytest -q
```

## Usage Instructions
- Navigate the monthly calendar using the Previous / Next month buttons
- Each day displays the number of scheduled events
- Click on a day to view all events for that date
- Add new events using the “Add event” form
- Edit or delete existing events from the event details page
- Search events by keyword, category, or date range
- Export the current week’s agenda (Monday–Sunday) as a PDF file from the calendar page

## Team Members & Individual Contributions

This project was developed by a team of two members.

### Amalia
- Worked on Flask routes for adding, editing, and viewing events
- Implemented form validation and input processing in Python
- Created and modified HTML templates using Jinja2 and Bootstrap
- Connected frontend pages with backend logic
- Helped with overall application structure

### Mario
- Implemented the database logic using SQLite
- Wrote functions for creating, reading, updating, and deleting events
- Implemented calendar logic and date handling
- Added weekly PDF export functionality using ReportLab
- Helped integrate backend logic with frontend pages and documentation

## Difficulties Encountered & Solutions

- **Calendar generation:** solved using Python’s `calendar` module and a custom helper function.
- **Form validation:** handled through server-side validation before database operations.
- **PDF export:** implemented using ReportLab with manual layout control for pagination.
- **Code organization:** resolved by separating logic into routes, models, utilities, and templates.

## File Descriptions

### run.py
Entry point of the application.
Creates the Flask application using the application factory and starts the development server

### app/__init__.py
Initializes and configures the Flask application.  
Creates the app instance, sets configuration values, initializes the database, and registers the application routes.

### app/models.py
Handles all database-related logic of the application.

This module:
- defines the `Event` data model using a dataclass
- initializes the SQLite database and required tables
- manages the database connection
- implements all CRUD operations (create, read, update, delete)
- provides query functions for listing, searching, and filtering events
- contains utility queries for day, month, and week-based event retrieval

The file acts as the data access layer, separating database logic from routing and presentation.

### app/calendar_utils.py
Provides helper functions for building the monthly calendar grid and formatting calendar data.

### app/pdf_export.py
Generates a weekly agenda PDF using ReportLab.

This module provides `export_week_pdf(any_date, events)` which:
- computes the Monday–Sunday range of the week containing `any_date`
- groups the provided events by date and sorts them by time
- renders a simple A4 PDF (title + day sections + event lines)
- returns the PDF as `bytes`, ready to be sent as a file download

### app/routes.py
Defines all application routes and connects the user interface to the data layer.

#### `_db()`
Returns the SQLite database path from the application configuration.

#### `_parse_int(value, default)`
Safely parses an integer from a query parameter, falling back to a default value on failure.

#### `_validate_event_form(form)`
Validates and cleans event form data, returning validation status, cleaned data, and error messages.

#### `home()`
Redirects the root URL to the current month calendar view.

#### `calendar_view()`
Renders the monthly calendar view, including event counts and month navigation.

#### `day_view(date_str)`
Displays all events for a specific day after validating the date parameter.

#### `add_event_view()`
Handles event creation via a form (GET to display, POST to validate and save).

#### `event_details(event_id)`
Displays details for a single event or redirects if the event does not exist.

#### `edit_event_view(event_id)`
Handles editing of an existing event with form validation and database update.

#### `delete_event_view(event_id)`
Deletes an event and redirects the user with a success or error message.

#### `search_view()`
Provides keyword, category, and date range search for events.

#### `export_week(date)`
Generates and returns a weekly agenda PDF for download.
