using SemiFlowCalculator.Model;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SemiFlowCalculator.UI
{
    public class CalcScanMotion_ViewModel : NotifyProperty
    {
        public CalculationParameters Parameters { get; }
        private MotionCalculator calculator { get; } = new MotionCalculator();
        public CalcScanMotion_ViewModel(CalculationParameters calculationParameters)
        {
            Parameters = calculationParameters;
            Parameters.PropertyChanged += CalculationParameters_PropertyChanged;
        }

        private void CalculationParameters_PropertyChanged(object sender, PropertyChangedEventArgs e)
        {
            Parameters.AccelerationTime = calculator.GetAccelTime(Parameters.Acceleration, Parameters.ScanSpeed);
            Parameters.AccelerationDist = calculator.GetAccelDistance(Parameters.Acceleration, Parameters.ScanSpeed);
            Parameters.ScanConstantDistance = calculator.GetConstantDistance(Parameters.WaferSize);
            Parameters.TotalScanDistance = calculator.GetTotalScanDistance(Parameters.AccelerationDist, Parameters.WaferSize, Parameters.AccelerationOffset);
        }
    }
}
