"""
Playwright插件
用于网页自动化操作
"""
import asyncio
from typing import Dict, Any, List, Optional
from loguru import logger
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from core.plugin_manager import BasePlugin


class PlaywrightPlugin(BasePlugin):
    """Playwright网页自动化插件"""
    
    def __init__(self, engine):
        """初始化Playwright插件"""
        super().__init__(engine)
        self.name = "playwright"
        self.version = "1.0.0"
        self.description = "网页自动化操作插件，支持多浏览器"
        self.author = "AutoScript Team"
        
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        self.browser_type = self.engine.get_config('plugins.playwright.browser', 'chromium')
        self.headless = self.engine.get_config('plugins.playwright.headless', False)
        self.timeout = self.engine.get_config('plugins.playwright.timeout', 30000)
        
    def initialize(self) -> bool:
        """初始化插件"""
        try:
            logger.info("Playwright插件正在初始化...")
            return True
        except Exception as e:
            logger.error(f"Playwright插件初始化失败: {e}")
            return False
    
    def cleanup(self):
        """清理插件资源"""
        try:
            if self.page:
                asyncio.run(self.page.close())
            if self.context:
                asyncio.run(self.context.close())
            if self.browser:
                asyncio.run(self.browser.close())
            if self.playwright:
                asyncio.run(self.playwright.stop())
            logger.info("Playwright插件资源已清理")
        except Exception as e:
            logger.error(f"清理Playwright插件资源失败: {e}")
    
    def get_actions(self) -> List[str]:
        """获取支持的动作列表"""
        return [
            'open_browser',
            'close_browser',
            'navigate',
            'click',
            'fill',
            'select',
            'wait_for_element',
            'wait_for_text',
            'screenshot',
            'get_text',
            'get_attribute',
            'scroll',
            'keyboard',
            'mouse',
            'execute_script',
            'wait',
            'back',
            'forward',
            'refresh',
            'new_page',
            'switch_page',
            'close_page'
        ]
    
    def execute_action(self, action: Dict[str, Any]) -> Any:
        """执行动作"""
        action_type = action.get('type', '')
        
        try:
            if action_type == 'open_browser':
                return asyncio.run(self._open_browser(action))
            elif action_type == 'close_browser':
                return asyncio.run(self._close_browser(action))
            elif action_type == 'navigate':
                return asyncio.run(self._navigate(action))
            elif action_type == 'click':
                return asyncio.run(self._click(action))
            elif action_type == 'fill':
                return asyncio.run(self._fill(action))
            elif action_type == 'select':
                return asyncio.run(self._select(action))
            elif action_type == 'wait_for_element':
                return asyncio.run(self._wait_for_element(action))
            elif action_type == 'wait_for_text':
                return asyncio.run(self._wait_for_text(action))
            elif action_type == 'screenshot':
                return asyncio.run(self._screenshot(action))
            elif action_type == 'get_text':
                return asyncio.run(self._get_text(action))
            elif action_type == 'get_attribute':
                return asyncio.run(self._get_attribute(action))
            elif action_type == 'scroll':
                return asyncio.run(self._scroll(action))
            elif action_type == 'keyboard':
                return asyncio.run(self._keyboard(action))
            elif action_type == 'mouse':
                return asyncio.run(self._mouse(action))
            elif action_type == 'execute_script':
                return asyncio.run(self._execute_script(action))
            elif action_type == 'wait':
                return asyncio.run(self._wait(action))
            elif action_type == 'back':
                return asyncio.run(self._back(action))
            elif action_type == 'forward':
                return asyncio.run(self._forward(action))
            elif action_type == 'refresh':
                return asyncio.run(self._refresh(action))
            elif action_type == 'new_page':
                return asyncio.run(self._new_page(action))
            elif action_type == 'switch_page':
                return asyncio.run(self._switch_page(action))
            elif action_type == 'close_page':
                return asyncio.run(self._close_page(action))
            else:
                raise ValueError(f"不支持的动作类型: {action_type}")
                
        except Exception as e:
            logger.error(f"执行Playwright动作失败: {action_type} - {e}")
            raise
    
    async def _open_browser(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """打开浏览器"""
        try:
            self.playwright = await async_playwright().start()
            
            # 选择浏览器类型
            if self.browser_type == 'firefox':
                browser_type = self.playwright.firefox
            elif self.browser_type == 'webkit':
                browser_type = self.playwright.webkit
            else:
                browser_type = self.playwright.chromium
            
            # 启动浏览器
            self.browser = await browser_type.launch(
                headless=self.headless,
                args=action.get('args', [])
            )
            
            # 创建浏览器上下文
            self.context = await self.browser.new_context(
                viewport=action.get('viewport', {'width': 1920, 'height': 1080}),
                user_agent=action.get('user_agent', None)
            )
            
            # 创建页面
            self.page = await self.context.new_page()
            self.page.set_default_timeout(self.timeout)
            
            logger.info(f"浏览器启动成功: {self.browser_type}")
            return {'success': True, 'browser_type': self.browser_type}
            
        except Exception as e:
            logger.error(f"启动浏览器失败: {e}")
            raise
    
    async def _close_browser(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """关闭浏览器"""
        try:
            if self.browser:
                await self.browser.close()
                self.browser = None
                self.context = None
                self.page = None
            
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
            
            logger.info("浏览器已关闭")
            return {'success': True}
            
        except Exception as e:
            logger.error(f"关闭浏览器失败: {e}")
            raise
    
    async def _navigate(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """导航到URL"""
        if not self.page:
            raise Exception("页面未初始化，请先打开浏览器")
        
        url = action.get('url', '')
        if not url:
            raise ValueError("URL不能为空")
        
        try:
            response = await self.page.goto(url, timeout=self.timeout)
            logger.info(f"导航到页面: {url}")
            return {
                'success': True,
                'url': url,
                'status': response.status if response else None
            }
            
        except Exception as e:
            logger.error(f"导航失败: {url} - {e}")
            raise
    
    async def _click(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """点击元素"""
        if not self.page:
            raise Exception("页面未初始化，请先打开浏览器")
        
        selector = action.get('selector', '')
        if not selector:
            raise ValueError("选择器不能为空")
        
        try:
            await self.page.click(
                selector,
                timeout=action.get('timeout', self.timeout),
                button=action.get('button', 'left'),
                click_count=action.get('click_count', 1),
                delay=action.get('delay', 0)
            )
            
            logger.info(f"点击元素成功: {selector}")
            return {'success': True, 'selector': selector}
            
        except Exception as e:
            logger.error(f"点击元素失败: {selector} - {e}")
            raise
    
    async def _fill(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """填充输入框"""
        if not self.page:
            raise Exception("页面未初始化，请先打开浏览器")
        
        selector = action.get('selector', '')
        text = action.get('text', '')
        
        if not selector:
            raise ValueError("选择器不能为空")
        
        try:
            await self.page.fill(
                selector,
                text,
                timeout=action.get('timeout', self.timeout)
            )
            
            logger.info(f"填充输入框成功: {selector}")
            return {'success': True, 'selector': selector, 'text': text}
            
        except Exception as e:
            logger.error(f"填充输入框失败: {selector} - {e}")
            raise
    
    async def _select(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """选择下拉选项"""
        if not self.page:
            raise Exception("页面未初始化，请先打开浏览器")
        
        selector = action.get('selector', '')
        value = action.get('value', '')
        
        if not selector:
            raise ValueError("选择器不能为空")
        
        try:
            await self.page.select_option(
                selector,
                value,
                timeout=action.get('timeout', self.timeout)
            )
            
            logger.info(f"选择选项成功: {selector} = {value}")
            return {'success': True, 'selector': selector, 'value': value}
            
        except Exception as e:
            logger.error(f"选择选项失败: {selector} - {e}")
            raise
    
    async def _wait_for_element(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """等待元素出现"""
        if not self.page:
            raise Exception("页面未初始化，请先打开浏览器")
        
        selector = action.get('selector', '')
        if not selector:
            raise ValueError("选择器不能为空")
        
        try:
            await self.page.wait_for_selector(
                selector,
                timeout=action.get('timeout', self.timeout),
                state=action.get('state', 'visible')
            )
            
            logger.info(f"元素出现: {selector}")
            return {'success': True, 'selector': selector}
            
        except Exception as e:
            logger.error(f"等待元素失败: {selector} - {e}")
            raise
    
    async def _wait_for_text(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """等待文本出现"""
        if not self.page:
            raise Exception("页面未初始化，请先打开浏览器")
        
        text = action.get('text', '')
        if not text:
            raise ValueError("文本不能为空")
        
        try:
            await self.page.wait_for_function(
                f'document.body.innerText.includes("{text}")',
                timeout=action.get('timeout', self.timeout)
            )
            
            logger.info(f"文本出现: {text}")
            return {'success': True, 'text': text}
            
        except Exception as e:
            logger.error(f"等待文本失败: {text} - {e}")
            raise
    
    async def _screenshot(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """截图"""
        if not self.page:
            raise Exception("页面未初始化，请先打开浏览器")
        
        try:
            path = action.get('path', 'screenshot.png')
            await self.page.screenshot(
                path=path,
                full_page=action.get('full_page', False),
                quality=action.get('quality', None),
                type=action.get('type', 'png')
            )
            
            logger.info(f"截图成功: {path}")
            return {'success': True, 'path': path}
            
        except Exception as e:
            logger.error(f"截图失败: {e}")
            raise
    
    async def _get_text(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """获取元素文本"""
        if not self.page:
            raise Exception("页面未初始化，请先打开浏览器")
        
        selector = action.get('selector', '')
        if not selector:
            raise ValueError("选择器不能为空")
        
        try:
            text = await self.page.inner_text(
                selector,
                timeout=action.get('timeout', self.timeout)
            )
            
            logger.info(f"获取文本成功: {selector} = {text}")
            return {'success': True, 'selector': selector, 'text': text}
            
        except Exception as e:
            logger.error(f"获取文本失败: {selector} - {e}")
            raise
    
    async def _get_attribute(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """获取元素属性"""
        if not self.page:
            raise Exception("页面未初始化，请先打开浏览器")
        
        selector = action.get('selector', '')
        attribute = action.get('attribute', '')
        
        if not selector or not attribute:
            raise ValueError("选择器和属性名不能为空")
        
        try:
            value = await self.page.get_attribute(
                selector,
                attribute,
                timeout=action.get('timeout', self.timeout)
            )
            
            logger.info(f"获取属性成功: {selector}.{attribute} = {value}")
            return {'success': True, 'selector': selector, 'attribute': attribute, 'value': value}
            
        except Exception as e:
            logger.error(f"获取属性失败: {selector}.{attribute} - {e}")
            raise
    
    async def _scroll(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """滚动页面"""
        if not self.page:
            raise Exception("页面未初始化，请先打开浏览器")
        
        try:
            x = action.get('x', 0)
            y = action.get('y', 0)
            
            await self.page.evaluate(f'window.scrollBy({x}, {y})')
            
            logger.info(f"滚动页面成功: ({x}, {y})")
            return {'success': True, 'x': x, 'y': y}
            
        except Exception as e:
            logger.error(f"滚动页面失败: {e}")
            raise
    
    async def _keyboard(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """键盘操作"""
        if not self.page:
            raise Exception("页面未初始化，请先打开浏览器")
        
        try:
            key = action.get('key', '')
            text = action.get('text', '')
            
            if key:
                await self.page.keyboard.press(key)
                logger.info(f"按键成功: {key}")
                return {'success': True, 'key': key}
            elif text:
                await self.page.keyboard.type(text)
                logger.info(f"输入文本成功: {text}")
                return {'success': True, 'text': text}
            else:
                raise ValueError("必须指定key或text")
                
        except Exception as e:
            logger.error(f"键盘操作失败: {e}")
            raise
    
    async def _mouse(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """鼠标操作"""
        if not self.page:
            raise Exception("页面未初始化，请先打开浏览器")
        
        try:
            x = action.get('x', 0)
            y = action.get('y', 0)
            button = action.get('button', 'left')
            
            await self.page.mouse.click(x, y, button=button)
            
            logger.info(f"鼠标点击成功: ({x}, {y}) {button}")
            return {'success': True, 'x': x, 'y': y, 'button': button}
            
        except Exception as e:
            logger.error(f"鼠标操作失败: {e}")
            raise
    
    async def _execute_script(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """执行JavaScript"""
        if not self.page:
            raise Exception("页面未初始化，请先打开浏览器")
        
        script = action.get('script', '')
        if not script:
            raise ValueError("脚本不能为空")
        
        try:
            result = await self.page.evaluate(script)
            
            logger.info(f"执行脚本成功: {script[:50]}...")
            return {'success': True, 'script': script, 'result': result}
            
        except Exception as e:
            logger.error(f"执行脚本失败: {script} - {e}")
            raise
    
    async def _wait(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """等待"""
        import asyncio
        
        duration = action.get('duration', 1)
        await asyncio.sleep(duration)
        
        logger.info(f"等待完成: {duration}秒")
        return {'success': True, 'duration': duration}
    
    async def _back(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """后退"""
        if not self.page:
            raise Exception("页面未初始化，请先打开浏览器")
        
        try:
            await self.page.go_back()
            logger.info("页面后退成功")
            return {'success': True}
            
        except Exception as e:
            logger.error(f"页面后退失败: {e}")
            raise
    
    async def _forward(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """前进"""
        if not self.page:
            raise Exception("页面未初始化，请先打开浏览器")
        
        try:
            await self.page.go_forward()
            logger.info("页面前进成功")
            return {'success': True}
            
        except Exception as e:
            logger.error(f"页面前进失败: {e}")
            raise
    
    async def _refresh(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """刷新页面"""
        if not self.page:
            raise Exception("页面未初始化，请先打开浏览器")
        
        try:
            await self.page.reload()
            logger.info("页面刷新成功")
            return {'success': True}
            
        except Exception as e:
            logger.error(f"页面刷新失败: {e}")
            raise
    
    async def _new_page(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """新建页面"""
        if not self.context:
            raise Exception("浏览器上下文未初始化，请先打开浏览器")
        
        try:
            new_page = await self.context.new_page()
            logger.info("新建页面成功")
            return {'success': True, 'page_id': id(new_page)}
            
        except Exception as e:
            logger.error(f"新建页面失败: {e}")
            raise
    
    async def _switch_page(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """切换页面"""
        if not self.context:
            raise Exception("浏览器上下文未初始化，请先打开浏览器")
        
        try:
            pages = self.context.pages
            page_index = action.get('page_index', 0)
            
            if 0 <= page_index < len(pages):
                self.page = pages[page_index]
                logger.info(f"切换到页面: {page_index}")
                return {'success': True, 'page_index': page_index}
            else:
                raise IndexError(f"页面索引超出范围: {page_index}")
                
        except Exception as e:
            logger.error(f"切换页面失败: {e}")
            raise
    
    async def _close_page(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """关闭页面"""
        if not self.page:
            raise Exception("页面未初始化，请先打开浏览器")
        
        try:
            await self.page.close()
            
            # 如果还有其他页面，切换到第一个
            if self.context and self.context.pages:
                self.page = self.context.pages[0]
            else:
                self.page = None
            
            logger.info("页面关闭成功")
            return {'success': True}
            
        except Exception as e:
            logger.error(f"关闭页面失败: {e}")
            raise