B2B Charge System

This project is a B2B recharge software. We have three user roles: Admin, Customer, and Vendor. The authentication system uses a phone number and OTP code. Anyone can sign up as a Customer in the system, and later, if they wish, they can apply to become a Vendor. After approval by the Admin, their role changes to Vendor. Then, they can request a recharge, and upon Admin approval, the Vendor’s panel is credited, allowing them to increase the balance of Customers.

In this system, PostgreSQL is used as the database. Pytest is used for writing tests, and Locust is used for stress testing and concurrent testing.

To set up the project, first clone the repository, then install the dependencies listed in the requirements.txt file.
