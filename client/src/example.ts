import { ElevenLabsClient } from './elevenlabs-client.js';
import { writeFileSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const outputDir = join(dirname(__dirname), 'output');

// Create output directory
mkdirSync(outputDir, { recursive: true });

async function main() {
  // Initialize client with the server command
  const client = new ElevenLabsClient('uv', ['--directory', 'd:/GitHub/elevenlabs-mcp-server', 'run', 'elevenlabs-mcp']);
  
  try {
    // Example 1: Simple text-to-speech
    console.log('\nGenerating simple audio...');
    const simpleResult = await client.generateSimpleAudio(
      'Hello! This is a test of the ElevenLabs MCP client.'
    );

    if (simpleResult.success && simpleResult.audioData) {
      console.log('Audio generated successfully!');
      console.log('Audio URI:', simpleResult.audioData.uri);
      
      // Save the audio file
      const outputPath = join(outputDir, simpleResult.audioData.name);
      writeFileSync(outputPath, Buffer.from(simpleResult.audioData.data, 'base64'));
      console.log('Audio saved to:', outputPath);
    } else {
      console.log('Simple generation failed:', simpleResult.message);
    }

    // Example 2: Multi-part script
    console.log('\nGenerating script audio...');
    const scriptResult = await client.generateScriptAudio({script:[
      { text: 'Hello there!', actor: 'Alice' },
      { text: 'Hi Alice, how are you?', actor: 'Bob' },
      { text: 'I\'m doing great, thanks for asking!', actor: 'Alice' }
    ]});

    if (scriptResult.success && scriptResult.audioData) {
      console.log('Script audio generated successfully!');
      console.log('Audio URI:', scriptResult.audioData.uri);
      
      // Save the audio file
      const outputPath = join(outputDir, scriptResult.audioData.name);
      writeFileSync(outputPath, Buffer.from(scriptResult.audioData.data, 'base64'));
      console.log('Audio saved to:', outputPath);
    } else {
      console.log('Script generation failed:', scriptResult.message);
    }

  } catch (error) {
    console.error('Error:', error);
  } finally {
    await client.close();
  }
}

main().catch(console.error);
