import { NextRequest, NextResponse } from 'next/server';

// MCP server communication endpoint
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message, userId, context } = body;

    // For now, we'll create a direct HTTP endpoint for the MCP server
    // In production, you might want to use WebSocket or other protocols
    const mcpResponse = await fetch('http://localhost:3001/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        tool: 'chat',
        arguments: {
          message,
          user_id: userId,
          context
        }
      })
    });

    if (!mcpResponse.ok) {
      throw new Error('Failed to communicate with MCP server');
    }

    const data = await mcpResponse.json();
    
    // Parse the response from MCP server
    let responseText = 'I apologize, but I couldn\'t process your request.';
    
    if (data && data.success && data.result) {
      const result = data.result;
      
      if (result.message) {
        responseText = result.message;
      } else if (result.response) {
        responseText = result.response;
      } else if (typeof result === 'string') {
        responseText = result;
      }
    }

    return NextResponse.json({ 
      response: responseText,
      success: true 
    });

  } catch (error) {
    console.error('Chat API error:', error);
    
    // For development, provide more detailed error messages
    const errorMessage = process.env.NODE_ENV === 'development' 
      ? `Error: ${error instanceof Error ? error.message : 'Unknown error'}`
      : 'I\'m sorry, I\'m having trouble connecting to the server. Please try again later.';

    return NextResponse.json({ 
      response: errorMessage,
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}
