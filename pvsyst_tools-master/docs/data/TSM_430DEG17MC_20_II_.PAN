PVObject_=pvModule
  Version=6.83
  Flags=$00D00043

  PVObject_Commercial=pvCommercial
    Flags=$0041
    Manufacturer=Trina Solar
    Model=TSM-430DEG17MC.20(II)
    DataSource=TS_ 2019_8
    YearBeg=2019
    Width=1.046
    Height=2.111
    Depth=0.035
    Weight=28.500
    NPieces=100
    PriceDate=24/06/19 15:39
    Currency=EUR
  End of PVObject pvCommercial

  Technol=mtSiMono
  NCelS=72
  NCelP=2
  NDiode=3
  GRef=1000
  TRef=25.0
  PNom=430.0
  PNomTolLow=0.00
  PNomTolUp=3.00
  BifacialityFactor=0.700
  Isc=11.200
  Voc=48.70
  Imp=10.620
  Vmp=40.50
  muISC=4.48
  muVocSpec=-140.0
  muPmpReq=-0.350
  RShunt=400
  Rp_0=7500
  Rp_Exp=5.50
  RSerie=0.238
  Gamma=0.976
  muGamma=-0.0004
  VMaxIEC=1500
  VMaxUL=1500
  Absorb=0.90
  ARev=3.200
  BRev=10.356
  RDiode=0.010
  VRevDiode=-0.70
  AirMassRef=1.500
  CellArea=137.0
  SandiaAMCorr=50.000
  RelEffic800=0.41
  RelEffic600=0.38
  RelEffic400=-0.30
  RelEffic200=-1.90

  PVObject_IAM=pvIAM
    Flags=$00
    IAMMode=UserProfile
    IAMProfile=TCubicProfile
      NPtsMax=9
      NPtsEff=9
      LastCompile=$B18D
      Mode=3
      Point_1=0.0,1.00000
      Point_2=30.0,1.00000
      Point_3=50.0,1.00000
      Point_4=60.0,0.99900
      Point_5=70.0,0.99400
      Point_6=75.0,0.97800
      Point_7=80.0,0.93000
      Point_8=85.0,0.72300
      Point_9=90.0,0.00000
    End of TCubicProfile
  End of PVObject pvIAM

  OperPoints, list of=4 tOperPoint
    Point_1=False,800,25.0,0.41,0.00,0.000,0.000,0.00
    Point_2=False,600,25.0,0.38,0.00,0.000,0.000,0.00
    Point_3=False,400,25.0,-0.30,0.00,0.000,0.000,0.00
    Point_4=False,200,25.0,-1.90,0.00,0.000,0.000,0.00
  End of List OperPoints
End of PVObject pvModule
