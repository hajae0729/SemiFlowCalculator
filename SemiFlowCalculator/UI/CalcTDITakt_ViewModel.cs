using SemiFlowCalculator.Model;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SemiFlowCalculator.UI
{
    public class CalcTDITakt_ViewModel : NotifyProperty
    {
        public CalculationParameters Parameters { get; }

        private TakttimeCalculator.TDITaktTimeCalc calculator = new TakttimeCalculator.TDITaktTimeCalc();

        public CalcTDITakt_ViewModel()
        {
        }

        public CalcTDITakt_ViewModel(CalculationParameters calculationParameters)
        {
            Parameters = calculationParameters;
            Parameters.PropertyChanged += CalculationParameters_PropertyChanged;
        }

        private void CalculationParameters_PropertyChanged(object sender, System.ComponentModel.PropertyChangedEventArgs e)
        {
            UpdateData();
        }

        private void UpdateData()
        {
            calculator.CalcTDITaktTime(Parameters);
        }
    }
}
