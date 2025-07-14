import { io, Socket } from 'socket.io-client';
import type { SocketEvents } from '@/types';

class SocketService {
  private socket: Socket | null = null;
  private listeners: Map<string, Function[]> = new Map();

  connect() {
    if (this.socket?.connected) return;

    this.socket = io('/', {
      transports: ['websocket', 'polling']
    });

    this.socket.on('connect', () => {
      console.log('已连接到服务器');
      this.emit('connect');
    });

    this.socket.on('disconnect', () => {
      console.log('与服务器断开连接');
      this.emit('disconnect');
    });

    this.socket.on('status_update', (data) => {
      this.emit('status_update', data);
    });

    this.socket.on('action_result', (data) => {
      this.emit('action_result', data);
    });

    this.socket.on('error', (data) => {
      this.emit('error', data);
    });

    this.socket.on('connected', (data) => {
      this.emit('connected', data);
    });

    this.socket.on('real_time_status', (data) => {
      this.emit('real_time_status', data);
    });
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  // 发送事件
  executeAction(pluginName: string, action: any) {
    if (this.socket) {
      this.socket.emit('execute_action', {
        plugin_name: pluginName,
        action: action
      });
    }
  }

  getRealTimeStatus() {
    if (this.socket) {
      this.socket.emit('get_real_time_status');
    }
  }

  // 监听事件
  on<K extends keyof SocketEvents>(event: K, callback: SocketEvents[K]) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(callback);
  }

  // 移除监听
  off<K extends keyof SocketEvents>(event: K, callback: SocketEvents[K]) {
    const listeners = this.listeners.get(event);
    if (listeners) {
      const index = listeners.indexOf(callback);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }
  }

  // 触发事件
  private emit(event: string, ...args: any[]) {
    const listeners = this.listeners.get(event);
    if (listeners) {
      listeners.forEach(callback => callback(...args));
    }
  }

  get connected() {
    return this.socket?.connected || false;
  }
}

export default new SocketService();