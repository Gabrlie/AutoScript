"""
模板匹配器
提供图像模板匹配功能
"""
import os
import cv2
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger
from dataclasses import dataclass
import pyautogui


@dataclass
class TemplateMatchResult:
    """模板匹配结果"""
    template_name: str
    confidence: float
    location: Tuple[int, int]  # (x, y)
    size: Tuple[int, int]      # (width, height)
    center: Tuple[int, int]    # (center_x, center_y)


class TemplateMatcher:
    """模板匹配器"""
    
    def __init__(self, engine):
        """
        初始化模板匹配器
        
        Args:
            engine: AutoScript引擎实例
        """
        self.engine = engine
        self.templates_dir = "templates"
        self.templates_cache = {}
        self.screenshot_cache = None
        self.screenshot_timestamp = 0
        
        # 确保模板目录存在
        os.makedirs(self.templates_dir, exist_ok=True)
        
        logger.info("模板匹配器初始化完成")
    
    def find_template(self, template_name: str, **kwargs) -> Optional[TemplateMatchResult]:
        """
        查找模板
        
        Args:
            template_name: 模板名称
            **kwargs: 其他参数
                - threshold: 匹配阈值 (default: 0.8)
                - region: 搜索区域 (x, y, width, height)
                - method: 匹配方法 (default: cv2.TM_CCOEFF_NORMED)
                - max_results: 最大结果数量 (default: 1)
                - screenshot: 是否使用新截图 (default: False)
                
        Returns:
            匹配结果
        """
        try:
            # 获取参数
            threshold = kwargs.get('threshold', self.engine.get_config('template_matcher.threshold', 0.8))
            region = kwargs.get('region', None)
            method = kwargs.get('method', cv2.TM_CCOEFF_NORMED)
            max_results = kwargs.get('max_results', 1)
            use_new_screenshot = kwargs.get('screenshot', False)
            
            # 加载模板
            template = self._load_template(template_name)
            if template is None:
                return None
            
            # 获取屏幕截图
            screenshot = self._get_screenshot(region, use_new_screenshot)
            if screenshot is None:
                return None
            
            # 执行模板匹配
            results = self._match_template(screenshot, template, method, threshold, max_results)
            
            if results:
                # 返回第一个结果
                result = results[0]
                
                # 如果有区域限制，需要调整坐标
                if region:
                    result.location = (result.location[0] + region[0], result.location[1] + region[1])
                    result.center = (result.center[0] + region[0], result.center[1] + region[1])
                
                result.template_name = template_name
                return result
                
            return None
            
        except Exception as e:
            logger.error(f"模板匹配失败: {template_name} - {e}")
            return None
    
    def find_all_templates(self, template_name: str, **kwargs) -> List[TemplateMatchResult]:
        """
        查找所有匹配的模板
        
        Args:
            template_name: 模板名称
            **kwargs: 其他参数
                
        Returns:
            匹配结果列表
        """
        try:
            # 设置最大结果数量
            kwargs['max_results'] = kwargs.get('max_results', 10)
            
            # 获取参数
            threshold = kwargs.get('threshold', self.engine.get_config('template_matcher.threshold', 0.8))
            region = kwargs.get('region', None)
            method = kwargs.get('method', cv2.TM_CCOEFF_NORMED)
            max_results = kwargs.get('max_results', 10)
            use_new_screenshot = kwargs.get('screenshot', False)
            
            # 加载模板
            template = self._load_template(template_name)
            if template is None:
                return []
            
            # 获取屏幕截图
            screenshot = self._get_screenshot(region, use_new_screenshot)
            if screenshot is None:
                return []
            
            # 执行模板匹配
            results = self._match_template(screenshot, template, method, threshold, max_results)
            
            # 调整坐标
            if region:
                for result in results:
                    result.location = (result.location[0] + region[0], result.location[1] + region[1])
                    result.center = (result.center[0] + region[0], result.center[1] + region[1])
            
            # 设置模板名称
            for result in results:
                result.template_name = template_name
            
            return results
            
        except Exception as e:
            logger.error(f"模板匹配失败: {template_name} - {e}")
            return []
    
    def wait_for_template(self, template_name: str, timeout: float = 10.0, **kwargs) -> Optional[TemplateMatchResult]:
        """
        等待模板出现
        
        Args:
            template_name: 模板名称
            timeout: 超时时间（秒）
            **kwargs: 其他参数
                
        Returns:
            匹配结果
        """
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # 强制使用新截图
            kwargs['screenshot'] = True
            result = self.find_template(template_name, **kwargs)
            if result:
                return result
            time.sleep(0.1)
        
        logger.warning(f"等待模板超时: {template_name}")
        return None
    
    def click_template(self, template_name: str, **kwargs) -> bool:
        """
        点击模板
        
        Args:
            template_name: 模板名称
            **kwargs: 其他参数
                - offset: 点击偏移 (x, y)
                - button: 鼠标按钮 ('left', 'right', 'middle')
                - clicks: 点击次数
                - interval: 点击间隔
                
        Returns:
            是否成功点击
        """
        try:
            result = self.find_template(template_name, **kwargs)
            if not result:
                return False
            
            # 计算点击位置
            offset = kwargs.get('offset', (0, 0))
            click_x = result.center[0] + offset[0]
            click_y = result.center[1] + offset[1]
            
            # 点击参数
            button = kwargs.get('button', 'left')
            clicks = kwargs.get('clicks', 1)
            interval = kwargs.get('interval', 0.1)
            
            # 执行点击
            pyautogui.click(click_x, click_y, clicks=clicks, interval=interval, button=button)
            
            logger.info(f"点击模板成功: {template_name} at ({click_x}, {click_y})")
            return True
            
        except Exception as e:
            logger.error(f"点击模板失败: {template_name} - {e}")
            return False
    
    def _load_template(self, template_name: str) -> Optional[np.ndarray]:
        """
        加载模板图像
        
        Args:
            template_name: 模板名称
            
        Returns:
            模板图像
        """
        # 检查缓存
        if template_name in self.templates_cache:
            return self.templates_cache[template_name]
        
        # 构建模板路径
        template_path = os.path.join(self.templates_dir, f"{template_name}.png")
        
        # 尝试其他格式
        if not os.path.exists(template_path):
            for ext in ['.jpg', '.jpeg', '.bmp']:
                alt_path = os.path.join(self.templates_dir, f"{template_name}{ext}")
                if os.path.exists(alt_path):
                    template_path = alt_path
                    break
        
        if not os.path.exists(template_path):
            logger.error(f"模板文件不存在: {template_path}")
            return None
        
        try:
            # 加载图像
            template = cv2.imread(template_path)
            if template is None:
                logger.error(f"无法加载模板图像: {template_path}")
                return None
            
            # 缓存模板
            self.templates_cache[template_name] = template
            
            logger.debug(f"模板加载成功: {template_name}")
            return template
            
        except Exception as e:
            logger.error(f"加载模板失败: {template_name} - {e}")
            return None
    
    def _get_screenshot(self, region: Optional[Tuple[int, int, int, int]] = None, 
                       force_new: bool = False) -> Optional[np.ndarray]:
        """
        获取屏幕截图
        
        Args:
            region: 截图区域 (x, y, width, height)
            force_new: 是否强制获取新截图
            
        Returns:
            截图图像
        """
        import time
        current_time = time.time()
        
        # 检查缓存（100ms内的截图可以重用）
        if not force_new and self.screenshot_cache is not None and \
           current_time - self.screenshot_timestamp < 0.1:
            screenshot = self.screenshot_cache
        else:
            # 获取新截图
            try:
                if region:
                    screenshot = pyautogui.screenshot(region=region)
                else:
                    screenshot = pyautogui.screenshot()
                
                # 转换为OpenCV格式
                screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                
                # 更新缓存
                if not region:  # 只缓存全屏截图
                    self.screenshot_cache = screenshot
                    self.screenshot_timestamp = current_time
                
            except Exception as e:
                logger.error(f"获取截图失败: {e}")
                return None
        
        # 如果有区域限制，裁剪截图
        if region and self.screenshot_cache is not None:
            x, y, w, h = region
            screenshot = screenshot[y:y+h, x:x+w]
        
        return screenshot
    
    def _match_template(self, screenshot: np.ndarray, template: np.ndarray, 
                       method: int, threshold: float, max_results: int) -> List[TemplateMatchResult]:
        """
        执行模板匹配
        
        Args:
            screenshot: 屏幕截图
            template: 模板图像
            method: 匹配方法
            threshold: 匹配阈值
            max_results: 最大结果数量
            
        Returns:
            匹配结果列表
        """
        try:
            # 获取模板尺寸
            template_height, template_width = template.shape[:2]
            
            # 执行模板匹配
            result = cv2.matchTemplate(screenshot, template, method)
            
            # 查找匹配位置
            results = []
            
            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                # 对于SQDIFF方法，值越小越好
                locations = np.where(result <= (1.0 - threshold))
                confidences = 1.0 - result[locations]
            else:
                # 对于其他方法，值越大越好
                locations = np.where(result >= threshold)
                confidences = result[locations]
            
            # 组合坐标和置信度
            points = list(zip(locations[1], locations[0], confidences))
            
            # 按置信度排序
            points.sort(key=lambda x: x[2], reverse=True)
            
            # 非极大值抑制
            filtered_points = self._non_max_suppression(points, template_width, template_height)
            
            # 创建结果对象
            for i, (x, y, confidence) in enumerate(filtered_points[:max_results]):
                result = TemplateMatchResult(
                    template_name="",
                    confidence=float(confidence),
                    location=(int(x), int(y)),
                    size=(template_width, template_height),
                    center=(int(x + template_width // 2), int(y + template_height // 2))
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"模板匹配执行失败: {e}")
            return []
    
    def _non_max_suppression(self, points: List[Tuple[int, int, float]], 
                            width: int, height: int, overlap_threshold: float = 0.5) -> List[Tuple[int, int, float]]:
        """
        非极大值抑制，去除重叠的检测结果
        
        Args:
            points: 检测点列表 (x, y, confidence)
            width: 模板宽度
            height: 模板高度
            overlap_threshold: 重叠阈值
            
        Returns:
            过滤后的点列表
        """
        if not points:
            return []
        
        # 转换为边界框
        boxes = []
        for x, y, confidence in points:
            boxes.append([x, y, x + width, y + height, confidence])
        
        # 按置信度排序
        boxes.sort(key=lambda x: x[4], reverse=True)
        
        # 非极大值抑制
        keep = []
        while boxes:
            # 选择置信度最高的框
            best = boxes.pop(0)
            keep.append(best)
            
            # 计算与其他框的重叠
            remaining = []
            for box in boxes:
                if self._calculate_overlap(best, box) < overlap_threshold:
                    remaining.append(box)
            
            boxes = remaining
        
        # 转换回点格式
        result = []
        for box in keep:
            result.append((box[0], box[1], box[4]))
        
        return result
    
    def _calculate_overlap(self, box1: List[float], box2: List[float]) -> float:
        """
        计算两个边界框的重叠度
        
        Args:
            box1: 边界框1 [x1, y1, x2, y2, confidence]
            box2: 边界框2 [x1, y1, x2, y2, confidence]
            
        Returns:
            重叠度 (0-1)
        """
        # 计算交集
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        
        if x2 <= x1 or y2 <= y1:
            return 0.0
        
        intersection = (x2 - x1) * (y2 - y1)
        
        # 计算并集
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def clear_cache(self):
        """清理缓存"""
        self.templates_cache.clear()
        self.screenshot_cache = None
        self.screenshot_timestamp = 0
        logger.info("模板匹配器缓存已清理")
    
    def get_template_list(self) -> List[str]:
        """获取可用模板列表"""
        templates = []
        if os.path.exists(self.templates_dir):
            for file in os.listdir(self.templates_dir):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    name = os.path.splitext(file)[0]
                    templates.append(name)
        return templates