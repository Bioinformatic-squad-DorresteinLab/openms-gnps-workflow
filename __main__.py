import os
import sys

# tmp_files = {0:'mapaligner', 1:'featurefindermetabo', 2:'metaboliteadductdecharge', 3:'in_3b.featureXML', 4:'in_4.featureXML', 5:'in_3a.featureXML', 6:'out.consensusXML'}
outputs = []
ini_files = {'featurefinder': "/Users/abipalli/Developer/openms/default_ini_steps/1_FeatureFinderMetabo",
    'mapaligner': "/Users/abipalli/Developer/openms/default_ini_steps/2_MapAlignerPoseClustering",
    'adductdecharger': "/Users/abipalli/Developer/openms/default_ini_steps/3_MetaboliteAdductDecharger",
    'featurelinker': "/Users/abipalli/Developer/openms/default_ini_steps/4_FeatureLinkerUnlabeledQT",
    'idmapper_ini': "/Users/abipalli/Developer/openms/default_ini_steps/1b_IDMapper",
    'idmapper_id': "/Users/abipalli/Developer/openms/empty.idXML"}


def usage():
    print('usage: python __main__.py <input.mzML>')


def per_file_workflow_pre(file, count):
    # 1 FeatureFinderMetabo
    print('\n==FeatureFinderMetabo==')
    output_1 = 'featurefindermetabo'+str(count)+'.featureXML'
    command = 'FeatureFinderMetabo -ini ' + ini_files['featurefinder'] + ' -in ' + file + ' -out ' + output_1
    print("COMMAND: " + command + '\n')
    os.system(command)

    # 1b IDMapper
    print('\n==IDMapper==')
    output_1b = 'idmapper'+str(count)+'.featureXML'
    command = 'IDMapper -ini ' + ini_files['idmapper_ini'] + ' -in ' + output_1 + ' -id ' + ini_files['idmapper_id'] + ' -out ' + output_1b
    print("COMMAND: " + command + '\n')
    os.system(command)


def per_file_workflow_post(file, count):
    input_path = 'mapalignerposeclustering' + str(count) + '.featureXML'

    # 3 MetaboliteAdductDecharger
    print('\n==MetaboliteAdductDecharge==')
    output_3_fm = 'metaboliteadductdecharger'+str(count)+'.featureXML'
    output_3_cm = 'metaboliteadductdecharger'+str(count)+'.consensusXML'
    command = 'MetaboliteAdductDecharger -ini ' + ini_files['adductdecharger'] + ' -in ' + input_path + ' -out_cm ' + output_3_cm + ' -out_fm ' + output_3_fm
    print("COMMAND: " + command + '\n')
    os.system(command)
    # outputs[file] = [output_3_fm,output_3_cm]
    # outputs[file] = [output_3_cm]
    outputs.append(output_3_cm)


def main():
    # 1 FeatureFinderMetabo
    for i in range(1, len(sys.argv)):
        per_file_workflow_pre(sys.argv[i], i)

    # 2 MapAlignerSpectrum (using featureXML)
    print('\n==MapAlignerPoseClustering==')
    command = 'MapAlignerPoseClustering -ini ' + ini_files['mapaligner'] + ' -in'
    #   module inputs
    for i in range(1, len(sys.argv)):
        command = command + ' ' + 'idmapper'+str(i)+'.featureXML'
    #   module outputs
    command = command + ' -out'
    for i in range(1, len(sys.argv)):
        command = command + ' mapalignerposeclustering' + str(i) + '.featureXML'
    #   module command
    print("COMMAND: " + command + '\n')
    os.system(command)

    # 3 MetaboliteAdductDecharger
    for i in range(1, len(sys.argv)):
        per_file_workflow_post(sys.argv[i], i)

    # 4 FeatureLinkerUnlabeledQT
    output_4 = ""
    if len(sys.argv) - 1 > 1:
        file_1s = [outputs[0]]
        file_2s = outputs[1:]

        for i in range(0, len(file_2s)):
            file_count = i
            print('\n==FeatureLinkerUnlabeledQT==')
            command = 'FeatureLinkerUnlabeledQT -ini ' + ini_files['featurelinker']
            #   featureXML
            file_1 = file_1s[file_count]
            file_2 = file_2s[file_count]
            command = command + ' -in ' + file_1 + ' ' + file_2

            outfile = 'featureLinker'+str(i)+'.consensusXML'
            file_1s.append(outfile)
            command = command + ' -out ' + outfile
            print("COMMAND: " + command + '\n')
            os.system(command)

        output_4 = file_1s[len(file_1s)-1]
    else:
        output_4 = outputs[0]

    # 5 GNPSExport
    print('\n==GNPSExport==')
    output_5 = "OUT.mgf"
    input_5 = output_4

    command = "GNPSExport -in " + input_5 + " -out " + output_5
    print("COMMAND: " + command + '\n')
    os.system(command)



def clean(orig_dir):
    print('\n==CLEANING OUT TEMP FILES==')
    for file in os.listdir('.'):
        if file not in orig_dir:
            print('removing ' + file + '...')
            os.system('rm ' + file)


if __name__ == '__main__':
    print("===RUNNING OPENMS MOCK WORKFLOW===")
    if len(sys.argv) < 2:
        print('Invalid num of arguments')
        usage()
        exit()
    # orig_dir = os.listdir('.')
    main()
    # clean(orig_dir)
