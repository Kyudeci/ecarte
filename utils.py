def logger(message,out=False):
    if out:
        print(message)
    with open('logs/ecarte_log.txt', 'a') as f:
        f.write(message + " \n")
