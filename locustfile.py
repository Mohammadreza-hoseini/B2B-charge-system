from locust import HttpUser, TaskSet, task, between
import random
import string


class UserBehavior(TaskSet):

    @task
    def register_and_verify(self):
        phone_number = "09123456" + ''.join(random.choices(string.digits, k=3))
        # Register user
        response = self.client.post("/accounts/register/", {"phone_number": phone_number, "role": 0})
        if response.status_code == 201:
            otp = response.json().get('otp')  # Assuming OTP is returned in the response
            # Verify OTP
            verify_response = self.client.post("/accounts/verify_otp/", {"phone_number": phone_number, "otp": otp})
            if verify_response.status_code == 200:
                print(f"Successfully verified OTP for phone number: {phone_number}")
            else:
                print(f"Failed to verify OTP: {verify_response.status_code}")


class VendorCreditRequest(TaskSet):

    def on_start(self):

        self.token = self.register_as_customer_and_become_vendor()

    def generate_phone_number(self):
        return "09123456" + ''.join(random.choices(string.digits, k=3))

    def register_as_customer_and_become_vendor(self):
        phone_number = self.generate_phone_number()

        # Register as Customer (Role = 0)
        response = self.client.post("/accounts/register/", json={"phone_number": phone_number, "role": 0})
        if response.status_code == 201:
            otp = response.json().get('otp')

            # Verify OTP
            verify_response = self.client.post("/accounts/verify_otp/", json={"phone_number": phone_number, "otp": otp})
            if verify_response.status_code == 200:
                token = verify_response.json().get('access')
                self.client.headers.update({"Authorization": f"Bearer {token}"})
                print(f"Successfully verified OTP for customer with phone number: {phone_number}")

                # Request to become a Vendor
                become_vendor_response = self.client.post("/accounts/become_seller/", json={"name": "sample"},
                                                          headers={"Authorization": f"Bearer {token}"})
                if become_vendor_response.status_code == 200:
                    vendor_id = become_vendor_response.json().get('id')

                    approve_response = self.client.post("/accounts/approve_seller/", json={"id": vendor_id},
                                                        headers={
                                                            "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI0NDkwNDUyLCJpYXQiOjE3MjQ0MDQwNTIsImp0aSI6ImZhYjlkZjEyNzVlNjQ0ZjZiNDM2Y2VlODZlMjg5MGMyIiwidXNlcl9pZCI6IjMxYzAxM2QxLTA4ZGQtNDMwMS1iYmUyLTcxZWE4N2E0ZjM5ZSJ9.jrlunsKVVJTNNPo6j7L9PCmGvyxGzsvToIJQsJINsSY"})
                    if approve_response.status_code == 200:
                        print(f"Vendor approved successfully for phone number: {phone_number}")
                        # vendor login
                        response = self.client.post("/accounts/register/",
                                                    json={"phone_number": phone_number, "role": 1})
                        if response.status_code == 201:
                            otp = response.json().get('otp')
                            verify_response = self.client.post("/accounts/verify_otp/",
                                                               json={"phone_number": phone_number, "otp": otp})
                            if verify_response.status_code == 200:
                                token = verify_response.json().get('access')
                                self.client.headers.update({"Authorization": f"Bearer {token}"})
                                print(f"Successfully verified OTP for vendor with phone number: {phone_number}")
                                print(token)
                                return token
                    else:
                        print(f"Failed to approve vendor: {approve_response.status_code}")
                else:
                    print(f"Failed to request to become a vendor: {become_vendor_response.status_code}")
            else:
                print(f"Failed to verify OTP: {verify_response.status_code}")
        else:
            print(f"Failed to register user: {response.status_code}")

    @task
    def create_credit_request(self):
        response = self.client.post("/transactions/vendor_credit_request/", json={
            "charge_amount": 1000.000
        }, headers={"Authorization": f"Bearer {self.token}"})
        if response.status_code == 200:
            print(f"Successfully created credit request")
        else:
            print(f"Failed to create credit request: {response.status_code}, {response.text}")


class VendorChargeCustomer(TaskSet):
    @task
    def charge_customer_vendor1(self):
        self.client.post("/transactions/vendor_charge_customer/", json={
            "phone_number": "09124552260",
            "charge_amount": "5"
        }, headers={
            "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI0NTg1NTQ4LCJpYXQiOjE3MjQ0OTkxNDgsImp0aSI6IjExN2NjMWI5OGE2MjRmZmJhODZmYjA5NGRiY2JhNDQyIiwidXNlcl9pZCI6IjcwYWViYWNhLTJkZDMtNDdkOS1iODNhLWM3NTg4Njg0MDVkNyJ9.L3UX0s_gIY2PBkgvs1h0lOZFUiqPeN3YrjyqVg5-w14"})

    @task
    def charge_customer_vendor2(self):
        self.client.post("/transactions/vendor_charge_customer/", json={
            "phone_number": "09379921755",
            "charge_amount": "5"
        }, headers={
            "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI0NTg1NTk3LCJpYXQiOjE3MjQ0OTkxOTcsImp0aSI6ImViZjIzN2I3Mjg2MjQxMDk4NDcwZGMzNjkxNjljNGZhIiwidXNlcl9pZCI6IjFjY2E2ZjBmLTBiNmQtNDc3Ni1hOTNlLTc3NzQ1NWI4NTg2MiJ9.m7h6BTQW0rbkW3Y58QlgNzIi_9EnJjToKbXU-bn_cRc"})


class WebsiteUser(HttpUser):
    tasks = [VendorChargeCustomer]
    wait_time = between(1, 5)
    host = "http://localhost:8000"  # Ensure this matches your Django server URL
