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

test.describe('Catalog Navigation Tests', () => {
  let homePage: HomePage;
  let catalogPage: CatalogPage;

  test.beforeEach(async ({ page }) => {
    homePage = new HomePage(page);
    catalogPage = new CatalogPage(page);
    await homePage.goto();
    await homePage.enterStore();
  });

  test('should display all pet categories', async () => {
    await catalogPage.verifyCatalogPage();

    // Verify all 5 categories are displayed
    await expect(catalogPage.categoryImages).toHaveCount(5);

    // Verify category descriptions
    await expect(catalogPage.page.getByText(/saltwater, freshwater/i)).toBeVisible();
    await expect(catalogPage.page.getByText(/various breeds/i)).toBeVisible();
    await expect(catalogPage.page.getByText(/exotic varieties/i)).toBeVisible();
    await expect(catalogPage.page.getByText(/lizards, turtles, snakes/i)).toBeVisible();
  });

  test('should navigate to Fish category', async () => {
    await catalogPage.selectCategory('FISH');

    const categoryPage = new CategoryPage(catalogPage.page);
    await categoryPage.verifyCategoryPage('Fish');

    // Verify fish products are displayed
    await expect(categoryPage.page.getByText(/angelfish/i)).toBeVisible();
    await expect(categoryPage.page.getByText(/tiger shark/i)).toBeVisible();
    await expect(categoryPage.page.getByText(/koi/i)).toBeVisible();
    await expect(categoryPage.page.getByText(/goldfish/i)).toBeVisible();
  });

  test('should navigate to Dogs category', async () => {
    await catalogPage.selectCategory('DOGS');

    const categoryPage = new CategoryPage(catalogPage.page);
    await categoryPage.verifyCategoryPage('Dogs');

    // Verify dog products are displayed
    await expect(categoryPage.page.getByText(/bulldog/i)).toBeVisible();
    await expect(categoryPage.page.getByText(/poodle/i)).toBeVisible();
    await expect(categoryPage.page.getByText(/dalmation/i)).toBeVisible();
  });

  test('should navigate to product details from category', async () => {
    await catalogPage.selectCategory('FISH');

    const categoryPage = new CategoryPage(catalogPage.page);
    await categoryPage.selectProduct('FI-SW-01');

    const productPage = new ProductPage(categoryPage.page);
    await productPage.verifyProductPage('Angelfish');

    // Verify product items are displayed
    const itemCount = await productPage.getItemCount();
    expect(itemCount).toBeGreaterThan(0);
  });

  test('should return to main menu from category page', async () => {
    await catalogPage.selectCategory('FISH');

    const categoryPage = new CategoryPage(catalogPage.page);
    await categoryPage.returnToMainMenu();

    await catalogPage.verifyCatalogPage();
  });

  test('should navigate through category breadcrumbs', async () => {
    await catalogPage.selectCategory('FISH');
    const categoryPage = new CategoryPage(catalogPage.page);

    await categoryPage.selectProduct('FI-SW-01');
    const productPage = new ProductPage(categoryPage.page);

    await productPage.returnToCategory();
    await categoryPage.verifyCategoryPage('Fish');
  });

  test('should display correct product counts in each category', async () => {
    const categories = [
      { name: 'FISH', expectedMin: 4 },
      { name: 'DOGS', expectedMin: 5 },
      { name: 'CATS', expectedMin: 2 },
      { name: 'REPTILES', expectedMin: 2 },
      { name: 'BIRDS', expectedMin: 2 }
    ];

    for (const category of categories) {
      await catalogPage.goto();
      await catalogPage.selectCategory(category.name);

      const categoryPage = new CategoryPage(catalogPage.page);
      const productCount = await categoryPage.getProductCount();
      expect(productCount).toBeGreaterThanOrEqual(category.expectedMin);
    }
  });

  test('should navigate between categories using quick links', async () => {
    await catalogPage.goToCategory('fish');
    const categoryPage = new CategoryPage(catalogPage.page);
    await categoryPage.verifyCategoryPage('Fish');

    await catalogPage.goToCategory('dogs');
    await categoryPage.verifyCategoryPage('Dogs');

    await catalogPage.goToCategory('cats');
    await categoryPage.verifyCategoryPage('Cats');
  });
});