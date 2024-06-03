# Secure Coding Practice
 A sample web application containing vulnerabilities from OWASP Top 10. All information in this repository is entirely fictional.

## The Case:
 Bikes as a Service* (BaaS) is a startup that offers easy-to-use bike rental across Oslo. Your task is to review the security of their Web Portal. Using your knowledge of OWASP Top 10, can you find any vulnerabilities?

 *BaaS as a concept for a fictional organization was originally created by Adam Shostack, to teach people how to perform threat modelling. I have repurposed this concept and scenario for this practical assignment.

## The Web Portal
 The Web Portal allows users to:
 - Create and update their profiles, including contact information, payment information, and their subscription to the bike rental service,
 - See a history of past bike rentals, and search for specific previous bike rentals.

 The application is built using Python and the web application framework «Django». Django handles functionality such as authentication and session management out of the box.

 ### Important files:
 - **core/models.py** – Defines the database tables using Djangos object relational mapping (ORM)
 - **baas/settings.py** – Defines the Django configuration for the web server
 - **webportal/urls.py** – Handles the routing of requests to the webportal
 - **webportal/views.py** – Handles the business logic of each request and renders responses using html from the templates folder
 - **webportal/forms.py** – Handles validation of user input

## The API
 The API is used by users, fleet managers, and the bikes themselves. It keeps track of the location and status of each bike, and provides some simple functionality to manage user accounts.

 The API is built using a popular addition to the Django framework called "Django Rest Framework (DRF)". It automates much of the creation and serialization of CRUD endpoints for objects/models defined through the Django ORM. 
 
 The API can be viewed and used directly from your browser from the "/api" route through DRFs "browseable API" functionality. An OpenAPI specification can also be downloaded from "/api/schema", or viewed in the browser through "api/schema/swagger" or "/api/schema/redoc".

 ### Important files
 - **core/models.py** – Defines the database tables using Djangos object relational mapping (ORM)
 - **baas/settings.py** – Defines the configuration of important components such as DRF and the JWT implementation
 - **api/urls.py** - Handles the routing of requests to the API endpoint
 - **api/views.py** - Handles the business logic of each route
 - **api/serializers.py** - Handles validation of user input

## Missions and Challenges:
  ### Elevation of Privilege (Starter-mission):
   1. Find a way to change the username of another user (Hint: A01 Broken Access Control)
   2. Using the trick from task 1, can you find any users of particular interest?
   3. Log in on the account you found in task 2 (Hint: A07 Identification and Authentication Failures)
   4. You got access! But now what? Can you find anything new you have access to?
   5. Give yourself a free lifetime subscription to the bike rental service

 ### Web Challenges:
  - **Security Misconfiguration:** The application is configured with DEBUG = TRUE, which means it will share way too much information if something goes wrong. Can you find a way to force the application into an error-state to reveal this information?
  - **Broken Access Control:** Can you find a way to use the credit card of another user to pay for your subscription without using admin privileges?
  - **Cross Site Scripting:** The profile page is looking a bit bland at the moment. Can you find a way to give it some more style?
  - **Broken Cryptography:** Find out what encryption algorithm is used to safeguard passwords in the database. Can you crack any of the passwords?

 ### API Challenges:
 - **Broken Function Level Authorization:** What actions you should be allowed to do often depends on business context. Can you find an instance where the endpoint logically should be limited to fewer users than the current implementation allows?
 - **Broken Object Property Level Authorization:** Normal users have limited access to the API. As a normal user, can you find a way to elevate your privileges to gain access to more of the API endpoints?
 - **Broken Authentication:** Something is not quite right with the JWT-implementation. Can you exploit this to log in as another user?
 - **Unrestricted Resource Consumption:** Seems like the Baas-developers have decided to not implement request-throttling on any of their routes. Which routes do you think would be most vulnerable to spam-attacks?

 ### Code Review:
Some vulnerabilities are not so easy to demonstrate in a live example, but they are still obvious when looking directly in the source code. How many more vulnerabilities can you find in this repository?