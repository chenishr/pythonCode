'''
delete log files
'''
import os
import sys
import time
class DeleteLog:

    def __init__(self,fileName,days):
        self.fileName = fileName
        self.days = days

    def delete(self):
        if os.path.isfile(self.fileName):
            print "usage: python %s dirName [days]" % sys.argv[0]
        elif os.path.isdir(self.fileName):
            for i in [os.sep.join([self.fileName,v]) for v in os.listdir(self.fileName)]:
                if os.path.isfile(i):
                    if self.compare_file_time(i):
                        #print i
                        os.remove(i)
                        self.log(i)
                elif os.path.isdir(i):
                    self.fileName = i
                    self.delete()

    def compare_file_time(self,file):
        time_of_last_access = os.path.getatime(file)
        age_in_days = (time.time()-time_of_last_access)/(60*60*24)
        #print "file %s | age %f | access %f " % (file,age_in_days , self.days)
        if age_in_days > self.days:
            return True
        return False

    def log(self,file):
        f   = open(self.fileName + os.sep + 'delete_log.log','a')
        tmp = '[' + time.strftime('%H-%M-%d %H:%M:%S') + '] DELETE ' + file + "\n"
        f.write(tmp)
        f.close()


if __name__ == '__main__':
    obj = DeleteLog('/var/log/wechat',60)
    obj.delete()

    obj1 = DeleteLog('/var/www/ims/logs',40)
    obj1.delete()
