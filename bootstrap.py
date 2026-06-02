import os
import sys
import streamlit.web.bootstrap

if __name__ == '__main__':
    # Determine the directory where app.py is located.
    # In PyInstaller, frozen resources are extracted to sys._MEIPASS.
    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
    app_path = os.path.join(base_dir, 'app.py')
    
    # Setup Streamlit arguments
    flag_options = {
        "server.port": 8501,
        "global.developmentMode": False,
        "server.fileWatcherType": "none",
    }
    
    streamlit.web.bootstrap.load_config_options(flag_options=flag_options)
    flag_options["_is_running_with_streamlit"] = True
    
    # Run the application
    streamlit.web.bootstrap.run(app_path, "streamlit run", [], flag_options)
