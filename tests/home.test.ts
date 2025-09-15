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

test.describe('Home Page Tests', () => {
  let homePage: HomePage;

  test.beforeEach(async ({ page }) => {
    homePage = new HomePage(page);
    await homePage.goto();
  });

  test('should display home page correctly', async () => {
    await homePage.verifyHomePage();
  });

  test('should navigate to store catalog', async () => {
    await homePage.enterStore();

    const catalogPage = new CatalogPage(homePage.page);
    await catalogPage.verifyCatalogPage();
  });

  test('should have correct page title', async () => {
    await expect(homePage.page).toHaveTitle(/jpetstore demo/i);
  });

  test('should display welcome message', async () => {
    await expect(homePage.welcomeHeading).toBeVisible();
    await expect(homePage.welcomeHeading).toHaveText(/welcome to jpetstore 6/i);
  });

  test('should display copyright information', async () => {
    await expect(homePage.page.getByText(/copyright www.mybatis.org/i)).toBeVisible();
  });
});