import logging
import cProfile
from time import perf_counter, time
from datetime import datetime
import requests
from urllib.parse import urlencode, quote
from typing import List
import threading

# Set up logging
logger1 = logging.getLogger('script1')
logger1.setLevel(logging.INFO)
handler1 = logging.FileHandler('./script1.log')
handler1.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger1.addHandler(handler1)

logger2 = logging.getLogger('script2')
logger2.setLevel(logging.INFO)
handler2 = logging.FileHandler('./script2.log')
handler2.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger2.addHandler(handler2)


QUERY_PARAMS_SOC_API = {"year": "2024", "term": "1", "campus": "NB"}

def construct_api_url(query_params: dict) -> str:
   params_encoded = urlencode(query_params, quote_via=quote)
   api_url = f"http://sis.rutgers.edu/soc/api/openSections.gzip?{params_encoded}"
   return api_url

def fetch_open_sections(api_url: str, retry_limit: int = 5) -> List[str]:
   for attempt in range(retry_limit):
       try:
           response = requests.get(api_url, timeout=0.2)
           response.raise_for_status()
           return response.json()
       except:
           pass

   raise Exception("Max retries reached while fetching open sections.")

def is_open_sections_changed(old_open_sections: list, new_open_sections: list) -> bool:
   if len(old_open_sections) != len(new_open_sections):
       return True
   for i in range(len(old_open_sections)):
       if old_open_sections[i] != new_open_sections[i]:
           return True
   return False

api_url = construct_api_url(QUERY_PARAMS_SOC_API)

def main_script1():
   old_open_sections = []
   new_open_sections = []
   print("Starting script 1")
   logger1.info(f"\n----Starting at {datetime.now()}")

   while True:
       start = perf_counter()
       try:
           new_open_sections = fetch_open_sections(api_url)
       except:
           continue
       if is_open_sections_changed(old_open_sections, new_open_sections) and old_open_sections != []:
           current_time = time()
           dt_object = datetime.fromtimestamp(current_time)
           formatted_time = dt_object.strftime('%Y-%m-%d %H:%M:%S') + f"{current_time % 1:.10f}"[1:]
           logger1.info(f"Open sections changed at {formatted_time}")
       old_open_sections = new_open_sections
       end = perf_counter()

def main_script2():
   old_open_sections = []
   new_open_sections = []
   sections_to_check = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10"]
   print("Starting script 2")
   logger2.info(f"\n----Starting at {datetime.now()}")
   while True:
       current_time = datetime.now()
       while current_time.second >= 1 and current_time.second < 59:
           current_time = datetime.now()
           
       while current_time.second >= 59 or current_time.second < 1:
           start = perf_counter()
           try:
               new_open_sections = fetch_open_sections(api_url)
           except:
               continue
           start_check = perf_counter()
               
           sections_changed = is_open_sections_changed(old_open_sections, new_open_sections) and old_open_sections != []
           end_check = perf_counter()
           if sections_changed:
               current_time = time()
               dt_object = datetime.fromtimestamp(current_time)
               formatted_time = dt_object.strftime('%Y-%m-%d %H:%M:%S') + f"{current_time % 1:.10f}"[1:]
               logger2.info(f"Open sections changed at {formatted_time}")
           old_open_sections = new_open_sections
           end = perf_counter()
           current_time = datetime.now()

if __name__ == "__main__":
   # do cProfile.run('main_script1()') and cProfile.run('main_script2()') in parallel by threading the cProfile.run
    thread1 = threading.Thread(target=cProfile.run, args=('main_script1()',))
    thread2 = threading.Thread(target=cProfile.run, args=('main_script2()',))
    thread1.start()
    thread2.start()
