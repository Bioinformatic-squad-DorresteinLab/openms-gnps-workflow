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
#include <OpenMS/FORMAT/ConsensusXMLFile.h>
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
		registerInputFile_("in_cm", "<file>", "", "Input file containing consensus elements");
		setValidFormats_("in_cm", ListUtils::create<String>("consensusXML"));

		registerOutputFile_("out", "<file>", "", "Output MGF file");
		// setValidFormats_("out", ListUtils::create<String>("mgf"));
	}

	// the main function is called after all parameters are read
	ExitCodes main_(int, const char **)
	{
		//-------------------------------------------------------------
    // parsing parameters
    //-------------------------------------------------------------
		String in(getStringOption_("in"));
		String out(getStringOption_("out"));

		//-------------------------------------------------------------
    // reading input
    //-------------------------------------------------------------
		ConsensusMap map;
		ConsensusXMLFile().load(in, map);

		//-------------------------------------------------------------
    // calculations
    //-------------------------------------------------------------

		// look through RT range (consensusXML) and look through mzML file (for matching RT)
		// look through MZ range (consensusXML) and look through mzML file (for matching MZ)

		std::stringstream outputStream;
		for(Size i = 0; i != map.size(); i ++)
		{
			const ConsensusFeature& feature = map[i];

			// store "mz rt" information from each scan
			String scansOutput = "";

			// default elem charge
			BaseFeature::ChargeType charge = feature.getCharge();

			// iterate through each scan
			auto mostIntensePrec = null;
			float mostIntenseVal = 0;
			for (ConsensusFeature::HandleSetType::const_iterator it = feature.begin(); it != feature.end(); ++it) {
				// append specific scan information to scansOutput
//				scansOutput += std::to_string(it->getMZ()) + " " + std::to_string(it->getRT()) + "\n";
				if(it->getIntensity() > mostIntenseVal) {
					mostIntenseVal = it->getIntensity();
					mostIntensePrec = *it;
				}

				// export the spectrum with the highest intensity (for precursor ion)



				// check if current scan charge value is largest
				if(it->getCharge() > charge) {
					charge = it->getCharge();
				}
			}

			// validate number of scans outputted
			std::stringstream featureStream;
			featureStream << "BEGIN IONS" << endl;
			featureStream << "FEATURE_ID=" << std::to_string(i+1) << endl;
			featureStream << "PEPMASS=" << precisionWrapper(feature.getMZ()) << endl;
			featureStream << "SCANS=" << std::to_string(i+1) << endl;
			featureStream << "RTINSECONDS=" << precisionWrapper(feature.getRT()) << endl; // round RTINSECONDS to 2 decimal points
			featureStream << "CHARGE=" << std::to_string(charge) << endl; // CHARGE = 1 when == 0
			featureStream << "MSLEVEL=2" << endl;

			// scansOutput must match original mzML spectral list
			featureStream << scansOutput;



			featureStream << "END IONS" << endl;


			outputStream << featureStream.str() << endl;
		}


		//-------------------------------------------------------------
    // writing output
    //-------------------------------------------------------------
		ofstream outputFile(out);
		outputFile.precision(writtenDigits<double>(0.0));
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
