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

test.describe('Search Functionality Tests', () => {
  let homePage: HomePage;
  let catalogPage: CatalogPage;

  test.beforeEach(async ({ page }) => {
    homePage = new HomePage(page);
    catalogPage = new CatalogPage(page);
    await homePage.goto();
    await homePage.enterStore();
  });

  test('should perform search for existing products', async () => {
    await catalogPage.search('fish');

    // Verify search results are displayed
    await expect(catalogPage.page.locator('table')).toBeVisible();
    await expect(catalogPage.page.getByText(/fish|angelfish|shark/i)).toBeVisible();
  });

  test('should perform search for specific product name', async () => {
    await catalogPage.search('angelfish');

    // Verify specific product is found
    await expect(catalogPage.page.getByText(/angelfish/i)).toBeVisible();
  });

  test('should perform search for product by ID', async () => {
    await catalogPage.search('FI-SW-01');

    // Verify product is found by ID
    await expect(catalogPage.page.getByText(/angelfish|FI-SW-01/i)).toBeVisible();
  });

  test('should handle search with no results', async () => {
    await catalogPage.search('nonexistentproduct12345');

    // Verify no results message or empty results
    // JPetStore might display different messages for no results
    const hasTable = await catalogPage.page.locator('table').count();
    if (hasTable > 0) {
      // If table exists, it should be empty or show no products
      const tableRows = await catalogPage.page.locator('table tr').count();
      expect(tableRows).toBeLessThanOrEqual(1); // Only header row if any
    }
  });

  test('should handle empty search query', async () => {
    await catalogPage.search('');

    // Should remain on catalog page or show all products
    await expect(catalogPage.page).toHaveURL(/catalog/i);
  });

  test('should handle special characters in search', async () => {
    await catalogPage.search('fish & chips');

    // Should handle gracefully without errors
    await expect(catalogPage.page).not.toHaveURL(/error/i);
  });

  test('should be case insensitive', async () => {
    // Search with uppercase
    await catalogPage.search('ANGELFISH');
    await expect(catalogPage.page.getByText(/angelfish/i)).toBeVisible();

    // Search with mixed case
    await catalogPage.goto();
    await catalogPage.search('AngelFish');
    await expect(catalogPage.page.getByText(/angelfish/i)).toBeVisible();
  });

  test('should search across different categories', async () => {
    await catalogPage.search('retriever');

    // Should find dog products
    await expect(catalogPage.page.getByText(/retriever/i)).toBeVisible();
  });

  test('should allow clicking on search results', async () => {
    await catalogPage.search('angelfish');

    // Click on a search result link (if available)
    const productLink = catalogPage.page.getByRole('link', { name: /FI-SW-01|angelfish/i }).first();
    if (await productLink.count() > 0) {
      await productLink.click();

      // Should navigate to product page
      await expect(catalogPage.page).toHaveURL(/viewProduct|viewItem/i);
    }
  });

  test('should maintain search functionality across different browsers', async () => {
    // This test will run on all configured browsers via playwright.config.ts
    await catalogPage.search('koi');

    await expect(catalogPage.page.getByText(/koi/i)).toBeVisible();
  });
});