using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text;
using System.Threading.Tasks;

namespace SemiFlowCalculator
{
    public class CalculationParameters : NotifyProperty
    {
        #region ScanMotion
        private double acceleration = 0.3;
        public double Acceleration
        {
            get { return acceleration; }
            set
            {
                if (acceleration == Math.Round(value, 6)) return;
                acceleration = Math.Round(value, 6);
                OnPropertyChanged();
            }
        }

        private double accelerationTime;
        public double AccelerationTime
        {
            get { return accelerationTime; }
            set
            {
                if (accelerationTime == Math.Round(value, 6)) return;
                accelerationTime = Math.Round(value, 6);
                OnPropertyChanged();
            }
        }

        private double accelerationOffset;
        public double AccelerationOffset
        {
            get { return accelerationOffset; }
            set
            {
                if (accelerationOffset == Math.Round(value, 6)) return;
                accelerationOffset = Math.Round(value, 6);
                OnPropertyChanged();
            }
        }

        private double waferSize = 310;
        public double WaferSize
        {
            get { return waferSize; }
            set
            {
                if (waferSize == Math.Round(value, 6)) return;
                waferSize = Math.Round(value, 6);
                OnPropertyChanged();
            }
        }

        private double accelerationDist;
        public double AccelerationDist
        {
            get { return accelerationDist; }
            set
            {
                if (accelerationDist == Math.Round(value, 6)) return;
                accelerationDist = Math.Round(value, 6);
                OnPropertyChanged();
            }
        }

        private double scanConstantDistance;
        public double ScanConstantDistance
        {
            get { return scanConstantDistance; }
            set
            {
                if (scanConstantDistance == Math.Round(value, 6)) return;
                scanConstantDistance = Math.Round(value, 6);
                OnPropertyChanged();
            }
        }

        private double totalScanDistance;
        public double TotalScanDistance
        {
            get { return totalScanDistance; }
            set
            {
                if (totalScanDistance == Math.Round(value, 6)) return;
                totalScanDistance = Math.Round(value, 6);
                OnPropertyChanged();
            }
        }
        #endregion

        #region Camera
        private double cameraResolution = 0.1875;
        public double CameraResolution
        {
            get { return cameraResolution; }
            set
            {
                if (cameraResolution == Math.Round(value, 6)) return;
                cameraResolution = Math.Round(value, 6);
                OnPropertyChanged();
            }
        }

        private int cameraFrequence = 1000;
        public int CameraFrequence
        {
            get { return cameraFrequence; }
            set
            {
                if (cameraFrequence == value) return;
                cameraFrequence = value;
                OnPropertyChanged();
            }
        }

        private int safetyFactor = 90;
        public int SafetyFactor
        {
            get { return safetyFactor; }
            set
            {
                if (safetyFactor == value) return;
                safetyFactor = value;
                OnPropertyChanged();
            }
        }

        private double scanSpeed = 100;
        public double ScanSpeed
        {
            get { return scanSpeed; }
            set
            {
                if (scanSpeed == Math.Round(value, 6)) return;
                scanSpeed = Math.Round(value, 6);
                OnPropertyChanged();
            }
        }

        private int fov = 6000;
        public int Fov
        {
            get { return fov; }
            set
            {
                if (fov == value) return;
                fov = value;
                OnPropertyChanged();
            }
        }

        private int scanCount;
        public int ScanCount
        {
            get { return scanCount; }
            set
            {
                if (scanCount == value) return;
                scanCount = value;
                OnPropertyChanged();
            }
        }

        private double fullScanTime;
        public double FullScanTime
        {
            get { return fullScanTime; }
            set
            {
                if (fullScanTime == value) return;
                fullScanTime = value;
                OnPropertyChanged();
            }
        }

        private double fullScanUPH;
        public double FullScanUPH
        {
            get { return fullScanUPH; }
            set
            {
                if (fullScanUPH == value) return;
                fullScanUPH = value;
                OnPropertyChanged();
            }
        }
        private double circleScanTime;
        public double CircleScanTime
        {
            get { return circleScanTime; }
            set
            {
                if (circleScanTime == value) return;
                circleScanTime = value;
                OnPropertyChanged();
            }
        }

        private double circleScanUPH;
        public double CircleScanUPH
        {
            get { return circleScanUPH; }
            set
            {
                if (circleScanUPH == value) return;
                circleScanUPH = value;
                OnPropertyChanged();
            }
        }
        #endregion


        #region Process
        private double scanDelay = 0.35;
        public double ScanDelay
        {
            get { return scanDelay; }
            set
            {
                if (scanDelay == Math.Round(value, 6)) return;
                scanDelay = Math.Round(value, 6);
                OnPropertyChanged();
            }
        }

        private double waferChangeDelay = 13;
        public double WaferChangeDelay
        {
            get { return waferChangeDelay; }
            set
            {
                if (waferChangeDelay == Math.Round(value, 6)) return;
                waferChangeDelay = Math.Round(value, 6);
                OnPropertyChanged();
            }
        }

        private int waferAlignScanCount = 1;
        public int WaferAlignScanCount
        {
            get { return waferAlignScanCount; }
            set
            {
                if (waferAlignScanCount == value) return;
                waferAlignScanCount = value;
                OnPropertyChanged();
            }
        }

        private double processDelay = 5;
        public double ProcessDelay
        {
            get { return processDelay; }
            set
            {
                if (processDelay == Math.Round(value, 6)) return;
                processDelay = Math.Round(value, 6);
                OnPropertyChanged();
            }
        }
        #endregion
    }
}
