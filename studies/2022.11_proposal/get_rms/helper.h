#include "UsefulAtriStationEvent.h"

std::vector<TGraph*> makeGraphsFromRF(UsefulAtriStationEvent* realAtriEvPtr, int numGraphs){

	std::vector<TGraph*> graphs;

	for (int i = 0; i < numGraphs; i++){
		TGraph* gr = realAtriEvPtr->getGraphFromRFChan(i);
		graphs.push_back(gr);
	}
	
	return graphs;
}

// get RMS for single array
double getRMS(double *array, int bin) {

  double x,y;
  double RMSVal = 0.;
  for(int i=0;i<bin;i++) {
    RMSVal += (array[i]*array[i]);
  }

  return sqrt(RMSVal/((double)bin));

}

// get RMS for graph
double getRMS( TGraph *plot, int numPointsToInclude)
{
  int nPoints = plot->GetN();
  //  Double_t *xVals = plot->GetX();                                                                                                          
  Double_t *yVals = plot->GetY();

  int pointsToAdd;
  if (numPointsToInclude > nPoints || numPointsToInclude == 0){
    pointsToAdd = nPoints;
  } else {
    pointsToAdd = numPointsToInclude;
  }

  double RMS = getRMS(yVals, pointsToAdd);

  return RMS;
}

// get RMS for vector of graphs
void getRMS(std::vector<TGraph*> graphs, std::vector<double> &vRMS, int numPointsToInclude){

  vRMS.clear();
  double RMS;

  for (int i = 0; i < graphs.size(); i++){
    int numPoints_temp = numPointsToInclude;
    if(numPointsToInclude == 0){
      numPoints_temp = graphs[i]->GetN();
    }

    RMS = getRMS(graphs[i], numPoints_temp);
    vRMS.push_back(RMS);
  }
}