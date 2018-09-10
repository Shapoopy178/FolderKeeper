"""
FolderKeeper
version 0.0.2

Run to execute folder maintenance tasks as determined in the
parameters section of the script.
"""
#%% Import necessary modules
import os
import sys
import time
import datetime
import send2trash
#%%
class FolderKeeper(object):
    '''
    Directory class containing methods and attributes for cataloging and executing
    operations on system directories. Not intended to be used directly,
    but as a master template for the RootDirectory and Subdirectory classes.
    '''
    def __init__(self, path):
        '''
        Initialize Directory settings and attributes
        '''
                
        #Check if arg path is absolute, else aborts execution
        if os.path.isabs(path):
            self.root_path = path
        else:
            print('ERROR:PATH DOES NOT EXIST!')
            print('Directory assignment aborted!')
            return
        self.bin_path = os.path.join(self.root_path, '.FolderKeeper')
        self.settings_fname = os.path.join(self.bin_path, 'fk_settings.fks')
        if not os.path.isdir(self.bin_path):
            os.mkdir(self.bin_path)
            os.chdir(self.bin_path)
            self._generate_settings_file()
        
        #Checks for settings file, if none exists, generates new one

        #Load in settings
        self._load_settings()
        
        self._master_except_ = ['.FolderKeeper',
                                'FolderKeeper.py',
                                '__pycache__']
        
        #Initial population of directory catalog
        self.refresh_dir()
        
        #Initial flag
        self.flags = {'Files':[],
                      'Directories':[]}
        self.flag_files()
        
    def menu(self):
        '''
        Opens interactive menu for management of Directory settings.
        '''        
        print('Main Menu')
        
        print('[1] Check files')
        print('[2] Clean flagged files')
        
    def refresh_dir(self):
        
        dir_dump = os.listdir(self.root_path)
        self.catalog = {'files':[], 'directories':[]}
        
        for item in dir_dump:
            
            if os.path.isfile(item):
                self.catalog['files'].append(item)
            elif os.path.isdir(item):
                self.catalog['directories'].append(item)
            else:
                print('Error: Unknown item detected in:')
                print(self.root_path)
                
        self.last_refresh = datetime.datetime.now()
        
        with open(self.settings_fname,'r') as file:
            data = file.readlines()
            data[4] = 'last_refresh = %s\n'%(self.last_refresh)
        with open(self.settings_fname,'w') as file:
            file.writelines(data)
        
        return
        
    def _generate_settings_file(self):
        
        f = open(self.settings_fname,'w')
        
        f.write('FolderKeeper Settings File for:\n'+self.root_path)
        f.write('\n\nlast_refresh = []')
        f.write('\n\nignore_list = []\n')
        f.write('extension_whitelist = []')
        f.write('\nrecursive = True')
        f.write('\nmonitor_age = True\nmax_age = 14 #days')
        f.write('\nauto_purge = False')
        f.write('\ndelete_empty_folders = True')
        
        f.close()
        
        return
    
    def _load_settings(self):
        
        self.settings = {}
        f = open(self.settings_fname,'r')
        lines = [line.rstrip('\n') for line in f]
        
        for line in lines[3:]:
            spltLine = line.split(sep=' = ')
            self.settings[spltLine[0]] = spltLine[1]

        f.close()
        
        return
    
    def flag_files(self):
        
        self.flags['Files'] = []
        
        for item in self.catalog['files']:
            self.flags['Files'].append(self._test_file(item))
            
    def _test_file(self,file):
        
        # Check in master ignore list
        if file in self._master_except_:
            return False
        
        # Check in ignore list
        if file in self.settings['ignore_list']:
            return False
        
        # Check extension against extension whitelist.
        spltFile = file.split('.')
        
        try:
            extension = '.'+spltFile[1]
        except IndexError:
            return None
        
        if extension in self.settings['extension_whitelist']:
            return False
        
        # File age check
        
        if self.settings['monitor_age']:
            now = datetime.datetime.now()
            file_last_edit = datetime.datetime.fromtimestamp(os.path.getmtime(file))
            cutoff = now - datetime.timedelta(days=self.settings['max_age'])
            
            if cutoff > file_last_edit:
                return True
            
        return False
    
    def clean_folder(self):
        
        for idx, item in enumerate(self.flags):
            if item:
                pass
                #send2trash.send2trash(self.catalog['files'][idx])
        elf.settings_fname = os.path.join(self.bin_path, 'fk_settings.fks')
        self.refresh_dir()
        
        return
        
    def flag_directories(self):
        '''
        Iterates through directories in Directory catalog, flags
        each directory in 2 steps. First bool sorts against binary checks;
        False for ignore, True for evaluate further. 
        
        Second step categorizes files for manipulation during clean_folder
        call.
        '''
        
        self.flags['Directories'] = []
        
        for directory in self.catalog['directories']:
            
            #Flags directories listed in Directory exception list as False
            if directory in self._master_except_:
                self.flags['Directories'].append(False)
                continue
            
        return            
#%%
root_directory = os.getcwd()
Root = FolderKeeper(root_directory)
Directories = [Root]
        
for Dir in reversed(Directories):
    Dir.flag_files()
    Dir.flag_directories()
    if Dir.settings['auto_purge'] == True:
        Dir.clean_folder()
