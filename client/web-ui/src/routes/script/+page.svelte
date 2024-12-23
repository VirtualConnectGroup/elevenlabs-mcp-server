<script lang="ts">
    import AudioPlayer from '$lib/components/AudioPlayer.svelte';
    import DebugInfo from '$lib/components/DebugInfo.svelte';
    import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
    import type { AudioGenerationResponse, ScriptPart } from '$lib/elevenlabs/client';

    let scriptParts: ScriptPart[] = [{ text: '', voice_id: '', actor: '' }];
    let loading = false;
    let result: AudioGenerationResponse | null = null;

    function addPart() {
        scriptParts = [...scriptParts, { text: '', voice_id: '', actor: '' }];
    }

    function removePart(index: number) {
        scriptParts = scriptParts.filter((_, i) => i !== index);
    }

    async function generateAudio() {
        if (scriptParts.length === 0 || scriptParts.every(part => !part.text)) return;
        
        loading = true;
        result = null;
        
        try {
            const response = await fetch('/api/tts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    type: 'script',
                    script: { script: scriptParts }
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
    <h1>Multi-part Script to Speech</h1>
    
    <form on:submit|preventDefault={generateAudio} class="script-form">
        {#each scriptParts as part, i}
            <div class="script-part">
                <div class="part-header">
                    <h3>Part {i + 1}</h3>
                    {#if scriptParts.length > 1}
                        <button 
                            type="button" 
                            class="remove-button"
                            on:click={() => removePart(i)}
                            aria-label="Remove part"
                        >
                            ✕
                        </button>
                    {/if}
                </div>
                
                <div class="form-group">
                    <label for="text-{i}">Text</label>
                    <textarea
                        id="text-{i}"
                        bind:value={part.text}
                        placeholder="Enter text for this part..."
                        rows="3"
                        required
                    ></textarea>
                </div>
                
                <div class="part-details">
                    <div class="form-group">
                        <label for="voice-{i}">Voice ID</label>
                        <input
                            id="voice-{i}"
                            type="text"
                            bind:value={part.voice_id}
                            placeholder="Enter voice ID..."
                        />
                    </div>
                    
                    <div class="form-group">
                        <label for="actor-{i}">Actor Name</label>
                        <input
                            id="actor-{i}"
                            type="text"
                            bind:value={part.actor}
                            placeholder="Enter actor name..."
                        />
                    </div>
                </div>
            </div>
        {/each}
        
        <div class="form-actions">
            <button 
                type="button" 
                class="secondary-button"
                on:click={addPart}
            >
                Add Part
            </button>
            
            <button 
                type="submit" 
                class="primary-button"
                disabled={loading || scriptParts.every(part => !part.text)}
            >
                {#if loading}
                    <LoadingSpinner size={16} />
                    Generating...
                {:else}
                    Generate Audio
                {/if}
            </button>
        </div>
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
    
    .script-form {
        display: flex;
        flex-direction: column;
        gap: 2rem;
        margin-bottom: 2rem;
    }
    
    .script-part {
        padding: 1.5rem;
        background: #f9f9f9;
        border: 1px solid #eee;
        border-radius: 0.5rem;
    }
    
    .part-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    h3 {
        margin: 0;
        color: #444;
    }
    
    .remove-button {
        padding: 0.25rem 0.5rem;
        background: #fee2e2;
        color: #dc2626;
        border: none;
        border-radius: 0.25rem;
        cursor: pointer;
        font-size: 0.875rem;
    }
    
    .remove-button:hover {
        background: #fecaca;
    }
    
    .form-group {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .part-details {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
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
        background: white;
    }
    
    textarea:focus, input:focus {
        outline: none;
        border-color: #666;
    }
    
    .form-actions {
        display: flex;
        gap: 1rem;
        justify-content: flex-end;
    }
    
    button {
        padding: 0.75rem 1.5rem;
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
    
    .primary-button {
        background: #0066cc;
        color: white;
    }
    
    .secondary-button {
        background: #e5e7eb;
        color: #374151;
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
