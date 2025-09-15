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

export class ProductPage extends BasePage {
  readonly productHeading: Locator;
  readonly itemTable: Locator;
  readonly addToCartLinks: Locator;
  readonly itemLinks: Locator;
  readonly returnToCategoryLink: Locator;

  constructor(page: Page) {
    super(page);
    this.productHeading = page.locator('h2');
    this.itemTable = page.locator('table');
    this.addToCartLinks = page.getByRole('link', { name: /add to cart/i });
    this.itemLinks = page.locator('table a[href*="viewItem"]');
    this.returnToCategoryLink = page.getByRole('link', { name: /return to/i });
  }

  async verifyProductPage(productName: string) {
    await expect(this.productHeading).toHaveText(productName);
    await expect(this.itemTable).toBeVisible();
    await expect(this.returnToCategoryLink).toBeVisible();
  }

  async addItemToCart(itemIndex: number = 0) {
    await this.addToCartLinks.nth(itemIndex).click();
    await this.waitForPageLoad();
  }

  async viewItemDetails(itemIndex: number = 0) {
    await this.itemLinks.nth(itemIndex).click();
    await this.waitForPageLoad();
  }

  async returnToCategory() {
    await this.returnToCategoryLink.click();
    await this.waitForPageLoad();
  }

  async getItemCount() {
    return await this.addToCartLinks.count();
  }
}