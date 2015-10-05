#!/usr/bin/python -u

import re

import os
import os.path
import signal
import sys
import time
import fileinput

#sys.stdin = os.fdopen(sys.stdin.fileno(), 'rb', 0)
#sys.stdout = os.fdopen(sys.stdout.fileno(), 'wb', 0)
#signal.signal(signal.SIGPIPE, signal.SIG_DFL)

Vendor = {0x5e: 'Thompson', 0x9e: 'Samsung', 0xaf: 'Pace', 0xcb: 'Amstrad'}

def main():
    if len(sys.argv) != 2:
        print "missing input file"
        sys.exit(1)

    if not os.path.exists("FW"):
        os.makedirs("FW")

    with open(sys.argv[1],'rb') as fh:
        bytes_read=""
        align = False
        next_block = 1
        cnt=0
        for bytes_read_chksum in fh:
            bytes_read += bytes_read_chksum[4:0xbc] #remove ts chksum!?
        
            #align block
            #while not align:
            #    if len(bytes_read) > 2 and not ((ord(bytes_read[0]) == 0x00) and \
            #       (ord(bytes_read[1]) == 0xb5 or ord(bytes_read[1]) == 0xb6)):
            #        bytes_read = bytes_read[1:len(bytes_read)]
            #        #print len(bytes_read)
            #    else:
            #        print "end align"
            #        align = True
            #        break
            #print len(bytes_read)
            #print len(bytes_read),(ord(bytes_read[2]) << 0x08 | ord(bytes_read[3])) & 0x0FFF
            if  (len(bytes_read) >4) and (len(bytes_read) >= (ord(bytes_read[2]) << 0x08 | ord(bytes_read[3])) & 0x0FFF) and \
                (ord(bytes_read[0]) == 0x00) and \
                (ord(bytes_read[1]) == 0xb5 or ord(bytes_read[1]) == 0xb6):
                  section_type = ord(bytes_read[ 4]) << 0x08 | ord(bytes_read[ 5])
                  box_model    = ord(bytes_read[10]) << 0x08 | ord(bytes_read[12])
                  vendor       = ord(bytes_read[10])
                  fw_version   = ord(bytes_read[16])
                  file_offset  = ord(bytes_read[17]) << 0x18 | ord(bytes_read[18]) << 0x10 | ord(bytes_read[19]) << 0x08 | ord(bytes_read[20])
                  file_length  = ord(bytes_read[21]) << 0x18 | ord(bytes_read[22]) << 0x10 | ord(bytes_read[23]) << 0x08 | ord(bytes_read[24])
                  print "SECTION_TYPE:%04x" % section_type
                  print cnt
                  if (section_type == 0x0000 or section_type == 0x0001 or section_type == 0xffff) and box_model != 0xffff :
                    block_length =(ord(bytes_read[ 2]) << 0x08 | ord(bytes_read[ 3])) & 0x0FFF
                    print cnt,block_length,next_block
                    next_block = 1 #block_length -2
                    try:
                        vendorname=Vendor[vendor]
                    except:
                        vendorname='unknown-0x%02x'%vendor
                    filename = "FW/SKY_FW_%s_%04x_%02x_%04x" %  (vendorname,box_model, fw_version, section_type)

                    if not os.path.isfile(filename+".fw"):
                        try:
                            fo = open(filename+".temp",'r+b')
                        except IOError:
                            fo = open(filename+".temp",'wb')

                        #foinfo = open(filename+".info",'a+')

                        msg = "BLOCK LENGTH: %04x SECTION %04x VENDOR %10s MODEL %04x FW_VER  %04x F_OFFSET %04x F_LENGTH %6d" % ( block_length, section_type, vendorname,box_model, fw_version, file_offset, file_length /1024/1024)
                        print msg
                        #foinfo.write(msg+"\n")
                    
                        fo.seek(file_offset)
                        fo.write(bytes_read[4+21:4+block_length-4]) # 21=HEADER 4=CRC
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
            bytes_read = bytes_read[next_block:len(bytes_read)]
            cnt+=1
    return 0

if __name__ == '__main__':
    sys.exit(main())
