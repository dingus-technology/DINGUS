#!/bin/bash
# entrypoint.sh

echo "

██████╗ ██╗███╗   ██╗ ██████╗ ██╗   ██╗███████╗
██╔══██╗██║████╗  ██║██╔════╝ ██║   ██║██╔════╝
██║  ██║██║██╔██╗ ██║██║  ███╗██║   ██║███████╗
██║  ██║██║██║╚██╗██║██║   ██║██║   ██║╚════██║
██████╔╝██║██║ ╚████║╚██████╔╝╚██████╔╝███████║
╚═════╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚══════╝
                                               
"

# Start FastAPI in the background
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &

# Start Streamlit
streamlit run app/streamlit.py --server.port=8501 --server.address=0.0.0.0