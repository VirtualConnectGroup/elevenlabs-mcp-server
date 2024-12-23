<script lang="ts">
    import { page } from '$app/stores';
</script>

<div class="layout">
    <nav>
        <a 
            href="/" 
            class="nav-link" 
            class:active={$page.url.pathname === '/'}
        >
            Simple TTS
        </a>
        <a 
            href="/script" 
            class="nav-link" 
            class:active={$page.url.pathname === '/script'}
        >
            Script TTS
        </a>
    </nav>

    <slot />
</div>

<style>
    .layout {
        min-height: 100vh;
        background: #f8fafc;
    }

    nav {
        background: white;
        padding: 1rem;
        border-bottom: 1px solid #e2e8f0;
        display: flex;
        gap: 1rem;
        justify-content: center;
    }

    .nav-link {
        padding: 0.5rem 1rem;
        color: #64748b;
        text-decoration: none;
        border-radius: 0.5rem;
        transition: all 0.2s;
    }

    .nav-link:hover {
        background: #f1f5f9;
        color: #0f172a;
    }

    .nav-link.active {
        background: #e2e8f0;
        color: #0f172a;
        font-weight: 500;
    }
</style>
