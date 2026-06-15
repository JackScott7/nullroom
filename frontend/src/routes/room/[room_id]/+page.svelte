<script lang="ts">
    import { page } from "$app/state";
    import { onMount } from "svelte";
    import {
        wsConnect,
        wsJoinRoom,
        currentRoom,
        users,
        messages,
        wsSendChatMessage,
        wsLeaveRoom,
        wsSendNameColor,
        joinRoomStatus
    } from "$lib/stores/websocket";
    import { goto } from "$app/navigation";
    import { setRandomNameColor } from "$lib";

    const roomId = page.params.room_id;
    let currentUser = $state("");
    let inputText = $state("");
    let copied = $state(false);
    let host = $derived($currentRoom?.host ?? "");
    let isHost = $derived(host === currentUser);
    let roomName = $derived($currentRoom?.name ?? "Loading...");
    let maxClients = $derived($currentRoom?.maxClients ?? 8);
    let userCount = $state(0);
    let visibility = $derived($currentRoom?.visibility ?? "public");
    let msgContainer: HTMLDivElement | undefined = $state();

    function copyInviteLink() {
        const link = `${window.location.origin}/join-room/${roomId}`;
        navigator.clipboard.writeText(link).then(() => {
            copied = true;
            setTimeout(() => (copied = false), 1000);
        });
    }

    async function sendMessage() {
        if (!inputText.trim()) return;
        wsSendChatMessage(inputText, roomId!, currentUser);
        inputText = "";
    }

    function leaveRoom() {
        wsLeaveRoom(roomId!);

        window.location.href = "/rooms";
    }

    function handleKeydown(e: KeyboardEvent) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    }

    $effect(() => {
        userCount = $users.length;
    });

    $effect(() => {
        $messages.length;
        if (msgContainer) {
            requestAnimationFrame(() => {
                msgContainer!.scrollTop = msgContainer!.scrollHeight;
            });
        }
    });

    $effect(() => {
        const status = $joinRoomStatus;

        if (status === "room_full" || status === "room_not_found") {
            currentRoom.set(null);
            window.location.href = "/rooms";
        }
    });

    onMount(async () => {
        // Retrieve logged-in user
        const stored = localStorage.getItem("nr_username");
        if (!stored) {
            goto("/");
            return;
        }
        currentUser = stored;

        wsConnect(currentUser);
        wsJoinRoom(roomId!);

        const nr_color = localStorage.getItem('nr_color');
        if (nr_color) {
            wsSendNameColor(currentUser, nr_color);
        }
        else {
            const color = setRandomNameColor();
            wsSendNameColor(currentUser, color);
        }
    });
</script>

<svelte:head>
    <title>Nullroom - {roomName !== "Loading..." ? roomName : "Chat"}</title>
</svelte:head>

<div
    class="flex h-screen flex-col bg-bg-primary font-[Inter,_-apple-system,_BlinkMacSystemFont,_'Segoe_UI',_sans-serif] text-text-primary"
>
    <!-- Minimal top bar -->
    <header
        class="flex items-center justify-between border-b border-border bg-bg-secondary/80 px-4 py-3 backdrop-blur-md"
    >
        <a href="/rooms" class="text-xl font-bold tracking-tight">
            Null<span class="text-accent">room</span>
        </a>
        <div class="text-sm text-text-secondary">
            Room: {roomName}
        </div>
        <div class="h-6 w-6"></div>
        <!-- spacer -->
    </header>

    <!-- Main content: chat + sidebar -->
    <div class="flex flex-1 overflow-hidden">
        <!-- Chat area -->
        <main class="flex flex-1 flex-col">
            <!-- Messages container -->
            <div
                bind:this={msgContainer}
                class="flex-1 overflow-y-auto p-4 space-y-3"
            >
                {#each $messages as msg}
                    <div class="flex items-start gap-3">
                        <!-- Person SVG – vertically centred outside the bubble -->
                        <div class="flex h-full items-center pt-1">
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="2"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                class="h-6 w-6 flex-shrink-0 text-text-secondary"
                            >
                                <path
                                    d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"
                                />
                                <circle cx="12" cy="7" r="4" />
                            </svg>
                        </div>

                        <!-- Rounded message bubble -->
                        <div
                            class="w-fit max-w-[80%] rounded-xl border border-border bg-bg-secondary px-4 py-3 shadow-sm"
                            style={`border: 2px solid ${msg.color}`}
                        >
                            <!-- Username – top left -->
                            <span
                                class="mb-1 block text-xs font-bold"
                                style="color: {msg.color};"
                            >
                                {msg.username}
                            </span>

                            <!-- Message text – middle, left aligned -->
                            <p
                                class="text-sm text-text-primary leading-relaxed"
                            >
                                {msg.text}
                            </p>

                            <!-- Time + ticks – bottom right -->
                            <div
                                class="mt-1.5 flex items-center justify-end gap-1.5 text-xs text-text-secondary"
                            >
                                <span>{msg.time}</span>
                                {#if msg.status === "sending"}
                                    <!-- Clock -->
                                    <svg
                                        class="h-3 w-3"
                                        fill="none"
                                        stroke="currentColor"
                                        viewBox="0 0 24 24"
                                        stroke-width="2"
                                    >
                                        <circle cx="12" cy="12" r="10" />
                                        <path d="M12 6v6l4 2" />
                                    </svg>
                                {:else if msg.status === "sent"}
                                    <!-- Double check -->
                                    <svg
                                        class="h-3 w-3 text-green-400"
                                        fill="none"
                                        stroke="currentColor"
                                        viewBox="0 0 24 24"
                                        stroke-width="2"
                                    >
                                        <path d="M20 6L9 17l-5-5" />
                                        <path d="M20 6l-10 7-1-1" />
                                    </svg>
                                {/if}
                            </div>
                        </div>
                    </div>
                {/each}
                {#if $messages.length === 0}
                    <p class="text-center text-text-secondary">
                        No messages yet. Say hello!
                    </p>
                {/if}
            </div>

            <!-- Input area -->
            <div class="border-t border-border bg-bg-secondary/50 p-4">
                <div class="flex gap-2">
                    <input
                        type="text"
                        bind:value={inputText}
                        placeholder="Type a message..."
                        spellcheck="true"
                        autocorrect="on"
                        autocapitalize="sentences"
                        class="flex-1 rounded-lg border border-border bg-bg-primary px-4 py-3 text-text-primary outline-none placeholder:text-text-secondary/70 focus:border-accent focus:shadow-[0_0_0_3px_rgba(88,166,255,0.15)]"
                        onkeydown={handleKeydown}
                    />
                    <button
                        onclick={sendMessage}
                        class="cursor-pointer rounded-lg bg-accent px-6 py-3 text-sm font-medium text-white transition hover:bg-accent-hover active:scale-[0.98]"
                    >
                        Send
                    </button>
                </div>
            </div>
        </main>

        <!-- Right Sidebar -->
        <aside
            class="w-72 border-l border-border bg-bg-secondary/50 p-4 flex flex-col gap-6"
        >
            <div class="text-xs text-text-secondary">
                Room is <span class="font-bold text-text-primary"
                    >{visibility}</span
                >
            </div>

            <!-- Invite link -->
            <div>
                <button
                    onclick={copyInviteLink}
                    class="cursor-pointer flex w-full items-center justify-between rounded-lg border border-border bg-bg-primary px-4 py-3 text-sm text-text-secondary transition hover:border-accent"
                >
                    <span class="truncate">Copy invite link</span>
                    {#if copied}
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            class="h-5 w-5 text-green-400"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                        >
                            <path
                                fill-rule="evenodd"
                                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                clip-rule="evenodd"
                            />
                        </svg>
                    {:else}
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
                                d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                            />
                        </svg>
                    {/if}
                </button>
            </div>

            <button
                onclick={leaveRoom}
                class="cursor-pointer flex w-full items-center justify-center gap-2 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm font-medium text-red-400 transition hover:bg-red-500/20 hover:border-red-500/50"
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
                        d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                    />
                </svg>
                Leave Room
            </button>

            <!-- User count -->
            <div class="text-sm text-text-secondary">
                <span class="font-medium">{userCount}</span> / {maxClients} online
            </div>

            <!-- User list -->
            <div class="flex-1 overflow-y-auto">
                <h3
                    class="mb-3 text-xs font-semibold uppercase tracking-wider text-text-secondary"
                >
                    Users
                </h3>
                <ul class="space-y-2">
                    {#each $users as user (user.username)}
                        <li
                            class="group flex items-center justify-between rounded-lg p-2 transition hover:bg-bg-primary/50"
                            style={user.username === currentUser
                                ? `border: 2px solid ${user.color}`
                                : ""}
                        >
                            <div class="flex items-center gap-2">
                                <span
                                    class="h-3 w-3 rounded-full"
                                    style="background-color: {user.color};"
                                ></span>
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="2"
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    class="h-5 w-5"
                                >
                                    <path
                                        d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"
                                    />
                                    <circle cx="12" cy="7" r="4" />
                                </svg>
                                <span class="text-sm">{user.username}</span>
                                {#if user.isHost}
                                    <span class="text-xs text-accent">👑</span>
                                {/if}
                            </div>
                            {#if isHost && user.username !== currentUser}
                                <button
                                    class="text-xs text-text-secondary opacity-0 hover:text-red-400 group-hover:opacity-100 transition"
                                    title="Kick user"
                                >
                                    ✕
                                </button>
                            {/if}
                        </li>
                    {/each}
                </ul>
            </div>
        </aside>
    </div>
</div>
