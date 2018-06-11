// --------------------------------------------------------------------------
//                   OpenMS -- Open-Source Mass Spectrometry
// --------------------------------------------------------------------------
// Copyright The OpenMS Team -- Eberhard Karls University Tuebingen,
// ETH Zurich, and Freie Universitaet Berlin 2002-2017.
//
// This software is released under a three-clause BSD license:
//  * Redistributions of source code must retain the above copyright
//    notice, this list of conditions and the following disclaimer.
//  * Redistributions in binary form must reproduce the above copyright
//    notice, this list of conditions and the following disclaimer in the
//    documentation and/or other materials provided with the distribution.
//  * Neither the name of any author or any participating institution
//    may be used to endorse or promote products derived from this software
//    without specific prior written permission.
// For a full list of authors, refer to the file AUTHORS.
// --------------------------------------------------------------------------
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
// ARE DISCLAIMED. IN NO EVENT SHALL ANY OF THE AUTHORS OR THE CONTRIBUTING
// INSTITUTIONS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
// EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
// PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
// OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
// WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
// OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
// ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
//
// --------------------------------------------------------------------------
// $Maintainer: UCSD Dorrestein Lab $
// $Authors: Abinesh Sarvepalli, Sean Nam $
// --------------------------------------------------------------------------

#include <OpenMS/APPLICATIONS/TOPPBase.h>
#include <OpenMS/CONCEPT/UniqueIdInterface.h>
#include <OpenMS/FORMAT/ConsensusXMLFile.h>
#include <OpenMS/FORMAT/MzMLFile.h>
#include <OpenMS/METADATA/PeptideIdentification.h>
#include <OpenMS/KERNEL/MSExperiment.h>
#include <OpenMS/KERNEL/MSSpectrum.h>
#include <iostream>
#include <fstream>

using namespace OpenMS;
using namespace std;

class TOPPGNPSExport : public TOPPBase
{
public:
	TOPPGNPSExport() :
	TOPPBase("GNPSExport", "Tool to export consensus features into MGF format", false) {}

protected:
	// this function will be used to register the tool parameters
	// it gets automatically called on tool execution
	void registerOptionsAndFlags_()
	{
		registerInputFile_("in_cm", "<file>", "", "input file containing consensus elements with PeptideIdentification annotation");
		setValidFormats_("in_cm", ListUtils::create<String>("consensusXML"));

		registerInputFileList_("in_mzml", "<files>", ListUtils::create<String>(""), "input files containing consensus elements with PeptideIdentification annotation");
		setValidFormats_("in_mzml", ListUtils::create<String>("mzML"));

		registerOutputFile_("out", "<file>", "", "Output MGF file");

		addEmptyLine_();

		registerStringOption_("condensed", "<choice>", "1", "Only output the most intense ion per feature", false);
		setValidStrings_("condensed", ListUtils::create<String>("0,1"));
		// setValidFormats_("out", ListUtils::create<String>("mgf"));
	}

	// the main function is called after all parameters are read
	ExitCodes main_(int, const char **)
	{
		ProgressLogger progressLogger;
		progressLogger.setLogType(log_type_);

		//-------------------------------------------------------------
		// parsing parameters
		//-------------------------------------------------------------
		String consensusFilePath(getStringOption_("in_cm"));
		StringList mzmlFilePaths(getStringList_("in_mzml"));

		String out(getStringOption_("out"));

		bool condensed = (getStringOption_("condensed") == "1");


		//-------------------------------------------------------------
		// reading input
		//-------------------------------------------------------------
		// ConsensusMap
		ConsensusXMLFile consensusFile;
		consensusFile.setLogType(log_type_);
		ConsensusMap consensusMap;
		consensusFile.load(consensusFilePath, consensusMap);

		// MSExperiment
		vector<MSExperiment> msMaps;
		for(auto mzmlFilePath : mzmlFilePaths) {
			MzMLFile mzmlFile;
			mzmlFile.setLogType(log_type_);
			MSExperiment map;
			mzmlFile.load(mzmlFilePath, map);
			msMaps.push_back(map);
		}


		//-------------------------------------------------------------
		// calculations
		//-------------------------------------------------------------
		progressLogger.startProgress(0, consensusMap.size(), "parsing consensusXML file for ms2 scans");
		std::stringstream outputStream;
		for(Size i = 0; i != consensusMap.size(); i ++)
		{
			progressLogger.setProgress(i);
			// current feature
			const ConsensusFeature& feature = consensusMap[i];

			// store "mz rt" information from each scan
			stringstream scansOutput;
			scansOutput << setprecision(2) << fixed;

			// default elem charge
			BaseFeature::ChargeType charge = feature.getCharge();
			// determining charge and most intense feature for header
			for (ConsensusFeature::HandleSetType::const_iterator featureIter = feature.begin(); featureIter != feature.end(); ++featureIter) {
				// check if current scan charge value is largest
				if(featureIter->getCharge() > charge) {
					charge = featureIter->getCharge();
				}
			}

			// print spectra information (PeptideIdentification tags)
			vector<PeptideIdentification> peptideAnnotations = feature.getPeptideIdentifications();

			vector<pair<pair<int,int>, double>> spectrumIntensities;
			int mapIndex = -1, spectrumIndex = -1;

			bool shouldSkipFeature = peptideAnnotations.empty();
			if(!shouldSkipFeature) {
				for (Size peptideIndex = 0; peptideIndex < peptideAnnotations.size(); peptideIndex++) {
					auto peptideAnnotation = peptideAnnotations[peptideIndex];

					// append spectra information to scansOutput
					if(peptideAnnotation.metaValueExists("spectrum_index")) {
						spectrumIndex = peptideAnnotation.getMetaValue("spectrum_index");
					}
					if(peptideAnnotation.metaValueExists("map_index")) {
						mapIndex = peptideAnnotation.getMetaValue("map_index");
					}

					if(spectrumIndex != -1 && mapIndex != -1) {
						// TEMP: log debug map index and spectrum index values once they are found
						LOG_DEBUG << "map index\t" << mapIndex << "\tspectrum index\t" << spectrumIndex << endl;

						// retrieve spectrum for current peptide annotation
						auto msMap = msMaps[mapIndex];
						auto ms2Scan = msMap.getSpectra()[spectrumIndex];
						ms2Scan.sortByIntensity(true);

						if(ms2Scan.getMSLevel() == 2 && !ms2Scan.empty()) {
							shouldSkipFeature = false;

							// store current peptideIndex and highest ms2 intensity
							pair<pair<int,int>, double> currSpectrumIntensity;
							currSpectrumIntensity.first = make_pair(mapIndex, spectrumIndex);
							currSpectrumIntensity.second = ms2Scan[0].getIntensity();
							spectrumIntensities.push_back(currSpectrumIntensity);

							// if(condensed) {
							// 	scansOutput << to_string(ms2Scan[0].getMZ()) << "\t" << ms2Scan[0].getIntensity() << endl;
							// } else {
							// 	for(Size l = 0; l < ms2Scan.size(); l++) {
							// 		scansOutput << to_string(ms2Scan[l].getMZ()) << "\t" << ms2Scan[l].getIntensity() << endl;
							// 	}
							// }
						}
					} else { shouldSkipFeature = true; }
				}
			}

			if(!shouldSkipFeature && !spectrumIntensities.empty()) {
				// prepare spectrumIntensities for output
				sort(spectrumIntensities.begin(), spectrumIntensities.end(), [](const pair<pair<int,int>, double> &a, const pair<pair<int,int>, double> &b) {
					return (a.second > b.second);
				});

				// consolidate feature+spectra annotation
				std::stringstream featureStream;

				featureStream << "FEATURE_ID=" << to_string(i+1) << endl;
				featureStream << "FILENAME=";
				set<string> filenames;
				for(auto spectrum : spectrumIntensities) {
					filenames.insert(mzmlFilePaths[spectrum.first.first]);
				}
				for(string filename : filenames) {
					featureStream << filename << " ";
				}
				featureStream << endl;
				featureStream << "SCANS=" << (i+1) << endl;
				featureStream << "MSLEVEL=2" << endl;
				featureStream << "CHARGE=" << std::to_string(charge == 0 ? 1 : charge) << "+" << endl;

				if(spectrumIntensities.empty()) {
					LOG_DEBUG << "FEATURE_ID=" << to_string(i+1) << endl;
					LOG_DEBUG << "SPECTRUMINTENSITIES SIZE=" << spectrumIntensities.size() << endl;
				}
				else if(condensed) {
					auto mostIntenseScanMetadata = spectrumIntensities[0].first;
					auto mostIntenseScan = msMaps[mostIntenseScanMetadata.first].getSpectra()[mostIntenseScanMetadata.second];

					featureStream << "PEPMASS=" << mostIntenseScan.getPrecursors()[0].getMZ() << endl;
					featureStream << "FILE_INDEX=" << mostIntenseScanMetadata.second << endl;
					featureStream << "RTINSECONDS=" << mostIntenseScan.getRT() << endl; // round RTINSECONDS to 2 decimal points
					featureStream << "BEGIN IONS" << endl;

					for(auto spectrum : spectrumIntensities) {
						auto ms2Scan = msMaps[spectrum.first.first].getSpectra()[spectrum.first.second];
						ms2Scan.sortByIntensity(true);

						featureStream << to_string(ms2Scan[0].getMZ()) << "\t" << ms2Scan[0].getIntensity() << endl;
					}

					// featureStream << scansOutput.str();
					featureStream << "END IONS" << endl;
				} else {
					for(auto spectrum : spectrumIntensities) {
						auto ms2Scan = msMaps[spectrum.first.first].getSpectra()[spectrum.first.second];
						ms2Scan.sortByIntensity(true);

						featureStream << endl;
						featureStream << "PEPMASS=" << ms2Scan.getPrecursors()[0].getMZ() << endl;
						featureStream << "FILE_INDEX=" << spectrum.first.second << endl;
						featureStream << "RTINSECONDS=" << ms2Scan.getRT() << endl; // round RTINSECONDS to 2 decimal points
						featureStream << "BEGIN IONS";
						for(Size l = 0; l < ms2Scan.size(); l++) {
							featureStream << to_string(ms2Scan[l].getMZ()) << "\t" << ms2Scan[l].getIntensity() << endl;
						}
						featureStream << "END IONS" << endl;
						featureStream << endl;						
					}
				}

				// output feature information to general outputStream
				outputStream << featureStream.str() << endl;
			}
		}
		progressLogger.endProgress();

		//-------------------------------------------------------------
		// writing output
		//-------------------------------------------------------------
		ofstream outputFile(out);
		outputFile << outputStream.str();
		outputFile.close();

		return EXECUTION_OK;
	}

};

// the actual main functioned needed to create an executable
int main(int argc, const char** argv) {
	TOPPGNPSExport tool;
	return tool.main(argc, argv);
}
/// @endcond
