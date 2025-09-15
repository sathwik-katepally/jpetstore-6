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

export class HomePage extends BasePage {
  readonly enterStoreLink: Locator;
  readonly welcomeHeading: Locator;

  constructor(page: Page) {
    super(page);
    this.enterStoreLink = page.getByRole('link', { name: /enter the store/i });
    this.welcomeHeading = page.getByRole('heading', { name: /welcome to jpetstore/i });
  }

  async goto() {
    await this.page.goto('/');
    await this.waitForPageLoad();
  }

  async enterStore() {
    await this.enterStoreLink.click();
    await this.waitForPageLoad();
  }

  async verifyHomePage() {
    await expect(this.welcomeHeading).toBeVisible();
    await expect(this.enterStoreLink).toBeVisible();
    await expect(this.page).toHaveTitle(/jpetstore demo/i);
  }
}