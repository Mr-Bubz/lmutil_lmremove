import os
import sys
import re
import subprocess
import time

def check_lmutil_path():
    """Check for lmutil.exe in UGFLEXLM directory or PATH environment variable."""
    ugii_base_dir = os.getenv('UGII_BASE_DIR')
    ugflexlm_path = None

    if ugii_base_dir:
        ugflexlm_path = os.path.join(ugii_base_dir, 'UGFLEXLM', 'lmutil.exe')
        if os.path.exists(ugflexlm_path):
            print("lmutil.exe found in UGII_BASE_DIR\\UGFLEXLM directory.")
            return ugflexlm_path

    # Check the PATH environment variable
    path_dirs = os.environ['PATH'].split(';')
    for dir in path_dirs:
        lmutil_path = os.path.join(dir, 'lmutil.exe')
        if os.path.exists(lmutil_path):
            print("lmutil.exe found in the PATH environment variable.")
            return lmutil_path

    print("lmutil.exe not found.")
    print("Please add the directory containing lmutil.exe to the PATH environment variable manually.")
    time.sleep(5)
    sys.exit(1)

def check_splm_license_server():
    """Check for SPLM_LICENSE_SERVER environment variable."""
    splm_license_server = os.getenv('SPLM_LICENSE_SERVER')

    if not splm_license_server:
        print("SPLM_LICENSE_SERVER environment variable not set.")
        print("Please set the SPLM_LICENSE_SERVER environment variable.")
        time.sleep(5)
        sys.exit(1)

    print("SPLM_LICENSE_SERVER environment variable set to ", splm_license_server)
    return splm_license_server

def run_lmstat(lmutil_path, splm_license_server):
    """Run lmutil lmstat command and save the output to a file."""
    try:
        command = [lmutil_path, 'lmstat', '-c', splm_license_server, '-f', 'nx_design_token']
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        with open('C:\\temp\\lmutil_output.txt', 'w') as file:
            file.write(result.stdout)

        print("Output saved to 'C:\\temp\\lmutil_output.txt'")
        return 'C:\\temp\\lmutil_output.txt'

    except subprocess.CalledProcessError as e:
        print(f"Error running lmutil: {e}")
        time.sleep(5)
        sys.exit(1)

def parse_lmstat_output(file_path):
    """Parse lmstat output to extract and display user information."""
    usernames = []
    hostnames = []
    displaynames = []
    featurenames = []
    start_times = []
    license_nums = []

    try:
        with open(file_path, "r") as file:
            for line in file:
                if "start" in line:
                    parts = line.strip().split(",")

                    match = re.match(r'^(\S+)\s+(\S+)\s+(\S+)\s+(\S+)', parts[0])
                    if match:
                        usernames.append(match.group(1))
                        hostnames.append(match.group(2))
                        displaynames.append(match.group(3))
                        featurenames.append(match.group(4))

                    match_start_time = re.search(r'start (.+)', parts[1])
                    if match_start_time:
                        start_times.append(match_start_time.group(1).strip())

                    match_license_num = re.search(r'(\d+ licenses?)', parts[2])
                    if match_license_num:
                        license_nums.append(match_license_num.group(1))

        # Check if no users are currently holding an nx_design_token license
        if not usernames:
            print("No users are currently pulling an nx_design_token license on", splm_license_server)
            time.sleep(5)  # Delay for 5 seconds
            sys.exit(0)

        print(f"{'#':<5} {'Username':<20} {'Hostname':<20} {'Displayname':<20} {'Featurename':<30} {'Start Time':<20} {'License Number':<15}")
        print("-" * 120)
        for i, (username, hostname, displayname, featurename, start_time, license_num) in enumerate(zip(usernames, hostnames, displaynames, featurenames, start_times, license_nums), 1):
            print(f"{i:<5} {username:<20} {hostname:<20} {displayname:<20} {featurename:<30} {start_time:<20} {license_num:<15}")

    except FileNotFoundError:
        print("Error: File not found.")
        time.sleep(5)
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(5)
        sys.exit(1)

    return usernames, hostnames, displaynames

def kick_off_tokens(selected_users, usernames, hostnames, displaynames, splm_license_server, lmutil_path):
    """Kick token licenses from selected users."""
    for index in selected_users:
        try:
            print(f"Attempting to kick user {usernames[index]}")
            command = [lmutil_path, 'lmremove', '-c', splm_license_server, 'nx_design_token', usernames[index], hostnames[index], displaynames[index]]
            subprocess.run(command, capture_output=True, text=True, check=True)
            print(f"Token license kicked off for user {usernames[index]}")
        except subprocess.CalledProcessError as e:
            print(f"Error kicking off token for user {usernames[index]}: {e}")

def get_user_input():
    """Get user input for selecting users to kick off token licenses."""
    while True:
        user_input = input("\nEnter the numbers of the users to kick off their token licenses (comma-separated, e.g., '1,2,3' or '1-3' or 'all'): ")

        selected_users = []
        try:
            if user_input.lower() == 'all':
                selected_users = list(range(len(usernames)))
                break
            else:
                parts = user_input.split(',')
                for part in parts:
                    if '-' in part:
                        start, end = map(int, part.split('-'))
                        selected_users.extend(range(start-1, end))
                    else:
                        selected_users.append(int(part) - 1)

                if any(index < 0 or index >= len(usernames) for index in selected_users):
                    raise ValueError("Invalid user number. Please enter valid user numbers.")

                break

        except ValueError as e:
            print(f"Error: {e}\nPlease enter valid user numbers.\n")

    return selected_users

def run_script_again():
    """Prompt user to run the script again."""
    while True:
        choice = input("\nDo you want to run the script again? (yes/no): ").lower()
        
        if choice in ['yes', 'no']:
            return choice == 'yes'
        else:
            print("Please enter 'yes' or 'no'.")

if __name__ == "__main__":
    first_run = True
    
    while True:
        if not first_run:
            if run_script_again():
                print("\n------------------\n")
                print("Running lmutil lmstat")

                lmstat_output_file = run_lmstat(lmutil_path, splm_license_server)

                print("\n------------------\n")
                print("Listing current users")
                usernames, hostnames, displaynames = parse_lmstat_output(lmstat_output_file)

                selected_users = get_user_input()

                kick_off_tokens(selected_users, usernames, hostnames, displaynames, splm_license_server, lmutil_path)
            else:
                print("\nExiting the script.")
                break
        else:
            first_run = False
            print("\n------------------\n")
            print("Kick NX Token users utility")
            print("source code: https://github.com/Mr-Bubz/lmutil_lmremove")
            print("\n------------------\n")
            print("Startup checks") 
 
            lmutil_path = check_lmutil_path()
            splm_license_server = check_splm_license_server()

            print("Startup checks complete")

            print("\n------------------\n")
            print("Running lmutil lmstat")
            lmstat_output_file = run_lmstat(lmutil_path, splm_license_server)

            print("\n------------------\n")
            print("Listing current users")
            usernames, hostnames, displaynames = parse_lmstat_output(lmstat_output_file)

            selected_users = get_user_input()

            kick_off_tokens(selected_users, usernames, hostnames, displaynames, splm_license_server, lmutil_path)

    print("License removal complete")