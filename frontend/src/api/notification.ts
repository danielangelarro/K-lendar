import axios from 'axios';

interface Notification {
    id: string;
    title: string;
    message: string;
    priority: boolean;
    date: string;
}

class NotificationService {
    private token: string | null;
    public socket: WebSocket | null;
    public handleNotifications: ((notifications: Notification[]) => void) | null;

    constructor() {
        this.token = localStorage.getItem('token');
        this.socket = null;
        this.handleNotifications = null;
    }

    connectWebSocket() {
        if (!this.token) {
            console.error('No token available');
            return;
        }

        // Crear conexión WebSocket
        this.socket = new WebSocket(`ws://${import.meta.env.VITE_API_UR}/notifications/ws?token=${this.token}`);

        this.socket.onopen = () => {
            console.log('WebSocket conectado');
        };

        this.socket.onmessage = (event) => {
            const notifications: Notification[] = JSON.parse(event.data);
            if (this.handleNotifications) {
                this.handleNotifications(notifications);
            }
        };

        this.socket.onclose = (event) => {
            console.log('WebSocket desconectado', event);
            // Implementar reconexión si es necesario
            setTimeout(() => this.connectWebSocket(), 5000);
        };
    }
}

export default new NotificationService();