"""
OCR引擎
提供文字识别功能
"""
import os
import cv2
import numpy as np
from typing import Optional, Tuple, List, Dict, Any
from loguru import logger
from PIL import Image
import pytesseract
import pyautogui


class OCREngine:
    """OCR文字识别引擎"""
    
    def __init__(self, engine):
        """
        初始化OCR引擎
        
        Args:
            engine: AutoScript引擎实例
        """
        self.engine = engine
        self.tesseract_config = self.engine.get_config('ocr.config', '--psm 8')
        self.tesseract_lang = self.engine.get_config('ocr.lang', 'chi_sim+eng')
        
        # 配置tesseract路径（Windows）
        if os.name == 'nt':
            tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            if os.path.exists(tesseract_path):
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        logger.info("OCR引擎初始化完成")
    
    def recognize_text(self, image_path: Optional[str] = None, 
                      region: Optional[Tuple[int, int, int, int]] = None) -> str:
        """
        识别文本
        
        Args:
            image_path: 图片路径，如果为None则截图
            region: 识别区域 (x, y, width, height)
            
        Returns:
            识别的文本
        """
        try:
            # 获取图像
            if image_path:
                image = cv2.imread(image_path)
                if image is None:
                    logger.error(f"无法加载图像: {image_path}")
                    return ""
            else:
                # 截图
                if region:
                    screenshot = pyautogui.screenshot(region=region)
                else:
                    screenshot = pyautogui.screenshot()
                
                # 转换为OpenCV格式
                image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # 如果有区域参数且是从文件读取的图像，则裁剪
            if region and image_path:
                x, y, w, h = region
                image = image[y:y+h, x:x+w]
            
            # 预处理图像
            processed_image = self._preprocess_image(image)
            
            # 转换为PIL图像
            pil_image = Image.fromarray(cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB))
            
            # 执行OCR
            text = pytesseract.image_to_string(
                pil_image, 
                lang=self.tesseract_lang,
                config=self.tesseract_config
            )
            
            # 清理结果
            text = self._clean_text(text)
            
            logger.debug(f"OCR识别结果: {text}")
            return text
            
        except Exception as e:
            logger.error(f"OCR识别失败: {e}")
            return ""
    
    def recognize_text_with_confidence(self, image_path: Optional[str] = None,
                                     region: Optional[Tuple[int, int, int, int]] = None) -> List[Dict[str, Any]]:
        """
        识别文本并返回置信度信息
        
        Args:
            image_path: 图片路径，如果为None则截图
            region: 识别区域 (x, y, width, height)
            
        Returns:
            识别结果列表，每个元素包含文本、置信度、位置信息
        """
        try:
            # 获取图像
            if image_path:
                image = cv2.imread(image_path)
                if image is None:
                    logger.error(f"无法加载图像: {image_path}")
                    return []
            else:
                # 截图
                if region:
                    screenshot = pyautogui.screenshot(region=region)
                else:
                    screenshot = pyautogui.screenshot()
                
                # 转换为OpenCV格式
                image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # 如果有区域参数且是从文件读取的图像，则裁剪
            if region and image_path:
                x, y, w, h = region
                image = image[y:y+h, x:x+w]
            
            # 预处理图像
            processed_image = self._preprocess_image(image)
            
            # 转换为PIL图像
            pil_image = Image.fromarray(cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB))
            
            # 执行OCR并获取详细信息
            data = pytesseract.image_to_data(
                pil_image,
                lang=self.tesseract_lang,
                config=self.tesseract_config,
                output_type=pytesseract.Output.DICT
            )
            
            # 处理结果
            results = []
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                confidence = int(data['conf'][i])
                
                # 过滤空文本和低置信度结果
                if text and confidence > 0:
                    result = {
                        'text': text,
                        'confidence': confidence,
                        'left': data['left'][i],
                        'top': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i],
                        'center_x': data['left'][i] + data['width'][i] // 2,
                        'center_y': data['top'][i] + data['height'][i] // 2
                    }
                    
                    # 如果有区域偏移，调整坐标
                    if region and not image_path:
                        result['left'] += region[0]
                        result['top'] += region[1]
                        result['center_x'] += region[0]
                        result['center_y'] += region[1]
                    
                    results.append(result)
            
            logger.debug(f"OCR识别到 {len(results)} 个文本块")
            return results
            
        except Exception as e:
            logger.error(f"OCR识别失败: {e}")
            return []
    
    def find_text(self, target_text: str, 
                  image_path: Optional[str] = None,
                  region: Optional[Tuple[int, int, int, int]] = None,
                  similarity_threshold: float = 0.8) -> Optional[Dict[str, Any]]:
        """
        在图像中查找指定文本
        
        Args:
            target_text: 要查找的文本
            image_path: 图片路径，如果为None则截图
            region: 搜索区域 (x, y, width, height)
            similarity_threshold: 相似度阈值
            
        Returns:
            找到的文本信息
        """
        try:
            results = self.recognize_text_with_confidence(image_path, region)
            
            # 查找最匹配的文本
            best_match = None
            best_similarity = 0
            
            for result in results:
                similarity = self._calculate_text_similarity(target_text, result['text'])
                if similarity >= similarity_threshold and similarity > best_similarity:
                    best_similarity = similarity
                    best_match = result
                    best_match['similarity'] = similarity
            
            if best_match:
                logger.info(f"找到文本: {best_match['text']} (相似度: {best_similarity:.2f})")
            else:
                logger.warning(f"未找到文本: {target_text}")
            
            return best_match
            
        except Exception as e:
            logger.error(f"查找文本失败: {e}")
            return None
    
    def wait_for_text(self, target_text: str, 
                      timeout: float = 10.0,
                      region: Optional[Tuple[int, int, int, int]] = None,
                      similarity_threshold: float = 0.8) -> Optional[Dict[str, Any]]:
        """
        等待指定文本出现
        
        Args:
            target_text: 要等待的文本
            timeout: 超时时间（秒）
            region: 搜索区域 (x, y, width, height)
            similarity_threshold: 相似度阈值
            
        Returns:
            找到的文本信息
        """
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            result = self.find_text(target_text, None, region, similarity_threshold)
            if result:
                return result
            time.sleep(0.5)
        
        logger.warning(f"等待文本超时: {target_text}")
        return None
    
    def click_text(self, target_text: str,
                   image_path: Optional[str] = None,
                   region: Optional[Tuple[int, int, int, int]] = None,
                   similarity_threshold: float = 0.8,
                   offset: Tuple[int, int] = (0, 0)) -> bool:
        """
        点击指定文本
        
        Args:
            target_text: 要点击的文本
            image_path: 图片路径，如果为None则截图
            region: 搜索区域 (x, y, width, height)
            similarity_threshold: 相似度阈值
            offset: 点击偏移 (x, y)
            
        Returns:
            是否成功点击
        """
        try:
            result = self.find_text(target_text, image_path, region, similarity_threshold)
            if not result:
                return False
            
            # 计算点击位置
            click_x = result['center_x'] + offset[0]
            click_y = result['center_y'] + offset[1]
            
            # 执行点击
            pyautogui.click(click_x, click_y)
            
            logger.info(f"点击文本成功: {target_text} at ({click_x}, {click_y})")
            return True
            
        except Exception as e:
            logger.error(f"点击文本失败: {target_text} - {e}")
            return False
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        预处理图像以提高OCR准确度
        
        Args:
            image: 输入图像
            
        Returns:
            预处理后的图像
        """
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 高斯模糊去噪
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # 自适应阈值二值化
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # 形态学操作去除噪点
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # 转换回BGR格式
        result = cv2.cvtColor(cleaned, cv2.COLOR_GRAY2BGR)
        
        return result
    
    def _clean_text(self, text: str) -> str:
        """
        清理识别的文本
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        # 移除多余的空白字符
        text = ' '.join(text.split())
        
        # 移除常见的OCR错误字符
        text = text.replace('|', 'I')  # 竖线替换为I
        text = text.replace('０', '0')  # 全角0替换为半角0
        text = text.replace('１', '1')  # 全角1替换为半角1
        
        return text.strip()
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        计算文本相似度
        
        Args:
            text1: 文本1
            text2: 文本2
            
        Returns:
            相似度 (0-1)
        """
        # 简单的字符串相似度计算
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()
        
        if not text1 or not text2:
            return 0.0
        
        # 计算编辑距离
        distance = self._levenshtein_distance(text1, text2)
        max_len = max(len(text1), len(text2))
        
        similarity = 1 - distance / max_len
        return max(0.0, similarity)
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        计算两个字符串的编辑距离
        
        Args:
            s1: 字符串1
            s2: 字符串2
            
        Returns:
            编辑距离
        """
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def get_available_languages(self) -> List[str]:
        """获取可用的OCR语言"""
        try:
            langs = pytesseract.get_languages()
            return sorted(langs)
        except Exception as e:
            logger.error(f"获取OCR语言失败: {e}")
            return ['eng', 'chi_sim']
    
    def set_language(self, language: str):
        """设置OCR语言"""
        self.tesseract_lang = language
        self.engine.set_config('ocr.lang', language)
        logger.info(f"OCR语言已设置为: {language}")
    
    def set_config(self, config: str):
        """设置OCR配置"""
        self.tesseract_config = config
        self.engine.set_config('ocr.config', config)
        logger.info(f"OCR配置已设置为: {config}")
    
    def save_debug_image(self, image: np.ndarray, filename: str):
        """保存调试图像"""
        debug_dir = "debug"
        os.makedirs(debug_dir, exist_ok=True)
        
        debug_path = os.path.join(debug_dir, f"{filename}.png")
        cv2.imwrite(debug_path, image)
        logger.debug(f"调试图像已保存: {debug_path}")