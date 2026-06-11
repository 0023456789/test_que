# UI Integration Guide - New Product Service

## 🎯 Overview
The e-commerce UI has been updated to work with the new product service that supports 10+ product types, each with their own database table and specialized fields.

## 🏗️ Architecture

### Frontend (API Gateway)
- **Location**: `api_gateway/app/templates/app/customer_browse.html`
- **Technology**: Django templates with vanilla JavaScript
- **API Proxy**: Routes requests through `/proxy/product/` to product service

### Backend (Product Service)
- **Location**: `product_service/`
- **Technology**: Django with separate models for each product type
- **Database**: 11 separate tables for different product categories

## 📱 Product Types & Endpoints

| Product Type | Endpoint | Icon | Badge Color | Key Features |
|-------------|-----------|------|-------------|--------------|
| Computers | `/api/computers/` | 💻 | Blue | CPU, RAM, Storage, GPU, Display |
| Mobile Phones | `/api/mobiles/` | 📱 | Yellow | Chipset, Camera, 5G, Battery |
| Tablets | `/api/tablets/` | 🧾 | Blue | Display, Stylus, Cellular |
| Smartwatches | `/api/smartwatches/` | ⌚ | Purple | Display, Health Sensors, GPS |
| Headphones | `/api/headphones/` | 🎧 | Yellow | Type, Noise Cancelling, Battery |
| Cameras | `/api/cameras/` | 📷 | Blue | Type, Sensor, Megapixels |
| Gaming Consoles | `/api/gaming_consoles/` | 🎮 | Red | Type, Storage, 4K Support |
| TVs | `/api/tvs/` | 📺 | Blue | Display Type, Resolution, Smart |
| Smart Home | `/api/smart_homes/` | 🏠 | Green | Category, Voice Assistant |
| Fitness Trackers | `/api/fitness_trackers/` | 💪 | Orange | Type, GPS, Battery Life |
| Drones | `/api/drones/` | 🚁 | Blue | Type, Camera, Flight Time |

## 🔄 API Flow

### Universal Endpoint
```
GET /proxy/product/api/all-products/
```
- Returns all products from all categories
- Each item includes `product_type` field
- Used for "All Products" view

### Category-Specific Endpoints
```
GET /proxy/product/api/{product_type}/
```
- Returns products from specific category
- Supports filtering (brand, price, stock, etc.)
- Used when user selects a category filter

### Filtering Parameters
- `brand` - Filter by brand name
- `min_price` / `max_price` - Price range filter
- `min_ram_gb` / `min_storage_gb` - Spec filters (where applicable)
- `in_stock=1` - Only in-stock items
- `q` - Search query (basic text search)

## 🎨 UI Components

### Category Chips
- Located in filter panel
- Updated to show new product types
- Each chip has appropriate icon and color
- Clicking filters products by category

### Product Cards
- Dynamic rendering based on product type
- Shows relevant specifications for each category
- Displays appropriate badge and icon
- Stock status and pricing always visible

### Specification Display
The `buildProductSpecs()` function intelligently displays relevant specs:

```javascript
// Computers: CPU, RAM, Storage, Display Size, GPU
// Mobiles: Chipset, RAM, Storage, Display, Camera, 5G
// Smartwatches: Display, GPS, Health Sensors
// TVs: Display Size, Resolution, Display Type
// etc.
```

## 🛠️ Integration Details

### JavaScript Functions

#### `loadProducts()`
- Determines correct API endpoint based on filters
- Handles both universal and category-specific calls
- Adds `product_type` to items if missing

#### `buildProductSpecs(item, productType)`
- Creates type-specific specification strings
- Handles common fields (CPU, RAM, Storage)
- Adds category-specific features

#### `productCard(item)`
- Renders product cards with appropriate icons/badges
- Displays relevant specifications
- Handles add-to-cart functionality

### CSS Classes
- `.badge-blue`, `.badge-yellow`, `.badge-purple`, etc.
- `.product-stock-ok` / `.product-stock-out`
- Responsive grid layout

## 🧪 Testing

### Manual Testing
1. Navigate to `http://localhost:8000/customer/browse/`
2. Test each category filter
3. Verify product cards show correct specs
4. Test brand and price filtering
5. Test search functionality

### Automated Testing
Run the test script:
```bash
python test_ui_integration.py
```

### Expected Results
- All 11 product types should load successfully
- Each product should display relevant specifications
- Filtering should work for brand, price, and stock
- Product cards should show appropriate icons and badges

## 🔧 Configuration

### Environment Variables
Ensure these are set in `api_gateway/settings.py`:
```python
PRODUCT_SERVICE_URL = "http://product-service:8000"
```

### Docker Services
Make sure these services are running:
- `api_gateway` (port 8000)
- `product_service` (port 8002)
- `postgres` (database)

## 📊 Data Structure

### Sample Computer Product
```json
{
  "id": 1,
  "product_type": "computers",
  "name": "MacBook Pro 14\"",
  "brand": "Apple",
  "cpu": "apple_m3",
  "ram_gb": 16,
  "storage_gb": 512,
  "gpu": "Integrated",
  "display_size_inches": 14.2,
  "price": 1999.99,
  "stock": 25,
  "is_active": true
}
```

### Sample Mobile Product
```json
{
  "id": 1,
  "product_type": "mobiles",
  "name": "iPhone 15 Pro",
  "brand": "Apple",
  "chipset": "apple_a17",
  "ram_gb": 8,
  "storage_gb": 256,
  "display_size_inches": 6.1,
  "main_camera_mp": 48,
  "has_5g": true,
  "price": 999.99,
  "stock": 50
}
```

## 🚀 Deployment

### Production Considerations
- Enable caching for product listings
- Implement pagination for large catalogs
- Add loading states for better UX
- Consider CDN for static assets

### Monitoring
- Track API response times
- Monitor error rates by product type
- Log user search patterns

## 🔄 Future Enhancements

### Planned Features
- Product detail pages
- Advanced filtering (spec ranges)
- Product comparisons
- Wishlist functionality
- Recently viewed items

### API Improvements
- GraphQL support
- Real-time inventory updates
- Product recommendations
- Advanced search with relevance scoring

---

## 📞 Support

For issues with UI integration:
1. Check service logs: `docker logs api_gateway`
2. Verify product service: `curl http://localhost:8002/api/all-products/`
3. Test individual endpoints: See test script above
4. Check browser console for JavaScript errors

The integration is designed to be backward compatible and extensible for future product types.
