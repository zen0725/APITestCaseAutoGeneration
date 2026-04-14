import asyncio
import aiohttp
from workerNode.worker_models import ExecutionTask, TaskResult, TaskStatus
import logging
import traceback
from datetime import datetime
import json
import re
from typing import Dict, List, Any, Callable
import tempfile
import ast

class TaskExecutor:
    def __init__(self, work_dir: str):
        self.work_dir = work_dir
        self.logger = logging.getLogger("TaskExecutor")
        self.http_client = None
        self.execution_envs = {}
        self.safe_builtins = self._create_safe_builtins()
        self.execution_cache = {}

        # 创建安全执行环境
        self.safe_globals = {
            '__builtins__': self.safe_builtins,
            'response': None,
            'json': json,
            're': re,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,
            'len': len,
            'range': range,
            'enumerate': enumerate,
            'zip': zip,
            'min': min,
            'max': max,
            'sum': sum,
            'abs': abs,
            'round': round
        }

    def _create_safe_builtins(self) -> Dict[str, Any]:
        """创建安全的builtins环境"""
        safe_builtins = {
            'None': None,
            'True': True,
            'False': False,
            'bool': bool,
            'int': int,
            'float': float,
            'str': str,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,
            'len': len,
            'range': range,
            'enumerate': enumerate,
            'zip': zip,
            'min': min,
            'max': max,
            'sum': sum,
            'abs': abs,
            'round': round,
            'isinstance': isinstance,
            'type': type,
            'hasattr': hasattr,
            'getattr': getattr,
            'setattr': setattr,
            'repr': repr,
            'sorted': sorted,
            'any': any,
            'all': all
        }
        return safe_builtins

    async def execute_task(self, task: ExecutionTask) -> TaskResult:
        """执行测试任务"""
        start_time = datetime.now()
        logs = []

        try:
            self.logger.info(f"开始执行任务: {task.task_id}")
            logs.append(f"开始执行任务: {task.task_id}")

            # 确保HTTP客户端存在
            if not self.http_client:
                self.http_client = aiohttp.ClientSession()

            # 执行HTTP请求
            response = await self._execute_http_request(task)
            logs.append(f"HTTP请求完成，状态码: {response.status}")

            # 处理响应
            response_data = await self._process_response(response)

            # 执行断言
            assertion_results = await self._execute_assertions(task, response_data)

            # 评估结果
            task_passed = all(result['passed'] for result in assertion_results)
            status = TaskStatus.COMPLETED if task_passed else TaskStatus.FAILED

            duration = (datetime.now() - start_time).total_seconds()

            self.logger.info(f"任务完成: {task.task_id}, 状态: {status}, 耗时: {duration:.3f}s")
            logs.append(f"任务完成，状态: {status}, 耗时: {duration:.3f}s")

            return TaskResult(
                task_id=task.task_id,
                test_id=task.test_id,
                status=status,
                duration=duration,
                start_time=start_time,
                end_time=datetime.now(),
                response=response_data,
                assertion_results=assertion_results,
                logs=logs
            )

        except asyncio.TimeoutError:
            error_msg = f"任务执行超时 ({task.timeout}s)"
            self.logger.error(error_msg)
            logs.append(error_msg)
            return self._create_error_result(task, start_time, error_msg, logs)

        except Exception as e:
            error_msg = f"任务执行错误: {str(e)}"
            self.logger.error(error_msg)
            logs.append(error_msg)
            logs.append(traceback.format_exc())
            return self._create_error_result(task, start_time, error_msg, logs)

    async def _execute_http_request(self, task: ExecutionTask) -> aiohttp.ClientResponse:
        """执行HTTP请求"""
        # 构建完整的URL
        #base_url = self._get_service_base_url(task.service_name)
        base_url = task.base_url
        full_url = f"{base_url}{task.endpoint}"

        # 准备请求头
        headers = self._prepare_headers(task)

        self.logger.debug(f"执行请求: {task.method} {full_url}")

        timeout = aiohttp.ClientTimeout(total=task.timeout)

        if task.method.upper() == 'GET':
            return await self.http_client.get(full_url, headers=headers, timeout=timeout)
        elif task.method.upper() == 'POST':
            return await self.http_client.post(full_url, json=task.payload, headers=headers, timeout=timeout)
        elif task.method.upper() == 'PUT':
            return await self.http_client.put(full_url, json=task.payload, headers=headers, timeout=timeout)
        elif task.method.upper() == 'DELETE':
            return await self.http_client.delete(full_url, headers=headers, timeout=timeout)
        elif task.method.upper() == 'PATCH':
            return await self.http_client.patch(full_url, json=task.payload, headers=headers, timeout=timeout)
        else:
            raise ValueError(f"不支持的HTTP方法: {task.method}")

    def _get_service_base_url(self, service_name: str) -> str:
        """获取服务基础URL"""
        # 这里可以从服务发现、配置或环境变量获取
        service_urls = {
            'user-service': 'http://user-service:8080',
            'order-service': 'http://order-service:8080',
            'product-service': 'http://product-service:8080',
            'payment-service': 'http://payment-service:8080',
            'auth-service': 'http://auth-service:8080'
        }
        return service_urls.get(service_name, f'http://{service_name}:8080')

    def _prepare_headers(self, task: ExecutionTask) -> Dict[str, str]:
        """准备请求头"""
        headers = {
            'User-Agent': f'TestWorker/{task.task_id}',
            'Accept': 'application/json',
        }

        # 添加内容类型头
        if task.method.upper() in ['POST', 'PUT', 'PATCH'] and task.payload:
            headers['Content-Type'] = 'application/json'

        # 添加认证头
        if 'auth_token' in task.metadata:
            headers['Authorization'] = f'Bearer {task.metadata["auth_token"]}'

        # 添加自定义头
        if 'headers' in task.metadata:
            headers.update(task.metadata['headers'])

        return headers

    async def _process_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """处理HTTP响应"""
        response_data = {
            'status_code': response.status,
            'headers': dict(response.headers),
            'url': str(response.url),
            'elapsed': response.elapsed.total_seconds() if response.elapsed else 0
        }

        try:
            # 解析响应体
            content_type = response.headers.get('Content-Type', '')

            if 'application/json' in content_type:
                response_data['body'] = await response.json()
            else:
                response_data['body'] = await response.text()

        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            self.logger.warning(f"响应体解析失败: {e}")
            response_data['body'] = await response.text()
            response_data['parse_error'] = str(e)

        finally:
            await response.release()

        return response_data

    async def _execute_assertions(self, task: ExecutionTask, response_data: Dict) -> List[Dict]:
        """执行断言"""
        assertion_results = []

        for i, assertion_config in enumerate(task.assertions):
            assertion_id = f"assertion_{i}"

            try:
                passed = await self._execute_single_assertion(assertion_config, response_data)

                assertion_results.append({
                    'assertion_id': assertion_id,
                    'passed': passed,
                    'expected': assertion_config.get('description', 'N/A'),
                    'actual': self._get_assertion_actual_value(assertion_config, response_data)
                })

            except Exception as e:
                self.logger.error(f"断言执行失败: {e}")
                assertion_results.append({
                    'assertion_id': assertion_id,
                    'passed': False,
                    'error_message': str(e),
                    'expected': assertion_config.get('description', 'N/A'),
                    'actual': 'N/A'
                })

        return assertion_results

    async def _execute_single_assertion(self, assertion_config: Dict, response_data: Dict) -> bool:
        """执行单个断言"""
        assertion_type = assertion_config.get('type')

        if assertion_type == 'status_code':
            expected = assertion_config.get('expected')
            return response_data.get('status_code') == expected

        elif assertion_type == 'response_time':
            max_time = assertion_config.get('max_time')
            return response_data.get('elapsed', 0) <= max_time

        elif assertion_type == 'json_path':
            # 需要安装 jsonpath-ng: pip install jsonpath-ng
            from jsonpath_ng import parse
            json_path = assertion_config.get('path')
            expected = assertion_config.get('expected')

            try:
                expr = parse(json_path)
                matches = expr.find(response_data.get('body', {}))
                if assertion_config.get('exists_only', False):
                    return bool(matches)
                else:
                    return matches and matches[0].value == expected
            except:
                return False

        elif assertion_type == 'contains_text':
            text = assertion_config.get('text')
            body_str = str(response_data.get('body', ''))
            return text in body_str

        else:
            # 自定义断言函数
            if 'function' in assertion_config:
                # 这里可以执行自定义的断言逻辑
                return await self._execute_custom_assertion(assertion_config['function'], response_data)

        return False

    async def _execute_custom_assertion(self, func_config: Dict, response_data: Dict) -> bool:
        """执行自定义断言"""
        # 这里可以实现自定义断言逻辑
        # 例如：执行Python代码、调用外部脚本等
        start_time = datetime.now()
        try:
            # 简单的表达式求值
            #expression = func_config.get('expression')
            #if expression:
                # 安全地执行表达式
            #    return eval(expression, {'response': response_data})
            assertion_type = func_config.get('type', 'expression')
            # 根据断言类型选择执行策略
            if assertion_type == 'expression':
                result = await self._execute_expression_assertion(func_config, response_data)
            elif assertion_type == 'python_code':
                result = await self._execute_python_code_assertion(func_config, response_data)
            elif assertion_type == 'external_script':
                result = await self._execute_external_script_assertion(func_config, response_data)
            elif assertion_type == 'javascript':
                result = await self._execute_javascript_assertion(func_config, response_data)
            elif assertion_type == 'sql_query':
                result = await self._execute_sql_assertion(func_config, response_data)
            else:
                self.logger.warning(f"未知的断言类型: {assertion_type}")
                result = False

            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.debug(f"自定义断言执行完成，类型: {assertion_type}, 结果: {result}, 耗时: {execution_time:.3f}s")

            return result
        except Exception as e:
            self.logger.error(f"自定义断言执行失败: {e}")
            return False

    async def _execute_expression_assertion(self, func_config: Dict, response_data: Dict) -> bool:
        """执行表达式断言"""
        expression = func_config.get('expression', '')
        if not expression:
            self.logger.warning("表达式断言缺少表达式")
            return False

        try:
            # 安全检查：解析AST并验证
            if not self._is_safe_expression(expression):
                self.logger.error(f"表达式安全检查失败: {expression}")
                return False

            # 准备执行环境
            execution_env = self.safe_globals.copy()
            execution_env['response'] = response_data

            # 添加自定义函数
            execution_env.update(self._get_custom_functions())

            # 执行表达式
            result = eval(expression, execution_env)

            # 确保返回布尔值
            return bool(result)

        except Exception as e:
            self.logger.error(f"表达式执行失败: {e}, 表达式: {expression}")
            return False

    def _is_safe_expression(self, expression: str) -> bool:
        """检查表达式是否安全"""
        try:
            # 解析AST
            tree = ast.parse(expression, mode='eval')

            # 定义不允许的节点类型
            unsafe_nodes = {
                ast.Import, ast.ImportFrom,  # 导入语句
                ast.Call,  # 函数调用（有限制）
                ast.Attribute,  # 属性访问（有限制）
                ast.Subscript,  # 下标访问
                ast.Lambda,  # Lambda表达式
                ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp,  # 推导式
                ast.Yield, ast.YieldFrom,  # 生成器
                ast.Global, ast.Nonlocal,  # 全局/非局部变量
                ast.Assert,  # 断言
                ast.Delete,  # 删除
                ast.AugAssign,  # 增强赋值
                ast.AsyncFunctionDef, ast.Await,  # 异步
                ast.With,  # with语句
            }

            # 检查AST节点
            for node in ast.walk(tree):
                if type(node) in unsafe_nodes:
                    # 允许有限的函数调用和属性访问
                    if isinstance(node, ast.Call):
                        if not self._is_safe_call(node):
                            return False
                    elif isinstance(node, ast.Attribute):
                        if not self._is_safe_attribute(node):
                            return False
                    else:
                        return False

            return True

        except SyntaxError:
            return False

    def _is_safe_call(self, node: ast.Call) -> bool:
        """检查函数调用是否安全"""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            # 只允许安全的函数
            safe_functions = {
                'len', 'str', 'int', 'float', 'bool', 'list', 'dict', 'tuple', 'set',
                'min', 'max', 'sum', 'abs', 'round', 'isinstance', 'type', 'hasattr',
                'getattr', 'repr', 'sorted', 'any', 'all', 'enumerate', 'zip', 'range'
            }
            return func_name in safe_functions

        return False

    def _is_safe_attribute(self, node: ast.Attribute) -> bool:
        """检查属性访问是否安全"""
        attr_name = node.attr
        # 允许访问响应数据的常见属性
        safe_attributes = {
            'status_code', 'headers', 'body', 'elapsed', 'url',
            'get', 'items', 'keys', 'values'
        }
        return attr_name in safe_attributes

    async def _execute_python_code_assertion(self, func_config: Dict, response_data: Dict) -> bool:
        """执行Python代码断言"""
        code = func_config.get('code', '')
        if not code:
            self.logger.warning("Python代码断言缺少代码")
            return False

        try:
            # 创建安全的执行环境
            execution_env = self.safe_globals.copy()
            execution_env['response'] = response_data
            execution_env.update(self._get_custom_functions())

            # 添加返回值变量
            execution_env['__result__'] = None

            # 执行代码
            exec(code, execution_env)

            # 获取结果
            result = execution_env.get('__result__')
            if result is None:
                # 如果没有显式设置结果，检查最后一条语句
                result = execution_env.get('___', None)

            return bool(result)

        except Exception as e:
            self.logger.error(f"Python代码执行失败: {e}")
            return False

    async def _execute_external_script_assertion(self, func_config: Dict, response_data: Dict) -> bool:
        """执行外部脚本断言"""
        script_path = func_config.get('script_path', '')
        script_content = func_config.get('script_content', '')

        if not script_path and not script_content:
            self.logger.warning("外部脚本断言缺少脚本路径或内容")
            return False

        try:
            # 如果提供了脚本内容，创建临时文件
            if script_content:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                    f.write(script_content)
                    script_path = f.name

            # 准备脚本参数
            args = [script_path]

            # 添加响应数据作为参数
            response_json = json.dumps(response_data, default=str)
            args.extend(['--response', response_json])

            # 执行外部脚本
            process = await asyncio.create_subprocess_exec(
                'python', *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            # 检查执行结果
            if process.returncode == 0:
                # 脚本成功执行，解析输出
                output = stdout.decode().strip()
                try:
                    result_data = json.loads(output)
                    return bool(result_data.get('success', False))
                except json.JSONDecodeError:
                    # 如果输出不是JSON，尝试解析为布尔值
                    return output.lower() in ('true', '1', 'yes', 'success')
            else:
                self.logger.error(f"外部脚本执行失败: {stderr.decode()}")
                return False

        except Exception as e:
            self.logger.error(f"外部脚本断言执行失败: {e}")
            return False

        finally:
            # 清理临时文件
            if script_content and 'f' in locals():
                import os
                os.unlink(script_path)

    async def _execute_javascript_assertion(self, func_config: Dict, response_data: Dict) -> bool:
        """执行JavaScript断言"""
        js_code = func_config.get('javascript_code', '')
        if not js_code:
            self.logger.warning("JavaScript断言缺少代码")
            return False

        try:
            # 使用Node.js执行JavaScript代码
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                # 创建JavaScript脚本
                js_script = f"""
    const response = {json.dumps(response_data, default=str)};

    // 用户定义的断言代码
    {js_code}

    // 输出结果
    console.log(JSON.stringify({{success: result !== undefined ? Boolean(result) : false}}));
    """
                f.write(js_script)
                js_file_path = f.name

            # 执行Node.js
            process = await asyncio.create_subprocess_exec(
                'node', js_file_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            # 清理临时文件
            import os
            os.unlink(js_file_path)

            if process.returncode == 0:
                output = stdout.decode().strip()
                try:
                    result_data = json.loads(output)
                    return bool(result_data.get('success', False))
                except json.JSONDecodeError:
                    return False
            else:
                self.logger.error(f"JavaScript执行失败: {stderr.decode()}")
                return False

        except Exception as e:
            self.logger.error(f"JavaScript断言执行失败: {e}")
            return False

    async def _execute_sql_assertion(self, func_config: Dict, response_data: Dict) -> bool:
        """执行SQL查询断言"""
        # 这个实现需要数据库连接，这里提供框架
        sql_query = func_config.get('sql_query', '')
        connection_config = func_config.get('connection', {})

        if not sql_query:
            self.logger.warning("SQL断言缺少查询语句")
            return False

        try:
            # 这里应该根据connection_config建立数据库连接
            # 由于数据库依赖较多，这里提供伪代码框架

            # 示例：使用SQLite进行演示
            import sqlite3

            # 创建内存数据库进行测试
            conn = sqlite3.connect(':memory:')
            cursor = conn.cursor()

            # 创建测试表并插入响应数据
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS response_data (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')

            # 插入响应数据
            for key, value in response_data.items():
                if isinstance(value, (str, int, float, bool)):
                    cursor.execute(
                        'INSERT OR REPLACE INTO response_data (key, value) VALUES (?, ?)',
                        (key, str(value))
                    )

            conn.commit()

            # 执行用户SQL查询
            cursor.execute(sql_query)
            result = cursor.fetchone()

            # 关闭连接
            conn.close()

            # 根据查询结果判断断言是否通过
            if result:
                return bool(result[0]) if result else False
            else:
                return False

        except Exception as e:
            self.logger.error(f"SQL断言执行失败: {e}")
            return False

    def _get_custom_functions(self) -> Dict[str, Callable]:
        """获取自定义函数"""
        return {
            'has_status_code': self._has_status_code,
            'has_header': self._has_header,
            'json_path': self._json_path,
            'contains_text': self._contains_text,
            'matches_pattern': self._matches_pattern,
            'is_within_range': self._is_within_range,
            'is_valid_json': self._is_valid_json,
            'response_time_less_than': self._response_time_less_than,
            'array_length': self._array_length,
            'has_field': self._has_field
        }

    # 自定义函数实现
    def _has_status_code(self, response: Dict, expected_code: int) -> bool:
        """检查状态码"""
        return response.get('status_code') == expected_code

    def _has_header(self, response: Dict, header_name: str, expected_value: str = None) -> bool:
        """检查响应头"""
        headers = response.get('headers', {})
        if header_name not in headers:
            return False
        if expected_value is not None:
            return headers.get(header_name) == expected_value
        return True

    def _json_path(self, response: Dict, json_path: str) -> Any:
        """JSON路径查询"""
        try:
            from jsonpath_ng import parse
            body = response.get('body', {})
            expr = parse(json_path)
            matches = expr.find(body)
            return matches[0].value if matches else None
        except:
            return None

    def _contains_text(self, response: Dict, text: str) -> bool:
        """检查是否包含文本"""
        body = response.get('body', {})
        return text in str(body)

    def _matches_pattern(self, response: Dict, pattern: str) -> bool:
        """检查是否匹配正则表达式"""
        body = response.get('body', {})
        return bool(re.search(pattern, str(body)))

    def _is_within_range(self, value: Any, min_val: Any, max_val: Any) -> bool:
        """检查值是否在范围内"""
        try:
            return min_val <= value <= max_val
        except TypeError:
            return False

    def _is_valid_json(self, response: Dict) -> bool:
        """检查是否为有效JSON"""
        try:
            body = response.get('body', {})
            if isinstance(body, (dict, list)):
                return True
            json.loads(str(body))
            return True
        except:
            return False

    def _response_time_less_than(self, response: Dict, max_time: float) -> bool:
        """检查响应时间"""
        elapsed = response.get('elapsed', 0)
        return elapsed < max_time

    def _array_length(self, response: Dict, json_path: str, expected_length: int) -> bool:
        """检查数组长度"""
        try:
            from jsonpath_ng import parse
            body = response.get('body', {})
            expr = parse(json_path)
            matches = expr.find(body)
            if matches:
                array = matches[0].value
                return len(array) == expected_length
            return False
        except:
            return False

    def _has_field(self, response: Dict, field_path: str) -> bool:
        """检查字段是否存在"""
        try:
            from jsonpath_ng import parse
            body = response.get('body', {})
            expr = parse(field_path)
            matches = expr.find(body)
            return bool(matches)
        except:
            return False

    def _get_assertion_actual_value(self, assertion_config: Dict, response_data: Dict) -> Any:
        """获取断言的实际值"""
        assertion_type = assertion_config.get('type')

        if assertion_type == 'status_code':
            return response_data.get('status_code')
        elif assertion_type == 'response_time':
            return response_data.get('elapsed')
        elif assertion_type == 'json_path':
            from jsonpath_ng import parse
            json_path = assertion_config.get('path')
            try:
                expr = parse(json_path)
                matches = expr.find(response_data.get('body', {}))
                return matches[0].value if matches else None
            except:
                return None
        else:
            return 'N/A'

    def _create_error_result(self, task: ExecutionTask, start_time: datetime,
                             error_message: str, logs: List[str]) -> TaskResult:
        """创建错误结果"""
        return TaskResult(
            task_id=task.task_id,
            test_id=task.test_id,
            status=TaskStatus.FAILED,
            duration=(datetime.now() - start_time).total_seconds(),
            start_time=start_time,
            end_time=datetime.now(),
            error_message=error_message,
            logs=logs
        )

    async def close(self):
        """关闭执行器"""
        if self.http_client:
            await self.http_client.close()