'''
This workflow script was intended to integrate OpenMS modules with GNPS.

The workflow operates as follows:
1. mzml         -> FeatureFinderMetabo          -> featureXml
2.              -> IDMapper
3. featureXml   -> FeautureLinkerUnlabeledQT    -> consensusXml
4. consensusXml -> FileConverter                -> featureXml
5. featureXml   -> MetaboliteAdductDecharger    -> featureXml & consensusXml
6. consensusXml -> GNPSExport                   -> mgf
'''

import os
import sys

# tmp_files = {0:'mapaligner', 1:'featurefindermetabo', 2:'metaboliteadductdecharge', 3:'in_3b.featureXML', 4:'in_4.featureXML', 5:'in_3a.featureXML', 6:'out.consensusXML'}
# outputs = []
ini_files = {
    'featurefinder': "/Users/abipalli/Developer/openms+gnps_workflow/ini_steps/1_FeatureFinderMetabo",
    'mapaligner': "/Users/abipalli/Developer/openms+gnps_workflow/ini_steps/2_MapAlignerPoseClustering",
    'adductdecharger': "/Users/abipalli/Developer/openms+gnps_workflow/ini_steps/3_MetaboliteAdductDecharger",
    'featurelinker': "/Users/abipalli/Developer/openms+gnps_workflow/ini_steps/4_FeatureLinkerUnlabeledQT",
    'idmapper_ini': "/Users/abipalli/Developer/openms+gnps_workflow/ini_steps/1b_IDMapper",
    'idmapper_id': "/Users/abipalli/Developer/openms+gnps_workflow/empty.idXML"
    }


def usage():
    print('usage: python __main__.py <input.mzML ...>')


def per_file_workflow_post(file, count):
    input_path = 'mapalignerposeclustering' + str(count) + '.featureXML'

    # 4 MetaboliteAdductDecharger
    print('\n==MetaboliteAdductDecharge==')
    output_3_fm = 'metaboliteadductdecharger'+str(count)+'.featureXML'
    output_3_cm = 'metaboliteadductdecharger'+str(count)+'.consensusXML'
    command = 'MetaboliteAdductDecharger -ini ' + ini_files['adductdecharger'] + ' -in ' + input_path + ' -out_cm ' + output_3_cm + ' -out_fm ' + output_3_fm
    print("COMMAND: " + command + '\n')
    os.system(command)
    # outputs[file] = [output_3_fm,output_3_cm]
    # outputs[file] = [output_3_cm]
    # outputs.append(output_3_cm)


def main():
    # 1 FeatureFinderMetabo & 2 IDMapper
    for i in range(1, len(sys.argv)):
        file = sys.argv[i]
        count = i

        # 1 FeatureFinderMetabo
        print('\n==FeatureFinderMetabo==')
        output_1 = 'featurefindermetabo'+str(count)+'.featureXML'
        command = 'FeatureFinderMetabo -ini ' + ini_files['featurefinder'] + ' -in ' + file + ' -out ' + output_1
        print("COMMAND: " + command + '\n')
        os.system(command)

        # 2 IDMapper
        print('\n==IDMapper==')
        output_2 = 'idmapper'+str(count)+'.featureXML'
        command = 'IDMapper -ini ' + ini_files['idmapper_ini'] + ' -in ' + output_1 + ' -id ' + ini_files['idmapper_id'] + ' -spectra:in ' + file + ' -out ' + output_2
        print("COMMAND: " + command + '\n')
        os.system(command)

        # 2a FileConverter
        print("\n==FileConverter==")
        output_2a = 'idmapper'+str(count)+'.consensusXML'
        command = "FileConverter -in " + output_2 + " -out " + output_2a
        print("COMMAND: " + command + '\n')
        os.system(command)


    # 3 FeatureLinkerUnlabeledQT (using featureXML)
    output_3 = ""
    # setup branching arrays for files
    file_1s = ["idmapper1.consensusXML"]; file_2s = []
    for i in range(2, len(sys.argv)):
        file_2s.append("idmapper" + str(i) + ".consensusXML")
    # run FeatureLinkerUnlabeledQT
    if len(sys.argv) - 1 > 1:
        for i in range(0, len(file_2s)):
            print('\n==FeatureLinkerUnlabeledQT==')

            file_count = i
            file_1 = file_1s[file_count]
            file_2 = file_2s[file_count]

            outfile = 'featureLinker'+str(i)+'.consensusXML'
            file_1s.append(outfile)

            command = 'FeatureLinkerUnlabeledQT -ini ' + ini_files['featurelinker'] + ' -in ' + file_1 + ' ' + file_2 + ' -out ' + outfile
            print("COMMAND: " + command + '\n')
            os.system(command)

        output_3 = file_1s[-1]
    else:
        output_3 = file_1s[0]


    # 4 FileConverter
    print("\n==FileConverter==")
    input_4 = output_3
    output_4 = "fileconverter.featureXML"
    command = "FileConverter -in " + input_4 + " -out " + output_4
    print("COMMAND: " + command + "\n")
    os.system(command)


    # 5 MetaboliteAdductDecharger
    input_5 = output_4
    print('\n==MetaboliteAdductDecharge==')
    output_5_fm = "metaboliteadductdecharger.featureXML"
    output_5_cm = "metaboliteadductdecharger.consensusXML"
    command = 'MetaboliteAdductDecharger -ini ' + ini_files['adductdecharger'] + ' -in ' + input_5 + ' -out_cm ' + output_5_cm + ' -out_fm ' + output_5_fm
    print("COMMAND: " + command + '\n')
    os.system(command)


    # 6 GNPSExport
    print('\n==GNPSExport==')
    input_6_cm = output_5_cm
    input_mzml = sys.argv[1:]
    output_6 = "OUT.mgf"
    command = "GNPSExport -in_cm " + input_6_cm + " -in_mzml "
    for mzml_file in input_mzml:
        command += mzml_file + " "
    command += "-out " + output_6
    print("COMMAND: " + command + '\n')
    os.system(command)


if __name__ == '__main__':
    print("===RUNNING OPENMS MOCK WORKFLOW===")

    # usage check
    if len(sys.argv) < 2:
        print('Invalid num of arguments')
        usage()
        exit()

    # run workflow
    main()

    # package folder contents
    # os.system("find ./ -type f -not -name 'OUT.mgf' -delete")

    os.system("mkdir inp")
    for i in range(1, len(sys.argv)):
        print(sys.argv[i])
        os.system("cp " + sys.argv[i] + " inp/")
