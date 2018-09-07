'''
This workflow script was intended to integrate OpenMS modules with GNPS.

The workflow operates as follows:
1.  mzml(s)          -> FeatureFinderMetabo          -> featureXML(s)
    featureXML(s)    -> IDMapper                     -> featureXML(s)
2.  featureXML(s)    -> MapAlignerPoseClustering     -> featureXML(s)
3.  featureXML       -> FeautureLinkerUnlabeledKD    -> consensusXML
    consensusXML     -> FileConverter                -> featureXML
4.  featureXML       -> MetaboliteAdductDecharger    -> featureXML & consensusXML
5.  consensusXML     -> GNPSExport                   -> mgf
'''

import os
import sys
import xmltodict as xtd


ini_path = "/data/beta-proteomics2/tools/openms/ini-steps"
ini_files = {
'featurefinder': ini_path+"/1-featurefindermetabo",
'idmapper_id': ini_path+"/empty.idXML",
'idmapper_ini': ini_path+"/1b-idmapper",
'mapaligner': ini_path+"/2-mapalignerposeclustering",
'featurelinker': ini_path+"/3-featurelinkerunlabeledqt",
'adductdecharger': ini_path+"/4-metaboliteadductdecharger"
}

command_dir = "/data/beta-proteomics2/tools/openms/openms-env/openms-build/bin/"


def main(input_files, output_dir, output_type, ini_files):
    # 1 FeatureFinderMetabo + IDMapper + FileConverter
    print('\n==FeatureFinderMetabo & IDMapper==')
    for i in range(len(input_files)):
        file = input_files[i]
        count = i

        # 1 FeatureFinderMetabo
        output_1 = output_dir + '/featurefindermetabo'+str(count)+'.featureXML'
        command = command_dir+'FeatureFinderMetabo -ini ' + ini_files['featurefinder'] + ' -in ' + file + ' -out ' + output_1
        print("COMMAND: " + command + '\n')
        os.system(command)

        print('\n')

        # 1a IDMapper
        output_1a = output_dir + '/idmapper'+str(count)+'.featureXML'
        command = command_dir+'IDMapper -ini ' + ini_files['idmapper_ini'] + ' -in ' + output_1 + ' -id ' + ini_files['idmapper_id'] + ' -spectra:in ' + file + ' -out ' + output_1a
        print("COMMAND: " + command + '\n')
        os.system(command)


        # Do not need FileConverter if featureXML is going to be fed into
        # MapAlignerPoseClustering...

        # 1b FileConverter
        # print("\n==FileConverter==")
        # output_2a = 'idmapper'+str(count)+'.consensusXML'
        # command = "FileConverter -in " + output_2 + " -out " + output_2a
        # print("COMMAND: " + command + '\n')
        # os.system(command)


    # 2 MapAlignerPoseClustering
    print("\n==MapAlignerPoseClustering==")
    output_2 = ''
    command = command_dir+"MapAlignerPoseClustering -ini " + ini_files['mapaligner'] + ' -in '
    for i in range(len(input_files)):
        command += output_dir + "/idmapper" + str(i) + ".featureXML "
        output_2 += output_dir + "/poseclustering" + str(i) + ".featureXML "
    command += "-out " + output_2
    print("COMMAND: " + command + '\n')
    os.system(command)


    # 3 FeatureLinkerUnlabeledQT (using featureXML)
    print("\n==FeatureLinkerUnlabeledKD==")
    if len(input_files) > 1:
        output_3 = output_dir + "/featureLinker.consensusXML"
        command = command_dir+"FeatureLinkerUnlabeledKD -ini " + ini_files['featurelinker'] + " -in " + output_2 + " -out " + output_3
        print("COMMAND: " + command + '\n')
        os.system(command)


    # 3a FileConverter
    print("\n==FileConverter==")
    if len(input_files) > 1:
        output_4 = output_dir + "/featureLinker.featureXML"
        command = ""
        command = command_dir+"FileConverter -in " + output_3 + " -out " + output_4
        print("COMMAND: " + command + "\n")
        os.system(command)


    # 4 MetaboliteAdductDecharger
    print('\n==MetaboliteAdductDecharge==')
    output_5_fm = output_dir + "/metaboliteadductdecharger.featureXML"
    output_5_cm = output_dir + "/metaboliteadductdecharger.consensusXML"
    command = ""
    if len(input_files) > 1:
        command = command_dir+'MetaboliteAdductDecharger -ini ' + ini_files['adductdecharger'] + ' -in ' + output_4 + ' -out_cm ' + output_5_cm + ' -out_fm ' + output_5_fm
    else:
        command = command_dir+'MetaboliteAdductDecharger -ini ' + ini_files['adductdecharger'] + ' -in ' + output_2 + ' -out_cm ' + output_5_cm + ' -out_fm ' + output_5_fm
    print("COMMAND: " + command + '\n')
    os.system(command)


    # 5 GNPSExport
    print('\n==GNPSExport==')
    output_6 = output_dir + "/OUT.mgf"
    command = command_dir+"GNPSExport -ini " + ini_files['gnpsexport'] + " -in_cm " + output_5_cm + " -in_mzml "
    for mzml_file in input_files:
        command += mzml_file + " "
    command += "-out " + output_6
    command += " -output_type " + output_type
    print("COMMAND: " + command + '\n')
    os.system(command)


if __name__ == '__main__':
    print("===RUNNING OPENMS MOCK WORKFLOW===")

    # input files
    input_files = []

    input_dir = os.path.abspath(sys.argv[1])

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            input_files.append(os.path.abspath(input_dir+'/'+file))


    #  output dir
    output_dir = sys.argv[2]


    # output type
    output_type = 'merged_spectra'
    with open(sys.argv[3], 'r') as fp:
        params = xtd.parse(fp.read())
        for param in params['parameters']['parameter']:
            if param['@name'] == "output_type":
                output_type = param['#text']
    print(output_type)

    # ini paths
    ini_files = {
    'featurefinder': sys.argv[4],
    'idmapper_id': ini_path+"/empty.idXML",
    'idmapper_ini': sys.argv[5],
    'mapaligner': sys.argv[6],
    'featurelinker': sys.argv[7],
    'adductdecharger':sys.argv[8],
    'gnpsexport': sys.argv[9]
    }

    # set env
    if os.environ.has_key("LD_LIBRARY_PATH"):
        os.environ["SANS_LD_LIBRARY_PATH"] = os.environ["LD_LIBRARY_PATH"]
    os.environ["LD_LIBRARY_PATH"] = "/data/beta-proteomics2/tools/openms/openms-env/conda/envs/openms_2.3/lib"

    if os.environ.has_key("PATH"):
        os.environ["SANS_PATH"] = os.environ["PATH"]
    os.environ["PATH"] = "/data/beta-proteomics2/tools/openms/openms-env/conda/envs/openms_2.3/bin"

    openms_data_path = '/data/beta-proteomics2/tools/openms/openms-env/share'
    os.environ["OPENMS_DATA_PATH"] = os.path.abspath(openms_data_path)
    print("output_dir: " + os.path.abspath(openms_data_path))


    # run workflow
    main(input_files, output_dir, output_type, ini_files)

    # restore env
    # os.system('export PATH=$SANS_PATH && unset SANS_PATH')
    # os.system('export LD_LIBRARY_PATH=$SANS_LD_LIBRARY_PATH && unset SANS_LD_LIBRARY_PATH')
    # os.system('unset LD_PRELOAD')

    # os.system("mv OUT.mgf " + sys.argv[2])

    # package folder contents
    # os.system("find ./ -type f -not -name 'OUT.mgf' -delete")

    # os.system("mkdir inp")
    # os.system("cp " + sys.argv[1] + "* inp/")
