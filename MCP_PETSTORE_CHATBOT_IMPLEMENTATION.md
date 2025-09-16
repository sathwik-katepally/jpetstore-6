# MCP Pet Store Support Chatbot Implementation

## Overview
A comprehensive MCP server implementation for JPetStore that provides an intelligent support chatbot capable of:
- Shopping cart operations (add, update, remove items)
- Detailed pet information and care guidance
- Breed-specific health and living condition advice
- Personalized food and nutrition recommendations

---

## 🤖 Custom MCP Server Implementation

### MCP Server Structure
```
mcp-servers/
└── petstore-assistant/
    ├── package.json
    ├── index.js
    ├── tools/
    │   ├── cartOperations.js
    │   ├── petKnowledge.js
    │   ├── productSearch.js
    │   └── orderManagement.js
    ├── knowledge/
    │   ├── breeds.json
    │   ├── health-conditions.json
    │   ├── nutrition-guide.json
    │   └── care-instructions.json
    └── utils/
        ├── openrouter.js
        └── context.js
```

### 1. **MCP Server Configuration**

```javascript
// .jpetstore/mcp.json
{
  "mcpServers": {
    "petstore-assistant": {
      "command": "node",
      "args": ["./mcp-servers/petstore-assistant/index.js"],
      "env": {
        "OPENROUTER_API_KEY": "${OPENROUTER_API_KEY}",
        "JPETSTORE_API_URL": "http://localhost:8081/api",
        "DATABASE_URL": "${DATABASE_URL}"
      }
    }
  }
}
```

### 2. **Main MCP Server Implementation**

```javascript
// mcp-servers/petstore-assistant/index.js
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { cartTools } from './tools/cartOperations.js';
import { petKnowledgeTools } from './tools/petKnowledge.js';
import { productTools } from './tools/productSearch.js';
import { orderTools } from './tools/orderManagement.js';
import { OpenRouterClient } from './utils/openrouter.js';

const server = new Server(
  {
    name: 'petstore-assistant',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
      resources: {},
    },
  }
);

// Initialize OpenRouter client
const aiClient = new OpenRouterClient(process.env.OPENROUTER_API_KEY);

// Register all tools
const tools = [
  ...cartTools,
  ...petKnowledgeTools,
  ...productTools,
  ...orderTools,
  {
    name: 'chat_with_assistant',
    description: 'Chat with the AI assistant for general queries',
    inputSchema: {
      type: 'object',
      properties: {
        message: { type: 'string', description: 'User message' },
        context: { type: 'object', description: 'Conversation context' }
      },
      required: ['message']
    },
    handler: async ({ message, context }) => {
      const response = await aiClient.chat({
        model: 'anthropic/claude-3-opus',
        messages: [
          {
            role: 'system',
            content: `You are a helpful pet store assistant for JPetStore. You can help customers with:
              - Adding, updating, or removing items from their cart
              - Providing detailed information about pets, breeds, and care
              - Recommending products based on pet needs
              - Answering questions about pet health and nutrition
              
              Always be friendly, knowledgeable, and focused on helping customers make the best choices for their pets.`
          },
          {
            role: 'user',
            content: message
          }
        ],
        context
      });
      
      return { response: response.content };
    }
  }
];

// Register tools with the server
tools.forEach(tool => {
  server.setRequestHandler({
    method: 'tools/call',
    handler: async (request) => {
      if (request.params.name === tool.name) {
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(await tool.handler(request.params.arguments))
            }
          ]
        };
      }
    }
  });
});

// List available tools
server.setRequestHandler({
  method: 'tools/list',
  handler: async () => ({
    tools: tools.map(({ handler, ...tool }) => tool)
  })
});

// Start the server
const transport = new StdioServerTransport();
await server.connect(transport);
```

### 3. **Cart Operations Tools**

```javascript
// mcp-servers/petstore-assistant/tools/cartOperations.js
import axios from 'axios';

const API_URL = process.env.JPETSTORE_API_URL;

export const cartTools = [
  {
    name: 'add_to_cart',
    description: 'Add an item to the shopping cart',
    inputSchema: {
      type: 'object',
      properties: {
        userId: { type: 'string', description: 'User ID' },
        itemId: { type: 'string', description: 'Item ID to add' },
        quantity: { type: 'integer', description: 'Quantity to add', minimum: 1 }
      },
      required: ['userId', 'itemId', 'quantity']
    },
    handler: async ({ userId, itemId, quantity }) => {
      try {
        const response = await axios.post(`${API_URL}/cart/${userId}/items`, {
          itemId,
          quantity
        });
        
        return {
          success: true,
          message: `Added ${quantity} item(s) to cart`,
          cart: response.data
        };
      } catch (error) {
        return {
          success: false,
          error: error.message
        };
      }
    }
  },
  
  {
    name: 'update_cart_item',
    description: 'Update quantity of an item in the cart',
    inputSchema: {
      type: 'object',
      properties: {
        userId: { type: 'string', description: 'User ID' },
        itemId: { type: 'string', description: 'Item ID to update' },
        quantity: { type: 'integer', description: 'New quantity', minimum: 0 }
      },
      required: ['userId', 'itemId', 'quantity']
    },
    handler: async ({ userId, itemId, quantity }) => {
      try {
        if (quantity === 0) {
          // Remove item if quantity is 0
          const response = await axios.delete(`${API_URL}/cart/${userId}/items/${itemId}`);
          return {
            success: true,
            message: 'Item removed from cart',
            cart: response.data
          };
        }
        
        const response = await axios.put(`${API_URL}/cart/${userId}/items/${itemId}`, {
          quantity
        });
        
        return {
          success: true,
          message: `Updated quantity to ${quantity}`,
          cart: response.data
        };
      } catch (error) {
        return {
          success: false,
          error: error.message
        };
      }
    }
  },
  
  {
    name: 'remove_from_cart',
    description: 'Remove an item from the cart',
    inputSchema: {
      type: 'object',
      properties: {
        userId: { type: 'string', description: 'User ID' },
        itemId: { type: 'string', description: 'Item ID to remove' }
      },
      required: ['userId', 'itemId']
    },
    handler: async ({ userId, itemId }) => {
      try {
        const response = await axios.delete(`${API_URL}/cart/${userId}/items/${itemId}`);
        
        return {
          success: true,
          message: 'Item removed from cart',
          cart: response.data
        };
      } catch (error) {
        return {
          success: false,
          error: error.message
        };
      }
    }
  },
  
  {
    name: 'view_cart',
    description: 'View current cart contents',
    inputSchema: {
      type: 'object',
      properties: {
        userId: { type: 'string', description: 'User ID' }
      },
      required: ['userId']
    },
    handler: async ({ userId }) => {
      try {
        const response = await axios.get(`${API_URL}/cart/${userId}`);
        
        return {
          success: true,
          cart: response.data,
          summary: {
            totalItems: response.data.items.reduce((sum, item) => sum + item.quantity, 0),
            totalPrice: response.data.totalPrice
          }
        };
      } catch (error) {
        return {
          success: false,
          error: error.message
        };
      }
    }
  }
];
```

### 4. **Pet Knowledge Tools**

```javascript
// mcp-servers/petstore-assistant/tools/petKnowledge.js
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Load knowledge bases
const loadKnowledge = async () => {
  const breeds = JSON.parse(await fs.readFile(path.join(__dirname, '../knowledge/breeds.json'), 'utf8'));
  const healthConditions = JSON.parse(await fs.readFile(path.join(__dirname, '../knowledge/health-conditions.json'), 'utf8'));
  const nutritionGuide = JSON.parse(await fs.readFile(path.join(__dirname, '../knowledge/nutrition-guide.json'), 'utf8'));
  const careInstructions = JSON.parse(await fs.readFile(path.join(__dirname, '../knowledge/care-instructions.json'), 'utf8'));
  
  return { breeds, healthConditions, nutritionGuide, careInstructions };
};

export const petKnowledgeTools = [
  {
    name: 'get_breed_info',
    description: 'Get detailed information about a specific pet breed',
    inputSchema: {
      type: 'object',
      properties: {
        species: { type: 'string', description: 'Pet species (dog, cat, bird, fish, reptile)' },
        breed: { type: 'string', description: 'Specific breed name' }
      },
      required: ['species', 'breed']
    },
    handler: async ({ species, breed }) => {
      const { breeds } = await loadKnowledge();
      const breedInfo = breeds[species]?.[breed];
      
      if (!breedInfo) {
        return {
          found: false,
          message: `No information found for ${breed} ${species}`
        };
      }
      
      return {
        found: true,
        breed: breed,
        species: species,
        info: breedInfo,
        characteristics: breedInfo.characteristics,
        temperament: breedInfo.temperament,
        size: breedInfo.size,
        lifespan: breedInfo.lifespan,
        exercise_needs: breedInfo.exercise_needs,
        grooming_needs: breedInfo.grooming_needs
      };
    }
  },
  
  {
    name: 'get_health_conditions',
    description: 'Get information about health conditions for a pet type',
    inputSchema: {
      type: 'object',
      properties: {
        species: { type: 'string', description: 'Pet species' },
        breed: { type: 'string', description: 'Specific breed (optional)' },
        age: { type: 'string', description: 'Pet age category (puppy/kitten, adult, senior)' }
      },
      required: ['species']
    },
    handler: async ({ species, breed, age }) => {
      const { healthConditions } = await loadKnowledge();
      
      let conditions = healthConditions[species]?.common || [];
      
      if (breed && healthConditions[species]?.breeds?.[breed]) {
        conditions = [...conditions, ...healthConditions[species].breeds[breed]];
      }
      
      if (age && healthConditions[species]?.age?.[age]) {
        conditions = [...conditions, ...healthConditions[species].age[age]];
      }
      
      return {
        species,
        breed,
        age,
        common_conditions: conditions,
        prevention_tips: healthConditions[species]?.prevention || [],
        warning_signs: healthConditions[species]?.warning_signs || []
      };
    }
  },
  
  {
    name: 'get_living_conditions',
    description: 'Get suitable living conditions for a pet',
    inputSchema: {
      type: 'object',
      properties: {
        species: { type: 'string', description: 'Pet species' },
        breed: { type: 'string', description: 'Specific breed' },
        living_space: { type: 'string', description: 'Type of living space (apartment, house, farm)' }
      },
      required: ['species']
    },
    handler: async ({ species, breed, living_space }) => {
      const { careInstructions } = await loadKnowledge();
      
      const generalCare = careInstructions[species]?.general || {};
      const breedSpecific = breed ? careInstructions[species]?.breeds?.[breed] : {};
      
      return {
        species,
        breed,
        living_requirements: {
          space_needed: breedSpecific.space || generalCare.space,
          temperature_range: generalCare.temperature,
          humidity: generalCare.humidity,
          indoor_outdoor: generalCare.indoor_outdoor,
          special_requirements: breedSpecific.special || generalCare.special
        },
        environment_setup: generalCare.environment_setup,
        safety_considerations: generalCare.safety,
        suitable_for: {
          apartment: generalCare.suitable_for?.apartment || false,
          house: generalCare.suitable_for?.house || true,
          families: generalCare.suitable_for?.families || true,
          first_time_owners: breedSpecific.first_time_friendly || generalCare.first_time_friendly
        }
      };
    }
  },
  
  {
    name: 'get_nutrition_guide',
    description: 'Get nutrition and feeding guidelines for a pet',
    inputSchema: {
      type: 'object',
      properties: {
        species: { type: 'string', description: 'Pet species' },
        breed: { type: 'string', description: 'Specific breed' },
        age: { type: 'string', description: 'Pet age' },
        weight: { type: 'number', description: 'Pet weight in kg' },
        activity_level: { type: 'string', description: 'Activity level (low, moderate, high)' }
      },
      required: ['species', 'age']
    },
    handler: async ({ species, breed, age, weight, activity_level }) => {
      const { nutritionGuide } = await loadKnowledge();
      
      const baseNutrition = nutritionGuide[species]?.[age] || {};
      const breedSpecific = breed ? nutritionGuide[species]?.breeds?.[breed] : {};
      
      // Calculate daily calorie needs
      let caloriesPerDay = baseNutrition.base_calories || 0;
      if (weight) {
        caloriesPerDay = Math.round(caloriesPerDay * weight);
      }
      if (activity_level === 'high') {
        caloriesPerDay = Math.round(caloriesPerDay * 1.3);
      } else if (activity_level === 'low') {
        caloriesPerDay = Math.round(caloriesPerDay * 0.8);
      }
      
      return {
        species,
        breed,
        age,
        daily_calories: caloriesPerDay,
        feeding_schedule: baseNutrition.feeding_schedule,
        recommended_foods: {
          primary: baseNutrition.primary_foods || [],
          treats: baseNutrition.treats || [],
          avoid: [...(baseNutrition.avoid || []), ...(breedSpecific.avoid || [])]
        },
        special_dietary_needs: breedSpecific.special_needs || baseNutrition.special_needs,
        hydration: baseNutrition.hydration,
        supplements: baseNutrition.supplements || []
      };
    }
  }
];
```

### 5. **Knowledge Base Examples**

```json
// mcp-servers/petstore-assistant/knowledge/breeds.json
{
  "dog": {
    "golden_retriever": {
      "characteristics": {
        "size": "Large",
        "weight_range": "25-35 kg",
        "height_range": "51-61 cm",
        "coat": "Dense, water-repellent double coat",
        "colors": ["Golden", "Cream", "Light Golden"]
      },
      "temperament": ["Friendly", "Intelligent", "Devoted", "Gentle"],
      "lifespan": "10-12 years",
      "exercise_needs": "High - requires 2+ hours daily",
      "grooming_needs": "High - daily brushing recommended",
      "good_with": {
        "children": true,
        "other_pets": true,
        "strangers": true
      },
      "special_considerations": [
        "Prone to hip dysplasia",
        "Needs mental stimulation",
        "Heavy shedder"
      ]
    },
    "poodle": {
      "characteristics": {
        "size": "Varies (Toy, Miniature, Standard)",
        "weight_range": "2-32 kg depending on variety",
        "coat": "Curly, hypoallergenic",
        "colors": ["Black", "White", "Brown", "Apricot", "Silver"]
      },
      "temperament": ["Intelligent", "Active", "Alert", "Trainable"],
      "lifespan": "12-15 years",
      "exercise_needs": "Moderate to High",
      "grooming_needs": "Very High - professional grooming every 6-8 weeks",
      "good_with": {
        "children": true,
        "other_pets": true,
        "allergies": true
      }
    }
  },
  "cat": {
    "persian": {
      "characteristics": {
        "size": "Medium to Large",
        "weight_range": "3.5-7 kg",
        "coat": "Long, thick, luxurious",
        "colors": ["Various solid and patterns"]
      },
      "temperament": ["Calm", "Gentle", "Quiet", "Sweet"],
      "lifespan": "12-17 years",
      "exercise_needs": "Low",
      "grooming_needs": "Very High - daily grooming essential",
      "special_considerations": [
        "Brachycephalic breed - breathing issues",
        "Eye discharge common",
        "Indoor cat only"
      ]
    }
  }
}
```

```json
// mcp-servers/petstore-assistant/knowledge/nutrition-guide.json
{
  "dog": {
    "puppy": {
      "base_calories": 55,
      "feeding_schedule": "3-4 times daily until 6 months",
      "primary_foods": [
        "High-quality puppy formula",
        "DHA-enriched food for brain development"
      ],
      "treats": ["Training treats", "Soft chews"],
      "avoid": ["Chocolate", "Grapes", "Onions", "Garlic", "Xylitol"],
      "hydration": "Fresh water available at all times",
      "supplements": ["Puppy vitamins if recommended by vet"]
    },
    "adult": {
      "base_calories": 30,
      "feeding_schedule": "2 times daily",
      "primary_foods": [
        "Complete and balanced adult dog food",
        "Protein-rich formulas"
      ],
      "treats": ["Dental chews", "Training treats (max 10% of daily calories)"],
      "avoid": ["Chocolate", "Grapes", "Onions", "Garlic", "Xylitol", "Cooked bones"],
      "hydration": "1 ounce per pound of body weight daily"
    },
    "senior": {
      "base_calories": 25,
      "feeding_schedule": "2 times daily, smaller portions",
      "primary_foods": [
        "Senior formula with joint support",
        "Lower calorie options"
      ],
      "supplements": ["Glucosamine", "Omega-3 fatty acids"]
    }
  }
}
```

### 6. **Frontend Integration**

```typescript
// components/PetStoreChat.tsx
'use client';

import { useState, useRef, useEffect } from 'react';
import { useMCPClient } from '@/hooks/useMCPClient';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  actions?: any[];
}

export default function PetStoreChat({ userId }: { userId: string }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { mcpClient } = useMCPClient();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Analyze intent and route to appropriate tool
      const intent = await analyzeIntent(input);
      
      let response;
      switch (intent.type) {
        case 'cart_operation':
          response = await handleCartOperation(intent, userId);
          break;
        case 'pet_info':
          response = await handlePetInfo(intent);
          break;
        case 'product_search':
          response = await handleProductSearch(intent);
          break;
        default:
          response = await handleGeneralChat(input);
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.message,
        timestamp: new Date(),
        actions: response.actions
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'I apologize, but I encountered an error. Please try again.',
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const analyzeIntent = async (message: string) => {
    // Use AI to analyze user intent
    const response = await mcpClient.useTools(
      'petstore-assistant',
      'analyze_intent',
      { message }
    );
    return response;
  };

  const handleCartOperation = async (intent: any, userId: string) => {
    const { operation, itemId, quantity } = intent.parameters;
    
    const response = await mcpClient.useTools(
      'petstore-assistant',
      operation,
      { userId, itemId, quantity }
    );

    return {
      message: response.message,
      actions: response.cart ? [{
        type: 'show_cart',
        data: response.cart
      }] : []
    };
  };

  const handlePetInfo = async (intent: any) => {
    const { infoType, species, breed } = intent.parameters;
    
    const response = await mcpClient.useTools(
      'petstore-assistant',
      `get_${infoType}`,
      { species, breed }
    );

    return {
      message: formatPetInfo(response),
      actions: [{
        type: 'show_related_products',
        data: { species, breed }
      }]
    };
  };

  const handleGeneralChat = async (message: string) => {
    const response = await mcpClient.useTools(
      'petstore-assistant',
      'chat_with_assistant',
      { 
        message,
        context: {
          previousMessages: messages.slice(-5),
          userId
        }
      }
    );

    return {
      message: response.response,
      actions: []
    };
  };

  const formatPetInfo = (info: any) => {
    // Format pet information into readable message
    let message = '';
    
    if (info.breed) {
      message += `Here's information about ${info.breed}:\n\n`;
      message += `**Characteristics:**\n`;
      message += `- Size: ${info.characteristics.size}\n`;
      message += `- Lifespan: ${info.lifespan}\n`;
      message += `- Exercise Needs: ${info.exercise_needs}\n\n`;
      
      if (info.temperament) {
        message += `**Temperament:** ${info.temperament.join(', ')}\n\n`;
      }
    }
    
    return message;
  };

  return (
    <div className="flex flex-col h-[600px] bg-white rounded-lg shadow-lg">
      <div className="bg-blue-600 text-white p-4 rounded-t-lg">
        <h3 className="text-lg font-semibold">Pet Store Assistant</h3>
        <p className="text-sm text-blue-100">Ask me about pets, products, or your cart!</p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[70%] rounded-lg p-3 ${
                message.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              <p className="whitespace-pre-wrap">{message.content}</p>
              
              {message.actions?.map((action, idx) => (
                <div key={idx} className="mt-2">
                  {action.type === 'show_cart' && (
                    <CartSummary cart={action.data} />
                  )}
                  {action.type === 'show_related_products' && (
                    <button className="text-sm underline">
                      View products for {action.data.species}
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg p-3">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="border-t p-4">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask about pets, products, or manage your cart..."
            className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
        
        <div className="mt-2 flex flex-wrap gap-2">
          <QuickAction onClick={() => setInput("What's in my cart?")}>
            View Cart
          </QuickAction>
          <QuickAction onClick={() => setInput("Tell me about Golden Retrievers")}>
            Dog Breeds
          </QuickAction>
          <QuickAction onClick={() => setInput("What food is best for a senior cat?")}>
            Pet Nutrition
          </QuickAction>
          <QuickAction onClick={() => setInput("Show me products for fish")}>
            Browse Products
          </QuickAction>
        </div>
      </div>
    </div>
  );
}

function QuickAction({ children, onClick }: { children: React.ReactNode; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="text-xs px-3 py-1 bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200"
    >
      {children}
    </button>
  );
}

function CartSummary({ cart }: { cart: any }) {
  return (
    <div className="bg-white rounded p-2 mt-2 text-sm">
      <div className="font-semibold">Cart Summary:</div>
      <div>Items: {cart.items.length}</div>
      <div>Total: ${cart.totalPrice}</div>
    </div>
  );
}
```

### 7. **OpenRouter Integration Utility**

```javascript
// mcp-servers/petstore-assistant/utils/openrouter.js
import axios from 'axios';

export class OpenRouterClient {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.baseURL = 'https://openrouter.ai/api/v1';
  }

  async chat({ model, messages, context }) {
    try {
      const response = await axios.post(
        `${this.baseURL}/chat/completions`,
        {
          model: model || 'anthropic/claude-3-opus',
          messages: messages,
          temperature: 0.7,
          max_tokens: 1000,
          top_p: 1,
          frequency_penalty: 0,
          presence_penalty: 0,
          stream: false
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'HTTP-Referer': 'https://jpetstore.com',
            'X-Title': 'JPetStore Assistant',
            'Content-Type': 'application/json'
          }
        }
      );

      return response.data.choices[0].message;
