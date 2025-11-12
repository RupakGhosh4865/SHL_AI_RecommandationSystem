"""
Interactive Testing Tool for SHL Assessment Recommender
Run this to test your API with sample queries
"""

import requests
import json
import time
from datetime import datetime

API_URL = "http://localhost:8000"

# Test queries with expected outcomes
TEST_CASES = [
    {
        "query": "Python developer with 5 years experience in backend development",
        "expected_keywords": ["python", "developer", "programming", "software"],
        "category": "Technical"
    },
    {
        "query": "Java developer who can collaborate effectively with business teams",
        "expected_keywords": ["java", "developer", "software"],
        "category": "Technical"
    },
    {
        "query": "Customer service representative with excellent communication skills",
        "expected_keywords": ["customer", "service", "communication"],
        "category": "Business"
    },
    {
        "query": "Data analyst with SQL, Excel, and data visualization experience",
        "expected_keywords": ["data", "sql", "analyst"],
        "category": "Technical"
    },
    {
        "query": "Marketing Manager with team leadership and strategic planning",
        "expected_keywords": ["manager", "leadership", "management"],
        "category": "Management"
    },
    {
        "query": "Administrative assistant for bank operations",
        "expected_keywords": ["administrative", "assistant", "bank"],
        "category": "Administrative"
    },
    {
        "query": ".NET developer with MVC and API development experience",
        "expected_keywords": [".net", "mvc", "developer"],
        "category": "Technical"
    },
    {
        "query": "Accounts payable specialist with attention to detail",
        "expected_keywords": ["accounts", "payable", "accounting"],
        "category": "Finance"
    },
    {
        "query": "Branch manager with 10 years banking experience",
        "expected_keywords": ["branch", "manager", "bank"],
        "category": "Management"
    },
    {
        "query": "Entry level position for new college graduate",
        "expected_keywords": ["entry", "apprentice", "graduate"],
        "category": "Entry Level"
    }
]


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def print_section(text):
    """Print formatted section"""
    print(f"\n{'─'*70}")
    print(f"  {text}")
    print(f"{'─'*70}")


def test_health():
    """Test API health"""
    print_section("Testing API Health")
    
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        
        if response.status_code == 200:
            print("✅ API is healthy!")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ API returned status: {response.status_code}")
            return False
    
    except requests.ConnectionError:
        print("❌ Cannot connect to API!")
        print(f"   Make sure the API is running at: {API_URL}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_recommendation(query, expected_keywords=[], category="General"):
    """Test a single recommendation query"""
    print_section(f"Test: {category} Role")
    print(f"Query: \"{query}\"")
    
    try:
        # Send request
        start_time = time.time()
        response = requests.post(
            f"{API_URL}/recommend",
            json={"query": query},
            timeout=30
        )
        response_time = time.time() - start_time
        
        # Check response
        if response.status_code != 200:
            print(f"❌ Failed with status: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
        
        data = response.json()
        assessments = data.get("recommended_assessments", [])
        
        # Validate results
        if not assessments:
            print("⚠️  No recommendations returned")
            return False
        
        if len(assessments) > 10:
            print(f"⚠️  Too many results: {len(assessments)} (max 10)")
            return False
        
        # Display results
        print(f"\n✅ Success! ({response_time:.2f}s)")
        print(f"   Found {len(assessments)} recommendations:")
        
        for i, assessment in enumerate(assessments[:5], 1):  # Show top 5
            print(f"\n   [{i}] {assessment['name']}")
            print(f"       Duration: {assessment['duration']} min")
            print(f"       Category: {', '.join(assessment['test_type'])}")
            print(f"       Remote: {assessment['remote_support']}")
            print(f"       URL: {assessment['url'][:60]}...")
        
        if len(assessments) > 5:
            print(f"\n   ... and {len(assessments) - 5} more")
        
        # Check for expected keywords
        if expected_keywords:
            found_keywords = []
            all_text = " ".join([a['name'].lower() + " " + a.get('description', '').lower() 
                                for a in assessments])
            
            for keyword in expected_keywords:
                if keyword.lower() in all_text:
                    found_keywords.append(keyword)
            
            if found_keywords:
                print(f"\n   ✓ Found expected keywords: {', '.join(found_keywords)}")
            else:
                print(f"\n   ⚠️  Expected keywords not found: {', '.join(expected_keywords)}")
        
        # Validate response format
        validation_ok = True
        for assessment in assessments:
            if not all(key in assessment for key in ['url', 'name', 'duration', 
                                                      'adaptive_support', 'remote_support']):
                print(f"\n   ⚠️  Missing required fields in: {assessment.get('name', 'Unknown')}")
                validation_ok = False
            
            if assessment['adaptive_support'] not in ['Yes', 'No']:
                print(f"\n   ⚠️  Invalid adaptive_support: {assessment['adaptive_support']}")
                validation_ok = False
            
            if not isinstance(assessment['duration'], int):
                print(f"\n   ⚠️  Invalid duration type: {type(assessment['duration'])}")
                validation_ok = False
        
        if validation_ok:
            print(f"\n   ✓ Response format valid")
        
        return True
    
    except requests.Timeout:
        print(f"❌ Request timeout (>30s)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_edge_cases():
    """Test edge cases"""
    print_section("Testing Edge Cases")
    
    edge_cases = [
        {
            "name": "Empty query",
            "query": "",
            "expected_status": 400
        },
        {
            "name": "Very short query",
            "query": "IT",
            "expected_status": 400
        },
        {
            "name": "Special characters",
            "query": "C++ & SQL @Company!",
            "expected_status": 200
        },
        {
            "name": "Numbers only",
            "query": "123456",
            "expected_status": 200
        }
    ]
    
    passed = 0
    for case in edge_cases:
        print(f"\n  Testing: {case['name']}")
        print(f"  Query: \"{case['query']}\"")
        
        try:
            response = requests.post(
                f"{API_URL}/recommend",
                json={"query": case['query']},
                timeout=10
            )
            
            if response.status_code == case['expected_status']:
                print(f"  ✅ Correct status: {response.status_code}")
                passed += 1
            else:
                print(f"  ❌ Wrong status: {response.status_code} (expected {case['expected_status']})")
        
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print(f"\nEdge Cases: {passed}/{len(edge_cases)} passed")
    return passed == len(edge_cases)


def run_all_tests():
    """Run complete test suite"""
    print_header("🧪 SHL Assessment Recommender - Test Suite")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API: {API_URL}")
    
    # Test 1: Health Check
    if not test_health():
        print("\n❌ API is not healthy. Please start the API first!")
        print("   Run: docker-compose up")
        return False
    
    # Test 2: Basic Recommendations
    print_header("Testing Recommendations")
    
    passed = 0
    failed = 0
    
    for test_case in TEST_CASES:
        success = test_recommendation(
            test_case['query'],
            test_case['expected_keywords'],
            test_case['category']
        )
        
        if success:
            passed += 1
        else:
            failed += 1
        
        time.sleep(1)  # Small delay between tests
    
    # Test 3: Edge Cases
    edge_cases_ok = test_edge_cases()
    
    # Summary
    print_header("📊 Test Summary")
    print(f"\n  Health Check:     ✅ Passed")
    print(f"  Basic Tests:      {passed} ✅ / {failed} ❌ (Total: {passed + failed})")
    print(f"  Edge Cases:       {'✅ Passed' if edge_cases_ok else '❌ Failed'}")
    
    total_tests = 1 + passed + failed + (1 if edge_cases_ok else 0)
    passed_tests = 1 + passed + (1 if edge_cases_ok else 0)
    
    print(f"\n  Overall: {passed_tests}/{total_tests} tests passed")
    
    if failed == 0 and edge_cases_ok:
        print("\n  🎉 ALL TESTS PASSED!")
        print("  Your API is working correctly! ✅")
        return True
    else:
        print("\n  ⚠️  Some tests failed. Please review the output above.")
        return False


def interactive_mode():
    """Interactive testing mode"""
    print_header("🎮 Interactive Test Mode")
    print("\nEnter your own queries to test the API.")
    print("Type 'quit' to exit.\n")
    
    while True:
        query = input("Enter query: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye! 👋")
            break
        
        if not query:
            continue
        
        test_recommendation(query, category="Custom")
        print()


def main():
    """Main entry point"""
    print("\n" + "="*70)
    print("  SHL Assessment Recommender - Testing Tool")
    print("="*70)
    print("\nWhat would you like to do?")
    print("  1. Run all automated tests")
    print("  2. Interactive mode (test your own queries)")
    print("  3. Run both")
    print("  4. Exit")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        run_all_tests()
    elif choice == "2":
        interactive_mode()
    elif choice == "3":
        run_all_tests()
        print("\n" + "="*70)
        interactive_mode()
    else:
        print("\nGoodbye! 👋")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user. Goodbye! 👋")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")