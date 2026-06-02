import os

file_path = 'e:/Fantasy Football/app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

in_func = False
for i in range(len(lines)):
    line = lines[i]
    if line.startswith('def render_ai_cohost():'):
        in_func = True
        continue
    
    if in_func:
        if line.startswith('view_mode = st.query_params.get("view", "default")'):
            in_func = False
            continue
        if line.strip() != '':
            lines[i] = '    ' + line
            
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
