# NLP-Based Tool Routing Guide

## Overview

The JPetStore MCP server now includes an intelligent NLP-based tool routing system that automatically selects and executes the appropriate tools based on natural language input from users. This eliminates the need for users to explicitly specify which tool to use - the AI analyzes their message and determines the best action.

## How It Works

### 1. **Natural Language Processing**
When a user sends a message through the `chat` tool, the system:
- Analyzes the intent using AI (via OpenRouter)
- Extracts relevant parameters from the message
- Determines which tool to execute
- Handles the execution and formats the response

### 2. **Intent Classification**
The system classifies user messages into these categories:
- **cart_operation**: Shopping cart management (add, remove, view, update)
- **pet_info**: Pet-related information (breeds, health, nutrition)
- **product_search**: Finding products in the store
- **order_management**: Order tracking and management
- **general**: General queries and conversations

### 3. **Parameter Extraction**
The router uses sophisticated pattern matching and NLP to extract:
- Item IDs (e.g., "EST-1")
- Quantities (e.g., "2 items", "5 pieces")
- Pet species and breeds
- Age categories (puppy, adult, senior)
- Product categories
- Order numbers
- And more...

## Usage Examples

### Through MCP Client

```json
{
  "tool": "chat",
  "arguments": {
    "message": "I want to add 3 items of EST-1 to my cart",
    "user_id": "user123"
  }
}
```

### Natural Language Examples

#### Shopping Cart Operations
- "Add EST-1 to my cart"
- "I want to buy 5 items of EST-2"
- "Show me what's in my shopping cart"
- "Remove EST-3 from my cart"
- "Update EST-1 quantity to 10"

#### Pet Information
- "Tell me about Golden Retriever dogs"
- "What health issues do Persian cats have?"
- "I need nutrition advice for my senior dog"
- "What should I feed my 6-month-old kitten?"
- "Tell me about caring for goldfish"

#### Product Search
- "Search for dog toys"
- "Find cat food products"
- "Show me fish tank accessories"
- "I'm looking for pet grooming supplies"

#### Order Management
- "What's the status of order #12345?"
- "Track my order 98765"
- "Create an order from my cart"

#### General Queries
- "How can you help me?"
- "What services do you offer?"
- "Tell me about your store"

## Response Format

The system returns structured responses:

```json
{
  "success": true,
  "type": "tool_result",
  "tool_name": "add_to_cart",
  "result": {
    "status": "success",
    "message": "Item added to cart"
  },
  "message": "I've successfully added 3 units of EST-1 to your cart!"
}
```

## Missing Parameters

If required information is missing, the system asks for it:

```json
{
  "success": false,
  "type": "missing_parameters",
  "missing": ["item_id"],
  "message": "I need a bit more information to help you:\n• Which item would you like to add? Please provide the item ID (e.g., EST-1)."
}
```

## Testing the System

### Automated Tests
Run the test suite to see various examples:
```bash
cd mcp-servers/petstore-assistant
python test_nlp_router.py
```

### Interactive Mode
Test the system interactively:
```bash
python test_nlp_router.py --interactive
```

## Architecture

### Components

1. **NLPToolRouter** (`nlp_tool_router.py`)
   - Main routing logic
   - Intent analysis
   - Parameter extraction
   - Tool execution
   - Response formatting

2. **OpenRouterClient** (`openrouter.py`)
   - AI integration for intent analysis
   - Natural language processing
   - Fallback responses

3. **Tool Handlers**
   - CartOperations
   - PetKnowledge
   - ProductSearch
   - OrderManagement

### Flow Diagram

```
User Message
    ↓
Intent Analysis (AI)
    ↓
Parameter Extraction
    ↓
Tool Selection
    ↓
Tool Execution
    ↓
Response Formatting
    ↓
User Response
```

## Configuration

### Environment Variables
```bash
OPENROUTER_API_KEY=your_api_key_here
JPETSTORE_API_URL=http://localhost:8081/api
```

### Supported AI Models
The system uses `anthropic/claude-3-haiku` by default but can be configured to use other models supported by OpenRouter.

## Extending the System

### Adding New Tools

1. Create the tool handler in the appropriate module
2. Add tool mapping in `NLPToolRouter.__init__`
3. Create parameter extractors if needed
4. Update the intent analysis patterns

### Adding New Intents

1. Update the `analyze_intent` method in `OpenRouterClient`
2. Add patterns to `_simple_intent_analysis`
3. Create corresponding tool mappings

## Best Practices

1. **Clear User Messages**: Encourage users to be specific about what they want
2. **Include IDs**: When referring to products, include the item ID
3. **Specify Quantities**: Be clear about how many items
4. **Pet Details**: Include species, breed, and age when asking about pets

## Troubleshooting

### Common Issues

1. **"Missing parameters" responses**
   - Solution: Include more specific information in the message

2. **Wrong tool selected**
   - Solution: Use more specific keywords related to the desired action

3. **API errors**
   - Check environment variables
   - Ensure the JPetStore API is running
   - Verify OpenRouter API key is valid

### Debug Mode

Enable debug logging by setting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

1. **Context Awareness**: Better handling of conversation context
2. **Multi-step Operations**: Support for complex workflows
3. **Learning**: Improve intent classification based on usage
4. **Multilingual Support**: Handle queries in multiple languages
5. **Voice Integration**: Support for voice-based queries

## Conclusion

The NLP-based tool routing system makes the JPetStore chatbot more intuitive and user-friendly. Users can interact naturally without needing to understand the underlying tool structure, while the AI handles the complexity of selecting and executing the appropriate actions.
