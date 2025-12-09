import pandas as pd
import json
import io
import re

def clean_sheet_name(name):
    """
    清洗Excel Sheet名称，移除非法字符，限制长度
    Excel限制：
    1. 最长31字符
    2. 不能包含: \ / ? * [ ] :
    """
    if not name:
        return "Sheet1"
    
    # 替换非法字符为下划线
    clean_name = re.sub(r'[\\/?*\[\]:]', '_', str(name))
    
    # 截取前30位
    return clean_name[:30]

def format_session_data(session):
    """
    将单个会话对象转换为扁平的字典
    """
    # 1. 基础信息
    row_data = {
        "序号ID": str(session.id),
        # 尝试多个可能的字段名
        "用户ID": getattr(session, 'participant_id', None) or getattr(session, 'visitor_uuid', None) or getattr(session, 'user_id', 'Unknown'),
        "开始时间": getattr(session, 'created_at', None) or getattr(session, 'start_time', ''),
        "结束时间": getattr(session, 'end_time', None) or getattr(session, 'ended_at', ''),
        "备注": getattr(session, 'note', '') or "",
    }

    # 2. 处理转录内容 (Transcript)
    transcript = getattr(session, 'transcript', [])
    
    # 如果是字符串 (JSON格式)，尝试解析
    if isinstance(transcript, str):
        try:
            transcript = json.loads(transcript)
        except:
            transcript = []
            
    # 如果是None，转为空列表
    if transcript is None:
        transcript = []

    question_index = 1
    answer_index = 1
    
    for record in transcript:
        # 确保 record 是字典
        if not isinstance(record, dict):
            continue
            
        role = record.get("role")
        content = record.get("content", "")

        # 根据角色填充
        if role in ["system", "assistant", "ai"]:
            row_data[f"问题{question_index}"] = content
            question_index += 1
        elif role == "user":
            row_data[f"回答{answer_index}"] = content
            answer_index += 1

    return row_data


def generate_excel_bytes(sessions, filename_prefix="export"):
    """
    生成Excel文件字节流
    """
    output = io.BytesIO()
    
    # 使用ExcelWriter
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        all_data = []
        
        # 遍历所有会话，收集所有数据
        if sessions:
            for i, session in enumerate(sessions):
                try:
                    # 1. 格式化数据
                    flat_data = format_session_data(session)
                    
                    # 2. 添加到数据列表
                    all_data.append(flat_data)
                    
                except Exception as e:
                    print(f"⚠️ [Excel导出警告] 会话 {session.id} 导出失败: {str(e)}")
                    # 继续下一个，不要中断
                    continue
        
        # 3. 创建包含所有数据的DataFrame
        if all_data:
            # 转换为DataFrame，所有会话在同一个sheet中
            df = pd.DataFrame(all_data)
            
            # 4. 写入单个Sheet
            df.to_excel(writer, sheet_name="访谈内容汇总", index=False)
        else:
            # 没有有效数据，创建一个提示Sheet
            error_df = pd.DataFrame([{"状态": "无有效数据导出", "原因": "没有选中的会话或数据解析失败"}])
            error_df.to_excel(writer, sheet_name="导出报告", index=False)

    output.seek(0)
    return output