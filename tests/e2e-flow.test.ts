///
///    Copyright 2010-2025 the original author or authors.
///
///    Licensed under the Apache License, Version 2.0 (the "License");
///    you may not use this file except in compliance with the License.
///    You may obtain a copy of the License at
///
///       https://www.apache.org/licenses/LICENSE-2.0
///
///    Unless required by applicable law or agreed to in writing, software
///    distributed under the License is distributed on an "AS IS" BASIS,
///    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
///    See the License for the specific language governing permissions and
///    limitations under the License.
///

import { test, expect } from '@playwright/test';
import { HomePage } from './pages/home.page';
import { CatalogPage } from './pages/catalog.page';
import { CategoryPage } from './pages/category.page';
import { ProductPage } from './pages/product.page';
import { CartPage } from './pages/cart.page';
import { LoginPage } from './pages/login.page';
import { RegistrationPage } from './pages/registration.page';
import { TEST_USER, NEW_USER_DATA } from './utils/test-data';

test.describe('End-to-End User Journey Tests', () => {
  test('complete shopping journey for existing user', async ({ page }) => {
    // Start from home page
    const homePage = new HomePage(page);
    await homePage.goto();
    await homePage.verifyHomePage();

    // Enter the store
    await homePage.enterStore();

    // Browse catalog
    const catalogPage = new CatalogPage(page);
    await catalogPage.verifyCatalogPage();

    // Navigate to Fish category
    await catalogPage.selectCategory('FISH');

    // Browse products in category
    const categoryPage = new CategoryPage(page);
    await categoryPage.verifyCategoryPage('Fish');

    // View product details
    await categoryPage.selectProduct('FI-SW-01');

    // Add item to cart
    const productPage = new ProductPage(page);
    await productPage.verifyProductPage('Angelfish');
    await productPage.addItemToCart(0);

    // Verify item in cart
    const cartPage = new CartPage(page);
    await cartPage.verifyItemInCart('EST-1');

    // Add another item
    await catalogPage.goto();
    await catalogPage.selectCategory('FISH');
    await categoryPage.selectProduct('FI-SW-02');
    await productPage.addItemToCart(0);

    // Go to cart and verify multiple items
    await cartPage.goto();
    const itemCount = await cartPage.getItemCount();
    expect(itemCount).toBe(2);

    // Login for checkout
    await catalogPage.signIn();
    const loginPage = new LoginPage(page);
    await loginPage.login(TEST_USER.username, TEST_USER.password);
    await loginPage.verifyLoginSuccess();

    // Proceed to checkout
    await cartPage.goto();
    await cartPage.proceedToCheckout();

    // Verify checkout process started
    await expect(page).toHaveURL(/checkout|order|billing/i);
  });

  test('complete new user registration and shopping journey', async ({ page }) => {
    const homePage = new HomePage(page);
    await homePage.goto();
    await homePage.enterStore();

    // Go to login page
    const catalogPage = new CatalogPage(page);
    await catalogPage.signIn();

    // Navigate to registration
    const loginPage = new LoginPage(page);
    await loginPage.goToRegister();

    // Complete registration
    const registrationPage = new RegistrationPage(page);
    const uniqueUserData = {
      ...NEW_USER_DATA,
      username: 'testuser' + Date.now()
    };

    await registrationPage.fillRegistrationForm(uniqueUserData);
    await registrationPage.selectLanguage('english');
    await registrationPage.selectFavoriteCategory('FISH');
    await registrationPage.enableMyList(true);
    await registrationPage.submitRegistration();

    // Verify registration success
    await registrationPage.verifyRegistrationSuccess();

    // Continue shopping as new user
    await catalogPage.goto();
    await catalogPage.selectCategory('DOGS');

    const categoryPage = new CategoryPage(page);
    await categoryPage.selectProduct('K9-BD-01');

    const productPage = new ProductPage(page);
    await productPage.addItemToCart(0);

    const cartPage = new CartPage(page);
    await cartPage.verifyCartPage();
    await cartPage.proceedToCheckout();

    // Should be able to checkout as authenticated user
    await expect(page).toHaveURL(/checkout|order|billing/i);
  });

  test('guest shopping experience with login requirement', async ({ page }) => {
    const homePage = new HomePage(page);
    await homePage.goto();
    await homePage.enterStore();

    // Shop as guest
    const catalogPage = new CatalogPage(page);
    await catalogPage.selectCategory('CATS');

    const categoryPage = new CategoryPage(page);
    await categoryPage.selectProduct('FL-DSH-01');

    const productPage = new ProductPage(page);
    await productPage.addItemToCart(0);

    // Try to checkout without login
    const cartPage = new CartPage(page);
    await cartPage.proceedToCheckout();

    // Should redirect to login
    await expect(page).toHaveURL(/signin|login|account/i);

    // Login and continue
    const loginPage = new LoginPage(page);
    await loginPage.login(TEST_USER.username, TEST_USER.password);

    // Cart should be preserved
    await cartPage.goto();
    const itemCount = await cartPage.getItemCount();
    expect(itemCount).toBeGreaterThan(0);
  });

  test('search and purchase workflow', async ({ page }) => {
    const homePage = new HomePage(page);
    await homePage.goto();
    await homePage.enterStore();

    // Search for specific product
    const catalogPage = new CatalogPage(page);
    await catalogPage.search('poodle');

    // Find and select product from search results
    await expect(page.getByText(/poodle/i)).toBeVisible();

    // Navigate to Dogs category to find poodle
    await catalogPage.selectCategory('DOGS');
    const categoryPage = new CategoryPage(page);

    // Select poodle product
    await categoryPage.selectProduct('K9-PO-02');

    // Add to cart
    const productPage = new ProductPage(page);
    await productPage.addItemToCart(0);

    // Verify and update cart
    const cartPage = new CartPage(page);
    await cartPage.updateQuantity(0, '2');

    // Login and checkout
    await catalogPage.signIn();
    const loginPage = new LoginPage(page);
    await loginPage.login(TEST_USER.username, TEST_USER.password);

    await cartPage.goto();
    await cartPage.proceedToCheckout();

    await expect(page).toHaveURL(/checkout|order|billing/i);
  });

  test('multi-category shopping experience', async ({ page }) => {
    const homePage = new HomePage(page);
    await homePage.goto();
    await homePage.enterStore();

    // Login first
    const catalogPage = new CatalogPage(page);
    await catalogPage.signIn();
    const loginPage = new LoginPage(page);
    await loginPage.login(TEST_USER.username, TEST_USER.password);

    // Shop from multiple categories
    const categoryPage = new CategoryPage(page);
    const productPage = new ProductPage(page);

    // Add fish
    await catalogPage.goto();
    await catalogPage.selectCategory('FISH');
    await categoryPage.selectProduct('FI-SW-01');
    await productPage.addItemToCart(0);

    // Add dog
    await catalogPage.goto();
    await catalogPage.selectCategory('DOGS');
    await categoryPage.selectProduct('K9-BD-01');
    await productPage.addItemToCart(0);

    // Add bird
    await catalogPage.goto();
    await catalogPage.selectCategory('BIRDS');
    await categoryPage.selectProduct('AV-CB-01');
    await productPage.addItemToCart(0);

    // Verify all items in cart
    const cartPage = new CartPage(page);
    await cartPage.goto();
    const itemCount = await cartPage.getItemCount();
    expect(itemCount).toBe(3);

    // Proceed to checkout
    await cartPage.proceedToCheckout();
    await expect(page).toHaveURL(/checkout|order|billing/i);
  });

  test('user session management across browser refresh', async ({ page }) => {
    const homePage = new HomePage(page);
    await homePage.goto();
    await homePage.enterStore();

    // Login
    const catalogPage = new CatalogPage(page);
    await catalogPage.signIn();
    const loginPage = new LoginPage(page);
    await loginPage.login(TEST_USER.username, TEST_USER.password);

    // Add item to cart
    await catalogPage.goto();
    await catalogPage.selectCategory('FISH');
    const categoryPage = new CategoryPage(page);
    await categoryPage.selectProduct('FI-SW-01');
    const productPage = new ProductPage(page);
    await productPage.addItemToCart(0);

    // Refresh browser
    await page.reload();

    // Verify user is still logged in
    await expect(loginPage.signOutLink).toBeVisible();

    // Verify cart is preserved
    const cartPage = new CartPage(page);
    await cartPage.goto();
    const itemCount = await cartPage.getItemCount();
    expect(itemCount).toBeGreaterThan(0);
  });
});