# Nullroom

Realtime public/private chat rooms built with FastAPI WebSockets and SvelteKit.

## Why I built this

Nullroom is a realtime chat-room platform designed around temporary rooms, simple joining, user presence, and fast message delivery.

## Features

- Public and private rooms
- Room creation and joining
- Room capacity limits
- Realtime WebSocket messaging
- User presence
- Host-based room ownership
- Message status handling
- SvelteKit frontend
- FastAPI backend

## Tech Stack

Backend:
- Python
- FastAPI
- WebSocket
- Pydantic

Frontend:
- SvelteKit
- TypeScript
- TailwindCSS
- Vite

## Architecture

Frontend connects to the FastAPI backend through a WebSocket endpoint.
The backend manages active users, rooms, room membership, and message broadcasting in memory.

## Screenshots

<img width="1837" height="848" alt="image" src="https://github.com/user-attachments/assets/c3f462f0-5532-4124-a126-a0417b8032b3" />
<img width="1842" height="856" alt="image" src="https://github.com/user-attachments/assets/df38c446-8196-4199-921d-48e6ff3413c6" />
<img width="1917" height="912" alt="image" src="https://github.com/user-attachments/assets/9b4973b9-ed4b-48f6-8cf0-d28ad0b224af" />
<img width="1915" height="913" alt="image" src="https://github.com/user-attachments/assets/a788a83c-c046-4c76-b8c1-cbe4d024d996" />


## WebSocket Events

| Event | Direction | Description |
|---|---|---|
| join_room | Client -> Server | Join an existing room |
| create_room | Client -> Server | Create a room |
| send_chat_message | Client -> Server | Send message |
| room_joined | Server -> Client | Confirms room joined |
| user_joined | Server -> Client | Broadcasts user joined |
| user_left | Server -> Client | Broadcasts user left |
| message_sent | Server -> Client | Broadcasts chat message |

## Limitations

- Rooms are stored in memory
- Messages are not persisted
- Designed as a realtime architecture/demo project

## Roadmap

- Host moderation actions
- Deployment
