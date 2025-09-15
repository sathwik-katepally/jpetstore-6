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

import { Page, Locator } from '@playwright/test';

export class BasePage {
  readonly page: Page;
  readonly logoLink: Locator;
  readonly cartLink: Locator;
  readonly signInLink: Locator;
  readonly signOutLink: Locator;
  readonly helpLink: Locator;
  readonly searchBox: Locator;
  readonly searchButton: Locator;
  readonly categoryLinks: {
    fish: Locator;
    dogs: Locator;
    cats: Locator;
    reptiles: Locator;
    birds: Locator;
  };

  constructor(page: Page) {
    this.page = page;
    this.logoLink = page.getByRole('link').first();
    this.cartLink = page.getByRole('link', { name: /cart/i });
    this.signInLink = page.getByRole('link', { name: /sign in/i });
    this.signOutLink = page.getByRole('link', { name: /sign out/i });
    this.helpLink = page.getByRole('link', { name: '?' });
    this.searchBox = page.getByRole('textbox');
    this.searchButton = page.getByRole('button', { name: /search/i });

    this.categoryLinks = {
      fish: page.getByRole('link', { name: /fish/i }).first(),
      dogs: page.getByRole('link', { name: /dogs/i }).first(),
      cats: page.getByRole('link', { name: /cats/i }).first(),
      reptiles: page.getByRole('link', { name: /reptiles/i }).first(),
      birds: page.getByRole('link', { name: /birds/i }).first(),
    };
  }

  async goto(path: string = '') {
    await this.page.goto(path);
  }

  async goToCategory(category: 'fish' | 'dogs' | 'cats' | 'reptiles' | 'birds') {
    await this.categoryLinks[category].click();
  }

  async search(searchTerm: string) {
    await this.searchBox.fill(searchTerm);
    await this.searchButton.click();
  }

  async goToCart() {
    await this.cartLink.click();
  }

  async signIn() {
    await this.signInLink.click();
  }

  async signOut() {
    await this.signOutLink.click();
  }

  async goToHelp() {
    await this.helpLink.click();
  }

  async waitForPageLoad() {
    await this.page.waitForLoadState('networkidle');
  }
}