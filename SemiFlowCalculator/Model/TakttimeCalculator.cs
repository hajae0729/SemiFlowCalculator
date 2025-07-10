using System;

namespace SemiFlowCalculator.Model
{
    public class TakttimeCalculator
    {
        public class TDITaktTimeCalc
        {
            private int ScanCount = 0;
            private double FullScanTime = 0;
            private double FullScanUPH = 0;
            private double CircleScanTime = 0;
            private double CircleScanUPH = 0;

            public void CalcTDITaktTime(CalculationParameters parameters)
            {
                ScanCount = (int)Math.Ceiling(parameters.WaferSize / (parameters.Fov * parameters.CameraResolution / 1000)) + parameters.WaferAlignScanCount;
                FullScanTime = ((parameters.TotalScanDistance * ScanCount) / parameters.ScanSpeed + ScanCount * 0.05) + parameters.ProcessDelay;
                FullScanUPH = 60 * 60 / (FullScanTime + parameters.WaferChangeDelay);
                CircleScanTime = FullScanTime * 0.95;
                CircleScanUPH = 60 * 60 / (CircleScanTime + parameters.WaferChangeDelay);
                UpdataParam(parameters);
            }

            private void UpdataParam(CalculationParameters parameters)
            {
                parameters.ScanCount = this.ScanCount;
                parameters.FullScanTime = this.FullScanTime;
                parameters.FullScanUPH = this.FullScanUPH;
                parameters.CircleScanTime = this.CircleScanTime;
                parameters.CircleScanUPH = this.CircleScanUPH;
            }
        }
    }
}
