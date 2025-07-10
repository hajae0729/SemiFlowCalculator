using SemiFlowCalculator.UI;
using System.Windows.Controls;

namespace SemiFlowCalculator
{
    public class MainWindow_ViewModel : NotifyProperty
    {
        public CalcScanMotion_ViewModel CalcScanMotionViewModel { get; }
        public CalcTDITakt_ViewModel CalcTDITaktViewModel { get; }
        public ProcessSetting_ViewModel ProcessSettingViewModel { get; }

        private UserControl motionView;
        public UserControl MotionView
        {
            get { return motionView; }
            set
            {
                motionView = value;
                OnPropertyChanged();
            }
        }

        private UserControl taktTimeView;
        public UserControl TaktTimeView
        {
            get { return taktTimeView; }
            set
            {
                taktTimeView = value;
                OnPropertyChanged();
            }
        }
        
        private UserControl processView;
        public UserControl ProcessView
        {
            get { return processView; }
            set
            {
                processView = value;
                OnPropertyChanged();
            }
        }

        public CalculationParameters calculationParameters { get; set; } = new CalculationParameters();

        public MainWindow_ViewModel()
        {
            ProcessSettingViewModel = new ProcessSetting_ViewModel(calculationParameters);
            CalcTDITaktViewModel = new CalcTDITakt_ViewModel(calculationParameters);
            CalcScanMotionViewModel = new CalcScanMotion_ViewModel(calculationParameters);

            MotionView = new CalcScanMotion_UI { DataContext = CalcScanMotionViewModel };
            TaktTimeView = new CalcTDITakt_UI { DataContext = CalcTDITaktViewModel };
            ProcessView = new ProcessSetting_UI { DataContext = ProcessSettingViewModel };
        }

        private void ShowCreaterView()
        {
            //TaktTimeView = new CalcTDITakt_UI { DataContext = TDITaktCalcViewModel };
        }

        public RelayCommand ShowTDICommand
        {
            get
            {
                return new RelayCommand(ShowCreaterView);
            }
        }
    }
}
