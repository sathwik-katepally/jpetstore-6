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

export class RegistrationPage extends BasePage {
  readonly userIdInput: Locator;
  readonly passwordInput: Locator;
  readonly repeatPasswordInput: Locator;
  readonly firstNameInput: Locator;
  readonly lastNameInput: Locator;
  readonly emailInput: Locator;
  readonly phoneInput: Locator;
  readonly address1Input: Locator;
  readonly address2Input: Locator;
  readonly cityInput: Locator;
  readonly stateInput: Locator;
  readonly zipInput: Locator;
  readonly countryInput: Locator;
  readonly languageSelect: Locator;
  readonly categorySelect: Locator;
  readonly myListCheckbox: Locator;
  readonly myBannerCheckbox: Locator;
  readonly saveButton: Locator;

  constructor(page: Page) {
    super(page);
    this.userIdInput = page.getByRole('textbox').first();
    this.passwordInput = page.getByRole('textbox').nth(1);
    this.repeatPasswordInput = page.getByRole('textbox').nth(2);
    this.firstNameInput = page.getByRole('textbox').nth(3);
    this.lastNameInput = page.getByRole('textbox').nth(4);
    this.emailInput = page.getByRole('textbox').nth(5);
    this.phoneInput = page.getByRole('textbox').nth(6);
    this.address1Input = page.getByRole('textbox').nth(7);
    this.address2Input = page.getByRole('textbox').nth(8);
    this.cityInput = page.getByRole('textbox').nth(9);
    this.stateInput = page.getByRole('textbox').nth(10);
    this.zipInput = page.getByRole('textbox').nth(11);
    this.countryInput = page.getByRole('textbox').nth(12);
    this.languageSelect = page.getByRole('combobox').first();
    this.categorySelect = page.getByRole('combobox').nth(1);
    this.myListCheckbox = page.getByRole('checkbox').first();
    this.myBannerCheckbox = page.getByRole('checkbox').nth(1);
    this.saveButton = page.getByRole('button', { name: /save account information/i });
  }

  async goto() {
    await this.page.goto('/actions/Account.action?newAccountForm=');
    await this.waitForPageLoad();
  }

  async fillRegistrationForm(userData: any) {
    await this.userIdInput.fill(userData.username);
    await this.passwordInput.fill(userData.password);
    await this.repeatPasswordInput.fill(userData.password);
    await this.firstNameInput.fill(userData.firstName);
    await this.lastNameInput.fill(userData.lastName);
    await this.emailInput.fill(userData.email);
    await this.phoneInput.fill(userData.phone);
    await this.address1Input.fill(userData.address1);
    await this.address2Input.fill(userData.address2 || '');
    await this.cityInput.fill(userData.city);
    await this.stateInput.fill(userData.state);
    await this.zipInput.fill(userData.zip);
    await this.countryInput.fill(userData.country);
  }

  async selectLanguage(language: string) {
    await this.languageSelect.selectOption(language);
  }

  async selectFavoriteCategory(category: string) {
    await this.categorySelect.selectOption(category);
  }

  async enableMyList(enable: boolean = true) {
    if (enable) {
      await this.myListCheckbox.check();
    } else {
      await this.myListCheckbox.uncheck();
    }
  }

  async enableMyBanner(enable: boolean = true) {
    if (enable) {
      await this.myBannerCheckbox.check();
    } else {
      await this.myBannerCheckbox.uncheck();
    }
  }

  async submitRegistration() {
    await this.saveButton.click();
    await this.waitForPageLoad();
  }

  async verifyRegistrationPage() {
    await expect(this.page.getByRole('heading', { name: /user information/i })).toBeVisible();
    await expect(this.page.getByRole('heading', { name: /account information/i })).toBeVisible();
    await expect(this.page.getByRole('heading', { name: /profile information/i })).toBeVisible();
    await expect(this.saveButton).toBeVisible();
  }

  async verifyRegistrationSuccess() {
    await expect(this.signOutLink).toBeVisible();
  }
}