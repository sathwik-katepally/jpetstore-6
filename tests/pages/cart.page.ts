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

export class CartPage extends BasePage {
  readonly cartTable: Locator;
  readonly updateCartButton: Locator;
  readonly proceedToCheckoutButton: Locator;
  readonly removeFromCartLinks: Locator;
  readonly quantityInputs: Locator;
  readonly subTotalCell: Locator;
  readonly emptyCartMessage: Locator;

  constructor(page: Page) {
    super(page);
    this.cartTable = page.locator('table');
    this.updateCartButton = page.getByRole('button', { name: /update cart/i });
    this.proceedToCheckoutButton = page.getByRole('button', { name: /proceed to checkout/i });
    this.removeFromCartLinks = page.getByRole('link', { name: /remove/i });
    this.quantityInputs = page.locator('input[name*="quantity"]');
    this.subTotalCell = page.locator('td:has-text("Sub Total:")').locator('..').locator('td').last();
    this.emptyCartMessage = page.getByText(/your cart is empty/i);
  }

  async goto() {
    await this.page.goto('/actions/Cart.action?viewCart=');
    await this.waitForPageLoad();
  }

  async verifyCartPage() {
    await expect(this.page).toHaveTitle(/jpetstore demo/i);
  }

  async verifyEmptyCart() {
    await expect(this.emptyCartMessage).toBeVisible();
  }

  async verifyItemInCart(itemId: string) {
    await expect(this.page.getByText(itemId)).toBeVisible();
  }

  async updateQuantity(itemIndex: number, quantity: string) {
    await this.quantityInputs.nth(itemIndex).fill(quantity);
    await this.updateCartButton.click();
    await this.waitForPageLoad();
  }

  async removeItem(itemIndex: number) {
    await this.removeFromCartLinks.nth(itemIndex).click();
    await this.waitForPageLoad();
  }

  async proceedToCheckout() {
    await this.proceedToCheckoutButton.click();
    await this.waitForPageLoad();
  }

  async getItemCount() {
    return await this.removeFromCartLinks.count();
  }

  async getSubTotal() {
    return await this.subTotalCell.textContent();
  }
}