import os
import sys
from constants import LOGO_STRING


PROMPTS = {
    'YEAR': "\nPlease enter the four-digit year for which you are registering. For example, if\nyou are registering for Spring 2024, just type '2024'.\nEnter year: ",
    'TERM': "\nPlease enter the number corresponding to\nyour term: '0' for Winter, '1' for Spring, '7' for Summer, '9' for Fall.\nEnter term: ",
    'CAMPUS': "\nPlease type the two-letter code for your campus: 'NB' for New Brunswick,\n'NK' for Newark, or 'CM' for Camden.\nEnter campus: ",
    'DESIRED_SECTIONS': "\nPlease enter the numbers of the course sections you want, separated\nby commas. For example: '06802, 05812'.\nEnter sections: ",
    'NETID': "\nPlease enter your Rutgers username, also known as your NetID.\nEnter NetID: ",
    'PASSWORD': "\nPlease enter your Rutgers password.\nEnter password: ",
}


VALIDATIONS = {
    'YEAR': lambda x: x.isdigit() and int(x) > 2000,
    'TERM': lambda x: x in ['0', '1', '7', '9'],
    'CAMPUS': lambda x: x.upper() in ['NB', 'NK', 'CM'],
    'DESIRED_SECTIONS': lambda x: all(s.strip().isdigit() for s in x.split(',')),
    'NETID': lambda x: x.isalnum(),
    'PASSWORD': lambda x: x.isalnum(),
}

def is_first_run():
    return not os.path.exists('config.txt') or os.stat('config.txt').st_size == 0

def get_input(key):
    while True:
        response = input(PROMPTS[key]).strip()
        if VALIDATIONS[key](response):
            if key == "CAMPUS":
                return response.upper()
            return response
        print("Invalid input. Please try again.")

def write_config(config):
    with open('config.txt', 'w') as file:
        for key, value in config.items():
            file.write(f"{key} = {value}\n")

def read_config():
    with open('config.txt', 'r') as file:
        return dict(line.strip().split(" = ") for line in file.readlines())

def main():
    if is_first_run():
        # clear console
        os.system('cls' if os.name == 'nt' else 'clear')
        print(LOGO_STRING)
        print("\n\n\nWelcome to Rutgers AutoSniper! Please enter your information to get started.\n")
        config = {key: get_input(key) for key in PROMPTS}
        write_config(config)
        print("\nConfig file created.\n")
        sys.exit()

    config = read_config()
    print(LOGO_STRING)
    print("\n\nWelcome back to Rutgers AutoSniper! You are currently sniping the following sections:")
    print(config['DESIRED_SECTIONS'])

    if input("\n1. Keep these sections\n2. Change sections\nChoice: ").lower() == '2':
        
        config['DESIRED_SECTIONS'] = get_input('DESIRED_SECTIONS')
        write_config(config)
        print("Your new desired sections are:")
        print(config['DESIRED_SECTIONS'])
        a = input("\nDoes this look correct? (y/n): ")
        if a.lower() == 'y':
            print("You're all set! Happy sniping!")
        else:
            print("Please run start.bat to reconfigure.")

    print("\n\nTo change other settings like the year, username, etc., please edit the config.txt file in the src folder directly.\n")

if __name__ == "__main__":
    main()