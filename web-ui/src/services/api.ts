import axios from 'axios';
import type {
  ApiResponse,
  EngineStatus,
  Plugin,
  Task,
  CreateScriptRequest,
  FindTemplateRequest,
  TemplateMatchResult,
  OcrRequest,
  Config
} from '@/types';

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
});

// 响应拦截器
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API请求失败:', error);
    throw error;
  }
);

// 引擎控制API
export const engineApi = {
  start: (): Promise<ApiResponse> => api.post('/engine/start'),
  stop: (): Promise<ApiResponse> => api.post('/engine/stop'),
  getStatus: (): Promise<ApiResponse<EngineStatus>> => api.get('/engine/status'),
};

// 插件管理API
export const pluginApi = {
  getAll: (): Promise<ApiResponse<Record<string, Plugin>>> => api.get('/plugins'),
  enable: (pluginName: string): Promise<ApiResponse> => 
    api.post(`/plugins/${pluginName}/enable`),
  disable: (pluginName: string): Promise<ApiResponse> => 
    api.post(`/plugins/${pluginName}/disable`),
  getActions: (pluginName: string): Promise<ApiResponse<string[]>> => 
    api.get(`/plugins/${pluginName}/actions`),
};

// 脚本管理API
export const scriptApi = {
  create: (script: CreateScriptRequest): Promise<ApiResponse<{ task_id: string }>> => 
    api.post('/scripts', script),
  getAll: (): Promise<ApiResponse<Task[]>> => api.get('/scripts'),
  get: (taskId: string): Promise<ApiResponse<Task>> => api.get(`/scripts/${taskId}`),
  cancel: (taskId: string): Promise<ApiResponse> => api.post(`/scripts/${taskId}/cancel`),
};

// 队列管理API
export const queueApi = {
  pause: (): Promise<ApiResponse> => api.post('/queue/pause'),
  resume: (): Promise<ApiResponse> => api.post('/queue/resume'),
  clear: (): Promise<ApiResponse> => api.post('/queue/clear'),
};

// 模板匹配API
export const templateApi = {
  getList: (): Promise<ApiResponse<string[]>> => api.get('/templates'),
  find: (request: FindTemplateRequest): Promise<ApiResponse<TemplateMatchResult>> => 
    api.post('/templates/find', request),
};

// OCR API
export const ocrApi = {
  recognize: (request: OcrRequest): Promise<ApiResponse<string>> => 
    api.post('/ocr/recognize', request),
};

// 配置API
export const configApi = {
  get: (): Promise<ApiResponse<Config>> => api.get('/config'),
  update: (config: Config): Promise<ApiResponse> => api.post('/config', config),
};

// 截图API
export const screenshotApi = {
  take: (): Promise<Blob> => api.post('/screenshot', {}, { responseType: 'blob' }),
};