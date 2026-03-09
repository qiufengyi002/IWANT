#!/usr/bin/env python3
# 修复stock_app.py的缩进问题

with open('stock_app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 从第601行（索引600）到第997行（索引996）需要缩进4个空格
# 但要排除已经是elif/else的行
output_lines = []
for i, line in enumerate(lines):
    line_num = i + 1
    if 601 <= line_num <= 997:
        # 检查是否是elif或else开头（这些不需要额外缩进）
        stripped = line.lstrip()
        if stripped.startswith('elif ') or stripped.startswith('else:'):
            output_lines.append(line)
        else:
            # 添加4个空格的缩进
            output_lines.append('    ' + line)
    else:
        output_lines.append(line)

# 写回文件
with open('stock_app.py', 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

print("缩进修复完成！")
