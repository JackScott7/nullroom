export interface User {
    username: string;
    color: string;
    isHost: boolean;
}

export interface Message {
    tempId?: string;
    username: string;
    text: string;
    color: string;
    time: string;
    status?: 'sending' | 'sent';
}

export interface Room {
    name: string;
    maxClients: number;
    host: string;
    visibility: string;
    roomId: string;
    users: User[];
}
