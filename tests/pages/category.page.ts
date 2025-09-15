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

export class CategoryPage extends BasePage {
  readonly returnToMainMenuLink: Locator;
  readonly categoryHeading: Locator;
  readonly productTable: Locator;
  readonly productLinks: Locator;

  constructor(page: Page) {
    super(page);
    this.returnToMainMenuLink = page.getByRole('link', { name: /return to main menu/i });
    this.categoryHeading = page.locator('h2');
    this.productTable = page.locator('table');
    this.productLinks = page.locator('table a');
  }

  async verifyCategoryPage(categoryName: string) {
    await expect(this.categoryHeading).toHaveText(categoryName);
    await expect(this.productTable).toBeVisible();
    await expect(this.returnToMainMenuLink).toBeVisible();
  }

  async selectProduct(productId: string) {
    await this.page.getByRole('link', { name: productId }).click();
    await this.waitForPageLoad();
  }

  async returnToMainMenu() {
    await this.returnToMainMenuLink.click();
    await this.waitForPageLoad();
  }

  async getProductCount() {
    return await this.productLinks.count();
  }
}