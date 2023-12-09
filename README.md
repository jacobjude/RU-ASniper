# RU ASniper 

RU ASniper (Rutgers AutoSniper) is fast course sniper that is designed to automate the process of sniping course sections on WebReg for Rutgers students. It eliminates the need for constant monitoring and manual registration by automatically enrolling people in their desired courses as soon as a spot becomes available, making it faster than any notification-based course sniper.

## Installation

To get started with Rutgers AutoSniper, follow these steps:

1. Ensure you have Python 3.10 or greater installed on your system.
2. Clone the RU ASniper repository to your local machine or download the source code.
   - Run `git clone https://github.com/jacobjude/RU-ASniper.git` or download the latest zip file from [Releases](https://github.com/jacobjude/RU-ASniper/releases)
4. Navigate to the directory where you have saved RU ASniper.
5. Run `start.bat` (Windows) or `start.sh` (Linux/MacOS). This will:
   - Create a Python virtual environment.
   - Install the necessary dependencies if they are not already installed.
   - Initiate the setup process for RU ASniper.

## Setup Process

To run the course sniper, run `start.bat` (Windows) or `start.sh` (Linux/MacOS).
During the initial setup, you will be prompted to provide the following information:

- The academic year and term for which you are registering (e.g., 2024, Spring).
- The campus for which you are registering courses (e.g., New Brunswick, Newark, Camden).
- The course section numbers you wish to snipe.
- Your Rutgers NetID and password for WebReg authentication. You will be prompted to authenticate via Duo upon login.
- Whether to hide the browser during the sniping process.
   - If you choose to hide the browser, only the terminal will be visible.
   - If you do not hide the browser, you will see the actions performed by the sniper in real-time.

For subsequent uses:

1. Run `start.bat` or `start.sh` again.
2. You will have the option to change the courses you want to snipe before starting the sniper.

Please ensure that your system's date and time are set accurately to avoid any synchronization issues with WebReg.

## How It Works

Once RU ASniper is set up, it operates as follows:

1. The tool will launch a Chrome browser window using the Selenium WebDriver module in Python.
2. It logs into WebReg using your provided credentials.
3. RU ASniper will continuously monitor the availability of the course sections you specified.
4. In the background, it will refresh and check to maintain your WebReg session.
5. If an open section is detected, RU ASniper will automatically register you for that course within ~0.6 seconds of it opening.

Logs of the sniper's activity are written to the `logs.log` file in the root directory of the project.

## License

This project is released under the [GNU General Public License v3.0](LICENSE). By using RU ASniper, you agree to the terms of this license.

## Disclaimer

RU ASniper is not affiliated with, authorized, maintained, sponsored, or endorsed by Rutgers University in any way. This is an independent and unofficial software. Use at your own risk.
