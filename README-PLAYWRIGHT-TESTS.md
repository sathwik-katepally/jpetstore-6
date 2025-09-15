# JPetStore Playwright E2E Tests

This directory contains comprehensive end-to-end tests for the JPetStore application using Playwright and TypeScript.

## Test Structure

The tests are organized into the following categories:

### Test Files
- `home.test.ts` - Homepage functionality tests
- `authentication.test.ts` - Login, logout, and registration tests
- `catalog.test.ts` - Product catalog navigation tests
- `shopping-cart.test.ts` - Shopping cart functionality tests
- `search.test.ts` - Search functionality tests
- `e2e-flow.test.ts` - Complete end-to-end user journey tests

### Page Object Model
The tests use the Page Object Model pattern for maintainable and reusable code:

- `pages/base.page.ts` - Base page with common functionality
- `pages/home.page.ts` - Home page interactions
- `pages/login.page.ts` - Login page interactions
- `pages/registration.page.ts` - Registration page interactions
- `pages/catalog.page.ts` - Catalog page interactions
- `pages/category.page.ts` - Category page interactions
- `pages/product.page.ts` - Product page interactions
- `pages/cart.page.ts` - Shopping cart page interactions

### Utilities
- `utils/test-data.ts` - Test data constants and user information

## Prerequisites

1. **Java 17+** - Required to run the JPetStore application
2. **Maven** - For building and running the application
3. **Node.js 18+** - For running Playwright tests

## Setup Instructions

### 1. Install Dependencies
```bash
npm install
npx playwright install
```

### 2. Start the JPetStore Application
```bash
./mvnw clean package
./mvnw cargo:run -P tomcat90
```

The application will be available at: `http://localhost:8080/jpetstore/`

### 3. Run Tests

#### Run all tests
```bash
npm test
```

#### Run tests with UI (interactive mode)
```bash
npm run test:ui
```

#### Run tests in headed mode (see browser)
```bash
npm run test:headed
```

#### Run specific test file
```bash
npx playwright test home.test.ts
```

#### Run tests in debug mode
```bash
npm run test:debug
```

#### View test report
```bash
npm run test:report
```

## Test Configuration

The tests are configured to run across multiple browsers:
- **Desktop**: Chromium, Firefox, WebKit
- **Mobile**: Chrome (Pixel 5), Safari (iPhone 12)

Configuration can be modified in `playwright.config.ts`.

## Test Data

### Default Test User
The tests use a pre-configured test user:
- **Username**: `j2ee`
- **Password**: `j2ee`

### Test Product Categories
- **FISH**: Angelfish, Tiger Shark, Koi, Goldfish
- **DOGS**: Bulldog, Poodle, Dalmatian, Golden Retriever, Labrador Retriever
- **CATS**: Manx, Persian
- **REPTILES**: Lizards, Turtles, Snakes
- **BIRDS**: Exotic Varieties

## Test Coverage

### Functional Areas Tested

1. **Homepage**
   - Landing page display
   - Navigation to store catalog
   - Basic page structure

2. **Authentication**
   - User login with valid/invalid credentials
   - User registration with complete form
   - Session management
   - Logout functionality

3. **Catalog Navigation**
   - Category browsing
   - Product listing
   - Product detail viewing
   - Navigation breadcrumbs

4. **Shopping Cart**
   - Add items to cart
   - Update item quantities
   - Remove items from cart
   - Cart persistence across sessions
   - Checkout process initiation

5. **Search Functionality**
   - Product search by name
   - Product search by ID
   - Search result navigation
   - Empty search handling

6. **End-to-End Workflows**
   - Complete shopping journey
   - New user registration and purchase
   - Multi-category shopping
   - Guest checkout with login requirement

### Cross-Browser Testing
All tests are configured to run across:
- Chrome/Chromium
- Firefox
- Safari/WebKit
- Mobile browsers

## Reporting

Test results are generated in HTML format and include:
- Test execution status
- Screenshots on failure
- Video recordings of failed tests
- Detailed error logs

## Continuous Integration

The tests can be integrated into CI/CD pipelines. The configuration includes:
- Automatic server startup/shutdown
- Headless execution for CI environments
- Retry logic for flaky tests
- Comprehensive reporting

## Troubleshooting

### Common Issues

1. **Server not starting**: Ensure port 8080 is available
   ```bash
   lsof -i :8080
   ```

2. **Tests timing out**: Increase timeout in `playwright.config.ts`

3. **Browser installation issues**: Run browser installation manually
   ```bash
   npx playwright install chromium firefox webkit
   ```

4. **Test data conflicts**: The tests create unique test users to avoid conflicts

### Debug Mode
For debugging failing tests:
```bash
npx playwright test --debug
```

This opens the Playwright Inspector for step-by-step debugging.

## Best Practices Implemented

1. **Page Object Model** - Encapsulates page interactions
2. **Test Data Management** - Centralized test data constants
3. **Wait Strategies** - Proper wait conditions for stable tests
4. **Error Handling** - Comprehensive error scenarios
5. **Cross-Browser Support** - Tests across multiple browsers
6. **Responsive Testing** - Mobile and desktop viewport testing
7. **CI/CD Ready** - Configuration for automated execution

## Contributing

When adding new tests:
1. Follow the existing Page Object Model pattern
2. Add appropriate wait conditions
3. Include both positive and negative test cases
4. Update test data constants if needed
5. Ensure tests are browser-agnostic
6. Add proper test documentation

## Example Test Execution Output

```
Running 45 tests using 1 worker

✓ home.test.ts:8:3 › Home Page Tests › should display home page correctly (1.2s)
✓ home.test.ts:13:3 › Home Page Tests › should navigate to store catalog (1.5s)
✓ authentication.test.ts:15:3 › Authentication Tests › should login with valid credentials (2.1s)
✓ catalog.test.ts:12:3 › Catalog Navigation Tests › should display all pet categories (1.8s)
✓ shopping-cart.test.ts:18:3 › Shopping Cart Tests › should add item to cart (2.4s)

45 passed (2.5m)
```

This test suite provides comprehensive coverage of the JPetStore application's core functionality and user workflows.