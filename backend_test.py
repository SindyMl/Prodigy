#!/usr/bin/env python3
"""
Backend API Testing for Prodigy Productivity Application
Tests all backend endpoints including authentication, quotes, users, projects, tasks, events, and flashcards
"""

import requests
import json
from datetime import datetime, timezone
import uuid
import time

# Configuration
BASE_URL = "https://study-work-app.preview.emergentagent.com/api"
MOCK_TOKEN = "mock_user123"
HEADERS = {
    "Authorization": f"Bearer {MOCK_TOKEN}",
    "Content-Type": "application/json"
}

class BackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS
        self.test_results = []
        self.created_resources = {
            "projects": [],
            "tasks": [],
            "events": [],
            "flashcards": []
        }
    
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()
    
    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("API Root Endpoint", True, f"Message: {data['message']}")
                    return True
                else:
                    self.log_test("API Root Endpoint", False, "No message in response", data)
                    return False
            else:
                self.log_test("API Root Endpoint", False, f"Status code: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("API Root Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_zenquotes_api(self):
        """Test ZenQuotes API integration"""
        try:
            response = requests.get(f"{self.base_url}/quote")
            if response.status_code == 200:
                data = response.json()
                if "quote" in data and "author" in data:
                    self.log_test("ZenQuotes API Integration", True, f"Quote: '{data['quote'][:50]}...' by {data['author']}")
                    return True
                else:
                    self.log_test("ZenQuotes API Integration", False, "Missing quote or author in response", data)
                    return False
            else:
                self.log_test("ZenQuotes API Integration", False, f"Status code: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("ZenQuotes API Integration", False, f"Exception: {str(e)}")
            return False
    
    def test_user_management(self):
        """Test user management endpoints"""
        success_count = 0
        
        # Test getting current user (should auto-create if not exists)
        try:
            response = requests.get(f"{self.base_url}/users/me", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "firebase_uid" in data and "email" in data:
                    self.log_test("Get Current User", True, f"User ID: {data['id']}, Email: {data['email']}")
                    success_count += 1
                else:
                    self.log_test("Get Current User", False, "Missing required user fields", data)
            else:
                self.log_test("Get Current User", False, f"Status code: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Get Current User", False, f"Exception: {str(e)}")
        
        # Test creating a new user manually
        try:
            user_data = {
                "firebase_uid": f"test_user_{uuid.uuid4().hex[:8]}",
                "email": f"testuser_{uuid.uuid4().hex[:8]}@example.com",
                "name": "Test User"
            }
            response = requests.post(f"{self.base_url}/users", json=user_data)
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data["email"] == user_data["email"]:
                    self.log_test("Create User", True, f"Created user: {data['name']} ({data['email']})")
                    success_count += 1
                else:
                    self.log_test("Create User", False, "User creation response invalid", data)
            else:
                self.log_test("Create User", False, f"Status code: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Create User", False, f"Exception: {str(e)}")
        
        return success_count == 2
    
    def test_projects_api(self):
        """Test projects CRUD operations"""
        success_count = 0
        project_id = None
        
        # Test creating a project
        try:
            project_data = {
                "title": "Test Project for API Testing",
                "description": "This is a test project created during API testing"
            }
            response = requests.post(f"{self.base_url}/projects", json=project_data, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data["title"] == project_data["title"]:
                    project_id = data["id"]
                    self.created_resources["projects"].append(project_id)
                    self.log_test("Create Project", True, f"Created project: {data['title']} (ID: {project_id})")
                    success_count += 1
                else:
                    self.log_test("Create Project", False, "Project creation response invalid", data)
            else:
                self.log_test("Create Project", False, f"Status code: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Create Project", False, f"Exception: {str(e)}")
        
        # Test getting all projects
        try:
            response = requests.get(f"{self.base_url}/projects", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get All Projects", True, f"Retrieved {len(data)} projects")
                    success_count += 1
                else:
                    self.log_test("Get All Projects", False, "Response is not a list", data)
            else:
                self.log_test("Get All Projects", False, f"Status code: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Get All Projects", False, f"Exception: {str(e)}")
        
        # Test getting specific project
        if project_id:
            try:
                response = requests.get(f"{self.base_url}/projects/{project_id}", headers=self.headers)
                if response.status_code == 200:
                    data = response.json()
                    if data["id"] == project_id:
                        self.log_test("Get Specific Project", True, f"Retrieved project: {data['title']}")
                        success_count += 1
                    else:
                        self.log_test("Get Specific Project", False, "Project ID mismatch", data)
                else:
                    self.log_test("Get Specific Project", False, f"Status code: {response.status_code}", response.text)
            except Exception as e:
                self.log_test("Get Specific Project", False, f"Exception: {str(e)}")
        
        return success_count >= 2, project_id
    
    def test_tasks_api(self, project_id):
        """Test tasks CRUD operations"""
        if not project_id:
            self.log_test("Tasks API Test", False, "No project ID available for testing tasks")
            return False
        
        success_count = 0
        task_id = None
        
        # Test creating a task
        try:
            task_data = {
                "title": "Test Task for API Testing",
                "description": "This is a test task created during API testing",
                "status": "todo"
            }
            response = requests.post(f"{self.base_url}/projects/{project_id}/tasks", json=task_data, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data["title"] == task_data["title"]:
                    task_id = data["id"]
                    self.created_resources["tasks"].append(task_id)
                    self.log_test("Create Task", True, f"Created task: {data['title']} (Status: {data['status']})")
                    success_count += 1
                else:
                    self.log_test("Create Task", False, "Task creation response invalid", data)
            else:
                self.log_test("Create Task", False, f"Status code: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Create Task", False, f"Exception: {str(e)}")
        
        # Test getting all tasks for project
        try:
            response = requests.get(f"{self.base_url}/projects/{project_id}/tasks", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get Project Tasks", True, f"Retrieved {len(data)} tasks for project")
                    success_count += 1
                else:
                    self.log_test("Get Project Tasks", False, "Response is not a list", data)
            else:
                self.log_test("Get Project Tasks", False, f"Status code: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Get Project Tasks", False, f"Exception: {str(e)}")
        
        # Test updating task (Kanban status change)
        if task_id:
            try:
                update_data = {
                    "status": "in_progress",
                    "position": 1
                }
                response = requests.put(f"{self.base_url}/tasks/{task_id}", json=update_data, headers=self.headers)
                if response.status_code == 200:
                    data = response.json()
                    if data["status"] == "in_progress":
                        self.log_test("Update Task (Kanban)", True, f"Updated task status to: {data['status']}")
                        success_count += 1
                    else:
                        self.log_test("Update Task (Kanban)", False, "Task status not updated correctly", data)
                else:
                    self.log_test("Update Task (Kanban)", False, f"Status code: {response.status_code}", response.text)
            except Exception as e:
                self.log_test("Update Task (Kanban)", False, f"Exception: {str(e)}")
        
        return success_count >= 2
    
    def test_events_api(self):
        """Test events CRUD operations"""
        success_count = 0
        
        # Test creating an event
        try:
            event_data = {
                "title": "Test Study Session",
                "event_type": "study",
                "datetime": datetime.now(timezone.utc).isoformat(),
                "duration": 90
            }
            response = requests.post(f"{self.base_url}/events", json=event_data, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data["title"] == event_data["title"]:
                    self.created_resources["events"].append(data["id"])
                    self.log_test("Create Event", True, f"Created event: {data['title']} ({data['event_type']})")
                    success_count += 1
                else:
                    self.log_test("Create Event", False, "Event creation response invalid", data)
            else:
                self.log_test("Create Event", False, f"Status code: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Create Event", False, f"Exception: {str(e)}")
        
        # Test getting all events
        try:
            response = requests.get(f"{self.base_url}/events", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get All Events", True, f"Retrieved {len(data)} events")
                    success_count += 1
                else:
                    self.log_test("Get All Events", False, "Response is not a list", data)
            else:
                self.log_test("Get All Events", False, f"Status code: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Get All Events", False, f"Exception: {str(e)}")
        
        # Test getting today's events
        try:
            response = requests.get(f"{self.base_url}/events/today", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get Today's Events", True, f"Retrieved {len(data)} events for today")
                    success_count += 1
                else:
                    self.log_test("Get Today's Events", False, "Response is not a list", data)
            else:
                self.log_test("Get Today's Events", False, f"Status code: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Get Today's Events", False, f"Exception: {str(e)}")
        
        return success_count >= 2
    
    def test_flashcards_api(self):
        """Test flashcards CRUD operations"""
        success_count = 0
        
        # Test creating a flashcard
        try:
            flashcard_data = {
                "question": "What is the capital of France?",
                "answer": "Paris"
            }
            response = requests.post(f"{self.base_url}/flashcards", json=flashcard_data, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data["question"] == flashcard_data["question"]:
                    self.created_resources["flashcards"].append(data["id"])
                    self.log_test("Create Flashcard", True, f"Created flashcard: {data['question']}")
                    success_count += 1
                else:
                    self.log_test("Create Flashcard", False, "Flashcard creation response invalid", data)
            else:
                self.log_test("Create Flashcard", False, f"Status code: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Create Flashcard", False, f"Exception: {str(e)}")
        
        # Test getting all flashcards
        try:
            response = requests.get(f"{self.base_url}/flashcards", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get All Flashcards", True, f"Retrieved {len(data)} flashcards")
                    success_count += 1
                else:
                    self.log_test("Get All Flashcards", False, "Response is not a list", data)
            else:
                self.log_test("Get All Flashcards", False, f"Status code: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Get All Flashcards", False, f"Exception: {str(e)}")
        
        return success_count >= 1
    
    def test_authentication_middleware(self):
        """Test Firebase authentication middleware"""
        success_count = 0
        
        # Test with valid mock token
        try:
            response = requests.get(f"{self.base_url}/users/me", headers=self.headers)
            if response.status_code == 200:
                self.log_test("Auth Middleware - Valid Token", True, "Mock token accepted")
                success_count += 1
            else:
                self.log_test("Auth Middleware - Valid Token", False, f"Status code: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Auth Middleware - Valid Token", False, f"Exception: {str(e)}")
        
        # Test with invalid token
        try:
            invalid_headers = {"Authorization": "Bearer invalid_token", "Content-Type": "application/json"}
            response = requests.get(f"{self.base_url}/users/me", headers=invalid_headers)
            if response.status_code == 401:
                self.log_test("Auth Middleware - Invalid Token", True, "Invalid token correctly rejected")
                success_count += 1
            else:
                self.log_test("Auth Middleware - Invalid Token", False, f"Expected 401, got {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Auth Middleware - Invalid Token", False, f"Exception: {str(e)}")
        
        # Test without token
        try:
            response = requests.get(f"{self.base_url}/users/me")
            if response.status_code == 403:  # FastAPI HTTPBearer returns 403 for missing auth
                self.log_test("Auth Middleware - No Token", True, "Missing token correctly rejected")
                success_count += 1
            else:
                self.log_test("Auth Middleware - No Token", False, f"Expected 403, got {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Auth Middleware - No Token", False, f"Exception: {str(e)}")
        
        return success_count >= 2
    
    def run_all_tests(self):
        """Run all backend API tests"""
        print("=" * 60)
        print("PRODIGY BACKEND API TESTING")
        print("=" * 60)
        print(f"Base URL: {self.base_url}")
        print(f"Mock Token: {MOCK_TOKEN}")
        print("=" * 60)
        print()
        
        # Test results tracking
        test_results = {}
        
        # 1. Test API Root
        test_results["api_root"] = self.test_api_root()
        
        # 2. Test ZenQuotes API
        test_results["zenquotes"] = self.test_zenquotes_api()
        
        # 3. Test Authentication Middleware
        test_results["auth_middleware"] = self.test_authentication_middleware()
        
        # 4. Test User Management
        test_results["user_management"] = self.test_user_management()
        
        # 5. Test Projects API
        projects_success, project_id = self.test_projects_api()
        test_results["projects"] = projects_success
        
        # 6. Test Tasks API (depends on project)
        test_results["tasks"] = self.test_tasks_api(project_id)
        
        # 7. Test Events API
        test_results["events"] = self.test_events_api()
        
        # 8. Test Flashcards API
        test_results["flashcards"] = self.test_flashcards_api()
        
        # Summary
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in test_results.values() if result)
        total = len(test_results)
        
        for test_name, success in test_results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status}: {test_name.replace('_', ' ').title()}")
        
        print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        # Detailed failure analysis
        failed_tests = [name for name, success in test_results.items() if not success]
        if failed_tests:
            print(f"\nFailed Tests: {', '.join(failed_tests)}")
            print("\nDetailed failure information:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"- {result['test']}: {result['details']}")
        
        return test_results

def main():
    """Main testing function"""
    tester = BackendTester()
    results = tester.run_all_tests()
    
    # Return exit code based on results
    all_passed = all(results.values())
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())