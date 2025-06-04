import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const App = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTime, setSearchTime] = useState(0);
  const [totalResults, setTotalResults] = useState(0);
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const debounceTimer = useRef(null);
  const searchInputRef = useRef(null);

  const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  // AI Categories based on clubhouse.ai structure
  const aiCategories = [
    { id: 'chatbot', name: 'Chatbot', icon: '🤖', query: 'AI chatbot assistant conversation' },
    { id: 'code', name: 'Code Assistant', icon: '💻', query: 'AI code assistant programming development' },
    { id: 'content', name: 'Content Creation', icon: '📝', query: 'AI content creation writing generator' },
    { id: 'education', name: 'Education', icon: '🎓', query: 'AI education learning tutorial platform' },
    { id: 'generative', name: 'Generative AI', icon: '✨', query: 'generative AI model LLM GPT' },
    { id: 'healthcare', name: 'Healthcare', icon: '🏥', query: 'AI healthcare medical diagnosis' },
    { id: 'image', name: 'Image Generation', icon: '🎨', query: 'AI image generation art DALL-E Midjourney' },
    { id: 'music', name: 'Music', icon: '🎵', query: 'AI music generation audio sound' },
    { id: 'productivity', name: 'Productivity', icon: '⚡', query: 'AI productivity automation workflow tools' },
    { id: 'research', name: 'Research', icon: '🔬', query: 'AI research papers academic science' },
    { id: 'video', name: 'Video Generation', icon: '🎬', query: 'AI video generation editing deepfake' }
  ];

  // Handle category click
  const handleCategoryClick = (category) => {
    setSelectedCategory(category.id);
    setQuery(category.name);
    setShowSuggestions(false);
    performSearch(category.query);
  };

  // Debounced search function
  const performSearch = async (searchQuery) => {
    if (!searchQuery.trim()) {
      setResults([]);
      setHasSearched(false);
      return;
    }

    setLoading(true);
    setHasSearched(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: searchQuery,
          page: 1
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResults(data.results || []);
      setSearchTime(data.search_time || 0);
      setTotalResults(data.total_results || 0);
    } catch (error) {
      console.error('Search error:', error);
      setResults([]);
      setSearchTime(0);
      setTotalResults(0);
    } finally {
      setLoading(false);
    }
  };

  // Get search suggestions
  const getSuggestions = async (searchQuery) => {
    if (!searchQuery.trim()) {
      setSuggestions([]);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/suggestions?q=${encodeURIComponent(searchQuery)}`);
      const data = await response.json();
      setSuggestions(data.suggestions || []);
    } catch (error) {
      console.error('Suggestions error:', error);
      setSuggestions([]);
    }
  };

  // Handle input change with debouncing
  const handleInputChange = (e) => {
    const value = e.target.value;
    setQuery(value);

    // Clear previous timer
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }

    // Set new timer for search
    debounceTimer.current = setTimeout(() => {
      performSearch(value);
    }, 300);

    // Get suggestions immediately
    getSuggestions(value);
    setShowSuggestions(true);
  };

  // Handle search form submission
  const handleSearch = (e) => {
    e.preventDefault();
    setShowSuggestions(false);
    performSearch(query);
  };

  // Handle suggestion click
  const handleSuggestionClick = (suggestion) => {
    setQuery(suggestion);
    setShowSuggestions(false);
    performSearch(suggestion);
    searchInputRef.current?.focus();
  };

  // Handle click outside to hide suggestions
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchInputRef.current && !searchInputRef.current.contains(event.target)) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900 flex items-center">
              <span className="text-blue-600">AI</span>
              <span className="ml-1">Search</span>
              <span className="ml-2 text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                Beta
              </span>
            </h1>
            <div className="text-sm text-gray-500">
              Search through AI websites & tools
            </div>
          </div>
        </div>
      </header>

      {/* Search Section */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className={`transition-all duration-300 ${hasSearched ? 'pt-8' : 'pt-20'}`}>
          {/* Logo for initial state */}
          {!hasSearched && (
            <div className="text-center mb-12">
              <h2 className="text-6xl font-light text-gray-800 mb-4">
                <span className="text-blue-600">AI</span>Search
              </h2>
              <p className="text-xl text-gray-600">
                Discover the best AI websites, tools, and resources
              </p>
            </div>
          )}

          {/* Search Form */}
          <form onSubmit={handleSearch} className="relative">
            <div className="relative max-w-2xl mx-auto">
              <div className="relative">
                <input
                  ref={searchInputRef}
                  type="text"
                  value={query}
                  onChange={handleInputChange}
                  onFocus={() => query && setShowSuggestions(true)}
                  placeholder="Search for AI tools, companies, tutorials..."
                  className="w-full px-6 py-4 text-lg border border-gray-300 rounded-full shadow-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-opacity-20 transition-all duration-200"
                />
                <button
                  type="submit"
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-blue-600 text-white p-3 rounded-full hover:bg-blue-700 transition-colors duration-200"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </button>
              </div>

              {/* Suggestions Dropdown */}
              {showSuggestions && suggestions.length > 0 && (
                <div className="absolute z-10 w-full mt-2 bg-white border border-gray-200 rounded-lg shadow-lg">
                  {suggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestionClick(suggestion)}
                      className="w-full px-4 py-3 text-left hover:bg-gray-50 focus:bg-gray-50 focus:outline-none transition-colors duration-150 first:rounded-t-lg last:rounded-b-lg"
                    >
                      <span className="flex items-center">
                        <svg className="w-4 h-4 text-gray-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                        {suggestion}
                      </span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </form>
        </div>

        {/* Search Stats */}
        {hasSearched && (
          <div className="mt-6 text-sm text-gray-600">
            {loading ? (
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                Searching AI websites...
              </div>
            ) : (
              <div>
                About {totalResults} results ({searchTime.toFixed(2)} seconds)
              </div>
            )}
          </div>
        )}

        {/* Search Results */}
        <div className="mt-8 pb-12">
          {loading && (
            <div className="space-y-6">
              {[...Array(5)].map((_, index) => (
                <div key={index} className="animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-full mb-1"></div>
                  <div className="h-3 bg-gray-200 rounded w-5/6"></div>
                </div>
              ))}
            </div>
          )}

          {!loading && results.length > 0 && (
            <div className="space-y-8">
              {results.map((result, index) => (
                <div key={index} className="group">
                  <div className="mb-1">
                    <span className="text-sm text-green-700 font-medium">
                      {result.displayed_link}
                    </span>
                  </div>
                  <h3 className="text-xl text-blue-600 hover:underline mb-2">
                    <a
                      href={result.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="visited:text-purple-600"
                    >
                      {result.title}
                    </a>
                  </h3>
                  <p className="text-gray-700 text-sm leading-relaxed">
                    {result.snippet}
                  </p>
                </div>
              ))}
            </div>
          )}

          {!loading && hasSearched && results.length === 0 && (
            <div className="text-center py-12">
              <div className="text-gray-400 mb-4">
                <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 15c-2.34 0-4.47-.881-6.08-2.33" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No AI websites found</h3>
              <p className="text-gray-600 mb-4">
                Try searching for specific AI tools, companies, or topics like:
              </p>
              <div className="flex flex-wrap justify-center gap-2">
                {['ChatGPT', 'Midjourney', 'Stable Diffusion', 'OpenAI', 'Machine Learning'].map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => handleSuggestionClick(suggestion)}
                    className="px-4 py-2 bg-blue-100 text-blue-700 rounded-full text-sm hover:bg-blue-200 transition-colors duration-200"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default App;