<script lang="ts">
    import { page } from "$app/state";
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import { wsConnect, wsJoinRoom, currentRoom } from "$lib/stores/websocket";

    const roomId = page.params.room_id;
    let currentUser = $state("");

    let loading = $state(true);
    let success = $state(false);
    let error = $state("");
    let room = $derived(currentRoom);

    async function fetchRoomInfo() {
        try {
            wsJoinRoom(roomId!);
            // const res = await fetch(
            //     `http://127.0.0.1:8000/api/room/${roomId}`,
            // );
            // if (!res.ok) {
            //     error = "Room not found or expired.";
            //     return;
            // }
            // const data = await res.json();
            // room = data.data;

            // const username = localStorage.getItem("nr_username") || "";

            // if (!username) {
            //     error = "Please Signup first";
            //     setTimeout(() => {
            //         goto(`/?redirectUrl=/room/${roomId}`);
            //     }, 2000);
            //     return
            // }

            // const joinRes = await fetch(
            //     `http://127.0.0.1:8000/api/join-room/${roomId}`,
            //     {
            //         method: "POST",
            //         headers: { "Content-Type": "application/json" },
            //         body: JSON.stringify({ username }),
            //     },
            // );

            // if (!joinRes.ok) {
            //     error = "Failed to join room. It may be full.";
            //     return;
            // }

            success = true;
            setTimeout(() => {
                goto(`/room/${roomId}`);
            }, 500);

        } catch (e) {
            error = "Network error. Please try again.";
        } finally {
            loading = false;
        }
    }

    onMount(() => {
        const stored = localStorage.getItem("nr_username");
        if (!stored) {
            window.location.href = "/";
            return;
        }
        currentUser = stored;
        wsConnect(currentUser);
        fetchRoomInfo();
    });
</script>

<svelte:head>
    <title>Nullroom - Joining Room</title>
</svelte:head>

<div
    class="flex h-screen items-center justify-center bg-bg-primary font-[Inter,_-apple-system,_BlinkMacSystemFont,_'Segoe_UI',_sans-serif] text-text-primary"
>
    <div class="text-center">
        {#if loading}
            <!-- Spinner -->
            <div
                class="mx-auto mb-6 h-12 w-12 animate-spin rounded-full border-4 border-border border-t-accent"
            ></div>
            <p class="text-lg">Joining the room...</p>
        {:else if error}
            <div
                class="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full border-2 border-red-500"
            >
                <svg
                    class="h-6 w-6 text-red-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M6 18L18 6M6 6l12 12"
                    />
                </svg>
            </div>
            <p class="text-red-400">{error}</p>
            <button
                onclick={() => (window.location.href = "/rooms")}
                class="mt-4 rounded-lg bg-accent px-4 py-2 text-sm text-white hover:bg-accent-hover"
            >
                Back to Rooms
            </button>
        {:else if success}
            <!-- Success checkmark -->
            <div
                class="mx-auto mb-6 flex h-12 w-12 items-center justify-center rounded-full bg-green-500/20"
            >
                <svg
                    class="h-6 w-6 text-green-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    stroke-width="2"
                >
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        d="M5 13l4 4L19 7"
                    />
                </svg>
            </div>
            <h2 class="text-2xl font-semibold">Joined</h2>
        {:else}
            <!-- Room info and joining animation -->
            {#if room}
                <div class="mb-6">
                    <h2 class="text-2xl font-semibold">{$room?.name}</h2>
                    <p class="text-text-secondary">
                        {$room?.users.length} / {$room?.maxClients} users connected
                    </p>
                </div>
                <div
                    class="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-4 border-border border-t-accent"
                ></div>
                <p class="text-lg">Joining...</p>
            {/if}
        {/if}
    </div>
</div>
