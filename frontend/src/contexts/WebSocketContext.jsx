import React, { createContext, useContext, useEffect, useState, useRef } from 'react';

const WebSocketContext = createContext(null);

export const WebSocketProvider = ({ children, clientId }) => {
    const [socket, setSocket] = useState(null);
    const [lastMessage, setLastMessage] = useState(null);
    const [isConnected, setIsConnected] = useState(false);
    const reconnectTimeout = useRef(null);

    const connect = () => {
        // Use a random ID if no clientId provided, ensuring it's an integer for the backend
        const id = clientId || Math.floor(Math.random() * 1000000);
        const ws = new WebSocket(`ws://localhost:8000/ws/${id}`);

        ws.onopen = () => {
            console.log("WebSocket Connected");
            setIsConnected(true);
        };

        ws.onmessage = (event) => {
            console.log("WebSocket Message:", event.data);
            setLastMessage(event.data);
        };

        ws.onclose = () => {
            console.log("WebSocket Disconnected");
            setIsConnected(false);
            // Try to reconnect after 3 seconds
            reconnectTimeout.current = setTimeout(connect, 3000);
        };

        ws.onerror = (error) => {
            console.error("WebSocket Error:", error);
            ws.close();
        };

        setSocket(ws);
    };

    useEffect(() => {
        connect();
        return () => {
            if (socket) {
                socket.close();
            }
            if (reconnectTimeout.current) {
                clearTimeout(reconnectTimeout.current);
            }
        };
    }, [clientId]);

    return (
        <WebSocketContext.Provider value={{ socket, lastMessage, isConnected }}>
            {children}
        </WebSocketContext.Provider>
    );
};

export const useWebSocket = () => {
    const context = useContext(WebSocketContext);
    if (!context) {
        return { socket: null, lastMessage: null, isConnected: false };
    }
    return context;
};
