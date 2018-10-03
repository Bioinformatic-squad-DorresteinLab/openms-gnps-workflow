import os
import shutil
import sys

'''
#2 module: id mapper
'''
def idmapper(input_port, ini_file, idxml_path, featurefinder_port, out_port):
    print("\n==ID MAPPER==")
    for file in os.listdir(featurefinder_port):
        if 'log' not in file:
            filename = os.path.splitext(file)[0].split('-')[1]
        else:
            continue

        input = featurefinder_port + '/' + file
        # input = featurefindermetabo_port + '/featurefinder-' + filename + '.featureXML'
        output = out_port + '/idmapper-' + filename + '.featureXML'
        # output = curr_port + '/out-' + filename + '.featureXML'

        command = 'IDMapper -ini ' + ini_file + ' -in ' + input + ' -id ' + idxml_path + ' -spectra:in '
        command += input_port+'/'+os.listdir(input_port)[int(filename)] + ' '
        # command += input_port+'/'+file + ' '
        command += '-out ' + output + ' >> ' + out_port+'/logfile.txt'

        print("COMMAND: " + command + '\n')
        os.system(command)



if __name__ == '__main__':
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

    idmapper(sys.argv[1], ini_file, "/data/beta-proteomics2/tools/openms/empty.idXML", sys.argv[4], sys.argv[5])
    # idmapper(sys.argv[1], ini_file, sys.argv[3], sys.argv[4], sys.argv[5])
