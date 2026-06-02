import os

file_path = 'e:/Fantasy Football/app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

tab3_start = -1
for i, line in enumerate(lines):
    if '# --- TAB 3: AI DATA ASSISTANT ---' in line:
        tab3_start = i
        break

ai_code_lines = lines[tab3_start+1:]
unindented_ai_code = []
for line in ai_code_lines:
    if line.startswith('with tab_ai:'):
        continue
    if line.startswith('    '):
        unindented_ai_code.append(line[4:])
    else:
        unindented_ai_code.append(line)

new_function = ['def render_ai_cohost():\n'] + unindented_ai_code

lines = lines[:tab3_start+1]
lines.append('with tab_ai:\n')
lines.append('    render_ai_cohost()\n')

sidebar_start = -1
for i, line in enumerate(lines):
    if '# --- SIDEBAR CONFIGURATION ---' in line:
        sidebar_start = i
        break

injection = new_function + [
    '\n',
    'view_mode = st.query_params.get("view", "default")\n',
    'if view_mode == "broadcast":\n',
    '    st.markdown("""\n',
    '        <style>\n',
    '            [data-testid="stSidebar"] {display: none !important;}\n',
    '            [data-testid="stHeader"] {display: none !important;}\n',
    '            .block-container {padding-top: 2rem !important; padding-bottom: 2rem !important;}\n',
    '        </style>\n',
    '    """, unsafe_allow_html=True)\n',
    '    render_ai_cohost()\n',
    '    st.stop()\n',
    '\n'
]

lines = lines[:sidebar_start] + injection + lines[sidebar_start:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
