from typing import Dict, List, Optional
from testGeneration.test_models import APIEndpoint, APIParameter, ParameterType
import re
import json


class OpenAPIContractParser:
    def __init__(self):
        self.schema_cache = {}
        self.host_url = ''

    def parse_openapi_spec(self, openapi_spec: Dict) -> Dict[str, List[APIEndpoint]]:
        """解析OpenAPI规范"""
        endpoints = {}

        self.host_url = openapi_spec.get('host')
        service_name = self._extract_service_name(self.host_url)

        for path, path_item in openapi_spec.get('paths', {}).items():
            for method, operation in path_item.items():
                if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']:
                    endpoint = self._parse_operation(path, method.upper(), operation, openapi_spec)

                    if service_name not in endpoints:
                        endpoints[service_name] = []
                    endpoints[service_name].append(endpoint)

        return endpoints

    def parse_host_url(self):
        if self.host_url:
            return self.host_url

    def _parse_operation(self, path: str, method: str, operation: Dict, full_spec: Dict) -> APIEndpoint:
        """解析单个API操作"""
        parameters = self._parse_parameters(operation.get('parameters', []), full_spec)
        request_body = self._parse_request_body(operation, full_spec)
        responses = self._parse_responses(operation.get('responses', {}), full_spec)

        return APIEndpoint(
            path=path,
            method=method,
            summary=operation.get('summary', 'No summary'),
            parameters=parameters,
            request_body=request_body,
            responses=responses,
            security=operation.get('security', []),
            tags=operation.get('tags', []),
            deprecated=operation.get('deprecated', False)
        )

    def _parse_parameters(self, parameters: List, full_spec: Dict) -> List[APIParameter]:
        """解析API参数"""
        parsed_params = []

        for param in parameters:
            schema = self._resolve_reference(param.get('schema', {}), full_spec)

            if schema:
                #print('There is a schema!')
                param_obj = APIParameter(
                    name=param.get('name', ''),
                    param_type=self._map_schema_type(schema.get('type', 'string')),
                    position=param.get('in'),
                    required=param.get('required', False),
                    min_value=schema.get('minimum'),
                    max_value=schema.get('maximum'),
                    min_length=schema.get('minLength'),
                    max_length=schema.get('maxLength'),
                    pattern=schema.get('pattern'),
                    enum_values=schema.get('enum', []),
                    format=schema.get('format'),
                    example=schema.get('example'),
                    description=param.get('description')
                )
            else:
                #print('There is no schema!')
                param_obj = APIParameter(
                    name=param.get('name', ''),
                    param_type=param.get('type'),
                    position=param.get('in'),
                    required=param.get('required', False),
                    min_value=param.get('minimum'),
                    max_value=param.get('maximum'),
                    min_length=param.get('minLength'),
                    max_length=param.get('maxLength'),
                    pattern=param.get('pattern'),
                    enum_values=param.get('enum', []),
                    format=param.get('format'),
                    example=param.get('default'),
                    description=param.get('description')
                )
            parsed_params.append(param_obj)

        return parsed_params

    def _parse_request_body(self, operation: Dict, full_spec: Dict) -> Optional[Dict]:
        """解析请求体"""
        # if not request_body:
        #     return None
        parameters = operation.get('parameters', [])
        for param in parameters:
            if 'body' == param.get('in'):
                content =  operation.get('consumes')
                if content:
                    for content_type in ['application/json', 'application/xml', 'text/plain']:
                        if content_type in content:
                            schema = param.get('schema', {})
                            return self._resolve_reference(schema, full_spec)
        # content = request_body.get('content', {})
        # for content_type in ['application/json', 'application/xml', 'text/plain']:
        #     if content_type in content:
        #         schema = content[content_type].get('schema', {})
        #         return self._resolve_reference(schema, full_spec)

        return None

    def _parse_responses(self, responses: Dict, full_spec: Dict) -> Dict:
        """解析响应定义"""
        parsed_responses = {}

        for status_code, response_def in responses.items():
            # content = response_def.get('content', {})
            # if 'application/json' in content:
            #     schema = content['application/json'].get('schema', {})
            #     parsed_responses[status_code] = self._resolve_reference(schema, full_spec)
            schema = response_def.get('schema', {})
            parsed_responses[status_code] = self._resolve_reference(schema, full_spec)

        return parsed_responses

    def _resolve_reference(self, schema: Dict, full_spec: Dict) -> Dict:
        """解析$ref引用"""
        if '$ref' in schema:
            ref_path = schema['$ref'].replace('#/', '').split('/')
            resolved = full_spec
            for part in ref_path:
                resolved = resolved.get(part, {})
            return resolved
        return schema

    def _map_schema_type(self, schema_type: str) -> ParameterType:
        """映射Schema类型到参数类型"""
        type_map = {
            'string': ParameterType.STRING,
            'integer': ParameterType.INTEGER,
            'number': ParameterType.NUMBER,
            'boolean': ParameterType.BOOLEAN,
            'array': ParameterType.ARRAY,
            'object': ParameterType.OBJECT
        }
        return type_map.get(schema_type, ParameterType.STRING)

    # def _extract_service_name(self, path: str) -> str:
    #     """从路径中提取服务名称"""
    #     # 多种路径模式匹配
    #     patterns = [
    #         r'/api/([^/]+)/',
    #         r'/([^/]+)/api/',
    #         r'/v\d+/([^/]+)/',
    #         r'/([^/]+)/v\d+/'
    #     ]
    #     for pattern in patterns:
    #         match = re.search(pattern, path)
    #         if match:
    #             return match.group(1)
    #     return 'default-service'

    def _extract_service_name(self, path: str) -> str:
        """从路径中提取服务名称"""
        if not path:
            return 'default-service'
        # 多种路径模式匹配
        pattern = '\.'
        split_list = re.split(pattern, path)
        if split_list:
            return split_list[0]
        return 'default-service'