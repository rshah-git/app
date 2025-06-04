
import requests
import sys
import time
import json

class AISearchEngineTester:
    def __init__(self, base_url="https://7c94e30c-574b-4087-9778-6d816ab2a5a5.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # AI Categories based on the frontend implementation
        self.ai_categories = [
            { "id": "chatbot", "name": "Chatbot", "icon": "🤖", "query": "AI chatbot assistant conversation" },
            { "id": "code", "name": "Code Assistant", "icon": "💻", "query": "AI code assistant programming development" },
            { "id": "content", "name": "Content Creation", "icon": "📝", "query": "AI content creation writing generator" },
            { "id": "education", "name": "Education", "icon": "🎓", "query": "AI education learning tutorial platform" },
            { "id": "generative", "name": "Generative AI", "icon": "✨", "query": "generative AI model LLM GPT" },
            { "id": "healthcare", "name": "Healthcare", "icon": "🏥", "query": "AI healthcare medical diagnosis" },
            { "id": "image", "name": "Image Generation", "icon": "🎨", "query": "AI image generation art DALL-E Midjourney" },
            { "id": "music", "name": "Music", "icon": "🎵", "query": "AI music generation audio sound" },
            { "id": "productivity", "name": "Productivity", "icon": "⚡", "query": "AI productivity automation workflow tools" },
            { "id": "research", "name": "Research", "icon": "🔬", "query": "AI research papers academic science" },
            { "id": "video", "name": "Video Generation", "icon": "🎬", "query": "AI video generation editing deepfake" }
        ]

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            start_time = time.time()
            
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            
            elapsed_time = time.time() - start_time
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code} - Response time: {elapsed_time:.2f}s")
                try:
                    response_data = response.json()
                    print(f"Response data: {json.dumps(response_data, indent=2)[:500]}...")
                except:
                    print(f"Response text: {response.text[:500]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"Response: {response.text[:500]}...")
            
            result = {
                "name": name,
                "success": success,
                "status_code": response.status_code,
                "expected_status": expected_status,
                "response_time": elapsed_time,
                "url": url,
                "method": method
            }
            
            self.test_results.append(result)
            
            if success:
                try:
                    return success, response.json()
                except:
                    return success, response.text
            else:
                return success, None

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.test_results.append({
                "name": name,
                "success": False,
                "error": str(e),
                "url": url,
                "method": method
            })
            return False, None

    def test_health_check(self):
        """Test the health check endpoint"""
        return self.run_test(
            "Health Check",
            "GET",
            "api/health",
            200
        )

    def test_search(self, query):
        """Test the search endpoint with a specific query"""
        return self.run_test(
            f"Search for '{query}'",
            "POST",
            "api/search",
            200,
            data={"query": query}
        )

    def test_suggestions(self, query):
        """Test the suggestions endpoint with a specific query"""
        return self.run_test(
            f"Suggestions for '{query}'",
            "GET",
            "api/suggestions",
            200,
            params={"q": query}
        )
        
    def test_category_search(self, category):
        """Test search with a specific AI category query"""
        category_query = next((cat["query"] for cat in self.ai_categories if cat["id"] == category), None)
        if not category_query:
            print(f"❌ Category '{category}' not found")
            return False, None
            
        return self.run_test(
            f"Category Search for '{category}'",
            "POST",
            "api/search",
            200,
            data={"query": category_query}
        )
        
    def test_all_categories(self):
        """Test search with all AI categories"""
        results = []
        for category in self.ai_categories:
            success, response = self.test_category_search(category["id"])
            results.append({
                "category": category["name"],
                "success": success,
                "results_count": len(response.get("results", [])) if success and response else 0
            })
        return results

    def print_summary(self):
        """Print a summary of all test results"""
        print("\n" + "="*50)
        print(f"📊 TEST SUMMARY: {self.tests_passed}/{self.tests_run} tests passed")
        print("="*50)
        
        for result in self.test_results:
            status = "✅ PASSED" if result.get("success") else "❌ FAILED"
            print(f"{status} - {result.get('name')}")
            if not result.get("success") and "error" in result:
                print(f"  Error: {result.get('error')}")
            elif "status_code" in result:
                print(f"  Status: {result.get('status_code')} (expected {result.get('expected_status')})")
                print(f"  Response time: {result.get('response_time'):.2f}s")
            print("-"*50)
        
        return self.tests_passed == self.tests_run

def main():
    # Get the backend URL from environment or use default
    tester = AISearchEngineTester()
    
    print("\n===== TESTING BACKEND API =====")
    
    # Test health check endpoint
    tester.test_health_check()
    
    # Test search endpoint with various AI-related queries
    ai_queries = [
        "OpenAI ChatGPT",
        "Midjourney AI art",
        "machine learning tutorials",
        "Anthropic Claude",
        "Stable Diffusion"
    ]
    
    print("\n===== TESTING GENERAL SEARCH =====")
    for query in ai_queries:
        tester.test_search(query)
    
    # Test suggestions endpoint
    suggestion_queries = ["openai", "mid", "machine", "claude", "stable"]
    
    print("\n===== TESTING SEARCH SUGGESTIONS =====")
    for query in suggestion_queries:
        tester.test_suggestions(query)
    
    # Test category searches
    print("\n===== TESTING CATEGORY SEARCHES =====")
    print("\nTesting specific categories:")
    tester.test_category_search("chatbot")
    tester.test_category_search("image")
    tester.test_category_search("code")
    
    print("\nTesting all categories:")
    category_results = tester.test_all_categories()
    
    print("\n===== CATEGORY SEARCH RESULTS =====")
    for result in category_results:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['category']}: {result['results_count']} results")
    
    # Print summary
    all_passed = tester.print_summary()
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
