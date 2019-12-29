'''
terminates serial_radio_rfm9x launched by rc.local and load a new instance so we can observe it on the terminal

@usage      place this script in /home/pi , then after connecting to crawler side radio over ssh
            use command: python name_of_this_script.py
'''
import subprocess, os
stream = subprocess.Popen('ps -ef | grep python3', stdout=subprocess.PIPE, shell = True)
(output, err) = stream.communicate()
print output
output_lines = output.split('\n')
foo = [" ".join(x.split()) for x in output_lines]
print 'foo',foo
tokenized_lines = [x.split(' ')  for x  in foo  if len(x)>0]
print tokenized_lines
for index, line in enumerate(tokenized_lines):
    user = line[0]
    process_id = line[1]
    if 'crawler_gui' in foo[index]:
        os.system('sudo kill {}'.format(process_id))
    print 'user:',user
    print 'process_id:',process_id

#launch crawler side radio
os.chdir('/home/crawler_gui/GUI/')
os.system('python3 serial_radio_rfm9x.py')
#os.system('python3 /home/crawler_gui/GUI/serial_radio_rfm9x.py')
