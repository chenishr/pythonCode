# -*- coding: utf-8 -*
from qiniu import Auth, put_file, etag
import qiniu.config
import os
import os.path
import time
import datetime
import re
import MySQLdb
from random import Random

# 此类是遍历给定的目录，  
# 将符合条件的文件上传到七牛 
# 依赖七牛的库 qiniu  

def createid():
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(32):
        str+=chars[random.randint(0, length)]
    return str

class phonevoice:
    voiceFiles  = []
    access_key  = "******"
    secret_key  = "******"
    bucket_name = "******"
    db  = None

    uploadCount	= 0

    def __init__(self):
        self.db = MySQLdb.connect(host="127.0.0.1", user="qiyongchen", passwd="QiYongChen@14990", db="imstest", charset="utf8")


    def __del__(self):
        self.db.close()

    def is_uploaded(self,f):
        cur = self.db.cursor()
        cur.execute("SELECT `IsUpload` FROM sys_phone_record WHERE Name='" + f + "';")
        
        res = cur.fetchone()
        if res is not None:
            if res[0] == 1:
                #print "uploaded:" + f
                return True
            else:
                #print "not uploaded:" + f
                return False
        else:
            return False

    def is_exist(self,f):
        cur = self.db.cursor()
        cur.execute("SELECT `Id` FROM sys_phone_record WHERE Name='" + f + "';")
        
        res = cur.fetchone()
        if res is not None:
            return True
        else:
            return False

    def update_db(self,f):
        cur = self.db.cursor()

        #pwdata  = (1,time.strftime('%Y-%m-%d %H:%M:%S'),f)
        #print "UPDATE sys_phone_record SET `IsUpload`=1,`UploadTime`='" + time.strftime('%Y-%m-%d %H:%M:%S') + "' WHERE `Name`='" + f + "';"
        r   = cur.execute("UPDATE sys_phone_record SET `IsUpload`=1,`UploadTime`='" + time.strftime('%Y-%m-%d %H:%M:%S') + "' WHERE `Name`='" + f + "';")
        self.db.commit();

    def insert_db(self,f):
        cur = self.db.cursor()

        #pwdata  = (createid(),f,1,time.strftime('%Y-%m-%d %H:%M:%S'))
        #print "INSERT INTO sys_phone_record (`Id`,`name`,`IsUpload`,`UploadTime`) VALUES ('" + createid() + "','" + f + "',1,'" + time.strftime('%Y-%m-%d %H:%M:%S') + "');"
        r   = cur.execute("INSERT INTO sys_phone_record (`Id`,`name`,`IsUpload`,`UploadTime`) VALUES ('" + createid() + "','" + f + "',1,'" + time.strftime('%Y-%m-%d %H:%M:%S') + "');")
        self.db.commit();

    def do_upload(self):
        for f in self.voiceFiles:
            #print self.uploadCount
            if not self.is_uploaded(f[1]):
                #print "begin upload" + f[1]
                if self.upload_file(f[0] , f[1]):
                    if self.is_exist(f[1]):
                        self.update_db(f[1])
                    else:
                        self.insert_db(f[1])

    def upload_file(self,parent,filename):
        if self.uploadCount >= 1000:
			#self.log("reach upload count")
			return False
        else:
			self.uploadCount += 1

        q = qiniu.Auth(self.access_key, self.secret_key)
        key = filename
        #key = 'hello' + time.strftime("%Y%m%d%H%M%S") + ".txt"

        policy={
                'callbackUrl':'http://ims.qitianzhen.cn/index.php?m=kms&c=Batch&a=qiniu_callback',
                'callbackBody':'filename=$(fname)&filesize=$(fsize)'
         }

        token = q.upload_token(self.bucket_name, key, 3600, policy)

        data    = os.path.join(parent,filename)
        ret, info = put_file(token, key, data)

        if ret is not None:
            self.log("file uploaded:" + data)
            return True
        else:
            self.log(info) # error message in info
            return False
    # 
    def log(self,string):
        filename = "phonevoice" + time.strftime('%y%m%d') + ".log"
        logFile	= open(filename,'a+')
        logFile.write('['+time.strftime('%Y-%m-%d %H:%M:%S')+']:')
        logFile.write(str(string))
        logFile.write("\r\n")

    # 73_B_18665051956_8012_20160901_18_34_24.wav
    def check_time(self,f,t=1):
        res      = re.search(r'_[\d]{8}_',f)
        if res:
            sub = res.group()

            d   = sub[1:5] + "-" + sub[5:7] + "-" + sub[7:9] #sub[1:len(sub) - 1]
            now = time.strftime('%Y-%m-%d')

            try:
				d1 = datetime.datetime.strptime(d, '%Y-%m-%d')
				d2 = datetime.datetime.strptime(now, '%Y-%m-%d')
            except:
				return False

            delta = d2 - d1

            #self.log("d:" + d)
            #self.log("now:" + now)
            #self.log(delta.days)
            if delta.days <= t and delta.days >= 0:
                #self.log("now:" + now + "d:" + d + "expirt:" + str(delta.days))
                return True
            else:
                return False
        else:
            return False

    #
    def get_files(self,rootdir):
        for parent,dirnames,filenames in os.walk(rootdir):    
            for filename in filenames:
                #tmp	= os.path.join(parent,filename)
                tmp	= [parent,filename]
                #self.log(tmp)
                if self.check_time(filename,1) :
					self.voiceFiles.append(tmp)
					#self.log("match::" + os.path.join(parent,filename))
    
    def list_files(self):
        for i in self.voiceFiles:
            print os.path.join(i[0] , i[1])


if __name__ == '__main__':
    v = phonevoice()
    v.get_files('/home/phonevoice')
    #v.list_files()
    v.do_upload()
