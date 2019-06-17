import requests
import os
import random
import json

total_sessions = 0
sessions = []
data_dir = 'data/'
auth = ('', '')
cookies = {}
headers = {}

def main():
  sessions = []
  total_sessions = 0
  with open('sessions.csv', 'r') as f:
    for line in f.read().splitlines():
      session, subject = line.split(',')
      if not os.path.isfile('{}{}/{}.json'.format(data_dir, subject, session)):
        sessions.append((subject, session))
      total_sessions += 1
  
  print('Setting up jsession...')
  
  r = None
  try:
    r = requests.get('https://central.xnat.org/data/JSESSION', auth=auth, timeout=60)
  except requests.exceptions.ConnectionError as ce:
    print(ce)
  
  if r is None:
    print('Failed to setup jsession.')
    sys.exit(1)
  else:
    print('Session id: {}'.format(r.text))
    headers = {'JSESSIONID': r.text}
    cookies = {'JSESSIONID': r.text}
  
  print('Downloaded {}/{}.'.format(total_sessions - len(sessions), total_sessions))
  print()
  
  while len(sessions) > 0:
    i = random.randrange(len(sessions))
    if download_session(sessions[i]):
      sessions.pop(i)
      print('Downloaded {}/{}.'.format(total_sessions - len(sessions), total_sessions))
      print()

def download_session(subject_and_session):
  subject, session = subject_and_session
  #url = 'https://central.xnat.org/data/projects/OASIS3/subjects/{}/experiments/{}/scans/T1w/files?format=zip'.format(subject, session)
  url = 'https://central.xnat.org/data/projects/OASIS3/subjects/{}/experiments/{}/scans/T1w/files'.format(subject, session)
  print('Getting file list for session {}...'.format(session))
  
  r = None
  try:
    r = requests.get(url, auth=auth, timeout=10)
  except requests.exceptions.ConnectionError as ce:
    print(ce)
  
  if r is not None and r.status_code == 200:
    path = '{}{}/{}.json'.format(data_dir, subject, session)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
      f.write(r.content)
    print('File list downloaded.')
    index = json.loads(r.content.decode('utf-8'))
    dir = '{}{}/{}/'.format(data_dir, subject, session)
    download_session_files(dir, index)
    return True
  elif r is None:
    print('Download failed.')
    return False
  else:
    print('Download failed ({})'.format(r.status_code))
    return False

def download_session_files(dir, index):
  index = index['ResultSet']['Result']
  for entry in index:
    print('Downloading file {}...'.format(entry['Name']))
    url = 'https://central.xnat.org' + entry['URI']
    
    success = False
    while not success:
      r = None
      try:
        r = requests.get(url, auth=auth, timeout=15)
      except IOError as ce:
        print(ce)
      if r is not None and r.status_code == 200:
        path = dir + entry['Name']
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
          f.write(r.content)
        print('Download successful.\n')
        success = True
      elif r is None:
        print('Download failed.\n')
      else:
        print('Download failed ({})\n'.format(r.status_code))

main()
