import { json, type RequestEvent } from "@sveltejs/kit";
import { ElevenLabsClient } from "$lib/elevenlabs/client";
import { env } from "$env/dynamic/private";

let client: ElevenLabsClient | null = null;

function getClient() {
  if (!client) {
    if (!env.MCP_SERVER_DIR) {
      throw new Error("MCP_SERVER_DIR environment variable is not set");
    }

    client = new ElevenLabsClient("uv", [
      "--directory",
      env.MCP_SERVER_DIR,
      "run",
      "elevenlabs-mcp",
    ]);
  }
  return client;
}

export async function POST({ request }: RequestEvent) {
  try {
    const { text, voice_id, type = "simple", script } = await request.json();
    const ttsClient = getClient();

    let result;
    if (type === "simple") {
      result = await ttsClient.generateSimpleAudio(text, voice_id);
    } else if (type === "script") {
      result = await ttsClient.generateScriptAudio(script);
    } else {
      throw new Error(`Invalid TTS type: ${type}`);
    }

    return json(result);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return json(
      {
        success: false,
        message: `Server error: ${message}`,
        debugInfo: [],
      },
      { status: 500 }
    );
  }
}
