using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SemiFlowCalculator.Model
{
    public class MotionCalculator
    {
        const int unit = 1000;
        const double gravity = 9.80665;
        public double GetAccelTime(double acceleration, double scanSpeed)
        {
            if (acceleration == 0) return 0;
            return (scanSpeed / unit) / (acceleration * gravity);
        }
        public double GetAccelDistance(double acceleration, double scanSpeed)
        {
            if (acceleration == 0) return 0;
            double accelTime = GetAccelTime(acceleration, scanSpeed);
            return 0.5 * acceleration * gravity * Math.Pow(accelTime,2) * 1000;
        }
        public double GetConstantDistance(double waferSize)
        {
            return waferSize;
        }
        public double GetTotalScanDistance(double accelDist, double waferSize, double accelOffset)
        {
            return (2 * accelDist) + waferSize + (2 * accelOffset);
        }
    }
}
