from datetime import date
import locale
import calendar


class DateUtil:
    """
        获取当前日期
    """
    @staticmethod
    def current_date_info() -> str:
        # 获取当前日期
        current_date = date.today()
        # 年月日
        year = current_date.year
        month = current_date.month
        day = current_date.day
        # 设置本地化（用于星期显示）
        try:
            locale.setlocale(locale.LC_TIME, "")
        except locale.Error:
            # 如果运行环境不支持本地 locale，忽略
            pass
        # 获取星期几（完整名称）
        weekday_index = current_date.weekday()  # Monday=0
        weekday_name = calendar.day_name[weekday_index]
        # 格式化日期：yyyy年M月d日
        formatted_date = f"{year}年{month}月{day}日"

        return f"今天是 {formatted_date} {weekday_name}"

if __name__=="__main__":
     print(DateUtil.current_date_info())
