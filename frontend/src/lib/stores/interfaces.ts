export interface User {
    username: string;
    color: string;
    isHost: boolean;
}

export interface Message {
    username: string;
    text: string;
    color: string;
    time: string;
}

export interface Room {
    name: string;
    maxClients: number;
    host: string;
    visibility: string;
    roomId: string;
    users: User[];
}
