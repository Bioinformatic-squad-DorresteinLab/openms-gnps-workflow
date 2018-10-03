import os
import shutil
import sys

'''
#3 module: map aligner pose clustering
'''
def mapalignerposeclustering(idmapper_port, ini_file, out_port):
    command = "MapAlignerPoseClustering -ini " + ini_file + " -in "
    output = ""

    for file in os.listdir(idmapper_port):
        if 'log' not in file:
            command += idmapper_port+'/'+file + ' '

    command += '-out '
    for file in os.listdir(idmapper_port):
        if 'log' not in file:
            filename = os.path.splitext(file)[0].split('-')[1]
            command += out_port+"/mapaligner-"+filename+".featureXML "
    command += ' >> ' + out_port+'/logfile.txt'

    print("COMMAND: " + command + "\n")
    os.system(command)


if __name__ == '__main__':
    print("===MAP ALIGNER POSE CLUSTERING===")

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

    mapalignerposeclustering(sys.argv[1], ini_file, sys.argv[3])
    # mapalignerposeclustering(sys.argv[1], sys.argv[2], sys.argv[3])
