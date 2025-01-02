## Dear Comrade (Chief),

Below is a **comprehensive guide** to the Flask API endpoints for our **Panchayat Data** service. The application is designed to serve hierarchical location data (state → district → taluk → village) and the **members** associated with each village.

---

### Table of Contents
1. [Project Overview](#project-overview)  
2. [Endpoint Documentation](#endpoint-documentation)  
   - [Root (`/`)](#1-root)  
   - [States (`/api/states`)](#2-get-states)  
   - [Districts (`/api/districts/<state_code>`)](#3-get-districts)  
   - [Taluks (`/api/taluks/<district_code>`)](#4-get-taluks)  
   - [Villages (`/api/villages/<taluk_code>`)](#5-get-villages)  
   - [Members (`/api/members`)](#6-get-members)  
   - [Add Member (`/api/members/add`)](#7-add-member)  
3. [Data Format & CSV Handling](#data-format--csv-handling)  
4. [Local & Render Deployment](#local--render-deployment)  

---

## Project Overview

This API provides a structured way to query **Indian Panchayat data** from a CSV file (`panchayat_data_with_members.csv`). Each record contains hierarchical location info:

- **State** (`state_code`, `state`)  
- **District** (`district_code`, `district`)  
- **Taluk** (`taluk_code`, `taluk`)  
- **Village** (`village_code`, `village`)  
- **Members** (like *name*, *phone*, *email*, *role*, etc.)

With these endpoints, you can:
- Fetch **all states** and their codes.
- Drill down by **state_code** to get **districts**.
- Drill down by **district_code** to get **taluks**.
- Drill down by **taluk_code** to get **villages**.
- Fetch **members** by specifying a **village_code** (or get all members if no code is given).
- **Add a new member** to an existing village in the CSV.

---

## Endpoint Documentation

### 1. **Root**  
```
GET /
```
- **Description**: Serves the `index.html` template (the home page for the web app).  
- **Response**: Renders an HTML page if it exists (not JSON).

---

### 2. **Get States**  
```
GET /api/states
```
- **Description**: Returns a **list** of all **unique states** in the dataset.  
- **Response** (JSON Array):
  ```json
  [
    {
      "state_code": 9,
      "state": "Uttar Pradesh"
    },
    {
      "state_code": 8,
      "state": "Rajasthan"
    },
    ...
  ]
  ```
- **Example**:
  ```bash
  curl http://localhost:<port>/api/states
  ```

---

### 3. **Get Districts**  
```
GET /api/districts/<state_code>
```
- **Description**: For a **given state_code**, returns all **districts** associated with that state.  
- **URL Parameters**:
  - `<state_code>` (integer) — Example: `28` for Andhra Pradesh.  
- **Response** (JSON Array):
  ```json
  [
    {
      "district_code": 576,
      "district": "North And Middle Andaman"
    },
    {
      "district_code": 552,
      "district": "South Andamans"
    },
    ...
  ]
  ```
- **Example**:
  ```bash
  curl http://localhost:<port>/api/districts/35
  ```

---

### 4. **Get Taluks**  
```
GET /api/taluks/<district_code>
```
- **Description**: For a **given district_code**, returns all **taluks** (sometimes referred to as *blocks* or *tehsils*).  
- **URL Parameters**:
  - `<district_code>` (integer) — Example: `576`.  
- **Response** (JSON Array):
  ```json
  [
    {
      "taluk_code": 6793,
      "taluk": "Diglipur"
    },
    {
      "taluk_code": 6796,
      "taluk": "Mayabunder"
    },
    ...
  ]
  ```
- **Example**:
  ```bash
  curl http://localhost:<port>/api/taluks/576
  ```

---

### 5. **Get Villages**  
```
GET /api/villages/<taluk_code>
```
- **Description**: For a **given taluk_code**, returns all **villages** under that taluk.  
- **URL Parameters**:
  - `<taluk_code>` (integer) — Example: `6793`.  
- **Response** (JSON Array):
  ```json
  [
    {
      "village_code": 234465,
      "village": "Diglipur"
    },
    {
      "village_code": 245696,
      "village": "Gandhi Nagar"
    },
    ...
  ]
  ```
- **Example**:
  ```bash
  curl http://localhost:<port>/api/villages/6793
  ```

---

### 6. **Get Members**  
```
GET /api/members
```
- **Description**: Returns **Panchayat members** (Sarpanch, Ward Member, Pradhan, etc.) based on **query parameters**.  
- **Query Parameters**:
  - `village_code` (integer, optional): If provided, filters members to only that village.  
- **Response** (JSON Array):
  ```json
  [
    {
      "name": "V Boopathi",
      "role": "Pradhan",
      "phone": "95XXXXXX41",
      "email": "gp**********37@gmail.com",
      "village": "Diglipur",
      "taluk": "Diglipur",
      "district": "North And Middle Andaman",
      "state": "Andaman And Nicobar Islands"
    },
    ...
  ]
  ```
- **Usage**:
  - Get **all members** (no filters):
    ```bash
    curl http://localhost:<port>/api/members
    ```
  - Get members **by village_code**:
    ```bash
    curl http://localhost:<port>/api/members?village_code=234465
    ```

---

### 7. **Add Member**  
```
POST /api/members/add
```
- **Description**: Adds a **new member** to an **existing village**. Updates the in-memory DataFrame and **persists** the change in `panchayat_data_with_members.csv`.
- **Request Body** (JSON):
  ```json
  {
    "village_code": 234465,
    "name": "John Doe",
    "phone": "9876543210",
    "email": "john@example.com",
    "role": "Ward Member"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "message": "Member added successfully"
  }
  ```
- **Error Handling**:
  - If the `village_code` does not exist or any other error occurs, returns `{"success": false, "message": "...error details..."}`.

---

## Data Format & CSV Handling

- **CSV File**: `panchayat_data_with_members.csv`  
- **Columns**:  
  - `state_code` (int)  
  - `state` (string)  
  - `district_code` (int)  
  - `district` (string)  
  - `taluk_code` (int)  
  - `taluk` (string)  
  - `village_code` (int)  
  - `village` (string)  
  - `member_id` (int)  
  - `name` (string) — member’s full name  
  - `phone` (string) — member’s phone  
  - `email` (string) — member’s email  
  - `role` (string) — e.g., “Pradhan,” “Ward Member,” etc.

Each endpoint reads from or writes to this CSV via **Pandas**.  
If you **add a member**, a new row is **appended** to the CSV, keeping data consistent across sessions (though you should be aware of concurrency issues if multiple users add members simultaneously).

---

## Local & Render Deployment

1. **Local**:
   - Install dependencies:
     ```bash
     pip install flask pandas
     ```
   - Run the script:
     ```bash
     python <filename>.py
     ```
   - The API defaults to `PORT=5000` if the environment variable `PORT` is not set.

2. **Render**:
   - Render sets an environment variable `PORT` dynamically.  
   - The script reads from `os.environ.get('PORT', 5000)`.  
   - Ensure your `requirements.txt` includes **Flask** and **pandas**.  
   - Deploy as a **Web Service** on Render, and it’ll handle the rest.

That’s all, **Comrade (Chief)**! You have a fully functional, hierarchical Panchayat data API, ready for local testing or deployment on Render. Enjoy exploring the data!
