using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SemiFlowCalculator.UI
{
    public class ProcessSetting_ViewModel : NotifyProperty
    {
        public CalculationParameters Parameters { get; }

        public ProcessSetting_ViewModel(CalculationParameters calculationParameters)
        {
            Parameters = calculationParameters;
            Parameters.PropertyChanged += CalculationParameters_PropertyChanged;
        }

        private void CalculationParameters_PropertyChanged(object sender, PropertyChangedEventArgs e)
        {
        }
    }
}
