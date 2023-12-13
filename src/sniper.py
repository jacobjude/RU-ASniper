import os
import sys
import logging
from datetime import datetime
from time import ctime, perf_counter, sleep
from colorama import Fore
import pytz
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_MISSED, EVENT_JOB_MAX_INSTANCES, EVENT_JOB_SUBMITTED
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler

from browser import Browser
from soc import fetch_open_sections, is_section_open, construct_api_url

import config
from constants import LOGO_STRING

logging.basicConfig(filename='logs.log', level=logging.INFO)


# Constants
PRINT_INTERVAL_SECONDS = 1
BROWSER_REFRESH_INTERVAL_SECONDS = 250
BROWSER_UPKEEP_INTERVAL_SECONDS = 60
EASTERN_TIMEZONE = pytz.timezone("US/Eastern")
SECOND_TO_START_AT = 57
SECOND_TO_STOP_AT = 3


class RutgersAutoSniper:
    def __init__(self, show_browser=False):
        self.api_url = construct_api_url(config.QUERY_PARAMS_SOC_API)
        self.setup_logging()
        self.clear_console()
        self.print_logo()
        self.main_scheduler = BlockingScheduler()
        self.refresh_scheduler = BackgroundScheduler()
        self.upkeep_scheduler = BackgroundScheduler()
        self.misc_background_scheduler = BackgroundScheduler()
        self.browser = Browser(show_browser=show_browser)
        self.desired_sections = set(config.DESIRED_SECTIONS)
        self.registered_sections = set()
        self.total_times_ran = 0
        self.fetching = False
        self.average_execution_time = 0
        self.length_of_job = (60 - SECOND_TO_START_AT) + (SECOND_TO_STOP_AT)

    def setup_logging(self):
        logger = logging.getLogger('apscheduler')
        logger.setLevel(logging.ERROR)

    @staticmethod
    def clear_console():
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def print_logo():
        print(LOGO_STRING)

    def start(self):
        try:
            self.schedule_background_operations()
                
            self.schedule_registration_checks()
            logging.info(f"Started all scheduleres at {ctime()}.\n")
            
        except (KeyboardInterrupt, SystemExit):
            print(LOGO_STRING)
            print("\n\nRutgers AutoSniper stopped.")
            os._exit(0)

    def execute_registration_job(self):
        times_ran = 0
        self.fetching = True
        second = datetime.now().second
        while second >= SECOND_TO_START_AT or second < SECOND_TO_STOP_AT:
            try:
                start = perf_counter()
                open_sections = fetch_open_sections(self.api_url)
                for section in self.desired_sections:
                    if is_section_open(section, open_sections):
                        self.browser.registering = True
                        try:
                            end = self.browser.register_course(section)
                            logging.info(f"Registered for section {section} in {end - start:.4f} seconds.")
                            self.desired_sections.discard(section)
                            self.registered_sections.add(section)
                            self.browser.registering = False
                        except Exception as e:
                            logging.error(f"Failed to register for section {section} at {ctime()}.\nError information: {e}\n{type(e)}\nTraceback: {sys.exc_info()}\n\n")
                            try:
                                self.browser.driver.quit()
                                self.browser.keep_driver_running()
                                self.browser.refresh_page_and_restore()
                                end = self.browser.register_course(section)
                                self.desired_sections.discard(section)
                                self.registered_sections.add(section)
                                self.browser.registering = False
                                logging.info(f"(Backup) Registered for section {section} in {end - start:.4f} seconds.")
                            except Exception as e:
                                logging.error(f"(Backup) Failed to register for section {section} at {ctime()}.\nError information: {e}\n{type(e)}\nTraceback: {sys.exc_info()}\n\n")
                        
            except:
                second = datetime.now().second
                logging.error(f"Failed to fetch open sections at {ctime()}.\nTraceback: {sys.exc_info()}\n\n")
                continue
            times_ran += 1
            second = datetime.now().second
        self.fetching = False
        self.browser.registering = False
        return times_ran
        
    def registration_job_listener(self, event):
        if event.code == EVENT_JOB_EXECUTED and not self.browser.registering:
            if self.total_times_ran < 10:
                self.total_times_ran += 1

            if event.retval > 0 and self.total_times_ran > 0:
                time_per_iteration = self.length_of_job / event.retval
                self.average_execution_time += (time_per_iteration - self.average_execution_time) / self.total_times_ran
            else:
                self.average_execution_time = 0
            logging.info(f"---{ctime()}---\nExecuted registration job {event.retval} times in {self.length_of_job} seconds.\nAverage execution time: {self.average_execution_time} seconds.\n")
        elif event.code == EVENT_JOB_ERROR:
            logging.exception(f'Registration job {event.job_id} raised an exception at {ctime()}: {event.exception}\nTraceback: {event.traceback}\n\n')

    def print_to_console(self):
        closed_sections_string = "\n".join(f"Section {Fore.LIGHTMAGENTA_EX}{section} {Fore.WHITE}is{Fore.LIGHTRED_EX} closed.{Fore.RESET}" for section in self.desired_sections)
        registered_sections_string = "\n".join(f"Section {Fore.LIGHTMAGENTA_EX}{section}{Fore.WHITE} has been {Fore.LIGHTGREEN_EX}registered. {Fore.RESET}" for section in self.registered_sections)
        registered_sections_string = f"\n\n{registered_sections_string}" if registered_sections_string != "" else ""
        time_until_next_check = (SECOND_TO_START_AT - datetime.now().second)
        fetching_string = f"{Fore.LIGHTGREEN_EX}Continuously fetching open sections!{Fore.RESET}" if self.fetching else f"Waiting until WebReg updates... {Fore.LIGHTRED_EX}({time_until_next_check} seconds left){Fore.RESET}"
        fetch_rate_string = f"Fetch rate: {Fore.LIGHTMAGENTA_EX}~{1/self.average_execution_time:.4f} times per second{Fore.RESET}" if self.average_execution_time > 0 else ""
        string_to_print = f"{LOGO_STRING}\n\n-------------------{Fore.LIGHTMAGENTA_EX}{ctime()}{Fore.RESET}--------------------\n\n{closed_sections_string}{registered_sections_string}\n\n---------------------------------------------------------------\n\n{fetching_string}\n{fetch_rate_string}"
        self.clear_console()
        print(string_to_print)

    def refresh_page_listener(self, event):
        if event.code == EVENT_JOB_EXECUTED:
            logging.info(f"Refresh page job executed at {ctime()} with return value {event.retval}\n")
        elif event.code == EVENT_JOB_ERROR:
            logging.exception(f'Refresh page job raised an exception at {ctime()}: {event.exception}\nTraceback: {event.traceback}\n\n')
        elif event.code == EVENT_JOB_MISSED:
            logging.warning(f'Refresh page job missed at {ctime()}.\n')
        elif event.code == EVENT_JOB_MAX_INSTANCES:
            logging.warning(f'Maximum instances of refresh page job reached at {ctime()}.\n')
        elif event.code == EVENT_JOB_SUBMITTED:
            logging.info(f"Refresh page job submitted at {ctime()}.\n")
                    
            
                    
    def keep_driver_running_listener(self, event):
        if event.code == EVENT_JOB_EXECUTED:
            logging.info(f"Kept driver running at {ctime()}.\n")
        elif event.code == EVENT_JOB_ERROR:
            logging.exception(f'Keep driver running job raised an exception at {ctime()}: {event.exception}\nTraceback: {event.traceback}\n\n')
        elif event.code == EVENT_JOB_MISSED:
            logging.warning(f'Keep driver running job missed at {ctime()}.\n')
        elif event.code == EVENT_JOB_MAX_INSTANCES:
            logging.warning(f'Maximum instances of keep driver running job reached at {ctime()}.\n')
        elif event.code == EVENT_JOB_SUBMITTED:
            logging.info(f"Keep driver running job submitted at {ctime()}.\n")
        

    def schedule_registration_checks(self):
        try:
            # the following jobs are run at 5:59:57 AM, and then every minute after that until 2:00:00 am
            self.main_scheduler.add_job(self.execute_registration_job, "cron", hour='5', minute='59', second=f'{str(SECOND_TO_START_AT)}')
            self.main_scheduler.add_job(self.execute_registration_job, "cron", hour='6-23', minute='*', second=f'{str(SECOND_TO_START_AT)}')
            self.main_scheduler.add_job(self.execute_registration_job, "cron", hour='0-1', minute='*', second=f'{str(SECOND_TO_START_AT)}')
            self.main_scheduler.add_listener(self.registration_job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
            self.main_scheduler.start()
        except:
            logging.exception(f'Failed to schedule registration checks at {ctime()}.\nTraceback: {sys.exc_info()}\n\n')

    def print_to_console_listener(self, event):
        logging.exception(f'Print to console job raised an exception at {ctime()}: {event.exception}\nTraceback: {event.traceback}\n\n')
        

    def schedule_background_operations(self):
        self.refresh_scheduler.add_job(self.browser.refresh_page_and_restore, "interval", seconds=BROWSER_REFRESH_INTERVAL_SECONDS, max_instances=9999999)
        self.upkeep_scheduler.add_job(self.browser.keep_driver_running, "interval", seconds=BROWSER_UPKEEP_INTERVAL_SECONDS, max_instances=9999999)
        self.misc_background_scheduler.add_job(self.print_to_console, "interval", seconds=PRINT_INTERVAL_SECONDS, max_instances=1)

        # add listeners
        self.refresh_scheduler.add_listener(self.refresh_page_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_MISSED | EVENT_JOB_MAX_INSTANCES | EVENT_JOB_SUBMITTED)
        self.upkeep_scheduler.add_listener(self.keep_driver_running_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_MISSED | EVENT_JOB_MAX_INSTANCES | EVENT_JOB_SUBMITTED)
        self.misc_background_scheduler.add_listener(self.print_to_console, EVENT_JOB_ERROR)
        
        self.browser.keep_driver_running()
        self.refresh_scheduler.start()
        self.upkeep_scheduler.start()
        self.misc_background_scheduler.start()


        

    @staticmethod
    def construct_browser_url():
        semester_selection = config.QUERY_PARAMS_WEBREG["semesterSelection"]
        return f"https://sims.rutgers.edu/webreg/editSchedule.htm?login=cas&semesterSelection={semester_selection}&indexList="


if __name__ == "__main__":
    if not "--legacy" in sys.argv and (config.NETID == "" or config.PASSWORD == ""):
        print("Error: Running in regular mode but NETID and/or PASSWORD is not set in ./src/config.txt. Please set these values and try again.")
        sys.exit(1)
    logging.info(f"Starting Rutgers AutoSniper at {ctime()}.\n")
    sniper = RutgersAutoSniper(show_browser="--browser" in sys.argv)
    sniper.start()
