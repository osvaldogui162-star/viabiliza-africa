"""
Test API endpoints
Quick script to verify the API is working
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Health check: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_create_project():
    """Test creating a project"""
    try:
        data = {
            "nome": "Projeto Teste",
            "primeiroAno": 2024,
            "numAnos": 5,
            "unidadeMonetaria": "EUR"
        }
        response = requests.post(
            f"{BASE_URL}/api/projects",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Create project: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"Create project failed: {e}")
        return False

def test_list_projects():
    """Test listing projects"""
    try:
        response = requests.get(f"{BASE_URL}/api/projects")
        print(f"List projects: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"List projects failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Viabiliza+África API")
    print("=" * 60)
    
    if not test_health():
        print("\n❌ API is not responding. Make sure the server is running:")
        print("   python -m backend.src.app")
        exit(1)
    
    print("\n✅ Health check passed")
    
    if test_create_project():
        print("\n✅ Create project passed")
    else:
        print("\n❌ Create project failed")
    
    if test_list_projects():
        print("\n✅ List projects passed")
    else:
        print("\n❌ List projects failed")
    
    print("\n" + "=" * 60)

