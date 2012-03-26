#!/usr/bin/python
#encoding: UTF-8
# 
# Name: pypodrecovery.py
# 
# Author: krosinski
#
#
import os
import re
import shutil
import optparse
import sys

from ID3 import *


class PyPodRecovery():

    #file extensions to process
    FILE_EXT = ['mp3', ]
    
    #fields refering to ID3 dict keys

    ARTIST = "ARTIST"
    ALBUM = "ALBUM"
    TITLE = "TITLE"
    TRACK_NUM = "TRACKNUMBER"
    YEAR = "YEAR" 
    
    #ID3 fields, and default mapping
    ID3_FIELDS = { 
        ARTIST : "Unknown",
        ALBUM : "Unknown_Album",
        TITLE : "Unknown_Track",
        TRACK_NUM : "0",
        YEAR : "2000",
    }

    #character mapping rules
    CHAR_MAPPING = (
        (r"[ -]", "_",),
        (r'[^a-zA-Z0-9_]', "",), 
    ) 
    #destination pattern: 
    #PATH_PATTERN = ( ARTIST , ALBUM, "%s_%s" % (TRACK_NUM, TIITLE))
    #ex: Artist: Megadeth, album Rust in Peace, track Five Magics / num: 4
    #file created: Megadeth/Rust_in_Peace/4_Five_Magics.mp3
    PATH_PATTERN = ( ARTIST , ALBUM, "%s_%s" % (TRACK_NUM, TITLE))
    
    #available operations
    COPY = shutil.copy
    MOVE = shutil.move

    def __init__(self, source_path, dest_path ):
        self.source_path = source_path
        self.dest_path = dest_path
        pass
       
    @classmethod
    def _extension_test(cls, file):
        ext = re.search(r"\.([a-z0-9]+)$", file.lower())
        if ext:
            return ext.group(1) in cls.FILE_EXT
        else:
            return False
    
    @classmethod
    def _gen_new_filename(cls,  id3, ext="mp3"):
        new_filename = os.path.join(*cls.PATH_PATTERN)
        
        for tag in cls.ID3_FIELDS.keys():
            tag_value = id3.get(tag, cls.ID3_FIELDS[tag])
            for mapping in cls.CHAR_MAPPING:
                tag_value = re.sub(mapping[0], mapping[1], tag_value)

            new_filename = new_filename.replace(tag, tag_value )

        return "%s.mp3" % new_filename

    def execute(self, file_operation="copy", verbose=True):
        
        for base_dir, dirs, files in os.walk(self.source_path):
            if verbose:
                print("Processing %s" % base_dir)
                
            for f in files:
                if not self._extension_test(f):
                    continue
                
                old_filename = os.path.join(base_dir, f)
                new_filename = self._gen_new_filename(ID3(old_filename)) 
                
                if verbose:
                    print("%s: %s -> %s" % (file_operation, os.path.basename(old_filename), new_filename) )
                
                new_filename = os.path.join(self.dest_path, new_filename)
                new_dir = os.path.dirname(new_filename)
                if not os.path.exists(new_dir):
                    os.makedirs(new_dir)

                if file_operation == "move":
                    shutil.move(old_filename, new_filename)
                else:
                    shutil.copy(old_filename, new_filename)

if __name__ == "__main__":
    msg = "\n".join(
        ("Usage: %prog [options] <source music dir> <destiation dir>", 
        "PyPodRecovery - downloads mp3 files from your ipod to a chosen directory",
        "It may be used to reform a music directory structure based on ID3 tags"
        )) 
    opt_parse = optparse.OptionParser(msg)
    opt_parse.add_option('-v', '--verbose', action="store_true", default=False,  help="Verbose mode" )
    opt_parse.add_option('-c', '--copy', action="store_true", default=False, help="Keep old files (copyi, default option!)")
    opt_parse.add_option('-m', '--move', action="store_true", default=False, help="Delete old files (move)")

    options, args =  opt_parse.parse_args()
    
    if len(args) < 2:
        print("Use --help for script usage")
        sys.exit(1)
    p_rec = PyPodRecovery(*args)
    p_rec.execute(file_operation="move" if options.move else "copy" ,verbose=options.verbose)
