Steps to set the environment:
- First install Python in your local workstation.
- Navigate to the folder "Tidal_Model"
- Inside the folder path, using command line create a virtual environment using the cmd: python -m venv venv
- Activate the virtual environment using the cmd: venv\Scripts\activate
- Once venv is activated, upgrade pip using the cmd: python -m pip install --upgrade pip
- Run this cmd to install all the required libraries to run the script: pip install -r requirements.txt
- Once all libraries are installed you can run the script using the cmd: python EOT20TidalModelling.py


- [Imp: To run the script successfully, we need to configure Tidal model constituents path. First we need to download the .zip file from this link: https://www.seanoe.org/data/00683/79489/data/85762.zip. After unzipping it we need to provide the correct path in the script.]

- Output of the script is .csv file and .png image