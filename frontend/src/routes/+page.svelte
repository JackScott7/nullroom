<script lang="ts">
    let username = $state("");
    let notification = $state({ message: "", success: false });
    let loading = $state(false);

    function showNotification(message: string, success: boolean) {
        notification = { message, success };
    }

    function hideNotification() {
        notification = { message: "", success: false };
    }

    async function handleEnter() {
        const trimmed = username.trim();

        if (!trimmed) {
            showNotification("Please enter a username to continue.", false);
            return;
        }
        if (trimmed.length < 3) {
            showNotification("Username must be at least 3 characters.", false);
            return;
        }

        loading = true;
        try {
            const request = await fetch(
                "http://127.0.0.1:8000/api/userAvailable",
                {
                    method: "POST",
                    headers: {
                        Accept: "application/json",
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ username: trimmed }),
                },
            );

            if (!request.ok) {
                if (request.status === 409) {
                    showNotification(
                        "Username is already taken. Please try another.",
                        false,
                    );
                } else {
                    showNotification("Something went wrong. Try again.", false);
                }
                return;
            }

            const response = await request.json();
            if (response.status === "available") {
                const ws = new WebSocket(
                    `ws://127.0.0.1:8000/api/ws/${trimmed}`,
                );
                showNotification(`Welcome, ${trimmed}! Redirecting...`, true);
                setTimeout(() => {
                    window.location.href = "/rooms";
                }, 1500);
            }
        } catch {
            showNotification("Network error. Please try again.", false);
        } finally {
            loading = false;
        }
    }
</script>

<svelte:head>
    <title>Nullroom - Sign Up</title>
</svelte:head>

<div
    class="flex min-h-screen items-center justify-center bg-bg-primary px-4 font-[Inter,_-apple-system,_BlinkMacSystemFont,_'Segoe_UI',_sans-serif] text-text-primary"
>
    <div class="w-full max-w-sm">
        <!-- Logo -->
        <div class="mb-8 text-center">
            <h1 class="text-5xl font-bold tracking-tight">
                Null<span class="text-accent">room</span>
            </h1>
        </div>

        <!-- Card -->
        <div class="rounded-xl border border-border bg-bg-secondary p-8">
            <!-- Notification -->
            {#if notification.message}
                <div
                    class="mb-6 rounded-lg border p-3 text-center text-sm font-medium {notification.success
                        ? 'border-[#3fb950] bg-[#04260f] text-[#3fb950]'
                        : 'border-[#f85149] bg-[#490202] text-[#f85149]'}"
                >
                    {notification.message}
                </div>
            {/if}

            <!-- Form -->
            <div class="mb-6">
                <label
                    for="username"
                    class="mb-2 block text-xs font-medium uppercase tracking-wider text-text-secondary"
                >
                    Username
                </label>
                <input
                    id="username"
                    type="text"
                    bind:value={username}
                    placeholder="Enter your username"
                    autocomplete="off"
                    class="w-full rounded-lg border border-border bg-bg-primary px-4 py-3 text-text-primary outline-none transition placeholder:text-text-secondary/70 focus:border-accent focus:shadow-[0_0_0_3px_rgba(88,166,255,0.15)]"
                    onkeypress={(e) => e.key === "Enter" && handleEnter()}
                    oninput={hideNotification}
                />
            </div>

            <button
                class="w-full rounded-lg bg-accent py-3 text-sm font-semibold uppercase tracking-wider text-white transition hover:bg-accent-hover active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60"
                onclick={handleEnter}
                disabled={loading}
            >
                {loading ? "Checking..." : "Enter Room"}
            </button>
        </div>

        <!-- Footer text -->
        <p class="mt-6 text-center text-xs text-text-secondary">
            Disposable chats. Nothing stored. Nothing tracked.
        </p>
    </div>
</div>
