import asyncio
import os
import aiohttp
import json
import logging
import base64
import re
from typing import List, Dict, Tuple
from plugins.base_plugin import BasePlugin

class QueryServerPlugin(BasePlugin):
    """
    SCP:SL服务器查询插件 - 完整名称显示版
    """
    
    def __init__(self):
        super().__init__(
            command="CX",
            description="查询SCP:SL服务器状态",
            is_builtin=True
        )
        self.save_dir = "ServerBindQQqun"
        self.api_url = "https://api.scpslgame.com/serverinfo.php"
        self.logger = logging.getLogger("plugin.query_server")
        self.timeout = aiohttp.ClientTimeout(total=15)
        # 匹配所有HTML标签和BBCode标签
        self.tag_regex = re.compile(r'<[^>]+>|\[\/?[a-z]+\]', re.IGNORECASE)
    
    async def handle(self, params: str, user_id: str = None, group_openid: str = None, **kwargs) -> str:
        try:
            file_path = os.path.join(self.save_dir, f"{group_openid}.txt")
            if not os.path.exists(file_path):
                return "⚠️ 本群未绑定服务器\n请先使用「/绑定服务器 Add」命令"
            
            # 读取服务器信息（兼容2个或3个参数）
            server_infos = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.split()
                        if len(parts) >= 2:  # 至少需要server_key和account_id
                            server_info = (parts[0], parts[1], parts[2] if len(parts) >= 3 else None)
                            if server_info not in server_infos:  # 去重
                                server_infos.append(server_info)
            
            if not server_infos:
                return "⚠️ 本群绑定的服务器信息为空"
            
            results = []
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                for server_key, account_id, port in server_infos:
                    try:
                        params = {
                            "id": account_id,
                            "key": server_key,
                            "lo": "true",
                            "players": "true",
                            "list": "true",
                            "info": "true",
                            "version": "true",
                            "flags": "true"
                        }
                        
                        async with session.get(self.api_url, params=params) as resp:
                            if resp.status != 200:
                                results.append(f"🔴 {server_key} 请求失败(HTTP {resp.status})")
                                continue
                            
                            text_data = await resp.text()
                            try:
                                data = json.loads(text_data)
                                results.extend(self._parse_servers(server_key, account_id, data, port))
                            except json.JSONDecodeError:
                                self.logger.error(f"JSON解析失败: {text_data}")
                                results.append(f"⚠️ {server_key} 返回数据格式异常")
                    
                    except asyncio.TimeoutError:
                        results.append(f"⏳ {server_key} 请求超时")
                    except Exception as e:
                        self.logger.error(f"查询异常: {type(e).__name__}", exc_info=True)
                        results.append(f"⚠️ {server_key} 查询异常: {type(e).__name__}")
            
            return "\n\n".join(results) if results else "❌ 所有服务器查询失败"

        except Exception as e:
            self.logger.error(f"系统错误: {str(e)}", exc_info=True)
            return "❌ 系统错误，请稍后再试"

    def _parse_servers(self, server_key: str, account_id: str, data: Dict, port: str = None) -> List[str]:
        """解析服务器数据，完整显示服务器名称"""
        if not data.get("Success", False):
            return [f"🔴 {server_key} 请求失败(API返回失败)"]
        
        servers = data.get("Servers", [])
        if not servers:
            return [f"🟡 {server_key} 无服务器数据"]
        
        server_infos = []
        for i, server in enumerate(servers, 1):
            if not isinstance(server, dict):
                continue
            
            # 端口过滤
            server_port = str(server.get('Port', ''))
            if port and server_port != port:
                continue
            
            # 完整解析服务器名称（去除所有HTML/BBCode标签）
            server_name = self._extract_server_name(server.get('Info', ''))
            
            # 构建响应信息
            info = [
                f"🖥️ 服务器{i} [{account_id}]",
                f"  🏷️ 名称: {server_name}",
                f"  🆔 ID: {server.get('ID', '未知')}",
                f"  🕒 最后在线: {server.get('LastOnline', '未知')}",
                f"  🔌 端口: {server_port}",
                f"  📦 版本: {server.get('Version', '未知')}",
                f"  👥 人数: {server.get('Players', '0/0')}"
            ]
            
            # 服务器特性
            flags = []
            if server.get('FF'): flags.append("💥友伤")
            if server.get('WL'): flags.append("🔒白名单")
            if server.get('Modded'): flags.append("🛠️模组服")
            if flags:
                info.append(f"  🏷️ 特性: {' | '.join(flags)}")
            
            # 玩家列表
            if server.get('Online'):
                players = server.get('PlayersList', [])
                if players:
                    info.append("  🎮 玩家列表:")
                    for j, player in enumerate(players[:10], 1):
                        info.append(f"    {j:2d}. {player.get('nickname', '未知')}")
                    if len(players) > 10:
                        info.append(f"    ...等{len(players)-10}人")
                else:
                    info.append("  🏜️ 当前无玩家在线")
            
            server_infos.append("\n".join(info))
        
        if port and not server_infos:
            return [f"🟡 未找到端口 {port} 的服务器数据"]
        
        return server_infos

    def _extract_server_name(self, info_b64: str) -> str:
        """从Base64编码的Info字段提取完整服务器名称"""
        if not info_b64:
            return "未知服务器"
        
        try:
            # Base64解码
            decoded_info = base64.b64decode(info_b64).decode('utf-8', errors='ignore')
            # 移除所有HTML和BBCode标签
            clean_text = self.tag_regex.sub('', decoded_info)
            # 移除多余空白字符，保留完整内容
            return ' '.join(clean_text.split())
        except Exception as e:
            self.logger.warning(f"解析服务器名称失败: {str(e)}")
            return "名称解析失败"

    def help(self) -> str:
        return (
            "/查询 - 查询服务器状态[确保已经绑定服务器]"
        )