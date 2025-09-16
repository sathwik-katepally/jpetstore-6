# JPetStore Modernization Plan
## Stripes → Spring Boot + JSP → Next.js Migration

### 🎯 Project Overview
**Goal**: Modernize JPetStore application by migrating from Stripes framework to Spring Boot and from JSP views to Next.js frontend

**Timeline**: 7-8 hours (Hackathon Implementation)

**Team Size**: 3 Developers

**Migration Strategy**: Parallel development with gradual cutover using feature toggles

---

## 📊 Current vs Target Architecture

### Current State
- **Framework**: Stripes 1.6.0 MVC
- **Frontend**: JSP + JSTL + Server-side rendering
- **Data**: MyBatis 3.5.19 + HSQLDB
- **Deployment**: Single WAR file
- **Request Flow**: Browser → Stripes Filter → ActionBean → JSP

### Target State
- **Backend**: Spring Boot 3.x with REST APIs
- **Frontend**: Next.js with SSR/SSG capabilities
- **Data**: Spring Data JPA + H2/PostgreSQL
- **Deployment**: Separate backend and frontend deployments
- **Request Flow**: Browser → Next.js → REST API → JSON Response

---

## 👥 Team Distribution

### 👤 Developer 1: Spring Boot Backend Migration (2.5-3 hours)
**Focus**: Convert Stripes ActionBeans to Spring REST Controllers

### 👤 Developer 2: Next.js Frontend Development (2.5-3 hours)
**Focus**: Convert JSP pages to Next.js pages and components

### 👤 Developer 3: Integration & Routing (2.5-3 hours)
**Focus**: Proxy setup, feature toggles, and system integration

---

## 🚀 Implementation Plan

### Phase 1: Project Setup (30 minutes each developer)

#### Developer 1 - Spring Boot Setup
```bash
# Create new Spring Boot project
mkdir jpetstore-api
cd jpetstore-api

# Initialize with Maven
mvn archetype:generate \
  -DgroupId=com.jpetstore \
  -DartifactId=jpetstore-api \
  -DarchetypeArtifactId=maven-archetype-quickstart \
  -DinteractiveMode=false
```

**Required Dependencies:**
```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>
    <dependency>
        <groupId>com.h2database</groupId>
        <artifactId>h2</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-validation</artifactId>
    </dependency>
</dependencies>
```

#### Developer 2 - Next.js Setup
```bash
# Create Next.js application
npx create-next-app@latest jpetstore-frontend --typescript --tailwind --eslint --app
cd jpetstore-frontend

# Install additional dependencies
npm install axios @types/node
```

#### Developer 3 - Integration Setup
```bash
# Set up proxy server for development
npm install -g http-proxy-middleware express
```

### Phase 2: Core Migration (90 minutes each developer)

#### Developer 1 Tasks: Backend Migration

**Priority Order**: Catalog → Account → Cart → Order

**Task 1A: Convert CatalogActionBean to REST Controller**
```java
@RestController
@RequestMapping("/api/catalog")
@CrossOrigin(origins = "http://localhost:3000")
public class CatalogController {

    @Autowired
    private CatalogService catalogService;

    @GetMapping("/categories")
    public ResponseEntity<List<CategoryDto>> getCategories() {
        // Implementation
    }

    @GetMapping("/categories/{categoryId}/products")
    public ResponseEntity<List<ProductDto>> getProductsByCategory(
            @PathVariable String categoryId) {
        // Implementation
    }

    @GetMapping("/search")
    public ResponseEntity<List<ProductDto>> searchProducts(
            @RequestParam String keyword) {
        // Implementation
    }
}
```

**Task 1B: Create DTOs for API Responses**
```java
public class CategoryDto {
    private String categoryId;
    private String name;
    private String description;
    // getters and setters
}

public class ProductDto {
    private String productId;
    private String name;
    private String description;
    private String categoryId;
    // getters and setters
}
```

**Task 1C: Configure Application**
```yaml
# application.yml
server:
  port: 8081
  servlet:
    context-path: /api

spring:
  datasource:
    url: jdbc:h2:mem:jpetstore
    driver-class-name: org.h2.Driver
  jpa:
    hibernate:
      ddl-auto: create-drop
    show-sql: true
  h2:
    console:
      enabled: true
```

#### Developer 2 Tasks: Frontend Migration

**Task 2A: Create API Service Layer**
```typescript
// lib/api.ts
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8081/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Category {
  categoryId: string;
  name: string;
  description: string;
}

export interface Product {
  productId: string;
  name: string;
  description: string;
  categoryId: string;
}

export const catalogAPI = {
  getCategories: () => api.get<Category[]>('/catalog/categories'),
  getProductsByCategory: (categoryId: string) =>
    api.get<Product[]>(`/catalog/categories/${categoryId}/products`),
  searchProducts: (keyword: string) =>
    api.get<Product[]>(`/catalog/search?keyword=${keyword}`),
};
```

**Task 2B: Convert JSP to Next.js Pages and Components**
```typescript
// app/page.tsx (Home page with categories)
import { catalogAPI, Category } from '@/lib/api';
import CategoryGrid from '@/components/CategoryGrid';

async function getCategories(): Promise<Category[]> {
  try {
    const response = await catalogAPI.getCategories();
    return response.data;
  } catch (error) {
    console.error('Error fetching categories:', error);
    return [];
  }
}

export default async function HomePage() {
  const categories = await getCategories();

  return (
    <main className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold text-center mb-8">
        Welcome to JPetStore
      </h1>
      <CategoryGrid categories={categories} />
    </main>
  );
}
```

```typescript
// components/CategoryGrid.tsx
'use client';
import Link from 'next/link';
import Image from 'next/image';
import { Category } from '@/lib/api';

interface CategoryGridProps {
  categories: Category[];
}

export default function CategoryGrid({ categories }: CategoryGridProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {categories.map((category) => (
        <Link
          key={category.categoryId}
          href={`/categories/${category.categoryId}`}
          className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6"
        >
          <div className="text-center">
            <Image
              src={`/images/${category.categoryId}.gif`}
              alt={category.name}
              width={100}
              height={100}
              className="mx-auto mb-4"
            />
            <h3 className="text-xl font-semibold mb-2">{category.name}</h3>
            <p className="text-gray-600">{category.description}</p>
          </div>
        </Link>
      ))}
    </div>
  );
}
```

**Task 2C: Create Dynamic Routes**
```typescript
// app/categories/[categoryId]/page.tsx
import { catalogAPI, Product } from '@/lib/api';
import ProductGrid from '@/components/ProductGrid';

interface CategoryPageProps {
  params: {
    categoryId: string;
  };
}

async function getProducts(categoryId: string): Promise<Product[]> {
  try {
    const response = await catalogAPI.getProductsByCategory(categoryId);
    return response.data;
  } catch (error) {
    console.error('Error fetching products:', error);
    return [];
  }
}

export default async function CategoryPage({ params }: CategoryPageProps) {
  const products = await getProducts(params.categoryId);

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8 capitalize">
        {params.categoryId} Products
      </h1>
      <ProductGrid products={products} />
    </div>
  );
}
```

```typescript
// components/ProductGrid.tsx
'use client';
import Link from 'next/link';
import Image from 'next/image';
import { Product } from '@/lib/api';

interface ProductGridProps {
  products: Product[];
}

export default function ProductGrid({ products }: ProductGridProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {products.map((product) => (
        <div
          key={product.productId}
          className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-4"
        >
          <Image
            src={`/images/${product.productId}.gif`}
            alt={product.name}
            width={150}
            height={150}
            className="w-full h-40 object-cover rounded-lg mb-4"
          />
          <h3 className="text-lg font-semibold mb-2">{product.name}</h3>
          <p className="text-gray-600 text-sm">{product.description}</p>
          <Link
            href={`/products/${product.productId}`}
            className="mt-4 block bg-blue-500 text-white text-center py-2 px-4 rounded hover:bg-blue-600 transition-colors"
          >
            View Details
          </Link>
        </div>
      ))}
    </div>
  );
}
```

#### Developer 3 Tasks: Integration Layer

**Task 3A: Next.js API Configuration**
```typescript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8081/api/:path*',
      },
      {
        source: '/legacy/:path*',
        destination: 'http://localhost:8080/:path*',
      },
    ];
  },
  images: {
    domains: ['localhost'],
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8080',
        pathname: '/images/**',
      },
    ],
  },
};

module.exports = nextConfig;
```

```typescript
// .env.local
NEXT_PUBLIC_API_URL=http://localhost:8081/api
NEXT_PUBLIC_LEGACY_URL=http://localhost:8080
```

**Task 3B: Feature Toggle Implementation**
```typescript
// lib/featureToggle.ts
export class FeatureToggle {
  static isModernUIEnabled(): boolean {
    if (typeof window === 'undefined') return true; // SSR default
    return localStorage.getItem('modern-ui') === 'true' ||
           window.location.search.includes('modern=true');
  }

  static enableModernUI(): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('modern-ui', 'true');
      window.location.reload();
    }
  }

  static disableModernUI(): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('modern-ui', 'false');
      window.location.href = process.env.NEXT_PUBLIC_LEGACY_URL || 'http://localhost:8080';
    }
  }
}
```

**Task 3C: Toggle Button Component**
```typescript
// components/FeatureToggle.tsx
'use client';
import { useState, useEffect } from 'react';
import { FeatureToggle } from '@/lib/featureToggle';

export default function FeatureToggleButton() {
  const [isModern, setIsModern] = useState(true);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    setIsModern(FeatureToggle.isModernUIEnabled());
  }, []);

  const handleToggle = () => {
    if (isModern) {
      FeatureToggle.disableModernUI();
    } else {
      FeatureToggle.enableModernUI();
    }
  };

  if (!mounted) {
    return <div className="w-32 h-10 bg-gray-200 rounded animate-pulse"></div>;
  }

  return (
    <div className="flex items-center space-x-4">
      <button
        onClick={handleToggle}
        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition-colors"
      >
        Switch to {isModern ? 'Legacy' : 'Modern'} UI
      </button>
      <span className="text-sm text-gray-600">
        Current: {isModern ? 'Modern Next.js' : 'Legacy JSP'}
      </span>
    </div>
  );
}
```

### Phase 3: Advanced Features (60 minutes each developer)

#### Developer 1: Extended API Development
- Add Account management endpoints
- Implement Cart operations
- Add Order processing APIs
- Include proper error handling and validation

#### Developer 2: Enhanced Next.js Features
- Add search functionality with client-side routing
- Implement shopping cart with Next.js state management
- Create user account forms with server actions
- Add loading states, error boundaries, and SEO optimization

#### Developer 3: Production Setup
- Configure build scripts
- Set up environment variables
- Add Docker configuration
- Implement health checks

### Phase 4: Integration & Testing (1 hour - All Developers)

#### Integration Checklist:
- [ ] Spring Boot API responds on port 8081
- [ ] Next.js app loads on port 3000
- [ ] Legacy app runs on port 8080
- [ ] API calls work from Next.js frontend
- [ ] Feature toggle switches between systems
- [ ] CORS configured properly
- [ ] SSR/SSG working correctly
- [ ] Image optimization functional
- [ ] Error handling works correctly
- [ ] Data flows correctly between components

#### Testing Scenarios:
1. **Legacy System**: Browse categories, search products, view items
2. **Modern System**: Same functionality via Next.js + API
3. **Feature Toggle**: Switch between old and new implementations
4. **API Testing**: Direct API calls work correctly
5. **SSR Testing**: Server-side rendering works properly
6. **Error Handling**: Network failures handled gracefully

---

## 🛠️ Development Setup

### Prerequisites
- Java 17
- Node.js 16+
- Maven 3.8+
- Git

### Quick Start Commands

```bash
# Terminal 1 - Start Legacy App (for comparison)
cd jpetstore-6
mvn cargo:run -Dcargo.servlet.port=8080

# Terminal 2 - Start Spring Boot API
cd jpetstore-api
mvn spring-boot:run

# Terminal 3 - Start Next.js Development Server
cd jpetstore-frontend
npm run dev

# Terminal 4 - API Testing
curl http://localhost:8081/api/catalog/categories
curl http://localhost:3000
```

### Build All Services
```bash
#!/bin/bash
# build-all.sh

echo "Building Spring Boot API..."
cd jpetstore-api
mvn clean package -DskipTests

echo "Building Next.js Frontend..."
cd ../jpetstore-frontend
npm run build

echo "Building Legacy App..."
cd ../jpetstore-6
mvn clean package -DskipTests

echo "All services built successfully!"
```

---

## 📁 Project Structure

```
jpetstore-6/                          # Root repository
├── MODERNIZATION_PLAN.md             # This file
├── src/                               # Original Stripes application
├── jpetstore-api/                     # New Spring Boot backend
│   ├── src/main/java/
│   │   └── com/jpetstore/api/
│   │       ├── JPetStoreApiApplication.java
│   │       ├── controller/
│   │       ├── service/
│   │       ├── repository/
│   │       ├── entity/
│   │       └── dto/
│   ├── src/main/resources/
│   │   ├── application.yml
│   │   └── data.sql
│   └── pom.xml
├── jpetstore-frontend/                # New Next.js frontend
│   ├── app/
│   │   ├── categories/
│   │   │   └── [categoryId]/
│   │   │       └── page.tsx
│   │   ├── products/
│   │   │   └── [productId]/
│   │   │       └── page.tsx
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── CategoryGrid.tsx
│   │   ├── ProductGrid.tsx
│   │   └── FeatureToggle.tsx
│   ├── lib/
│   │   ├── api.ts
│   │   └── featureToggle.ts
│   ├── public/
│   │   └── images/
│   ├── next.config.js
│   └── package.json
├── proxy-server.js                    # Development proxy
├── build-all.sh                       # Build script
└── docker-compose.yml                 # Container orchestration
```

---

## 🎯 Demo Script

### 1. Show Current Legacy System (2 minutes)
- Open http://localhost:8080
- Navigate through categories
- Search for products
- Explain Stripes/JSP architecture

### 2. Show New Spring Boot API (2 minutes)
- Open http://localhost:8081/api/catalog/categories
- Show JSON responses
- Demonstrate REST endpoints
- Explain modern backend architecture

### 3. Show New Next.js Frontend (3 minutes)
- Open http://localhost:3000
- Navigate through modern interface with SSR
- Show same functionality with better UX and SEO
- Demonstrate responsive design and fast page loads

### 4. Feature Toggle Demo (2 minutes)
- Use toggle button to switch between systems
- Show seamless transition
- Explain gradual migration approach

### 5. Architecture Comparison (1 minute)
- Side-by-side comparison
- Highlight benefits of new architecture
- Discuss scalability and maintainability

---

## 🏆 Success Criteria

### Minimum Viable Demo (MVP):
- [ ] Legacy system running on port 8080
- [ ] Spring Boot API running on port 8081
- [ ] Next.js frontend running on port 3000
- [ ] At least one API endpoint working (categories)
- [ ] Feature toggle functionality
- [ ] Basic navigation between pages
- [ ] SSR working for SEO benefits

### Stretch Goals:
- [ ] Complete catalog API implementation
- [ ] Search functionality with client-side routing
- [ ] Shopping cart implementation with state management
- [ ] User authentication with server actions
- [ ] Error boundaries and loading states
- [ ] Image optimization and responsive design
- [ ] Static generation for product pages
- [ ] Docker containerization

---

## 🔧 Troubleshooting

### Common Issues:

**CORS Errors:**
```java
// Add to Spring Boot controller
@CrossOrigin(origins = "http://localhost:3000")
```

**Port Conflicts:**
- Legacy app: 8080
- Spring Boot: 8081
- Next.js dev server: 3000

**Database Issues:**
- Check H2 console: http://localhost:8081/api/h2-console
- JDBC URL: jdbc:h2:mem:jpetstore

**Build Failures:**
```bash
# Clean all caches
mvn clean
npm cache clean --force
rm -rf node_modules && npm install
```

---

## 📚 Additional Resources

- [Spring Boot Documentation](https://spring.io/projects/spring-boot)
- [Next.js Documentation](https://nextjs.org/docs)
- [Next.js App Router](https://nextjs.org/docs/app)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Strangler Fig Pattern](https://martinfowler.com/bliki/StranglerFigApplication.html)
- [Migration Strategies](https://microservices.io/patterns/refactoring/)

---

## 🤝 Team Coordination

### Communication Protocol:
- Use Git branches for each developer
- Regular check-ins every 2 hours
- Share progress via team chat
- Document blockers immediately

### Git Workflow:
```bash
# Create feature branches
git checkout -b feature/spring-boot-api
git checkout -b feature/nextjs-frontend
git checkout -b feature/integration

# Merge when ready
git checkout main
git merge feature/spring-boot-api
```

### Final Integration:
- All developers merge changes
- Test complete system
- Prepare demo presentation
- Document lessons learned

---

*Last Updated: [Current Date]*
*Team: Developer 1, Developer 2, Developer 3*
*Event: Modernization Hackathon*