import os
import shutil
import sys
import xmltodict as xtd

'''
#6 module: gnps export
'''
def textexporter(input_port, ini_file, out_port):
    file = input_port+'/'+"featurelinker.consensusXML"

    command = "TextExporter -ini " + ini_file + " -in " + file + " -out " + out_port+'/textexporter.csv' + ' >> ' + out_port+'/logfile.txt'
    # command = command_dir+"TextExporter -ini " + ini_file + " -in " + file + " -out " + curr_port+'/out.csv'

    print("COMMAND: " + command + "\n")
    os.system(command)



if __name__ == '__main__':
    print("===TEXT EXPORTER===")

    # set env
    if os.environ.has_key("LD_LIBRARY_PATH"):
        os.environ["SANS_LD_LIBRARY_PATH"] = os.environ["LD_LIBRARY_PATH"]
    os.environ["LD_LIBRARY_PATH"] = "/data/beta-proteomics2/tools/openms_2.4/openms-env/conda/lib"

    if os.environ.has_key("PATH"):
        os.environ["SANS_PATH"] = os.environ["PATH"]
    os.environ["PATH"] = "/data/beta-proteomics2/tools/openms_2.4/openms-env/conda/bin:/data/beta-proteomics2/tools/openms_2.4/openms-env/openms-build/bin:$PATH"

    openms_data_path = '/data/beta-proteomics2/tools/openms_2.4/openms-env/share'
    os.environ["OPENMS_DATA_PATH"] = os.path.abspath(openms_data_path)


    curr_dir = os.listdir('.')
    print(curr_dir)
    for dir in curr_dir:
        print(dir+":")
        print(os.listdir(dir))


    # ini file
    ini_file = 'iniFiles/'+os.listdir('iniFiles')[0]
    # shutil.copyfile(ini_file, sys.argv[2])

    textexporter(sys.argv[1], ini_file, sys.argv[3])
