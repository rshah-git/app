from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from serpapi import GoogleSearch
import os
from dotenv import load_dotenv
import re
from typing import List, Optional
import asyncio
import httpx

load_dotenv()

app = FastAPI(title="AI Search Engine API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str
    page: Optional[int] = 1

class SearchResult(BaseModel):
    title: str
    link: str
    snippet: str
    displayed_link: str
    position: int

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total_results: int
    search_time: float
    query: str

# Comprehensive AI-related keywords for strict filtering
AI_KEYWORDS = [
    # Core AI terms
    "artificial intelligence", "machine learning", "deep learning", "neural network",
    "natural language processing", "computer vision", "robotics", "automation",
    
    # AI Companies & Products
    "openai", "anthropic", "claude", "chatgpt", "gpt", "gemini", "bard",
    "midjourney", "stable diffusion", "dall-e", "runwayml", "replicate",
    "hugging face", "transformers", "pytorch", "tensorflow", "keras",
    
    # AI Tools & Platforms
    "langchain", "vector database", "embedding", "llm", "large language model",
    "generative ai", "ai assistant", "chatbot", "ai tool", "ai platform",
    "ai api", "ai service", "ai model", "ai framework", "ai library",
    
    # AI Applications
    "ai writing", "ai image", "ai video", "ai code", "ai research",
    "ai startup", "ai company", "ai news", "ai blog", "ai tutorial",
    "prompt engineering", "fine-tuning", "rag", "retrieval augmented",
    
    # Technical AI terms
    "transformer", "attention mechanism", "diffusion model", "gan", 
    "reinforcement learning", "supervised learning", "unsupervised learning",
    "gradient descent", "backpropagation", "convolutional", "recurrent"
]

# AI-focused domains (known AI companies and platforms)
AI_DOMAINS = [
    "openai.com", "anthropic.com", "google.ai", "microsoft.com/ai",
    "huggingface.co", "replicate.com", "runway.com", "midjourney.com",
    "stability.ai", "cohere.ai", "ai21.com", "deepmind.com",
    "nvidia.com/ai", "ibm.com/watson", "aws.amazon.com/machine-learning",
    "azure.microsoft.com/cognitive-services", "cloud.google.com/ai",
    "paperswithcode.com", "arxiv.org", "towards", "medium.com",
    "github.com", "kaggle.com", "fast.ai", "deeplearning.ai"
]

def is_ai_related(title: str, snippet: str, link: str) -> bool:
    """
    Strict AI filtering function that checks if content is AI-related
    """
    # Combine title and snippet for analysis
    text_content = f"{title} {snippet}".lower()
    domain = link.lower()
    
    # Check for AI-related domains first (high confidence)
    for ai_domain in AI_DOMAINS:
        if ai_domain in domain:
            return True
    
    # Check for AI keywords in content
    keyword_matches = 0
    for keyword in AI_KEYWORDS:
        if keyword in text_content:
            keyword_matches += 1
            
    # Require at least 2 keyword matches for strict filtering
    # or 1 match if it's a core AI term
    core_ai_terms = ["artificial intelligence", "machine learning", "deep learning", 
                     "neural network", "openai", "chatgpt", "claude", "gemini"]
    
    has_core_term = any(term in text_content for term in core_ai_terms)
    
    return keyword_matches >= 2 or (keyword_matches >= 1 and has_core_term)

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "AI Search Engine API is running"}

@app.post("/api/search", response_model=SearchResponse)
async def search_ai_sites(request: SearchRequest):
    """
    Search the web for AI-related content using SerpAPI
    """
    try:
        import time
        start_time = time.time()
        
        # Get API key
        serpapi_key = os.getenv("SERPAPI_KEY")
        if not serpapi_key:
            raise HTTPException(status_code=500, detail="SerpAPI key not configured")
        
        # Enhanced query for better AI results
        enhanced_query = f"{request.query} AI artificial intelligence machine learning"
        
        # SerpAPI parameters
        params = {
            "engine": "google",
            "q": enhanced_query,
            "num": 20,  # Get more results for better filtering
            "start": (request.page - 1) * 10,
            "api_key": serpapi_key,
            "gl": "us",
            "hl": "en"
        }
        
        # Perform search
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "error" in results:
            raise HTTPException(status_code=500, detail=f"Search API error: {results['error']}")
        
        # Process and filter results
        organic_results = results.get("organic_results", [])
        filtered_results = []
        
        for i, result in enumerate(organic_results):
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            link = result.get("link", "")
            displayed_link = result.get("displayed_link", link)
            
            # Skip if essential fields are missing
            if not title or not link:
                continue
                
            # Apply strict AI filtering
            if is_ai_related(title, snippet, link):
                filtered_results.append(SearchResult(
                    title=title,
                    link=link,
                    snippet=snippet or "No description available",
                    displayed_link=displayed_link,
                    position=len(filtered_results) + 1
                ))
        
        # Limit to top 10 results per page
        filtered_results = filtered_results[:10]
        
        search_time = time.time() - start_time
        
        return SearchResponse(
            results=filtered_results,
            total_results=len(filtered_results),
            search_time=search_time,
            query=request.query
        )
        
    except Exception as e:
        print(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/api/suggestions")
async def get_search_suggestions(q: str):
    """
    Get AI-related search suggestions
    """
    suggestions = [
        "OpenAI ChatGPT",
        "Anthropic Claude",
        "Google Gemini",
        "Midjourney AI art",
        "Stable Diffusion",
        "Hugging Face transformers",
        "LangChain development",
        "AI code generation",
        "Machine learning tutorials",
        "AI news and updates"
    ]
    
    # Filter suggestions based on query
    if q:
        filtered_suggestions = [s for s in suggestions if q.lower() in s.lower()]
        return {"suggestions": filtered_suggestions[:5]}
    
    return {"suggestions": suggestions[:5]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)