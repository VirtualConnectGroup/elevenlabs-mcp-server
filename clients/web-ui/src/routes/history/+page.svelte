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

<div class="container mx-auto px-4 py-8">
  <h1 class="text-3xl font-bold mb-6">Voiceover History</h1>

  {#if error}
    <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
      {error}
    </div>
  {/if}

  {#if loading}
    <div class="flex justify-center items-center h-32">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
    </div>
  {:else if jobs.length === 0}
    <div class="text-center text-gray-600 py-8">
      No voiceover jobs found
    </div>
  {:else}
    <div class="bg-white shadow-md rounded-lg overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              ID
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Created
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Progress
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          {#each jobs as job}
            <tr>
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
                <button
                  on:click={() => deleteJob(job.id)}
                  class="text-red-600 hover:text-red-900"
                >
                  Delete
                </button>
                {#if job.output_file}
                  <a
                    href={job.output_file}
                    target="_blank"
                    rel="noopener noreferrer"
                    class="ml-4 text-blue-600 hover:text-blue-900"
                  >
                    Download
                  </a>
                {/if}
              </td>
            </tr>
            <tr>
              <td colspan="5" class="px-6 py-4">
                <div class="text-sm text-gray-900">
                  <strong>Script:</strong>
                  {#each job.script_parts as part}
                    <div class="mt-1 pl-4">
                      {#if part.actor}
                        <span class="text-blue-600">{part.actor}:</span>
                      {/if}
                      {part.text}
                      {#if part.voice_id}
                        <span class="text-gray-500 text-xs">(Voice: {part.voice_id})</span>
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
</div>
