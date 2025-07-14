// 系统状态相关类型
export interface EngineStatus {
  running: boolean;
  queue_status: QueueStatus;
  plugin_status: Record<string, boolean>;
}

export interface QueueStatus {
  paused: boolean;
  running_tasks: number;
  completed_tasks: number;
  pending_tasks: number;
}

// 插件相关类型
export interface Plugin {
  name: string;
  description: string;
  version: string;
  author: string;
  enabled: boolean;
  actions: string[];
}

export interface PluginAction {
  type: string;
  [key: string]: any;
}

// 脚本任务相关类型
export interface Task {
  id: string;
  name: string;
  status: TaskStatus;
  progress: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
  result?: any;
}

export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

export interface CreateScriptRequest {
  name: string;
  plugin_name: string;
  actions: PluginAction[];
  priority: number;
}

// API响应类型
export interface ApiResponse<T = any> {
  success: boolean;
  message?: string;
  data?: T;
}

// Socket.IO事件类型
export interface SocketEvents {
  connect: () => void;
  disconnect: () => void;
  status_update: (data: SystemStatus) => void;
  action_result: (data: ActionResult) => void;
  error: (data: { message: string }) => void;
  connected: (data: { message: string }) => void;
  real_time_status: (data: SystemStatus) => void;
}

export interface SystemStatus {
  engine_running: boolean;
  queue_status: QueueStatus;
  running_tasks: RunningTask[];
}

export interface RunningTask {
  id: string;
  name: string;
  progress: number;
  status: string;
}

export interface ActionResult {
  success: boolean;
  plugin_name: string;
  action: PluginAction;
  result?: any;
  message?: string;
}

// 模板匹配类型
export interface TemplateMatchResult {
  template_name: string;
  confidence: number;
  location: [number, number];
  size: [number, number];
  center: [number, number];
}

export interface FindTemplateRequest {
  template_name: string;
  [key: string]: any;
}

// OCR类型
export interface OcrRequest {
  image_path?: string;
  region?: [number, number, number, number];
}

// 配置类型
export interface Config {
  [key: string]: any;
}