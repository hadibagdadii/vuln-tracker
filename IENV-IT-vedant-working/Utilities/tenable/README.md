# Tenable Security Vulnerability Tracker

## Purpose
~~This script utilizes the Tenable API to automatically create ServiceNow tickets for vulnerabilities. One ticket is created with all the vulnerabilites of that particular IP/asset.~~
This script reads a Tenable vulnerability report CSV file parsing all vulnerabilities by IP/asset and storing them into individual report files or optionally creating individual tickets for each IP/asset its respective vulnerabilities.
Each report or ticket will have details of the IP/asset and details of each vulnerability.

## Installing and Setting up Visual Studio Code (VSCode)

1. **Download and Install VSCode**
   - Visit the [Visual Studio Code](https://code.visualstudio.com/) website.
   - Download the installer for your operating system (Windows, macOS, Linux) and follow the installation instructions.

2. **Install Python Extension**
   - Open VSCode.
   - Go to the Extensions view by clicking on the Extensions icon in the Activity Bar on the side of the window or by pressing `Ctrl+Shift+X`.
   - Search for "Python" in the Extensions view.
   - Click "Install" on the Python extension provided by Microsoft.

3. **Open and Configure Your Project**
   - Open your Python email script project folder in VSCode.
   - Configure the Python interpreter and other settings as needed for your project.

4. **Start Coding**
   - You're all set to start coding! Use VSCode's powerful features and the Python extension for a smooth development experience.

## Installing Git on Windows

1. **Download Git**
   - Visit the [Git website](https://git-scm.com/) to download the Git installer for Windows.

2. **Run the Installer**
   - Double-click the downloaded Git installer to start the installation process.
   - Follow the on-screen instructions in the Git Setup wizard.
   - Choose the default settings unless you have specific preferences.

3. **Verify Installation**
   - Open Command Prompt (cmd) or PowerShell.
   - Type `git --version` and press Enter.
   - If Git is installed correctly, you should see the Git version information displayed.

4. **Configure Git** (Optional)
   - Open Command Prompt (cmd) or PowerShell.
   - Set your Git username using the command:
     ```
     git config --global user.name "Your Name"
     ```
   - Set your Git email address using the command:
     ```
     git config --global user.email "your_email@example.com"
     ```
   - Replace `"Your Name"` with your actual name and `"your_email@example.com"` with your actual email address.

5. **Start Using Git**
   - You can now use Git for version control in your projects. Navigate to your project folder in Command Prompt or PowerShell and use Git commands like `git init`, `git add`, `git commit`, etc.

### Setting Up PowerShell for Script Execution

If you encounter a security error while trying to activate the virtual environment in PowerShell on Windows, you may need to adjust the execution policy to allow running scripts.

Follow these steps to set up PowerShell for script execution:

1. **Open PowerShell as an Administrator**
   - Search for PowerShell in the Start menu.
   - Right-click on "Windows PowerShell" or "PowerShell" and choose "Run as administrator."

2. **Check the Current Execution Policy**
   - Run the following command to view the current execution policy:
     ```
     Get-ExecutionPolicy
     ```

3. **Change the Execution Policy**
   - If the current execution policy is `Restricted`, scripts are not allowed to run.
   - To change the execution policy to allow running scripts signed by a trusted publisher, use the command:
     ```
     Set-ExecutionPolicy RemoteSigned
     ```
   - Confirm the change by entering `Y` when prompted.

4. **Activate the Virtual Environment** (Do not apply this command right now in terminal. For Later Use while setting up python virtual environment)
   - After changing the execution policy, you can activate the virtual environment as usual with the command:
     ```
     . .\env\Scripts\activate
     ```

By following these steps, you'll allow PowerShell to run scripts and be able to activate the virtual environment without encountering security errors.


## Prerequistes (Not applicable for IENV)
- **Tenable API Access**. Obtain access from the ISO by emailing cybersecurity@ucdavis.edu (in the past, Josh Rector was the one in charge of the Tenable service... I'm not sure who it is now. Perhaps Jeff Rowe?)
- Create an **Office365 mailbox/service account**. The best way to do it is submit a request to create a departmental account through [this form](https://ucdavisit.service-now.com/servicehub/?id=ucd_cat_item&sys_id=dfa48d39138707003527bd122244b044); however, it's also possible to create an OU account and mail enable it. COE is migrating away from OU accounts and groups to AD3.
- *(optional)* **InfoBlox API Access**. Obtain access from the NOC by emailing noc@ucdavis.edu and request to allow your Kerberos credentials to make API calls to your VLANs. The script can run without this part - just make sure the `kerbid` field is blank in the config.json file. The VLAN info was included to make it easier for COE's student service desk to more easily route these tickets to the right group/department tech.

## Setup
*Note: these instructions were tested in macOS's Terminal*
*Note: this has been adapted to Windows terminal for IENV*

Follow the [latest training video](https://ucdavis.box.com/s/dlq1ybx82kmeh2uddmdyq1ytt5bhq3b0) for this setup.

## Getting Started

### Download The Script

1. **Create a Directory**
   - Open your terminal or command prompt.
   - Create a directory for GitHub scripts:
     ```
     mkdir GitHubStuff
     cd GitHubStuff
     ```

2. **Clone the Repository**
   - Download the script by cloning the GitHub repository:
     ```
     git clone https://github.com/ucdavis/IENV-IT.git
     ```

3. **Switch to the latest working branch**
   - Once the GitHub Repository is cloned, use the following command in VSCode terminal:
     ```
     git checkout vedant-working
     ```
     This branch contains all the requried files. 

### Set Up Your Environment

1. **Navigate to the Script Directory**
   - Change directory to the script's location:
     ```
     cd ./Utilities/tenable
     ```

2. **Create a Virtual Environment**
   - Create a clean environment for the repository:
     ```
     python -m venv env
     ```
     or
     ```
     python3 -m venv env
     ```
     or
     ```
     py -m venv env
     ```

3. **Activate the Virtual Environment**
   - Activate the virtual environment:
     - macOS:
       ```
       source env/bin/activate
       ```
     - Windows:
       ```
       . .\env\Scripts\activate
       ```

4. **Install Required Packages**
   - Install necessary Python packages:
     ```
     pip install -r requirements.txt
     ```

### Get Tenable vulns.csv (IENV: provided by George Scheer)
Obtain the latest vulns.csv file or if testing use the vulns-test.csv from the [IE Vulns Box folder](https://ucdavis.box.com/s/75tnep8agxw3nuovq79r1c9qrf2w9maz).  
Or generate the latest vulnerabilities as a vulns.csv file on from Tenable (requires admin access).
1. Navigate to https://security-center.ucdavis.edu/ and log in
2. Analysis > Vulnerabilities (*Note: To view a specific scan result, go to Scans > Scan Results > click the scan you'd like to see the vulnerabilites from. Currently, COE has a credentialed scan set up for all our VLANs that we run weekly.*)
3. If desired, click the blue >> on the left to filter the vulnerabilities. I'd suggest setting exploit available to yes and the severity to medium/high/critical. At minimum, you probably don't want to open tickets for those categorized as Info. For COE, I use the following filters:
- Severity = Critical or High && Vulnerability Discovered more than 30 days ago
- Severity = Medium, Low, or Info && Vulnerability Priority Rating between 6 and 10 && Vulnerability Discovered more than 30 days ago
You may also want to choose "Cumulative" on the right side as that contains currently vulnerable vulnerabilities, including recast, accepted, or previously mitigated vulnerabilities per https://docs.tenable.com/tenablesc/Content/CumulativeMitigatedVulnerabilities.htm.
4. Make sure you change the dropdown on the left to Vulnerability List before clicking Export > Export as CSV

### Set Environment Variables (IENV: skip)
I've included **set_envs.sh** to assist with this. You'll need to replace the XXX in the file with your Tenable API keys. Before running the script, you'll need to run `source set_envs.sh` to activate it/set the appropriate environment variables. It will last until that Terminal window's session ends.

### Edit The Configuration File (example provided for IENV)
I've included **config.json** with sample values for your convenience, but I'm happy to switch this to command line arguments if you find that easier. I figured you'd only need to set this once, so it would be annoying to have to keep typing in all the command line arguments (arguably, you could set up some sort of alias, but I digress). Please only change the values of the following variables:
- `kerbid` (optional) Leave blank if you don't want your vlan information included. Otherwise, replace the default value with the username / Kerberos ID of the account that has InfoBlox API access.
- `sender` The email you want the ticket to come from (e.g. coesecvuln@ou.ad3.ucdavis.edu) (not applicable for IENV-IT)
- `receiver` The email for the ServiceNow group you want these tickets to route to (e.g. coeithelp@ucdavis.edu) (removed) (not applicable for IENV-IT)
- `signature` How you'd like the SN vulnerability tickets to be signed. If you want a signature with multiple lines, use \n to separate the lines (e.g. "Shannon Chee\nCOE IT Security Team") (not applicable for IENV-IT)
- `csv_filename` The full path and filename of the vulnerabilities .csv from Tenable (e.g. "/Users/shchee/GitHubStuff/coe_tenable_security_vulnerability_tracker/vulns.csv") or just the filename if you copied it into the same directory you're running the script in (for IENV it will be in a separate folder where the output files will be stored)
- `folder` absolute/full path of the folder to write the output files to (ex. "C:/Users/Ruprabhu/Documents/dev/vulns-2023-5-16/", "/Users/Ruprabhu/Desktop/....)
Note: on Windows try prefixing the path with "C:" and ensure that the path uses forward slashes for directory/path navigation



## Example Config File
Create a file named config.json under **"Utilities/tenable/"**

An ideal config file looks as follows:

```json
{
  "kerberosID": "ie-security",
  "sender": "ie-security@ucdavis.edu",
  "password": "ie-security_app_password",
  "receiver": "ie-securityp@ucdavis.edu",
  "signature": "IE Security",
  "csv_file": "C:/Users/your_username/Box/IENV-IT/Security/VMP/Vulns/2024-05-03.csv",
  "folder": "C:/Users/your_username/Box/IENV-IT/Security/VMP/Vulns/"
}
```

App password for ie-security@ucdavis.edu will be provided.  See instructions below for general info on app passwords.

Instructions for generating google app password for passing double factor authetication is given below. 
Follow those instructions if app password not provided already.

# Setting up Google App Passwords for Python Email Script

This guide provides step-by-step instructions for setting up Google App Passwords to skip two-factor authentication (2FA) when sending emails using a Python script.

## Prerequisites

Before proceeding, make sure you have the following:

- A Google account with two-factor authentication enabled.
- Python installed on your system.
- Access to the Google Account settings.

## Steps to Set Up Google App Passwords

1. **Access Google Account Settings**
   - Open your web browser and go to [https://myaccount.google.com](https://myaccount.google.com).
   - Sign in with your Google account credentials.

2. **Navigate to Security Settings**
   - In the Google Account dashboard, locate and click on the "Security" tab in the left sidebar.

3. **Enable Two-Factor Authentication (if not already enabled)**
   - If two-factor authentication (2FA) is not enabled, click on "2-Step Verification" and follow the on-screen instructions to set it up.

4. **Generate App Password**
   - In the "Security" tab, scroll down to the "Signing in to Google" section.
   - Look for the "App passwords" option and click on it. You may need to verify your identity again.
   - If prompted, select the app and device you want to generate the app password for. Choose "Other (Custom name)" for the app.
   - Enter a custom name for the app password (e.g., "Python Email Script") and click on "Generate."

5. **Copy and Use the App Password**
   - Google will generate a unique 16-character app password.
   - Copy this app password and store it securely. **Note: You won't be able to see this password again, so make sure to copy it now.**
   - Use this app password in your Python script to authenticate when sending emails.


## Run the Script (IENV)
Make sure you're on a campus network/VPN before running the script. Otherwise, you won't be able to connect to Tenable. (not applicable to IENV)
```python3 or py .\tenable-terminal.py .\config.json``` (Windows) (assuming you are in the tenable folder upon execution) This will generate just the output files.
```python3 or py .\tenable-terminal.py .\config.json --send-emails``` (Windows) (assuming you are in the tenable folder upon execution) This will generate the output files and send emails according to the address given in config file.


Script help message/usage:
```
usage: tenable.py [-h] configfile

This script creates ServiceNow tickets for Tenable vulnerabilities.

positional arguments:
  configfile  Use the full file path for the JSON config file or move it to the same directory
  --send-emails Flag to send emails

optional arguments:
  -h, --help  show this help message and exit



  - during installation:
  - need to install python if you already dont have it, and make to include it in the path during the install (there is a checkbox)
  - vscode does have a link for a Git installation, also make to include it in the path
  - you might have to restart vscode and any other command prompts after installing these two so that the path/environment variables are updated
  - switching to the vuln tracker branch: "git checkout -b vuln-tracker: the message afterwards shoulld indicate that its tracking origin/vuln-tracker"
  - 
```
