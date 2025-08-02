import os
import logging
from typing import List, Tuple
from plugins.base_plugin import BasePlugin
from auth_manager import auth_manager

class BindServerPlugin(BasePlugin):
    """
    SCP:SL服务器管理插件 - 管理员专用
    命令格式：/绑定服务器 [Add/Remove/Check] [serverKey] [accountId] [Port(可选)]
    """
    
    def __init__(self):
        super().__init__(
            command="绑定服务器",
            description="SCP:SL服务器管理(仅限群管理)",
            is_builtin=True
        )
        self.save_dir = "ServerBindQQqun"
        os.makedirs(self.save_dir, exist_ok=True)
        self.logger = logging.getLogger("plugin.bind_server")
    
    async def handle(self, params: str, user_id: str = None, group_openid: str = None, **kwargs) -> str:
        try:
            # 检查权限和群聊环境
            if not auth_manager.is_admin(user_id):
               return "权限不足，此命令仅限管理员使用"
            
            # 解析参数
            parts = params.strip().split()
            if len(parts) < 1:
                return self._get_usage_help()
            
            mode = parts[0].lower()
            
            # 处理不同模式
            if mode == "add":
                if len(parts) < 3:
                    return "⚠️ 参数错误！格式：/绑定服务器 Add serverKey accountId [Port]"
                port = parts[3] if len(parts) >= 4 else None
                return await self._add_server(group_openid, parts[1], parts[2], port)
            
            elif mode == "remove":
                if len(parts) != 3:
                    return "⚠️ 参数错误！格式：/绑定服务器 Remove serverKey accountId"
                return await self._remove_server(group_openid, parts[1], parts[2])
            
            elif mode == "check":
                if len(parts) != 3:
                    return "⚠️ 参数错误！格式：/绑定服务器 Check serverKey accountId"
                return await self._check_server(group_openid, parts[1], parts[2])
            
            else:
                return self._get_usage_help()
                
        except Exception as e:
            self.logger.error(f"操作失败: {str(e)}", exc_info=True)
            return "❌ 操作失败，请检查日志"

    async def _add_server(self, group_id: str, server_key: str, account_id: str, port: str = None) -> str:
        """添加服务器信息（支持可选端口）"""
        file_path = os.path.join(self.save_dir, f"{group_id}.txt")
        servers = await self._load_servers(group_id)
        
        # 检查是否已存在（仅检测前两个参数）
        for record in servers:
            if record[0] == server_key and record[1] == account_id:
                return "ℹ️ 该服务器信息已存在"
        
        # 构建写入内容
        record = f"{server_key} {account_id}"
        if port:
            record += f" {port}"
        record += "\n"
        
        # 添加新记录
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(record)
        
        response = f"✅ 已添加服务器\nKey: {server_key}\nAccountID: {account_id}"
        if port:
            response += f"\nPort: {port}"
        return response

    async def _remove_server(self, group_id: str, server_key: str, account_id: str) -> str:
        """移除服务器信息（仍按前两个参数匹配）"""
        servers = await self._load_servers(group_id)
        new_servers = [r for r in servers if r[0] != server_key or r[1] != account_id]
        
        if len(new_servers) == len(servers):
            return "ℹ️ 未找到匹配的服务器信息"
        
        file_path = os.path.join(self.save_dir, f"{group_id}.txt")
        with open(file_path, 'w', encoding='utf-8') as f:
            for record in new_servers:
                line = ' '.join(record) + '\n'
                f.write(line)
        
        return f"✅ 已移除服务器\nKey: {server_key}\nAccountID: {account_id}"

    async def _check_server(self, group_id: str, server_key: str, account_id: str) -> str:
        """检查服务器信息（仍按前两个参数匹配）"""
        servers = await self._load_servers(group_id)
        exists = any(r[0] == server_key and r[1] == account_id for r in servers)
        
        if exists:
            return f"🟢 服务器存在\nKey: {server_key}\nAccountID: {account_id}"
        return f"🔴 服务器不存在\nKey: {server_key}\nAccountID: {account_id}"

    async def _load_servers(self, group_id: str) -> List[Tuple[str, ...]]:
        """加载服务器列表（支持可变参数）"""
        file_path = os.path.join(self.save_dir, f"{group_id}.txt")
        if not os.path.exists(file_path):
            return []
        
        servers = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split()
                    if len(parts) >= 2:  # 至少需要两个参数
                        servers.append(tuple(parts))
        return servers

    def _get_usage_help(self) -> str:
        """使用帮助"""
        return (
            "SCPSL服务器绑定命令使用指南：\n"
            "<1>添加服务器：/绑定服务器 Add <serverKey> <accountId> [Port(可选)]\n"
            "<2>移除服务器：/绑定服务器 Remove <serverKey> <accountId>\n"
            "<3>检查服务器：/绑定服务器 Check <serverKey> <accountId>\n"
        )

    def help(self) -> str:
        return self._get_usage_help()