echo "Please run as sudo,press enter to confirm..."
read
echo "Confirmed, initiating env..."
python3 -m venv venv
echo "Activating env..."
source venv/bin/activate
echo "Installing dependencies..."
pip install pyqt6 PyQtWebEngine
chmod +x start.sh
deactivate
echo "Done, run start.sh to launch the browser!"