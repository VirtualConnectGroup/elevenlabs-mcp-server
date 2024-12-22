import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { 
  TextContent, 
  EmbeddedResource, 
  CallToolRequest,
  CallToolResult,
  CallToolResultSchema,
  BlobResourceContents,
  TextResourceContents
} from "@modelcontextprotocol/sdk/types.js";

interface AudioGenerationResponse {
  success: boolean;
  message: string;
  debugInfo: string[];
  audioData?: {
    uri: string;
    name: string;
    data: string; // base64 encoded audio
  };
}

interface ScriptInterface {
  script: ScriptPart[];
}

interface ScriptPart {
  text: string;
  voice_id?: string;
  actor?: string;
}

export class ElevenLabsClient {
  private client: Client;
  private connectionPromise: Promise<void>;

  constructor(command: string, args?: string[]) {
    const transport = new StdioClientTransport({
      command,
      args
    });

    this.client = new Client({
      name: 'elevenlabs-client',
      version: '0.1.0'
    }, {
      capabilities: {}
    });

    // Initialize connection promise
    this.connectionPromise = this.client.connect(transport);
    this.connectionPromise.catch((error: Error) => {
      console.error('Failed to connect:', error);
    });
  }

  private parseToolResponse(response: CallToolResult): AudioGenerationResponse {
    const result: AudioGenerationResponse = {
      success: false,
      message: '',
      debugInfo: []
    };

    if (response.content) {
      for (const content of response.content) {
        if (content.type === 'text') {
          // Split the text content into lines
          const lines = content.text.split('\n');
          // First line is the status message
          result.message = lines[0];
          // Rest are debug info (skip the "Debug info:" line)
          result.debugInfo = lines.slice(2);
          // Check if the message indicates success
          result.success = result.message.includes('successful');
        } else if (content.type === 'resource') {
          const resource = content.resource as BlobResourceContents;
          result.audioData = {
            uri: resource.uri,
            name: (resource.name as string) || resource.uri.split('/').pop() || 'audio',
            data: resource.blob
          };
        }
      }
    }

    return result;
  }

  async generateSimpleAudio(text: string, voice_id?: string): Promise<AudioGenerationResponse> {
    try {
      // Wait for connection before making request
      await this.connectionPromise;

      const request: CallToolRequest = {
        method: "tools/call",
        params: {
          name: "generate_audio_simple",
          arguments: {
            text,
            voice_id
          }
        }
      };

      const response = await this.client.request(request, CallToolResultSchema);
      return this.parseToolResponse(response);
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      return {
        success: false,
        message: `Error generating audio: ${errorMessage}`,
        debugInfo: []
      };
    }
  }

  async generateScriptAudio(script: string | ScriptInterface): Promise<AudioGenerationResponse> {
    try {
      // Wait for connection before making request
      await this.connectionPromise;

      const scriptJson = typeof script === 'string' ? script : JSON.stringify(script);

      const request: CallToolRequest = {
        method: "tools/call",
        params: {
          name: "generate_audio_script",
          arguments: {
            script: scriptJson
          }
        }
      };

      const response = await this.client.request(request, CallToolResultSchema);
      return this.parseToolResponse(response);
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      return {
        success: false,
        message: `Error generating audio: ${errorMessage}`,
        debugInfo: []
      };
    }
  }

  async close(): Promise<void> {
    try {
      // Wait for connection before closing
      await this.connectionPromise;
      if (this.client) {
        await this.client.close();
      }
    } catch (error) {
      console.error('Error closing client:', error);
    }
  }
}
