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

export class CatalogPage extends BasePage {
  readonly categoryImages: Locator;
  readonly quickLinks: Locator;

  constructor(page: Page) {
    super(page);
    this.categoryImages = page.locator('#QuickLinks img');
    this.quickLinks = page.locator('#QuickLinks a');
  }

  async goto() {
    await this.page.goto('/actions/Catalog.action');
    await this.waitForPageLoad();
  }

  async verifyCatalogPage() {
    await expect(this.categoryImages).toHaveCount(5);
    await expect(this.page.getByText(/saltwater, freshwater/i)).toBeVisible();
    await expect(this.page.getByText(/various breeds/i)).toBeVisible();
  }

  async selectCategory(categoryId: string) {
    await this.page.getByRole('link', { name: new RegExp(categoryId, 'i') }).first().click();
    await this.waitForPageLoad();
  }
}