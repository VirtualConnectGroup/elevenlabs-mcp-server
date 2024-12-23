<script lang="ts">
  import { onMount } from 'svelte';
  import type { JobHistory } from '$lib/client';

  let jobs: JobHistory[] = [];
  let loading = true;
  let error: string | null = null;

  async function loadJobs() {
    try {
      loading = true;
      error = null;
      const response = await fetch('/api/history');
      if (!response.ok) {
        throw new Error('Failed to load job history');
      }
      jobs = await response.json();
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to load job history';
    } finally {
      loading = false;
    }
  }

  async function deleteJob(jobId: string) {
    if (!confirm('Are you sure you want to delete this job?')) {
      return;
    }

    try {
      const response = await fetch(`/api/history?id=${jobId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        jobs = jobs.filter(job => job.id !== jobId);
      } else {
        const data = await response.json();
        error = data.error || 'Failed to delete job';
      }
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to delete job';
    }
  }

  function formatDate(dateStr: string) {
    return new Date(dateStr).toLocaleString();
  }

  function getStatusColor(status: string) {
    switch (status) {
      case 'completed':
        return 'text-green-600';
      case 'failed':
        return 'text-red-600';
      case 'processing':
        return 'text-blue-600';
      default:
        return 'text-gray-600';
    }
  }

  onMount(() => {
    loadJobs();
  });
</script>

<main>
  <h2>Voiceover History</h2>
  <p class="page-description">View and manage your previously generated voiceover jobs.</p>

  {#if error}
    <div class="error">
      {error}
    </div>
  {/if}

  {#if loading}
    <div class="loading-container">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
    </div>
  {:else if jobs.length === 0}
    <div class="empty-state">
      No voiceover jobs found
    </div>
  {:else}
    <div class="history-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Status</th>
            <th>Created</th>
            <th>Progress</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {#each jobs as job}
            <tr class="result-row">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {job.id.slice(0, 8)}...
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <span class={getStatusColor(job.status)}>
                  {job.status}
                </span>
                {#if job.error}
                  <span class="text-red-600 text-xs block">
                    {job.error}
                  </span>
                {/if}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {formatDate(job.created_at)}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {job.completed_parts} / {job.total_parts} parts
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <div class="actions">
                  <button
                    on:click={() => deleteJob(job.id)}
                    class="button button-danger"
                  >
                    Delete
                  </button>
                  {#if job.output_file}
                    <a
                      href={`/api/download?id=${job.id}`}
                      download={`voiceover-${job.id}.mp3`}
                      class="button button-primary"
                    >
                      Download
                    </a>
                  {/if}
                </div>
              </td>
            </tr>
            <tr class="script-row">
              <td colspan="5">
                <div class="script-content">
                  <strong>Script:</strong>
                  {#each job.script_parts as part}
                    <div class="script-part">
                      {#if part.actor}
                        <span class="actor">{part.actor}:</span>
                      {/if}
                      {part.text}
                      {#if part.voice_id}
                        <span class="voice-id">(Voice: {part.voice_id})</span>
                      {/if}
                    </div>
                  {/each}
                </div>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</main>

<style>
  main {
    max-width: 800px;
    margin: 0 auto;
    padding: var(--spacing-8);
  }

  h2 {
    margin-bottom: var(--spacing-2);
    color: var(--color-text);
    font-size: var(--font-size-2xl);
    text-align: center;
  }

  .page-description {
    text-align: center;
    color: var(--color-text-light);
    margin-bottom: var(--spacing-8);
  }

  .loading-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 8rem;
  }

  .empty-state {
    text-align: center;
    color: var(--color-text-light);
    padding: var(--spacing-8);
  }

  .error {
    color: var(--color-error);
    padding: var(--spacing-4);
    background: #fef2f2;
    border: 1px solid #fee2e2;
    border-radius: var(--border-radius-base);
    margin-bottom: var(--spacing-4);
  }

  .history-table {
    background: var(--color-surface);
    padding: var(--spacing-6);
    border-radius: var(--border-radius-lg);
    box-shadow: var(--shadow-base);
    overflow-x: auto;
  }

  table {
    width: 100%;
    border-collapse: collapse;
  }

  th {
    text-align: left;
    padding: var(--spacing-4) var(--spacing-6);
    font-size: var(--font-size-sm);
    font-weight: 500;
    color: var(--color-text-light);
    background: var(--color-background);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  td {
    padding: var(--spacing-4) var(--spacing-6);
    font-size: var(--font-size-sm);
    color: var(--color-text);
    border-bottom: 1px solid var(--border-color);
  }

  .result-row:hover {
    background: var(--color-background);
  }

  .script-row td {
    background: var(--color-background);
    border-bottom: 1px solid var(--border-color);
  }

  .script-content {
    padding: var(--spacing-2) 0;
  }

  .script-part {
    margin: var(--spacing-2) 0;
    padding-left: var(--spacing-4);
  }

  .actor {
    color: var(--color-primary);
    font-weight: 500;
    margin-right: var(--spacing-2);
  }

  .voice-id {
    color: var(--color-text-light);
    font-size: var(--font-size-xs);
    margin-left: var(--spacing-2);
  }

  .actions {
    display: flex;
    gap: var(--spacing-2);
    align-items: center;
  }

  .button {
    padding: var(--spacing-1) var(--spacing-3);
    border: none;
    border-radius: var(--border-radius-base);
    font-size: var(--font-size-sm);
    font-weight: 500;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    transition: all var(--transition-base);
    min-width: 70px;
  }

  .button:hover {
    transform: translateY(-1px);
    opacity: 0.9;
  }

  .button-primary {
    background: var(--color-primary);
    color: var(--color-surface);
  }

  .button-danger {
    background: var(--color-error);
    color: var(--color-surface);
  }

  @media (max-width: 640px) {
    main {
      padding: var(--spacing-4);
    }

    h2 {
      font-size: var(--font-size-xl);
      margin-bottom: var(--spacing-2);
    }

    .page-description {
      font-size: var(--font-size-sm);
      margin-bottom: var(--spacing-6);
    }

    .history-table {
      padding: var(--spacing-2);
    }

    th, td {
      padding: var(--spacing-3) var(--spacing-4);
    }
  }
</style>
