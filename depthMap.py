import numpy as np
import cv2
import time
from PySpectralRadar import *  # Assuming this is the Python wrapper for the OCT imaging library

PI = 3.14159265358979323846

# Assuming ScanResult can be represented as a dictionary in Python
def getSurfaceFrom3DScan(AScansPerBScan, LengthOfBScan, BScansPerVolume, WidthOfVolume):
    try:
        Dev = initDevice()
        Probe = initProbe(Dev, "Probe_Standard_OCTG_LSM04.ini")
        Proc = createProcessingForDevice(Dev)

        RawVolume = createRawData()
        Volume = createData()
        Surface = createData()

        # Set device presets and parameters
        setDevicePreset(Dev, CATEGORY_SPEED_SENSITIVITY, Probe, Proc, PRESET_HIGH_SPEED_146kHz)
        AScanAveraging = 3
        setProbeParameterInt(Probe, ProbeParameterInt.Probe_Oversampling, AScanAveraging)
        setProcessingParameterInt(Proc, ProcessingParameterInt.Processing_AScanAveraging, AScanAveraging)

        Pattern = createVolumePattern(Probe, LengthOfBScan, AScansPerBScan, WidthOfVolume, BScansPerVolume,
                                      ScanPatternApodizationType.ScanPattern_ApoOneForAll,
                                      ScanPatternAcquisitionOrder.ScanPattern_AcqOrderAll)

        # Start and stop measurement
        start = time.time()
        startMeasurement(Dev, Pattern, AcquisitionType.Acquisition_AsyncContinuous)
        getRawData(Dev, RawVolume)
        setProcessedDataOutput(Proc, Volume)
        executeProcessing(Proc, RawVolume)
        stopMeasurement(Dev)
        stop = time.time()

        numOfLostBScan = getRawDataPropertyInt(RawVolume, RawDataPropertyInt.RawData_LostFrames)
        actualTime = stop - start
        expectedTime = expectedAcquisitionTime_s(Pattern, Dev)

        determineSurface(Volume, Surface)

        # Clean up
        clearScanPattern(Pattern)
        clearData(Volume)
        clearRawData(RawVolume)
        clearProcessing(Proc)
        closeProbe(Probe)
        closeDevice(Dev)

        return {"surface": Surface, "actualTime": actualTime, "expectedTime": expectedTime, "numOfLostBScan": numOfLostBScan}

    except Exception as e:
        print(f"ERROR: {e}")
        return {"surface": None, "actualTime": -1.0, "expectedTime": -1.0, "numOfLostBScan": -1}

def main():
    LengthOfBScan = 10.0
    WidthOfVolume = 10.0
    FullAScansPerBScan = 256
    FullBScansPerVolume = 100
    AscanCompressionRatio = 0.5
    BscanCompressionRatio = 0.25

    CompressiveAScansPerBScan = int(FullAScansPerBScan * AscanCompressionRatio)
    CompressiveBScansPerVolume = int(FullBScansPerVolume * BscanCompressionRatio)

    AScansPerBScan = CompressiveAScansPerBScan
    BScansPerVolume = CompressiveBScansPerVolume
    fileName = "surfaceCompressive"
    folderLocation = "C:/Ajay_OCT/OCTAssistedSurgicalLaserbot/data/getDepthFromSparse3Doct/"

    result = getSurfaceFrom3DScan(AScansPerBScan, LengthOfBScan, BScansPerVolume, WidthOfVolume)

    if result["surface"]:
        # Exporting the surface data
        surface_data_csv_path = f"{folderLocation}{fileName}.csv"
        with open(surface_data_csv_path, 'w') as csv_file:
            # Replace the following line with the actual method of writing the surface data to the CSV file
            csv_file.write(str(result["surface"]))  # Placeholder for actual export logic

        # Writing metadata to a separate file
        metadata_csv_path = f"{folderLocation}{fileName}_meta.csv"
        with open(metadata_csv_path, 'w') as meta_file:
            meta_file.write(f"{BScansPerVolume}\n")
            meta_file.write(f"{AScansPerBScan}\n")
            meta_file.write(f"{result['actualTime']}\n")
            meta_file.write(f"{FullBScansPerVolume}\n")
            meta_file.write(f"{FullAScansPerBScan}\n")
            meta_file.write(f"{BscanCompressionRatio}\n")
            meta_file.write(f"{AscanCompressionRatio}\n")
            meta_file.write(f"{CompressiveBScansPerVolume}\n")
            meta_file.write(f"{CompressiveAScansPerBScan}\n")
            meta_file.write(f"{LengthOfBScan}\n")
            meta_file.write(f"{WidthOfVolume}\n")
            meta_file.write(f"{result['numOfLostBScan']}\n")
            meta_file.write(f"{result['expectedTime']}")
    else:
        print("No surface data to export.")



if __name__ == "__main__":
    main()
