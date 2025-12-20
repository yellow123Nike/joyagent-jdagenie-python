from dataclasses import dataclass
from typing import Optional


@dataclass
class FileInformation:
    # ========= 当前态文件信息（系统加工后） =========
    file_name: Optional[str] = None          # 当前系统内文件名
    file_desc: Optional[str] = None          # 文件业务描述
    oss_url: Optional[str] = None            # 对象存储内部地址
    domain_url: Optional[str] = None         # 对外可访问地址
    file_size: Optional[int] = None          # 文件大小（字节）
    file_type: Optional[str] = None          # 文件类型 / MIME / 扩展名

    # ========= 原始态文件信息（可回溯） =========
    origin_file_name: Optional[str] = None   # 原始文件名
    origin_file_url: Optional[str] = None    # 原始业务访问地址
    origin_oss_url: Optional[str] = None     # 原始对象存储地址
    origin_domain_url: Optional[str] = None  # 原始对外访问地址
