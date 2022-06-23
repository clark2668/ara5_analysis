TGraph *do_with_FFTtools ( TGraph *grWave ) {
    
    double *oldY = grWave->GetY(); // mV
    double *oldX = grWave->GetX(); // ns
    int length=grWave->GetN();
    double deltaT = (oldX[1]-oldX[0]) * 1.e-9; // deltaT in s
    FFTWComplex *theFFT=FFTtools::doFFT(length,oldY); // FFT with mV unit
    int newLength=(length/2)+1;
    double *newY = new double [newLength];
    double *newX = new double [newLength];
    double deltaF=1./(deltaT*(double)length); //Hz
    deltaF*=1E-6; // from Hz to MHz
    double tempF=0;
    for(int i=0;i<newLength;i++) {
        
        // Half of the power is missing in this FFT convention
        // because we have no negative frequencies.
        // So in the time domain, remember voltage = sqrt(power),
        // we need to correct by sqrt(2).
        
        newY[i] = sqrt(2.) * FFTtools::getAbs(theFFT[i]); // from mV to V
        newX[i]=tempF;
        tempF+=deltaF;
    }
    TGraph *grSpectrum = new TGraph(newLength,newX,newY);

    // check Parseval

    // time domain
    double power_time = 0;
    for(int i=0; i<grWave->GetN(); i++ ){
        power_time += TMath::Power(grWave->GetY()[i], 2.);
    }

    // frequency domain
    double power_freq = 0;
    for(int i=0; i<grSpectrum->GetN(); i++){
        power_freq += TMath::Power(grSpectrum->GetY()[i], 2.);
    }
    power_freq/=double(grWave->GetN());

    std::cout<<"Power time "<<power_time<<" and power frequency "<<power_freq<<std::endl;

    delete [] theFFT;
    delete [] newY;
    delete [] newX;
    return grSpectrum;
}

