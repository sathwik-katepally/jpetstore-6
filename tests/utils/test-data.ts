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

export const TEST_USER = {
  username: 'j2ee',
  password: 'j2ee',
  email: 'yourname@yourdomain.com',
  firstName: 'ABC',
  lastName: 'XYX'
};

export const TEST_PRODUCTS = {
  FISH: {
    categoryId: 'FISH',
    products: [
      { id: 'FI-SW-01', name: 'Angelfish', items: ['EST-1', 'EST-2'] },
      { id: 'FI-SW-02', name: 'Tiger Shark', items: ['EST-3'] },
      { id: 'FI-FW-01', name: 'Koi', items: ['EST-4', 'EST-5'] },
      { id: 'FI-FW-02', name: 'Goldfish', items: ['EST-20'] }
    ]
  },
  DOGS: {
    categoryId: 'DOGS',
    products: [
      { id: 'K9-BD-01', name: 'Bulldog' },
      { id: 'K9-PO-02', name: 'Poodle' },
      { id: 'K9-DL-01', name: 'Dalmation' },
      { id: 'K9-RT-01', name: 'Golden Retriever' },
      { id: 'K9-RT-02', name: 'Labrador Retriever' }
    ]
  },
  CATS: {
    categoryId: 'CATS',
    products: [
      { id: 'FL-DSH-01', name: 'Manx' },
      { id: 'FL-DLH-02', name: 'Persian' }
    ]
  }
};

export const NEW_USER_DATA = {
  username: 'testuser' + Date.now(),
  password: 'testpass123',
  firstName: 'Test',
  lastName: 'User',
  email: 'test@example.com',
  phone: '555-123-4567',
  address1: '123 Test St',
  address2: 'Apt 1',
  city: 'Test City',
  state: 'TS',
  zip: '12345',
  country: 'USA'
};