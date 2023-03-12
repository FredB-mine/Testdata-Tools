from importlib import import_module
from os import system, listdir
from sys import argv
from zipfile import *

from cyaron import *

try:
    root = argv[1]
except IndexError:
    print("No Problem Id given, data generation terminated")
    exit(0)

if root.startswith('.\\') or root.startswith('./'):
    root = root[2:]

print('Problem Root:', root)
moduleRoot = root.replace('/', '.')
try:
    Config = import_module(moduleRoot + '.Config')
except Exception:
    if 'gen.py' in listdir(f'./{moduleRoot}'):
        print('Old generater found, running...')
        system(f'python3 ./{moduleRoot}/gen.py')
    else:
        print('No Config.py or gen.py found, please check the directory')
    exit(0)

print('Read Config v' + Config.version)

useConfigGen = False
try:
    useConfigGen = Config.genOut
except Exception:
    pass

zipName = root.split('/')[-1] + '.zip'
zipFile = ZipFile(root + '/' + zipName, 'w')

def compileCpp() -> int:
    realCpp = root + '/' + Config.std_name
    cmd = f"g++ -O3 -g -m64 -std=c++14 -Wall -o {root}/std.exe {realCpp}"
    print("Compile cmd: ", cmd)
    return system(cmd)

def main() -> int:
    if not useConfigGen:
        retval = compileCpp()
        if retval != 0:
            print('Compile Failure')
            return 0
    for textGroup in range(1, Config.data_set + 1):
        # IO Object Creation
        file = IO(
            file_prefix = root + '/',
            data_id = textGroup
        )
        # Gen Data 
        if Config.version.split('.')[0] == '1':
            file.input_write(Config.generater(textGroup))
        else:
            ret = Config.Gen.generater(textGroup, file)
            if ret != None:
                file.input_write(ret)   
        # Gen Output
        if not useConfigGen:
            file.output_gen(f'{root}/std.exe')
        print(f'Generated Testcase {textGroup}')
        zipFile.write(
            f'{root}/{textGroup}.in', arcname = f'{textGroup}.in', 
            compress_type = ZIP_DEFLATED, compresslevel = 9
        )
        zipFile.write(
            f'{root}/{textGroup}.out', arcname = f'{textGroup}.out', 
            compress_type = ZIP_DEFLATED, compresslevel = 9
        )
    zipFile.close()
    return 0
        
if __name__ == '__main__':
    exit(main())