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
      
      // Display debug info
      console.log('\nDebug Information:');
      simpleResult.debugInfo.forEach(line => console.log(line));
    } else {
      console.log('Simple generation failed:', simpleResult.message);
      if (simpleResult.debugInfo.length > 0) {
        console.log('\nDebug Information:');
        simpleResult.debugInfo.forEach(line => console.log(line));
      }
    }

    // Example 2: Multi-part script
    console.log('\nGenerating script audio...');
    const scriptResult = await client.generateScriptAudio({script:[
      { text: 'Hello there!', actor: 'Tom' },
      { text: 'Hi Tom, how are you?', actor: 'Bob' },
      { text: 'I\'am doing great, thanks for asking!', actor: 'Tom' }
    ]});

    if (scriptResult.success && scriptResult.audioData) {
      console.log('Script audio generated successfully!');
      console.log('Audio URI:', scriptResult.audioData.uri);
      
      // Save the audio file
      const outputPath = join(outputDir, scriptResult.audioData.name);
      writeFileSync(outputPath, Buffer.from(scriptResult.audioData.data, 'base64'));
      console.log('Audio saved to:', outputPath);
      
      // Display debug info
      console.log('\nDebug Information:');
      scriptResult.debugInfo.forEach(line => console.log(line));
    } else {
      console.log('Script generation failed:', scriptResult.message);
      if (scriptResult.debugInfo.length > 0) {
        console.log('\nDebug Information:');
        scriptResult.debugInfo.forEach(line => console.log(line));
      }
    }

  } catch (error) {
    console.error('Error:', error);
  } finally {
    await client.close();
  }
}

main().catch(console.error);
