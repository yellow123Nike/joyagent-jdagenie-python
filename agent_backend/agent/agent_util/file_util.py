from typing import List, Optional
from agent_backend.agent.agent_schema.file import File


class FileUtil:

    @staticmethod
    def format_file_info(files: List[File], filter_internal_file: bool) -> str:
        """
        把一组 File 对象，按统一、可读、可直接注入 Prompt 的文本格式整理出来，并在必要时过滤掉内部文件
        """
        lines = []

        for file in files:
            #控制“哪些文件对 Agent 可见”
            if filter_internal_file and file.getIsInternalFile():
                continue
            # originOssUrl 优先，其次 ossUrl
            file_url = (
                file.getOriginOssUrl()
                if file.getOriginOssUrl() is not None and file.getOriginOssUrl() != ""
                else file.getOssUrl()
            )
            lines.append(
                f"fileName:{file.getFileName()} "
                f"fileDesc:{file.getDescription()} "
                f"fileUrl:{file_url}"
            )

        return "\n".join(lines) + ("\n" if lines else "")


if __name__=="__main__":
    files = [
        File(
            file_name="contract.pdf",
            description="客户合同文件",
            oss_url="oss://bucket/contract.pdf",
            origin_oss_url="https://cdn.example.com/contract.pdf",
            is_internal_file=False,
        ),
        File(
            file_name="internal.docx",
            description="系统内部说明",
            oss_url="oss://bucket/internal.docx",
            is_internal_file=True,
        ),
        File(
            file_name="report.xlsx",
            description="2024年财务报表",
            oss_url="oss://bucket/report.xlsx",
            origin_oss_url="",
            is_internal_file=False,
        ),
    ]

    # 开启内部文件过滤
    result = FileUtil.format_file_info(files, filter_internal_file=True)
    print("=== filter_internal_file=True ===")
    print(result)

    # 关闭内部文件过滤
    result_all = FileUtil.format_file_info(files, filter_internal_file=False)
    print("=== filter_internal_file=False ===")
    print(result_all)
    