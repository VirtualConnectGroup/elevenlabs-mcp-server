import { ElevenLabsClient } from "./elevenlabs-client.js";
import { browser } from "$app/environment";

// Only initialize the client on the server side
export const elevenlabsClient = !browser
  ? new ElevenLabsClient("uv", [
      "--directory",
      "/home/atomrem/dev/Projects/elevenlabs-mcp-server/src/elevenlabs_mcp",
      "run",
      "elevenlabs-mcp",
    ])
  : null;

// Export the client type for use in components
export type { JobHistory } from "./elevenlabs-client.js";
