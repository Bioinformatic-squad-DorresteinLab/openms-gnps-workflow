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


input_files = []

ini_files = {
'featurefinder': "/Users/abipalli/Developer/openms+gnps_workflow/ini_steps/1_FeatureFinderMetabo",
'idmapper_id': "/Users/abipalli/Developer/openms+gnps_workflow/empty.idXML",
'idmapper_ini': "/Users/abipalli/Developer/openms+gnps_workflow/ini_steps/1b_IDMapper",
'mapaligner': "/Users/abipalli/Developer/openms+gnps_workflow/ini_steps/2_MapAlignerPoseClustering",
'featurelinker': "/Users/abipalli/Developer/openms+gnps_workflow/ini_steps/3_FeatureLinkerUnlabeledKD",
'adductdecharger': "/Users/abipalli/Developer/openms+gnps_workflow/ini_steps/4_MetaboliteAdductDecharger"
}


def usage():
    print('usage: python __main__.py <dir>')


def main():
    # 1 FeatureFinderMetabo + IDMapper + FileConverter
    for i in range(1, len(input_files)):
        file = input_files[i]
        count = i

        # 1 FeatureFinderMetabo
        print('\n==FeatureFinderMetabo==')
        output_1 = 'featurefindermetabo'+str(count)+'.featureXML'
        command = 'FeatureFinderMetabo -ini ' + ini_files['featurefinder'] + ' -in ' + file + ' -out ' + output_1
        print("COMMAND: " + command + '\n')
        os.system(command)

        # 1a IDMapper
        print('\n==IDMapper==')
        output_1a = 'idmapper'+str(count)+'.featureXML'
        command = 'IDMapper -ini ' + ini_files['idmapper_ini'] + ' -in ' + output_1 + ' -id ' + ini_files['idmapper_id'] + ' -spectra:in ' + file + ' -out ' + output_1a
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
    output_2 = "poseclustering.featureXML"
    command = "MapAlignerPoseClustering -ini " + ini_files['mapaligner'] + ' -in '
    for i in range(1, len(input_files)):
        command += "idmapper" + str(i) + ".featureXML "
        output_2 += "poseclustering" + str(i) + ".featureXML "
    command += "-out " + output_2
    print("COMMAND: " + command + '\n')
    os.system(command)


    # 3 FeatureLinkerUnlabeledQT (using featureXML)
    print("\n==FeatureLinkerUnlabeledKD==")
    output_3 = "featureLinker.consensusXML"
    command = "FeatureLinkerUnlabeledKD -ini " + ini_files['featurelinker'] + " -in " + output_2 + " -out " + output_3
    print("COMMAND: " + command + '\n')
    os.system(command)
    # Setup branching arrays for files
    # file_1s = ["idmapper1.consensusXML"]; file_2s = []
    # for i in range(2, len(input_files)):
    #     file_2s.append("idmapper" + str(i) + ".consensusXML")
    # Run FeatureLinkerUnlabeledQT
    # if len(input_files) - 1 > 1:
    #     for i in range(0, len(file_2s)):
    #         print('\n==FeatureLinkerUnlabeledQT==')
    #
    #         file_count = i
    #         file_1 = file_1s[file_count]
    #         file_2 = file_2s[file_count]
    #
    #         outfile = 'featureLinker'+str(i)+'.consensusXML'
    #         file_1s.append(outfile)
    #
    #         command = 'FeatureLinkerUnlabeledQT -ini ' + ini_files['featurelinker'] + ' -in ' + file_1 + ' ' + file_2 + ' -out ' + outfile
    #         print("COMMAND: " + command + '\n')
    #         os.system(command)
    #
    #     output_3 = file_1s[-1]
    # else:
    #     output_3 = file_1s[0]


    # 3a FileConverter
    print("\n==FileConverter==")
    input_4 = output_3
    output_4 = "featureLinker.featureXML"
    command = "FileConverter -in " + input_4 + " -out " + output_4
    print("COMMAND: " + command + "\n")
    os.system(command)


    # 4 MetaboliteAdductDecharger
    input_5 = output_4
    print('\n==MetaboliteAdductDecharge==')
    output_5_fm = "metaboliteadductdecharger.featureXML"
    output_5_cm = "metaboliteadductdecharger.consensusXML"
    command = 'MetaboliteAdductDecharger -ini ' + ini_files['adductdecharger'] + ' -in ' + input_5 + ' -out_cm ' + output_5_cm + ' -out_fm ' + output_5_fm
    print("COMMAND: " + command + '\n')
    os.system(command)


    # 5 GNPSExport
    print('\n==GNPSExport==')
    input_6_cm = output_5_cm
    output_6 = "OUT.mgf"
    command = "GNPSExport -in_cm " + input_6_cm + " -in_mzml "
    for mzml_file in input_files[1:]:
        command += mzml_file + " "
    command += "-out " + output_6
    command += " -condensed 1"
    print("COMMAND: " + command + '\n')
    os.system(command)


if __name__ == '__main__':
    print("===RUNNING OPENMS MOCK WORKFLOW===")

    # usage check
    if len(sys.argv) is not 2:
        print('Invalid num of arguments')
        usage()
        exit()

    # input files
    if sys.argv[1][-1] is not '/':
        sys.argv[1] += '/'

    input_files.append(sys.argv[0])
    # input_files.append(sys.argv[1])
    for root, dirs, files in os.walk(sys.argv[1]):
        for file in files:
            input_files.append(sys.argv[1] + file)

    # run workflow
    main()

    # package folder contents
    # os.system("find ./ -type f -not -name 'OUT.mgf' -delete")

    # os.system("mkdir inp")
    # os.system("cp " + sys.argv[1] + "* inp/")
