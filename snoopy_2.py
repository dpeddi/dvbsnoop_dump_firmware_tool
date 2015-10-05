#!/usr/bin/python -u

import re

import os
import os.path
import signal
import sys
import time
import fileinput

sys.stdin = os.fdopen(sys.stdin.fileno(), 'rb', 0)
sys.stdout = os.fdopen(sys.stdout.fileno(), 'wb', 0)
signal.signal(signal.SIGPIPE, signal.SIG_DFL)

def main():
    for arg in sys.argv[1:]:
        fh = arg == '-' and sys.stdin or open(arg, 'rb', 0)
        try:
            if not os.path.exists("FW"):
              os.makedirs("FW")
            bytes_read_tofix = fh.read()
            a=0
            bytes_read=""
            #ff = open("test","wb")
            while a<len(bytes_read_tofix):
                bytes_read += bytes_read_tofix[a+4:a+0xbc]
                #ff.write(bytes_read_tofix[a+4:a+0xbc])
                a+=0xbc
                #sys.stdout.write('.')
            #ff.write(bytes_read)
          
            cnt=0
            #print "LEN",len(bytes_read)
            #for b in xrange(0,len(bytes_read)):
            b=0
            while True:
                #print len(bytes_read)-b 
                #sys.stdout.write('.')
                if (len(bytes_read) - b  > 1) and ord(bytes_read[b]) == 0x00 and ( ord(bytes_read[b+1]) == 0xb5 or ord(bytes_read[b+1]) == 0xb6):
                  block_length =(ord(bytes_read[b+ 2]) << 0x08 | ord(bytes_read[b+ 3])) & 0x0FFF
                  section_type = ord(bytes_read[b+ 4]) << 0x08 | ord(bytes_read[b+ 5])
                  box_model    = ord(bytes_read[b+10]) << 0x08 | ord(bytes_read[b+12])
                  fw_version   = ord(bytes_read[b+16])
                  file_offset  = ord(bytes_read[b+17]) << 0x18 | ord(bytes_read[b+18]) << 0x10 | ord(bytes_read[b+19]) << 0x08 | ord(bytes_read[b+20])
                  file_length  = ord(bytes_read[b+21]) << 0x18 | ord(bytes_read[b+22]) << 0x10 | ord(bytes_read[b+23]) << 0x08 | ord(bytes_read[b+24])
                  if (section_type == 0x0000 or section_type == 0x0001 or section_type == 0xffff) and box_model != 0xffff :
                    b+=4

                    filename = "FW/SKY_FW_"+"%04x_%02x_%04x" %  (box_model, fw_version, section_type)


                    if not os.path.isfile(filename+".fw"):
                        try:
                            fo = open(filename+".temp",'r+b')
                        except IOError:
                            fo = open(filename+".temp",'wb')

                        #foinfo = open(filename+".info",'a+')

                        msg = "BLOCK LENGTH: %04x SECTION %04x MODEL %04x FW_VER  %04x F_OFFSET %04x F_LENGTH %04x" % ( block_length, section_type, box_model, fw_version, file_offset, file_length)
                        print msg
                        #foinfo.write(msg+"\n")
                    
                        fo.seek(file_offset)
                        fo.write(bytes_read[b+21:b+block_length-4]) # 21=HEADER 4=CRC
                        fo.close
                        #foinfo.close
                        #os.exit(1)

                        try:
                            with open(filename+".progress",'rb') as foprogress:
                                newlines = []
                                fpcnt=1
                                for line in foprogress.read():
                                    if fpcnt == (file_length - file_offset)/ (block_length - 25):
                                        newlines.append("x")
                                    else:
                                        newlines.append(line)
                                    fpcnt+=1
                            foprogress.closed

                            with open(filename+".progress",'wb') as foprogress:
                                for line in newlines:
                                    foprogress.write(line)
                            foprogress.closed

                            match=True
                            for x in newlines:
                                if x == "_":
                                  match=False
                            if match:
                                os.rename(filename+".temp",filename+".fw")

                        except IOError:
                            with open(filename+".progress",'wb') as foprogress:
                                fpcnt=1
                                for p in xrange(0,(file_length / (block_length - 25))):
                                    if fpcnt == (file_length - file_offset)/ (block_length - 25):
                                        foprogress.write("x")
                                    else:
                                        foprogress.write("_")
                                    fpcnt+=1
                            foprogress.closed
                            #os.exit(1)

                    b += block_length
                  else:
                    b += 1
                else:
                  b += 1
                if b > len(bytes_read):
                  break
                #  print "LEN",len(bytes_read)," ",b
                #if b % 1024 == 0:
                #    print "b 0x%x" % b
        finally:
            if fh is not sys.stdin:
                fh.close()
    return 0

if __name__ == '__main__':
    sys.exit(main())
