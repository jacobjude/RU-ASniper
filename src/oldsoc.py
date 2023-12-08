### DEPRECATED ###
# Used to be for legacy mode. Code is here just for reference purposes.

# only import pyautogui if 'DISPLAY' in os.environ
from typing import List, Optional
import config
import pyautogui
import pygetwindow as gw
import time
import webbrowser
from threading import Timer
from urllib.parse import urlencode, quote

REGISTER_BUTTON_IMAGE = "src/register_button.png"
LOGIN_BUTTON_IMAGE = "src/login_button.png"
CHROME_PATH = config.CHROME_PATH
SEMESTER = config.QUERY_PARAMS_WEBREG["semesterSelection"]



def locate_button(button_image: str, confidence: float = 0.9):
    """
    Locate a button based on its image on the screen.
    
    Args:
        button_image: Path to the image of the button.
        confidence: The confidence threshold for image recognition.
    
    Returns:
        The location of the button if found, otherwise None.
    """
    button_location = pyautogui.locateCenterOnScreen(button_image, confidence=confidence)
    return button_location

def wait_for_buttons(button_images: list, confidence: float = 0.9, timeout: int = 15) -> Optional[tuple]:
    """
    Wait for buttons to appear on the screen within a certain timeout period.
    
    Args:
        button_images: List of paths to the image of the buttons.
        confidence: The confidence threshold for image recognition.
        timeout: Time in seconds to keep searching for the button before giving up.
    
    Returns:
        A tuple of the button location and image if found, otherwise None.
    """
    end_time = time.time() + timeout
    while time.time() < end_time:
        for button_image in button_images:
            try:
                button_location = locate_button(button_image, confidence=confidence)
            except:
                button_location = None
            if button_location:
                print(f"Found button {button_image}!")
                return button_location, button_image

    print(f"Buttons {button_images} not found on screen within timeout of {timeout} seconds.")
    return None

def click_button(button_location: Optional[tuple]) -> bool:
    """
    Click a button at a given location on the screen.
    
    Args:
        button_location: The location of the button to click.
    
    Returns:
        True if the button was clicked, otherwise False.
    """
    if button_location:
        pyautogui.click(button_location)
        return True
    return False

def open_browser_with_url(url: str) -> None:
    """
    Open a web browser with the given URL.
    
    Args:
        url: The URL to open.
    """
    webbrowser.get(CHROME_PATH).open(url)

def activate_window(title: str, timeout: int = 20) -> bool:
    """
    Activate and maximize the window with the given title within a certain timeout period.
    
    Args:
        title: The title of the window to focus.
        timeout: Time in seconds to keep searching for the window before giving up.
    
    Returns:
        True if the browser window was successfully focused, otherwise False.
    """
    end_time = time.time() + timeout
    print("Trying to focus on the window...")
    while time.time() < end_time:
        window_list = gw.getWindowsWithTitle(title)
        if window_list:
            print("Found window")
            window = window_list[0]
            time.sleep(0.1)
            window.moveTo(0, 0)
            time.sleep(0.1)
            window.maximize()
            time.sleep(0.1)
            window.activate()
            return True

    print(f"Window with title '{title}' not found within timeout of {timeout} seconds.")
    return False

def open_registration_page(course_index: str) -> None:
    """
    Open the Rutgers Web Registration System with a given course index for registration.
    
    Args:
        course_index: The course index number to add to the registration URL.
    """
    url = f"https://sims.rutgers.edu/webreg/editSchedule.htm?login=cas&semesterSelection={SEMESTER}&indexList={course_index}"

    Timer(0, open_browser_with_url, args=(url,)).start()
    window_title = "Chrome"
    activated = activate_window(window_title)

    if not activated:
        raise RuntimeError("Failed to activate the browser window for course registration.")

def register_course_nondriver(course_index: str, attempts: int = 5) -> bool:
    """
    Attempt to register for a course by automatically clicking the buttons.
    
    Args:
        course_index: The course index for the course to register.
        attempts: Number of attempts to try registering the course.
    
    Returns:
        True if the course was successfully registered, otherwise False.
    """
    print("Attempting to register for course...")
    
    # A helper function to wait for a button, shared between login and register button.
    def wait_and_click(button_images, purpose, attempt):
        print("Waiting for button to appear...")
        button_to_press = wait_for_buttons(button_images)
        print(f"Clicking {button_to_press[0]}")
        if button_to_press:
            click_button(button_to_press[0])
            click_button(button_to_press[0]) # click a second time to be sure
            return button_to_press[1]
        else:
            print(f"Attempt {attempt}: Failed to find the {purpose} button.")
            return None

    for attempt in range(1, attempts + 1):
        print("Opening registration page...")
        open_registration_page(course_index)
        print("Handling login/register...")
        button_to_press = wait_and_click([LOGIN_BUTTON_IMAGE, REGISTER_BUTTON_IMAGE], 'login or register', attempt)
        if button_to_press == LOGIN_BUTTON_IMAGE:
            # We must now click the register button
            print(f"Attempt {attempt}: Found login button. Now looking for register button.")
            if wait_and_click([REGISTER_BUTTON_IMAGE], 'register', attempt):
                print("Registered for the course successfully.")
                return True
        elif button_to_press == REGISTER_BUTTON_IMAGE:
            # We can just click the register button
            print("Registered for the course successfully.")
            return True
    
    print("Failed to register for the course after multiple attempts.")
    return False