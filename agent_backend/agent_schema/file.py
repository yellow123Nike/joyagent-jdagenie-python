from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class File:
    """
    File 的 Docstring
    oss_url:文件在 对象存储（OSS）中的访问地址
    domain_url:文件对应的 域名访问地址，一般是对外可访问的 HTTP/HTTPS URL
    file_name:文件在系统中的 展示名称
    file_size:文件大小，单位通常为 字节
    description:文件的 文字描述或备注信息
    origin_file_name:文件的 原始文件名（用户上传时的名称
    origin_oss_url:文件在 OSS 中的 原始存储地址
    origin_domain_url:文件的 原始对外访问域名地址
    is_internal_file:标识该文件是否为 系统内部文件
    """
    oss_url: Optional[str] = None
    domain_url: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    description: Optional[str] = None
    origin_file_name: Optional[str] = None
    origin_oss_url: Optional[str] = None
    origin_domain_url: Optional[str] = None
    is_internal_file: Optional[bool] = None

    def getOssUrl(self) -> Optional[str]:
        return self.oss_url

    def getDomainUrl(self) -> Optional[str]:
        return self.domain_url

    def getFileName(self) -> Optional[str]:
        return self.file_name

    def getFileSize(self) -> Optional[int]:
        return self.file_size

    def getDescription(self) -> Optional[str]:
        return self.description

    def getOriginFileName(self) -> Optional[str]:
        return self.origin_file_name

    def getOriginOssUrl(self) -> Optional[str]:
        return self.origin_oss_url

    def getOriginDomainUrl(self) -> Optional[str]:
        return self.origin_domain_url

    def getIsInternalFile(self) -> Optional[bool]:
        return self.is_internal_file
