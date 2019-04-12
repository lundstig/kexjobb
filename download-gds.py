import requests
import os
import json

total_sessions = 0
sessions = []
data_dir = 'data/'
auth = ('***REMOVED***', '***REMOVED***')
cookies = {}
headers = {}

def printStatus():
  print('Downloaded {}/{}.'.format(total_sessions - len(sessions), total_sessions))
  print()

def main():
  global sessions
  global total_sessions
  sessions = []
  total_sessions = 0
  with open('/mnt/data/oasis-3/subjects', 'r') as f:
    for subject in f.read().splitlines():
      if not os.path.isfile('{}{}/{}.json'.format(data_dir, subject, 'experiments')):
        sessions.append(subject)
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
  
  printStatus()
  while len(sessions) > 0:
    if download_session(sessions[0]):
      sessions.pop(0)
      printStatus()

def download_session(subject):
  url = 'https://central.xnat.org/data/projects/OASIS3/subjects/{}/experiments?format=json'.format(subject)
  print('Getting experiment list for subject {}...'.format(subject))
  
  r = None
  try:
    r = requests.get(url, auth=auth, timeout=10)
  except requests.exceptions.ConnectionError as ce:
    print(ce)
  
  if r is not None and r.status_code == 200:
    path = '{}{}/{}.json'.format(data_dir, subject, 'experiments')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
      f.write(r.content)
    print('Experiment list downloaded.')
    index = json.loads(r.content.decode('utf-8'))
    dir = '{}{}/'.format(data_dir, subject)
    download_gdr_files(dir, index)
    return True
  elif r is None:
    print('Download failed.')
    return False
  else:
    print('Download failed ({})'.format(r.status_code))
    return False

def download_gdr_files(dir, index):
  index = index['ResultSet']['Result']
  index = list(filter(lambda entry: 'USDb6' in entry['label'], index))
  for entry in index:
    print('Downloading file {}...'.format(entry['label']))
    url = 'https://central.xnat.org' + entry['URI'] + '?format=json'
    
    success = False
    while not success:
      r = None
      try:
        r = requests.get(url, auth=auth, timeout=15)
      except IOError as ce:
        print(ce)
      if r is not None and r.status_code == 200:
        path = dir + entry['label'] + '.json'
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
