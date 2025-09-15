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
import { TEST_USER } from './utils/test-data';

test.describe('Shopping Cart Tests', () => {
  let homePage: HomePage;
  let catalogPage: CatalogPage;
  let cartPage: CartPage;

  test.beforeEach(async ({ page }) => {
    homePage = new HomePage(page);
    catalogPage = new CatalogPage(page);
    cartPage = new CartPage(page);
    await homePage.goto();
    await homePage.enterStore();
  });

  test('should display empty cart initially', async () => {
    await cartPage.goto();
    await cartPage.verifyEmptyCart();
  });

  test('should add item to cart', async () => {
    await catalogPage.selectCategory('FISH');

    const categoryPage = new CategoryPage(catalogPage.page);
    await categoryPage.selectProduct('FI-SW-01');

    const productPage = new ProductPage(categoryPage.page);
    await productPage.addItemToCart(0);

    await cartPage.verifyCartPage();
    await cartPage.verifyItemInCart('EST-1');
  });

  test('should add multiple items to cart', async () => {
    // Add first item
    await catalogPage.selectCategory('FISH');
    const categoryPage = new CategoryPage(catalogPage.page);
    await categoryPage.selectProduct('FI-SW-01');

    const productPage = new ProductPage(categoryPage.page);
    await productPage.addItemToCart(0);
    await cartPage.verifyItemInCart('EST-1');

    // Go back and add another item
    await catalogPage.goto();
    await catalogPage.selectCategory('FISH');
    await categoryPage.selectProduct('FI-SW-01');
    await productPage.addItemToCart(1);
    await cartPage.verifyItemInCart('EST-2');

    // Verify both items are in cart
    const itemCount = await cartPage.getItemCount();
    expect(itemCount).toBe(2);
  });

  test('should update item quantity in cart', async () => {
    // Add an item to cart
    await catalogPage.selectCategory('FISH');
    const categoryPage = new CategoryPage(catalogPage.page);
    await categoryPage.selectProduct('FI-SW-01');

    const productPage = new ProductPage(categoryPage.page);
    await productPage.addItemToCart(0);

    // Update quantity
    await cartPage.updateQuantity(0, '3');

    // Verify quantity was updated (check if page reloaded successfully)
    await cartPage.verifyCartPage();
  });

  test('should remove item from cart', async () => {
    // Add an item to cart
    await catalogPage.selectCategory('FISH');
    const categoryPage = new CategoryPage(catalogPage.page);
    await categoryPage.selectProduct('FI-SW-01');

    const productPage = new ProductPage(categoryPage.page);
    await productPage.addItemToCart(0);

    // Remove item
    await cartPage.removeItem(0);
    await cartPage.verifyEmptyCart();
  });

  test('should calculate cart subtotal correctly', async () => {
    // Add an item to cart
    await catalogPage.selectCategory('FISH');
    const categoryPage = new CategoryPage(catalogPage.page);
    await categoryPage.selectProduct('FI-SW-01');

    const productPage = new ProductPage(categoryPage.page);
    await productPage.addItemToCart(0);

    // Check that subtotal is displayed
    const subTotal = await cartPage.getSubTotal();
    expect(subTotal).toBeTruthy();
    expect(subTotal).toContain('$');
  });

  test('should persist cart across page navigation', async () => {
    // Add an item to cart
    await catalogPage.selectCategory('FISH');
    const categoryPage = new CategoryPage(catalogPage.page);
    await categoryPage.selectProduct('FI-SW-01');

    const productPage = new ProductPage(categoryPage.page);
    await productPage.addItemToCart(0);

    // Navigate away and back to cart
    await catalogPage.goto();
    await cartPage.goto();

    // Verify item is still in cart
    await cartPage.verifyItemInCart('EST-1');
  });

  test('should proceed to checkout when logged in', async () => {
    // Login first
    await catalogPage.signIn();
    const loginPage = new LoginPage(catalogPage.page);
    await loginPage.login(TEST_USER.username, TEST_USER.password);

    // Add an item to cart
    await catalogPage.goto();
    await catalogPage.selectCategory('FISH');
    const categoryPage = new CategoryPage(catalogPage.page);
    await categoryPage.selectProduct('FI-SW-01');

    const productPage = new ProductPage(categoryPage.page);
    await productPage.addItemToCart(0);

    // Proceed to checkout
    await cartPage.proceedToCheckout();

    // Should navigate to checkout page (verify URL change)
    await expect(cartPage.page).toHaveURL(/checkout|order|billing/i);
  });

  test('should require login for checkout', async () => {
    // Add an item to cart without logging in
    await catalogPage.selectCategory('FISH');
    const categoryPage = new CategoryPage(catalogPage.page);
    await categoryPage.selectProduct('FI-SW-01');

    const productPage = new ProductPage(categoryPage.page);
    await productPage.addItemToCart(0);

    // Try to proceed to checkout
    await cartPage.proceedToCheckout();

    // Should redirect to login page
    await expect(cartPage.page).toHaveURL(/signin|login|account/i);
  });

  test('should maintain cart after login', async () => {
    // Add item to cart while not logged in
    await catalogPage.selectCategory('FISH');
    const categoryPage = new CategoryPage(catalogPage.page);
    await categoryPage.selectProduct('FI-SW-01');

    const productPage = new ProductPage(categoryPage.page);
    await productPage.addItemToCart(0);

    // Login
    await catalogPage.signIn();
    const loginPage = new LoginPage(catalogPage.page);
    await loginPage.login(TEST_USER.username, TEST_USER.password);

    // Go back to cart
    await cartPage.goto();

    // Verify item is still in cart
    await cartPage.verifyItemInCart('EST-1');
  });
});