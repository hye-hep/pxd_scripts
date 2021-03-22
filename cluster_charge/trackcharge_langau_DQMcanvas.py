import ROOT
from ROOT import gStyle, TF1, TMath, TH1F

# Global style settings
gStyle.SetOptStat(1111)
gStyle.SetOptFit(111)
gStyle.SetLabelSize(0.03,"x")
gStyle.SetLabelSize(0.03,"y")

#Numeric constants
invsq2pi = 0.3989422804014  #(2 pi)^(-1/2)
mpshift  = -0.22278298  # Landau maximum location

def langaufun(x, par):
    '''
        Fit parameters:
        par[0]=Width (scale) parameter of Landau density
        par[1]=Most Probable (MP, location) parameter of Landau density
        par[2]=Total area (integral -inf to inf, normalization constant)
        par[3]=Width (sigma) of convoluted Gaussian function

        In the Landau distribution (represented by the CERNLIB approximation),
        the maximum is located at x=-0.22278298 with the location parameter=0.
        This shift is corrected within this function, so that the actual
        maximum is identical to the MP parameter.
        '''

    # control constants
    ns = 100  # number of convolution steps
    sc = 5.0  # convolution extends to +-sc Gaussian sigmas

    # MP shift correction
    mpc = par[1] - mpshift * par[0]
    xlow = x[0] - sc * par[3]
    xupp = x[0] + sc * par[3]
    step = (xupp-xlow) / ns

    sumup = 0
    for i in range(1,ns/2):
        xx = xlow + (i-0.5) * step
        fland = TMath.Landau(xx,mpc,par[0]) / par[0]
        sumup += fland * TMath.Gaus(x[0],xx,par[3])

        xx = xupp - (i-.5) * step
        fland = TMath.Landau(xx,mpc,par[0]) / par[0]
        sumup += fland * TMath.Gaus(x[0],xx,par[3])


    return par[2] * step * sumup * invsq2pi / par[3]

def langaufit(his, fitrange, startvalues, parlimitslo, parlimitshi):
    '''
        // Landau * Gaussian parameters:
        //   par[0]=Width (scale) parameter of Landau density
        //   par[1]=Most Probable (MP, location) parameter of Landau density
        //   par[2]=Total area (integral -inf to inf, normalization constant)
        //   par[3]=Width (sigma) of convoluted Gaussian function
        //
        // Variables for langaufit call:
        //   his             histogram to fit
        //   fitrange[2]     lo and hi boundaries of fit range
        //   startvalues[4]  reasonable start values for the fit
        //   parlimitslo[4]  lower parameter limits
        //   parlimitshi[4]  upper parameter limits
        //   fitparams[4]    returns the final fit parameters
        //   fiterrors[4]    returns the final fit errors
        //   ChiSqr          returns the chi square
        //   NDF             returns ndf
        '''

    ffit = TF1('langau',langaufun,fitrange[0],fitrange[1],4)
    for i in range(4):
        ffit.SetParameter(i,startvalues[i])
    ffit.SetParNames("Width","MPV","Area","GSigma")

    for i in range(4):
        ffit.SetParLimits(i, parlimitslo[i], parlimitshi[i])


    fitres = his.Fit('langau',"RB0QS")  # fit within specified range, use ParLimits, do not plot

    return ffit, fitres

from os.path import isfile, join
from os import listdir
from argparse import ArgumentParser
import numpy as np

if __name__=='__main__':

    parser = ArgumentParser(description='analysis')
    parser.add_argument('--exp', dest='exp', type=int)
    parser.add_argument('--run', dest='run', type=int)
    parser.add_argument('--path', dest='path', type=str)
    args = parser.parse_args()

    expnr = args.exp
    runnr = args.run
    path = args.path

    histnames = {'PXDER/c_Fit_PXD_Track_Cluster_Charge_1_1_1':'PXDER/PXD_Track_Cluster_Charge_1_1_1',
            'PXDER/c_Fit_PXD_Track_Cluster_Charge_1_1_2':'PXDER/PXD_Track_Cluster_Charge_1_1_2',
            'PXDER/c_Fit_PXD_Track_Cluster_Charge_1_2_1':'PXDER/PXD_Track_Cluster_Charge_1_2_1',
            'PXDER/c_Fit_PXD_Track_Cluster_Charge_1_2_2':'PXDER/PXD_Track_Cluster_Charge_1_2_2',
            'PXDER/c_Fit_PXD_Track_Cluster_Charge_1_3_1':'PXDER/PXD_Track_Cluster_Charge_1_3_1',
            #'PXDER/c_Fit_PXD_Track_Cluster_Charge_1_3_2':'PXDER/PXD_Track_Cluster_Charge_1_3_2',
            'PXDER/c_Fit_PXD_Track_Cluster_Charge_1_4_1':'PXDER/PXD_Track_Cluster_Charge_1_4_1',
            'PXDER/c_Fit_PXD_Track_Cluster_Charge_1_4_2':'PXDER/PXD_Track_Cluster_Charge_1_4_2',
            'PXDER/c_Fit_PXD_Track_Cluster_Charge_1_5_1':'PXDER/PXD_Track_Cluster_Charge_1_5_1',
            'PXDER/c_Fit_PXD_Track_Cluster_Charge_1_5_2':'PXDER/PXD_Track_Cluster_Charge_1_5_2',
            'PXDER/c_Fit_PXD_Track_Cluster_Charge_1_6_1':'PXDER/PXD_Track_Cluster_Charge_1_6_1',
            'PXDER/c_Fit_PXD_Track_Cluster_Charge_1_6_2':'PXDER/PXD_Track_Cluster_Charge_1_6_2',
            'PXDER/c_Fit_PXD_Track_Cluster_Charge_1_7_1':'PXDER/PXD_Track_Cluster_Charge_1_7_1',
            'PXDER/c_Fit_PXD_Track_Cluster_Charge_1_7_2':'PXDER/PXD_Track_Cluster_Charge_1_7_2',
            'PXDER/c_Fit_PXD_Track_Cluster_Charge_1_8_1':'PXDER/PXD_Track_Cluster_Charge_1_8_1',
            'PXDER/c_Fit_PXD_Track_Cluster_Charge_1_8_2':'PXDER/PXD_Track_Cluster_Charge_1_8_2',
            'PXDER/c_Fit_PXD_Track_Cluster_Charge_2_4_1':'PXDER/PXD_Track_Cluster_Charge_2_4_1',
            'PXDER/c_Fit_PXD_Track_Cluster_Charge_2_4_2':'PXDER/PXD_Track_Cluster_Charge_2_4_2',
            'PXDER/c_Fit_PXD_Track_Cluster_Charge_2_5_1':'PXDER/PXD_Track_Cluster_Charge_2_5_1',
            'PXDER/c_Fit_PXD_Track_Cluster_Charge_2_5_2':'PXDER/PXD_Track_Cluster_Charge_2_5_2'}



    mpv_dict={}
    mpv_dict['run'] = runnr

    f = ROOT.TFile.Open(join(path,'dqm_e%04ir%06i_canvas.root'%(expnr,runnr)),"READ")

    for pname in histnames.keys():
        canv = f.GetKey(pname).ReadObj()

        keys = [item.GetName() for item in canv.GetListOfPrimitives()]

        hist = None
        if histnames[pname] in keys:
            hist = canv.GetPrimitive(histnames[pname])
        elif "h_"+histnames[pname] in keys:
            hist = canv.GetPrimitive("h_"+histnames[pname])
        assert hist is not None

        fr = [10,80]

        pllo = [0.5,20.0,1.0,0.5]
        plhi = [5.0,70.0,1000000.0,10.0]
        sv = [2,30.0,50000.0,3.0]

        ffit, fitres = langaufit(hist,fr,sv,pllo,plhi)

        #mpv_dict[histnames[pname]] = [ffit.GetParameter(1), ffit.GetParameter(3),
        #                                   ffit.GetChisquare(), ffit.GetNDF()]
        mpv_dict[histnames[pname]] = [fitres.Parameter(1), fitres.Parameter(3),
                                           fitres.Chi2(), fitres.Ndf()]
        #mpv_dict['%s_langau'%histnames[pname]] = [ffit, fitres]

    #print runnr, histnames[pname], hist.GetMean(), ffit.GetParameter(1), ffit.GetParameter(3), ffit.GetChisquare(), ffit.GetNDF()

    np.save(join(path,'trackcharge_langau_e%04ir%06i'%(expnr,runnr)),mpv_dict)

