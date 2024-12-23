<script lang="ts">
    import AudioPlayer from '$lib/components/AudioPlayer.svelte';
    import DebugInfo from '$lib/components/DebugInfo.svelte';
    import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
    import type { AudioGenerationResponse } from '$lib/elevenlabs/client';

    let text = '';
    let voiceId = '';
    let loading = false;
    let result: AudioGenerationResponse | null = null;

    async function generateAudio() {
        if (!text) return;
        
        loading = true;
        result = null;
        
        try {
            const response = await fetch('/api/tts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text,
                    voice_id: voiceId || undefined,
                    type: 'simple'
                })
            });
            
            const data = await response.json() as AudioGenerationResponse;
            
            if (!data.success) {
                throw new Error(data.message);
            }
            
            result = data;
        } catch (error) {
            result = {
                success: false,
                message: error instanceof Error ? error.message : String(error),
                debugInfo: []
            };
        } finally {
            loading = false;
        }
    }
</script>

<main>
    <h1>Text to Speech</h1>
    
    <form on:submit|preventDefault={generateAudio} class="tts-form">
        <div class="form-group">
            <label for="text">Text</label>
            <textarea
                id="text"
                bind:value={text}
                placeholder="Enter text to convert to speech..."
                rows="4"
                required
            ></textarea>
        </div>
        
        <div class="form-group">
            <label for="voice">Voice ID (optional)</label>
            <input
                id="voice"
                type="text"
                bind:value={voiceId}
                placeholder="Enter voice ID..."
            />
        </div>
        
        <button type="submit" disabled={loading || !text}>
            {#if loading}
                <LoadingSpinner size={16} />
                Generating...
            {:else}
                Generate Audio
            {/if}
        </button>
    </form>
    
    {#if result}
        <div class="result">
            {#if result.success && result.audioData}
                <AudioPlayer 
                    audioData={result.audioData.data}
                    name={result.audioData.name}
                />
            {:else}
                <p class="error">{result.message}</p>
            {/if}
            
            <DebugInfo info={result.debugInfo} />
        </div>
    {/if}
</main>

<style>
    main {
        max-width: 800px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    h1 {
        margin-bottom: 2rem;
        color: #333;
    }
    
    .tts-form {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .form-group {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    label {
        font-weight: 500;
        color: #555;
    }
    
    textarea, input {
        padding: 0.75rem;
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        font-size: 1rem;
        font-family: inherit;
    }
    
    textarea:focus, input:focus {
        outline: none;
        border-color: #666;
    }
    
    button {
        padding: 0.75rem 1.5rem;
        background: #0066cc;
        color: white;
        border: none;
        border-radius: 0.5rem;
        font-size: 1rem;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        transition: opacity 0.2s;
    }
    
    button:disabled {
        opacity: 0.7;
        cursor: not-allowed;
    }
    
    button:not(:disabled):hover {
        opacity: 0.9;
    }
    
    .result {
        margin-top: 2rem;
    }
    
    .error {
        color: #dc2626;
        padding: 1rem;
        background: #fef2f2;
        border: 1px solid #fee2e2;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
