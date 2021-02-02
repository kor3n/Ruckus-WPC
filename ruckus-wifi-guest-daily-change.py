#!/usr/bin/env python3
import paramiko, time, smtplib, secrets, string

# Script for changing the guest password on the ruckus wifi using the cli
# V1.2 - 02/02/2021
# To run this daily on use cron on Unix / Linux based systems for an easy solution
# requires python 3.6+ and the paramiko dependency

# Change below as per required
controller = '' # enter password
username = '' # enter password
password = '' # enter password
enable_password = password # leave or change for a string of the enable password
zone_list = [''] # Add Zones in List format
wlan_list = [''] #  Add Zones in List format

# Dont change
LOGIN_SLEEP_TIME = 10
SLEEP_TIME = 1
RECV_SIZE = 1048576

# send email function
def smtp(key):
    sender = '' # who sent the email, users will see this
    receivers = [''] # enter recivers email addresses in list format
    
    # What do you want the message to say that the users will see in the email
    message = """Subject: Daily Guest Wifi Password - Ruckus

Todays Wifi Code is: {}

""".format(key)

    try:
       smtpObj = smtplib.SMTP('') # enter your smtp server / relay
       smtpObj.sendmail(sender, receivers, message)
       print("[+] - Successfully sent email")
    except SMTPException:
       print("[!] - Error: unable to send email")


# output all config commands sent to the controller from the main function
def print_output(chan):
    print('[+] - Output:\n\n')
    print(chan.recv(RECV_SIZE).decode())
    print('\n\n')

# generate a new key for the script
def gen_key():
    pool = string.ascii_letters + string.digits # use all ascii letters, upper and lower and numbers
    key = ''.join(secrets.choice(pool) for i in range(8)) # generate a 8 char string for the key change as size requires
    return key

# main body of the script.
def main():
    # Generate new key for the time the script is run
    new_pass = gen_key()
    print('[+] - Todays Wifi Key is: {}'.format(new_pass))
    
    # performing the connection the the WLC
    print('[+] - Connecting to the Ruckus Controller: {}'.format(controller))
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(controller, username=username, password=password)
    time.sleep(LOGIN_SLEEP_TIME)
    print('[+] - Invoking a shell')
    chan = ssh.invoke_shell()
    time.sleep(LOGIN_SLEEP_TIME)
    
    # entering enable and putting the password in
    print('[+] - Accessing enable mode')
    chan.send('enable\n')
    time.sleep(SLEEP_TIME)
    print('[+] - Entering the enable password')
    chan.send('{}\n'.format(enable_password))
    time.sleep(SLEEP_TIME)
    
    # iterating arround the two lists using zip and changing the passkey for each SSID in each zone untill done...
    for zone, wlan in zip(zone_list, wlan_list):
        print('[+] - Entering config mode')
        chan.send('config\n')
        time.sleep(SLEEP_TIME)
        
        print('[+] - Entering zone: {}'.format(zone))
        chan.send('zone "{}"\n'.format(zone))
        time.sleep(SLEEP_TIME)
        
        print('[+] - Entering wlan: {}'.format(wlan))
        chan.send('wlan "{}"\n'.format(wlan))
        time.sleep(SLEEP_TIME)
        
        print('[+] - Entering change password mode')
        chan.send('enc-passphrase\n')
        time.sleep(SLEEP_TIME)
        
        print('[+] - Changing password to {}'.format(new_pass))
        chan.send('{}\n'.format(new_pass))
        time.sleep(SLEEP_TIME)
        
        print('[+] - Saving password change')
        chan.send('end\n')
        time.sleep(SLEEP_TIME)
        chan.send('yes\n')
        time.sleep(5)
        
    chan.send('exit\n')
    time.sleep(SLEEP_TIME)
    
    print('[+] - Done')
    # send the passkey to using the function below, comment out if you dont want it to send an email...
    smtp(myfile)
    # output all commands sent to the controller the the screen
    print_output(chan)

if __name__ == "__main__":
    # basic multi-try upto 5 times then quit if fails
    COUNT_FAIL = 0
    try:
        main()
    except:
        print('[!] - Failed to run script trying again')
        if COUNT_FAIL > 4:
            main()
            COUNT_FAIL += 1
        else:
            print('[!] - Failed 5 times quiting script')