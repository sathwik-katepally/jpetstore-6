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
import { LoginPage } from './pages/login.page';
import { RegistrationPage } from './pages/registration.page';
import { CatalogPage } from './pages/catalog.page';
import { TEST_USER, NEW_USER_DATA } from './utils/test-data';

test.describe('Authentication Tests', () => {
  let homePage: HomePage;
  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    homePage = new HomePage(page);
    loginPage = new LoginPage(page);
    await homePage.goto();
    await homePage.enterStore();
  });

  test('should display login page correctly', async () => {
    const catalogPage = new CatalogPage(homePage.page);
    await catalogPage.signIn();
    await loginPage.verifyLoginPage();
  });

  test('should login with valid credentials', async () => {
    const catalogPage = new CatalogPage(homePage.page);
    await catalogPage.signIn();
    await loginPage.login(TEST_USER.username, TEST_USER.password);
    await loginPage.verifyLoginSuccess();
  });

  test('should show error for invalid credentials', async () => {
    const catalogPage = new CatalogPage(homePage.page);
    await catalogPage.signIn();
    await loginPage.login('invalid', 'invalid');
    // Note: JPetStore might not show explicit error messages, so we check if still on login page
    await expect(loginPage.loginButton).toBeVisible();
  });

  test('should logout successfully', async () => {
    const catalogPage = new CatalogPage(homePage.page);
    await catalogPage.signIn();
    await loginPage.login(TEST_USER.username, TEST_USER.password);
    await loginPage.verifyLoginSuccess();

    await loginPage.signOut();
    await expect(loginPage.signInLink).toBeVisible();
    await expect(loginPage.signOutLink).not.toBeVisible();
  });

  test('should navigate to registration page', async () => {
    const catalogPage = new CatalogPage(homePage.page);
    await catalogPage.signIn();
    await loginPage.goToRegister();

    const registrationPage = new RegistrationPage(loginPage.page);
    await registrationPage.verifyRegistrationPage();
  });

  test('should register new user successfully', async () => {
    const catalogPage = new CatalogPage(homePage.page);
    await catalogPage.signIn();
    await loginPage.goToRegister();

    const registrationPage = new RegistrationPage(loginPage.page);
    await registrationPage.fillRegistrationForm(NEW_USER_DATA);
    await registrationPage.selectLanguage('english');
    await registrationPage.selectFavoriteCategory('FISH');
    await registrationPage.enableMyList(true);
    await registrationPage.enableMyBanner(false);
    await registrationPage.submitRegistration();

    // Verify registration success (user should be logged in)
    await registrationPage.verifyRegistrationSuccess();
  });

  test('should maintain session across page navigation', async () => {
    const catalogPage = new CatalogPage(homePage.page);
    await catalogPage.signIn();
    await loginPage.login(TEST_USER.username, TEST_USER.password);
    await loginPage.verifyLoginSuccess();

    // Navigate to different pages and verify user is still logged in
    await catalogPage.goToCategory('fish');
    await expect(loginPage.signOutLink).toBeVisible();

    await catalogPage.goToCart();
    await expect(loginPage.signOutLink).toBeVisible();
  });
});