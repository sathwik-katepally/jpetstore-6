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

import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base.page';

export class LoginPage extends BasePage {
  readonly usernameInput: Locator;
  readonly passwordInput: Locator;
  readonly loginButton: Locator;
  readonly registerLink: Locator;
  readonly loginForm: Locator;

  constructor(page: Page) {
    super(page);
    this.usernameInput = page.getByRole('textbox').first();
    this.passwordInput = page.getByRole('textbox').nth(1);
    this.loginButton = page.getByRole('button', { name: /login/i });
    this.registerLink = page.getByRole('link', { name: /register now/i });
    this.loginForm = page.locator('form, #Catalog');
  }

  async goto() {
    await this.page.goto('/actions/Account.action?signonForm=');
    await this.waitForPageLoad();
  }

  async login(username: string, password: string) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
    await this.waitForPageLoad();
  }

  async goToRegister() {
    await this.registerLink.click();
    await this.waitForPageLoad();
  }

  async verifyLoginPage() {
    await expect(this.usernameInput).toBeVisible();
    await expect(this.passwordInput).toBeVisible();
    await expect(this.loginButton).toBeVisible();
    await expect(this.registerLink).toBeVisible();
    await expect(this.page.getByText(/please enter your username and password/i)).toBeVisible();
  }

  async verifyLoginSuccess() {
    await expect(this.signOutLink).toBeVisible();
    await expect(this.signInLink).not.toBeVisible();
  }

  async verifyLoginFailure() {
    await expect(this.page.getByText(/invalid username or password/i)).toBeVisible();
  }
}