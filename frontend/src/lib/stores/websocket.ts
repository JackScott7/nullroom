import { writable } from 'svelte/store';
import type { Room, Message, User } from './interfaces';
import { generateTempId } from './utils';

export const currentRoom = writable<Room | null>(null);
export const messages = writable<Message[]>([]);
export const users = writable<User[]>([]);
export const publicRooms = writable<Room[]>([]);
export const createdRoom = writable<Room | null>(null);

let ws: WebSocket | undefined;
let outgoingQueue: string[] = [];
let currentUsername: string | undefined;

function flushQueue() {
    if (!ws) return;
    while (outgoingQueue.length > 0) {
        const msg = outgoingQueue.shift()!;
        ws.send(msg);
    }
}

function send(json: string) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(json);
    } else {
        outgoingQueue.push(json);
    }
}

function handleServerMessage(msg: any) {
    switch (msg.type) {
        case 'room_joined':
            currentRoom.set(msg.room);
            users.set(msg.room.users);
            messages.set([]);
            break;
        case 'user_joined':
            users.set(msg.room_users)
            break;
        case 'public_rooms':
            publicRooms.set(msg.data);
            break;
        case 'room_created':
            createdRoom.set(msg.room);
            break;
        case 'new_room_available':
            publicRooms.update(rooms => [...rooms, msg.room])
            break;
        case 'message_sent':
            const serverTempId: string | undefined = msg.tempId;
            let matched = false;

            if (serverTempId) {
                messages.update(msgs =>
                    msgs.map(m => {
                        if (m.tempId === serverTempId) {
                            matched = true;
                            return { ...m, status: 'sent', color: msg.color, time: msg.time };
                        }
                        return m;
                    })
                );
            }

            if (!matched) {
                messages.update(msgs => [
                    ...msgs,
                    {
                        username: msg.sender,
                        text: msg.text,
                        color: msg.color,
                        time: msg.time,
                        status: 'sent',
                    },
                ]);
            }
            break;
        case 'user_left':
            users.update(usrs => usrs.filter(u => u.username !== msg.username));
            break;
        case 'room_closed':
            currentRoom.set(null);
            location.href = '/rooms';
            break;
    }
}

export function wsConnect(username: string) {
    if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) && currentUsername === username) {
        return;
    }

    if (ws && currentUsername !== username) {
        ws.close(4000, "new user")
    }

    currentUsername = username
    ws = new WebSocket(`ws://127.0.0.1:8000/api/ws/${username}`);

    ws.onopen = () => {
        flushQueue();
    };

    ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        handleServerMessage(msg);
    };

    ws.onclose = () => {
        ws = undefined;
        currentUsername = undefined;
    }
}

export function wsJoinRoom(roomId: string) {
    send(JSON.stringify(
        {
            type: 'join_room',
            room_id: roomId,
            user: currentUsername
        }
    ));
}

export function wsSendChatMessage(text: string, roomId: string, username: string) {
    const tempId = generateTempId();
    send(JSON.stringify({
        type: 'send_chat_message',
        message: text,
        roomId,
        sender: username,
        tempId
    }));

    messages.update(msgs => [...msgs, {
        tempId,
        username,
        text,
        color: '', // will be filled by server; or use local color
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        status: 'sending'
    }]);
}

export function wsSendNameColor(username: string, color: string) {
    send(JSON.stringify(
        {
            type: 'set_color',
            username,
            color
        }
    ));
}

export function wsGetPublicRooms(username: string) {
    send(JSON.stringify({
        type: 'get_public_rooms',
        username
    }));
}

export function wsCreateRoom(host: string, name: string, maxClients: number, visibility: string) {
    send(JSON.stringify({
        type: 'create_room',
        name,
        maxClients,
        visibility,
        user: host
    }));
}

export function wsLeaveRoom(roomId: string) {
    send(JSON.stringify({
        type: 'leave_room',
        roomId: roomId,
        username: currentUsername
    }));
}
