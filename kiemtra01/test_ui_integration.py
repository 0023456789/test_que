#!/usr/bin/env python3
"""
Test script to verify UI integration with new product endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint, description):
    """Test a specific endpoint"""
    print(f"\n🧪 Testing: {description}")
    print(f"   URL: {endpoint}")
    
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            print(f"   ✅ Success! Found {len(items)} items")
            
            if items:
                sample = items[0]
                print(f"   📋 Sample item: {sample.get('name', 'Unknown')} ({sample.get('brand', 'Unknown')})")
                print(f"   🔧 Product type: {sample.get('product_type', 'Not specified')}")
                print(f"   💰 Price: ${sample.get('price', 0)}")
                print(f"   📦 Stock: {sample.get('stock', 0)}")
                
                # Show specs
                specs = []
                for field in ['cpu', 'chipset', 'ram_gb', 'storage_gb', 'display_size_inches']:
                    if sample.get(field):
                        specs.append(f"{field}: {sample[field]}")
                if specs:
                    print(f"   ⚙️  Specs: {', '.join(specs)}")
        else:
            print(f"   ❌ Failed: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
    except json.JSONDecodeError as e:
        print(f"   ❌ JSON decode error: {e}")

def main():
    print("🚀 Testing UI Integration with New Product Endpoints")
    print("=" * 60)
    
    # Test all product endpoints
    endpoints = [
        ("/proxy/product/api/all-products/", "All Products (Universal)"),
        ("/proxy/product/api/computers/", "Computers"),
        ("/proxy/product/api/mobiles/", "Mobile Phones"),
        ("/proxy/product/api/tablets/", "Tablets"),
        ("/proxy/product/api/smartwatches/", "Smartwatches"),
        ("/proxy/product/api/headphones/", "Headphones"),
        ("/proxy/product/api/cameras/", "Cameras"),
        ("/proxy/product/api/gaming_consoles/", "Gaming Consoles"),
        ("/proxy/product/api/tvs/", "TVs"),
        ("/proxy/product/api/smart_homes/", "Smart Home"),
        ("/proxy/product/api/fitness_trackers/", "Fitness Trackers"),
        ("/proxy/product/api/drones/", "Drones"),
    ]
    
    for endpoint, description in endpoints:
        test_endpoint(endpoint, description)
        time.sleep(1)  # Small delay between requests
    
    # Test filtering
    print(f"\n🔍 Testing Filtering Features")
    print("=" * 30)
    
    filter_tests = [
        ("/proxy/product/api/computers/?brand=Apple", "Apple Computers"),
        ("/proxy/product/api/mobiles/?min_price=500", "Mobile phones over $500"),
        ("/proxy/product/api/tvs/?min_price=1000&max_price=2000", "TVs $1000-$2000"),
        ("/proxy/product/api/computers/?in_stock=1", "In-stock computers"),
    ]
    
    for endpoint, description in filter_tests:
        test_endpoint(endpoint, description)
        time.sleep(1)
    
    print(f"\n✅ UI Integration Test Complete!")
    print("=" * 30)
    print("📝 Summary:")
    print("   • All product types should be accessible via the UI")
    print("   • Each product type should show relevant specifications")
    print("   • Filtering should work for brand, price, and stock")
    print("   • Product cards should display appropriate badges and icons")

if __name__ == "__main__":
    main()
