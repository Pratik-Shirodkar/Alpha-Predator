
import { useState, useEffect, useRef } from 'react';

type WebSocketStatus = 'CONNECTING' | 'OPEN' | 'CLOSED';

export function useWebSocket(url: string) {
    const [status, setStatus] = useState<WebSocketStatus>('CLOSED');
    const [messages, setMessages] = useState<any[]>([]);
    const ws = useRef<WebSocket | null>(null);

    useEffect(() => {
        if (!url) return;

        const connect = () => {
            setStatus('CONNECTING');
            ws.current = new WebSocket(url);

            ws.current.onopen = () => {
                setStatus('OPEN');
                console.log('WS Connected');
            };

            ws.current.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    setMessages((prev) => [...prev, data]);
                } catch (e) {
                    console.error('Failed to parse WS message', e);
                }
            };

            ws.current.onclose = () => {
                setStatus('CLOSED');
                // Reconnect after delay
                setTimeout(connect, 3000);
            };
        };

        connect();

        return () => {
            ws.current?.close();
        };
    }, [url]);

    const sendMessage = (msg: any) => {
        if (ws.current?.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify(msg));
        }
    };

    return { status, messages, sendMessage };
}
