<script lang="ts">
    import { onMount } from "svelte";

    interface Game {
        id: number;
        title: string;
        description: string;
        publisher?: { id: number; name: string };
        category?: { id: number; name: string };
        starRating?: number;
    }

    interface PaginationData {
        data: Game[];
        page: number;
        per_page: number;
        total: number;
        total_pages: number;
    }

    export let games: Game[] = [];
    let loading = true;
    let error: string | null = null;
    let currentPage = 1;
    let totalPages = 1;
    let total = 0;
    let perPage = 20;
    let goToPageInput = '';

    const fetchGames = async (page: number = 1) => {
        loading = true;
        try {
            const response = await fetch(`/api/games?page=${page}&per_page=${perPage}`);
            if(response.ok) {
                const data: PaginationData = await response.json();
                games = data.data;
                currentPage = data.page;
                totalPages = data.total_pages;
                total = data.total;
                perPage = data.per_page;
                
                // Update URL without reload
                const url = new URL(window.location.href);
                if (page === 1) {
                    url.searchParams.delete('page');
                } else {
                    url.searchParams.set('page', page.toString());
                }
                window.history.replaceState({}, '', url.toString());
            } else {
                error = `Failed to fetch data: ${response.status} ${response.statusText}`;
            }
        } catch (err) {
            error = `Error: ${err instanceof Error ? err.message : String(err)}`;
        } finally {
            loading = false;
        }
    };

    const goToPreviousPage = () => {
        if (currentPage > 1) {
            fetchGames(currentPage - 1);
        }
    };

    const goToNextPage = () => {
        if (currentPage < totalPages) {
            fetchGames(currentPage + 1);
        }
    };

    const goToPage = (page: number) => {
        if (page >= 1 && page <= totalPages) {
            fetchGames(page);
        }
    };

    const handleGoToPageSubmit = () => {
        const pageNum = parseInt(goToPageInput);
        if (pageNum && pageNum >= 1 && pageNum <= totalPages) {
            goToPage(pageNum);
            goToPageInput = '';
        }
    };

    const handleGoToPageKeydown = (event: KeyboardEvent) => {
        if (event.key === 'Enter') {
            handleGoToPageSubmit();
        }
    };

    onMount(() => {
        // Check URL for page parameter
        const urlParams = new URLSearchParams(window.location.search);
        const pageParam = urlParams.get('page');
        const initialPage = pageParam ? parseInt(pageParam) : 1;
        fetchGames(initialPage);
    });
</script>

<div>
    <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-medium text-slate-100">Featured Games</h2>
        {#if !loading && !error && total > 0}
            <div class="text-sm text-slate-400">
                Showing {((currentPage - 1) * perPage) + 1}-{Math.min(currentPage * perPage, total)} of {total} games
            </div>
        {/if}
    </div>
    
    {#if loading}
        <!-- loading animation -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each Array(6) as _, i}
                <div class="bg-slate-800/60 backdrop-blur-sm rounded-xl overflow-hidden shadow-lg border border-slate-700/50">
                    <div class="p-6">
                        <div class="animate-pulse">
                            <div class="h-6 bg-slate-700 rounded w-3/4 mb-3"></div>
                            <div class="h-4 bg-slate-700 rounded w-1/2 mb-4"></div>
                            <div class="h-3 bg-slate-700 rounded w-full mb-3"></div>
                            <div class="h-3 bg-slate-700 rounded w-5/6 mb-4"></div>
                            <div class="h-2 bg-slate-700 rounded-full w-full mb-2"></div>
                            <div class="h-4 bg-slate-700 rounded w-1/4 mt-4"></div>
                        </div>
                    </div>
                </div>
            {/each}
        </div>
    {:else if error}
        <!-- error display -->
        <div class="text-center py-12 bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700">
            <p class="text-red-400">{error}</p>
        </div>
    {:else if games.length === 0}
        <!-- no games found -->
        <div class="text-center py-12 bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700">
            <p class="text-slate-300">No games available at the moment.</p>
        </div>
    {:else}
        <!-- game list -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6" data-testid="games-grid">
            {#each games as game (game.id)}
                <a 
                    href={`/game/${game.id}`} 
                    class="group block bg-slate-800/60 backdrop-blur-sm rounded-xl overflow-hidden shadow-lg border border-slate-700/50 hover:border-blue-500/50 hover:shadow-blue-500/10 hover:shadow-xl transition-all duration-300 hover:translate-y-[-6px]"
                    data-testid="game-card"
                    data-game-id={game.id}
                    data-game-title={game.title}
                >
                    <div class="p-6 relative">
                        <div class="absolute inset-0 bg-gradient-to-r from-blue-600/10 to-purple-600/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                        <div class="relative z-10">
                            <h3 class="text-xl font-semibold text-slate-100 mb-2 group-hover:text-blue-400 transition-colors" data-testid="game-title">{game.title}</h3>
                            
                            {#if game.category || game.publisher}
                                <div class="flex gap-2 mb-3">
                                    {#if game.category}
                                        <span class="text-xs font-medium px-2.5 py-0.5 rounded bg-blue-900/60 text-blue-300" data-testid="game-category">
                                            {game.category.name}
                                        </span>
                                    {/if}
                                    {#if game.publisher}
                                        <span class="text-xs font-medium px-2.5 py-0.5 rounded bg-purple-900/60 text-purple-300" data-testid="game-publisher">
                                            {game.publisher.name}
                                        </span>
                                    {/if}
                                </div>
                            {/if}
                            
                            <p class="text-slate-400 mb-4 text-sm line-clamp-2" data-testid="game-description">{game.description}</p>
                            
                            <div class="mt-4 text-sm text-blue-400 font-medium flex items-center">
                                <span>View details</span>
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1 transform transition-transform duration-300 group-hover:translate-x-2" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M12.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-2.293-2.293a1 1 0 010-1.414z" clip-rule="evenodd" />
                                </svg>
                            </div>
                        </div>
                    </div>
                </a>
            {/each}
        </div>

        <!-- Pagination Controls -->
        {#if totalPages > 1}
            <div class="mt-8 flex flex-col sm:flex-row justify-between items-center gap-4" data-testid="pagination-controls">
                <!-- Previous/Next buttons and page info -->
                <div class="flex items-center gap-4">
                    <button 
                        on:click={goToPreviousPage}
                        disabled={currentPage === 1}
                        class="flex items-center px-4 py-2 rounded-lg bg-slate-800/60 border border-slate-700 text-slate-300 hover:bg-slate-700/60 hover:border-blue-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-slate-800/60 disabled:hover:border-slate-700"
                        aria-label="Go to previous page"
                        data-testid="prev-page-button"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M7.707 14.707a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l2.293 2.293a1 1 0 010 1.414z" clip-rule="evenodd" />
                        </svg>
                        Previous
                    </button>

                    <span class="text-slate-400 text-sm" data-testid="page-info">
                        Page {currentPage} of {totalPages}
                    </span>

                    <button 
                        on:click={goToNextPage}
                        disabled={currentPage === totalPages}
                        class="flex items-center px-4 py-2 rounded-lg bg-slate-800/60 border border-slate-700 text-slate-300 hover:bg-slate-700/60 hover:border-blue-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-slate-800/60 disabled:hover:border-slate-700"
                        aria-label="Go to next page"
                        data-testid="next-page-button"
                    >
                        Next
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-2" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M12.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-2.293-2.293a1 1 0 010-1.414z" clip-rule="evenodd" />
                        </svg>
                    </button>
                </div>

                <!-- Page number navigation -->
                <div class="flex items-center gap-2">
                    <!-- Go to page input -->
                    <div class="flex items-center gap-2">
                        <label for="go-to-page" class="text-sm text-slate-400">Go to:</label>
                        <input 
                            id="go-to-page"
                            type="number" 
                            min="1" 
                            max={totalPages}
                            bind:value={goToPageInput}
                            on:keydown={handleGoToPageKeydown}
                            placeholder="Page"
                            class="w-16 px-2 py-1 rounded bg-slate-800/60 border border-slate-700 text-slate-300 text-sm focus:border-blue-500/50 focus:outline-none"
                            aria-label="Go to page number"
                            data-testid="goto-page-input"
                        />
                        <button 
                            on:click={handleGoToPageSubmit}
                            class="px-3 py-1 text-sm rounded bg-blue-600/80 hover:bg-blue-600 text-white transition-colors"
                            aria-label="Go to specified page"
                            data-testid="goto-page-button"
                        >
                            Go
                        </button>
                    </div>

                    <!-- Page number buttons for nearby pages -->
                    <div class="flex items-center gap-1 ml-4">
                        {#each Array(Math.min(5, totalPages)) as _, index}
                            {@const pageNum = Math.max(1, Math.min(totalPages - 4, currentPage - 2)) + index}
                            {#if pageNum <= totalPages}
                                <button 
                                    on:click={() => goToPage(pageNum)}
                                    class="w-8 h-8 rounded text-sm transition-all {pageNum === currentPage ? 'bg-blue-600 text-white' : 'bg-slate-800/60 border border-slate-700 text-slate-300 hover:bg-slate-700/60 hover:border-blue-500/50'}"
                                    aria-label="Go to page {pageNum}"
                                    aria-current={pageNum === currentPage ? 'page' : undefined}
                                    data-testid="page-number-button"
                                    data-page={pageNum}
                                >
                                    {pageNum}
                                </button>
                            {/if}
                        {/each}
                    </div>
                </div>
            </div>
        {/if}
    {/if}
</div>