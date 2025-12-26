import os
import yaml
from typing import Dict, Any

class Config:
    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._config is None:
            self.load_config()

    def load_config(self) -> None:
        """加载配置文件"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                 'config', 'config.yaml')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
        except Exception as e:
            raise Exception(f"加载配置文件失败: {str(e)}")

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        try:
            keys = key.split('.')
            value = self._config
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    @property
    def export_dir(self) -> str:
        """获取导出目录"""
        return self.get('paths.export_dir')

    @property
    def template_dir(self) -> str:
        """获取模板目录"""
        return self.get('paths.template_dir')

    @property
    def log_dir(self) -> str:
        """获取日志目录"""
        return self.get('paths.log_dir')

    @property
    def price_template_config(self) -> Dict:
        """获取价格表模板配置"""
        return self.get('templates.price_template', {})

    @property
    def delivery_template_config(self) -> Dict:
        """获取送货单模板配置"""
        return self.get('templates.delivery_template', {})

    @property
    def export_config(self) -> Dict:
        """获取导出配置"""
        return self.get('export', {})

    @property
    def logging_config(self) -> Dict:
        """获取日志配置"""
        return self.get('logging', {})

# 全局配置实例
config = Config()