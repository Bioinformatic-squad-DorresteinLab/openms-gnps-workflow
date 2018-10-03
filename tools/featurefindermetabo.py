import os
import shutil
import sys

'''
#1 module: feature finder metabo
'''
def featurefindermetabo(input_port, ini_file, out_port):
    for file in os.listdir(input_port):
        filename = os.path.splitext(file)[0].split('-')[1]
        # output = curr_port + '/out-' + filename + '.featureXML'
        output = out_port + '/featurefinder-' + filename + '.featureXML'

        command = 'FeatureFinderMetabo -ini ' + ini_file + ' -in ' + input_port+'/'+file + ' -out ' + output + ' >> ' + out_port+'/logfile.txt'

        print("COMMAND: " + command + '\n')
        os.system(command)



if __name__ == '__main__':
    print("===FEATURE FINDER METABO===")

    # set env
    if os.environ.has_key("LD_LIBRARY_PATH"):
        os.environ["SANS_LD_LIBRARY_PATH"] = os.environ["LD_LIBRARY_PATH"]
    os.environ["LD_LIBRARY_PATH"] = "/data/beta-proteomics2/tools/openms_2.4/openms-env/conda/lib"

    if os.environ.has_key("PATH"):
        os.environ["SANS_PATH"] = os.environ["PATH"]
    os.environ["PATH"] = "/data/beta-proteomics2/tools/openms_2.4/openms-env/conda/bin:/data/beta-proteomics2/tools/openms_2.4/openms-env/openms-build/bin:$PATH"

    openms_data_path = '/data/beta-proteomics2/tools/openms_2.4/openms-env/share'
    os.environ["OPENMS_DATA_PATH"] = os.path.abspath(openms_data_path)

    curr_dir = os.listdir(os.path.dirname(os.path.abspath(sys.argv[1])))
    print(curr_dir)
    for i in range(len(curr_dir)):
        print(os.listdir(curr_dir[i]))

    # ini file
    ini_file = 'iniFiles/'+os.listdir('iniFiles')[0]
    shutil.copyfile(ini_file, sys.argv[2])

    featurefindermetabo(sys.argv[1], ini_file, sys.argv[3])
    # featurefindermetabo(sys.argv[1], sys.argv[2], sys.argv[3])
