<script lang="ts">
    import { onMount } from "svelte";
    import {
        wsConnect,
        wsGetPublicRooms,
        wsSendNameColor,
        publicRooms,
        wsCreateRoom,
        createdRoom,

        wsJoinRoom

    } from "$lib/stores/websocket";
    import { goto } from "$app/navigation";


    let user: string = $state("");

    const nameColors = [
        "#f87171",
        "#fb923c",
        "#facc15",
        "#4ade80",
        "#2dd4bf",
        "#60a5fa",
        "#a78bfa",
        "#f472b6",
    ];
    let selectedColor = $state(nameColors[0]);

    let showModal = $state(false);
    let roomName = $state("");
    let maxClients = $state(8);
    let visibility = $state("");

    function openModal() {
        showModal = true;
    }

    function closeModal() {
        showModal = false;
    }

    function generateRandomName() {
        const adjectives = [
            "silent",
            "frosty",
            "crimson",
            "hidden",
            "azure",
            "ember",
            "twilight",
            "quantum",
        ];
        const nouns = [
            "forest",
            "nebula",
            "cipher",
            "haven",
            "vault",
            "echo",
            "drift",
            "node",
        ];
        const adj = adjectives[Math.floor(Math.random() * adjectives.length)];
        const noun = nouns[Math.floor(Math.random() * nouns.length)];
        roomName = `${adj}-${noun}`;
    }

    // function validateUserConnectivity() {
    //     const user = localStorage.getItem("nr_username");
    //     if (!user) {
    //         console.error("username is empty, new login required");
    //         location.href = "/";
    //         localStorage.removeItem("nr_username");
    //         return;
    //     }
    // }

    async function handleCreateRoom() {
        if (roomName.trim().length < 4) {
            alert("Room name must be at least 4 characters.");
            return;
        }

        wsCreateRoom(user, roomName, maxClients, visibility);

        closeModal();
    }

    // Close modal on Escape key
    function handleKeydown(e: KeyboardEvent) {
        if (e.key === "Escape" && showModal) {
            closeModal();
        }
    }

    function selectNameColor(color: string) {
        selectedColor = color;
        wsSendNameColor(user, color);
    }

    function joinSingleRoom(roomId: string) {
        wsJoinRoom(roomId);
    }

    $effect(() => {
        const room = $createdRoom;
        if (room) {
            goto(`/room/${room.roomId}`);
            createdRoom.set(null);
        }
    });

    onMount(() => {
        user = localStorage.getItem("nr_username") || "";
        if (!user) {
            location.href = "/";
            return;
        }
        wsConnect(user);
        wsGetPublicRooms(user);
    });
</script>

<svelte:head>
    <title>Nullroom - Rooms</title>
</svelte:head>

<svelte:window on:keydown={handleKeydown} />

<div
    class="min-h-screen bg-bg-primary text-text-primary font-[Inter,_-apple-system,_BlinkMacSystemFont,_'Segoe_UI',_sans-serif]"
>
    <!-- ========== Top Navbar ========== -->
    <nav
        class="fixed top-0 z-40 flex w-full items-center justify-between border-b border-border bg-bg-secondary/80 px-6 py-4 backdrop-blur-md"
    >
        <a href="/" class="text-xl font-bold tracking-tight">
            Null<span class="text-accent">room</span>
        </a>
        <a
            href="/about"
            class="text-sm text-text-secondary transition hover:text-accent"
            >About</a
        >
    </nav>

    <!-- ========== Main layout ========== -->
    <div class="flex h-screen pt-[65px]">
        <!-- Left: scrollable room list -->
        <main class="flex-1 overflow-y-auto px-6 pb-12">
            <h2 class="mb-6 mt-6 text-2xl font-semibold">Public Rooms - Join any room by clicking on it</h2>
            <div
                class="grid grid-cols-2 gap-6 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5"
            >
                {#each $publicRooms as room (room.roomId)}
                <a href="/join-room/{room.roomId}">
                    <div
                        class="relative flex h-48 flex-col justify-between rounded-xl border border-border bg-bg-secondary p-5 transition hover:border-accent"
                    >
                        <span
                            class="text-sm font-medium text-text-primary"
                            >{room.name}</span
                        >
                        <div
                            class="flex items-center gap-1.5 text-text-secondary"
                        >
                            <svg
                                class="h-4 w-4"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="2"
                                viewBox="0 0 24 24"
                            >
                                <path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z"
                                />
                            </svg>
                            <span class="text-sm">{room.users.length} / {room.maxClients}</span>
                        </div>
                    </div>
                </a>
                {/each}
            </div>
        </main>

        <!-- Right: floating sidebar -->
        <aside
            class="w-72 border-l border-border bg-bg-secondary/50 p-6 flex flex-col gap-8"
        >
            <!-- Create Room button -->
            <button
                onclick={openModal}
                class="flex w-full items-center justify-center gap-2 rounded-lg bg-accent px-4 py-3 text-sm font-medium text-white transition hover:bg-accent-hover active:scale-[0.98]"
            >
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-5 w-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    stroke-width="2"
                >
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        d="M12 4v16m8-8H4"
                    />
                </svg>
                Create Room
            </button>

            <!-- Name color picker -->
            <div>
                <label
                    class="mb-3 block text-xs font-semibold uppercase tracking-wider text-text-secondary"
                >
                    Select your name color
                </label>
                <div class="grid grid-cols-4 gap-3">
                    {#each nameColors as color}
                        <button
                            class="h-8 w-8 rounded-full border-2 transition {color ===
                            selectedColor
                                ? 'border-white scale-110 shadow-lg'
                                : 'border-transparent hover:scale-105'}"
                            style="background-color: {color};"
                            onclick={() => selectNameColor(color)}
                            aria-label="Select color {color}"
                        ></button>
                    {/each}
                </div>
            </div>
        </aside>
    </div>

    <!-- ========== Create Room Modal ========== -->
    {#if showModal}
        <!-- Backdrop -->
        <button
            class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm"
            onclick={closeModal}
            aria-label="Close modal"
        ></button>

        <!-- Modal container -->
        <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div
                class="w-full max-w-md rounded-xl border border-border bg-bg-secondary p-6 shadow-2xl"
            >
                <h3 class="mb-6 text-xl font-semibold text-text-primary">
                    Create New Room
                </h3>

                <!-- Room Name -->
                <div class="mb-4">
                    <label
                        for="roomName"
                        class="mb-2 block text-xs font-medium uppercase tracking-wider text-text-secondary"
                    >
                        Room Name
                    </label>
                    <div class="flex gap-2">
                        <input
                            id="roomName"
                            type="text"
                            bind:value={roomName}
                            placeholder="e.g., chill-lounge"
                            class="flex-1 rounded-lg border border-border bg-bg-primary px-4 py-3 text-text-primary outline-none placeholder:text-text-secondary/70 focus:border-accent focus:shadow-[0_0_0_3px_rgba(88,166,255,0.15)]"
                        />
                        <button
                            onclick={generateRandomName}
                            class="rounded-lg border border-border bg-bg-primary px-4 py-3 text-sm font-medium text-text-secondary transition hover:text-accent hover:border-accent"
                            title="Generate random name"
                        >
                            🎲
                        </button>
                    </div>
                </div>

                <!-- Max Clients -->
                <div class="mb-4">
                    <label
                        for="maxClients"
                        class="mb-2 block text-xs font-medium uppercase tracking-wider text-text-secondary"
                    >
                        Max Clients: {maxClients}
                    </label>
                    <input
                        id="maxClients"
                        type="range"
                        min="2"
                        max="16"
                        bind:value={maxClients}
                        class="w-full accent-accent"
                    />
                    <div
                        class="flex justify-between text-xs text-text-secondary mt-1"
                    >
                        <span>2</span>
                        <span>16</span>
                    </div>
                </div>

                <!-- Visibility -->
                <div class="mb-6">
                    <span
                        class="mb-2 block text-xs font-medium uppercase tracking-wider text-text-secondary"
                        >Visibility</span
                    >
                    <div class="flex gap-3">
                        <button
                            onclick={() => (visibility = "public")}
                            class="flex-1 rounded-lg px-4 py-3 text-sm font-medium transition {visibility
                                ? 'bg-accent text-white'
                                : 'bg-bg-primary text-text-secondary border border-border hover:border-accent'}"
                        >
                            Public
                        </button>
                        <button
                            onclick={() => (visibility = "private")}
                            class="flex-1 rounded-lg px-4 py-3 text-sm font-medium transition {!visibility
                                ? 'bg-accent text-white'
                                : 'bg-bg-primary text-text-secondary border border-border hover:border-accent'}"
                        >
                            Private
                        </button>
                    </div>
                </div>

                <!-- Action buttons -->
                <div class="flex gap-3">
                    <button
                        onclick={closeModal}
                        class="flex-1 rounded-lg border border-border px-4 py-3 text-sm font-medium text-text-secondary transition hover:bg-bg-primary"
                    >
                        Cancel
                    </button>
                    <button
                        onclick={handleCreateRoom}
                        class="flex-1 rounded-lg bg-accent px-4 py-3 text-sm font-medium text-white transition hover:bg-accent-hover active:scale-[0.98]"
                    >
                        Create
                    </button>
                </div>
            </div>
        </div>
    {/if}
</div>
