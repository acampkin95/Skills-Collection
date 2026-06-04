#!/usr/bin/env python3
"""
Perplexity AI Search Script
Query Perplexity's Sonar models for AI-powered search.
API key loaded from environment variables.
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error
from typing import Optional, Dict, List, Any


class PerplexityAPI:
    """Perplexity AI API client."""
    
    BASE_URL = "https://api.perplexity.ai"
    
    MODELS = {
        "sonar": "sonar",
        "sonar-pro": "sonar-pro",
        "sonar-reasoning": "sonar-reasoning",
        "sonar-reasoning-pro": "sonar-reasoning-pro"
    }
    
    def __init__(self):
        self.api_key = os.environ.get("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY environment variable not set")
    
    def _request(self, endpoint: str, data: Dict) -> Dict:
        """Make request to Perplexity API."""
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        body = json.dumps(data).encode()
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            try:
                return {"error": json.loads(error_body)}
            except:
                return {"error": error_body, "status": e.code}
    
    def search(self, query: str, model: str = "sonar", 
               system_prompt: Optional[str] = None,
               temperature: float = 0.2,
               max_tokens: int = 1024,
               return_citations: bool = True,
               return_images: bool = False,
               search_recency: Optional[str] = None) -> Dict:
        """
        Perform AI-powered search.
        
        Args:
            query: Search query
            model: Model to use (sonar, sonar-pro, sonar-reasoning, sonar-reasoning-pro)
            system_prompt: Optional system prompt
            temperature: Response creativity (0-1)
            max_tokens: Maximum response length
            return_citations: Include source citations
            return_images: Include relevant images
            search_recency: Filter by recency (day, week, month, year)
        """
        if model not in self.MODELS:
            raise ValueError(f"Invalid model. Choose from: {list(self.MODELS.keys())}")
        
        messages = [{"role": "user", "content": query}]
        
        data = {
            "model": self.MODELS[model],
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "return_citations": return_citations,
            "return_images": return_images
        }
        
        if system_prompt:
            data["messages"].insert(0, {"role": "system", "content": system_prompt})
        
        if search_recency:
            data["search_recency_filter"] = search_recency
        
        return self._request("/chat/completions", data)
    
    def chat(self, messages: List[Dict], model: str = "sonar",
             temperature: float = 0.2, max_tokens: int = 1024) -> Dict:
        """
        Multi-turn chat conversation.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use
            temperature: Response creativity
            max_tokens: Maximum response length
        """
        if model not in self.MODELS:
            raise ValueError(f"Invalid model. Choose from: {list(self.MODELS.keys())}")
        
        data = {
            "model": self.MODELS[model],
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        return self._request("/chat/completions", data)


def format_response(response: Dict[str, Any], verbose: bool = False) -> str:
    """Format API response for display."""
    if "error" in response:
        return f"Error: {response['error']}"
    
    output = []
    
    # Extract main content
    if "choices" in response:
        for choice in response["choices"]:
            message = choice.get("message", {})
            content = message.get("content", "")
            if content:
                output.append(content)
    
    # Add citations if present
    if verbose and "citations" in response:
        citations = response.get("citations", [])
        if citations:
            output.append("\n--- Citations ---")
            for i, cite in enumerate(citations, 1):
                output.append(f"[{i}] {cite}")
    
    # Add images if present
    if verbose and "images" in response:
        images = response.get("images", [])
        if images:
            output.append("\n--- Images ---")
            for img in images:
                output.append(img)
    
    return "\n".join(output) if output else "No response"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Perplexity AI Search",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  perplexity_search.py "What is quantum computing?"
  perplexity_search.py "Latest AI news" --model sonar-pro --recency week
  perplexity_search.py "Explain transformers" --model sonar-reasoning --verbose
        """
    )
    
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("--model", "-m", default="sonar",
                        choices=["sonar", "sonar-pro", "sonar-reasoning", "sonar-reasoning-pro"],
                        help="Model to use (default: sonar)")
    parser.add_argument("--system", "-s", help="System prompt")
    parser.add_argument("--temperature", "-t", type=float, default=0.2,
                        help="Response creativity 0-1 (default: 0.2)")
    parser.add_argument("--max-tokens", type=int, default=1024,
                        help="Max response tokens (default: 1024)")
    parser.add_argument("--recency", "-r", choices=["day", "week", "month", "year"],
                        help="Filter results by recency")
    parser.add_argument("--no-citations", action="store_true",
                        help="Disable citations")
    parser.add_argument("--images", action="store_true",
                        help="Include relevant images")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show citations and metadata")
    parser.add_argument("--json", action="store_true",
                        help="Output raw JSON response")
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="Interactive chat mode")
    
    args = parser.parse_args()
    
    try:
        pplx = PerplexityAPI()
        
        if args.interactive:
            # Interactive chat mode
            print("Perplexity Interactive Chat (type 'quit' to exit)")
            print(f"Model: {args.model}")
            print("-" * 40)
            
            messages = []
            while True:
                try:
                    user_input = input("\nYou: ").strip()
                    if user_input.lower() in ["quit", "exit", "q"]:
                        break
                    if not user_input:
                        continue
                    
                    messages.append({"role": "user", "content": user_input})
                    response = pplx.chat(messages, args.model, args.temperature, args.max_tokens)
                    
                    if "choices" in response:
                        assistant_msg = response["choices"][0]["message"]["content"]
                        messages.append({"role": "assistant", "content": assistant_msg})
                        print(f"\nPerplexity: {assistant_msg}")
                    else:
                        print(f"\nError: {response}")
                        
                except KeyboardInterrupt:
                    print("\n\nExiting...")
                    break
            
            sys.exit(0)
        
        if not args.query:
            parser.print_help()
            sys.exit(1)
        
        # Single query mode
        response = pplx.search(
            query=args.query,
            model=args.model,
            system_prompt=args.system,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            return_citations=not args.no_citations,
            return_images=args.images,
            search_recency=args.recency
        )
        
        if args.json:
            print(json.dumps(response, indent=2))
        else:
            print(format_response(response, args.verbose))
        
        sys.exit(0 if "error" not in response else 1)
        
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
