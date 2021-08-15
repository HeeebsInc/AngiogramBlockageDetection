# Angiogram Blockage Detection | CPE-645-FinalProject

<p align="center" width="100%">
    <img width="75%" src="readme-assets/cover-photo.jpg"> 
</p>

## Contributer
- Samuel Mohebban 
- [LinkedIn](https://www.linkedin.com/in/samuel-mohebban-b50732139/)
- [Medium](https://medium.com/@heeebsinc)

### Prompt
`Image segmentation has been one of the classical image processing techniques. It intends to abstract some important feature from an image based on its global and/or local amplitude distribution. One of the major application areas of this technique is medical imaging, where segmentation can automatically highlight the objects (e.g. vessel, cardiac chamber etc.) to help physicians diagnosing disease.`

`In this project, you are to apply image segmentation techniques to X-ray angiography, where X-ray images are taken when an X-ray absorbing substance is injected into the patient's blood stream to produce contrast. The resulting X-ray images have dark regions representing the blood flow within vessels. Your system should be able to automatically locate any occlusion and follow the surrounding vessel wall to compute the ratio between the minimum and nominal vessel diameters. Such results are practically important in detecting coronary disease. Your system should also accept user input of occlusion locations and perform the same percent occlusion measurement in that particular area.`


### Data
- [Medpix](https://medpix.nlm.nih.gov/search?allen=false&allt=false&alli=true&query=angiography)
- Sample images used for testing can be found [here](sample-images)

### Reference Articles
- [Liang, Dongxue, et al. “Coronary Angiography Video Segmentation Method for Assisting Cardiovascular Disease Interventional Treatment.” BMC Medical Imaging, vol. 20, no. 1, 2020, doi:10.1186/s12880-020-00460-9.](https://bmcmedimaging.biomedcentral.com/articles/10.1186/s12880-020-00460-9)
- [Dehkordi, Maryam  Taghizadeh, et al. “Retraction: A Review of Coronary Vessel Segmentation Algorithms.” Journal of Medical Signals &amp; Sensors, vol. 9, no. 1, 2019, p. 76., doi:10.4103/2228-7477.253755.](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3317762/)


### Abstract

### Description of work accomplished

## Running the program (Tested using Ubuntu 20.04)
#### **Docker [recommended]**
To avoid package conflicts, I recommend using docker as I have already created a working environment for running this program
1) Clone this repository
   1) `git clone <repo url>`
2) Install [Docker](https://docs.docker.com/get-docker/)
3) Pull my image
   1) `docker pull`
4) Run the container and mount the project directory to the container
   1) `docker run --name blockage-detection -v <localpath/to/project>/AngiogramBlockageDetection:/home/AngiogramBlockageDetection -w /home/AngiogramBlockageDetection -itd angiogram-blockage-detection:latest`
   2) Only thing unique to your computer is switching the `localpath/to/project` with the path to the project you cloned in Step 1
   3) Command above was testing with Ubuntu
      1) Because the program uses a GUI, you must mount your display to the container
5) Outside of the container, move into the project directory you created in step
6) Gather images you wish to run inference on and place them in `AngiogramBlockageDetection/sample-images`
7) Move into the running container
   1) `docker exec -it blockage-detection bash`
8) Move into the project directory
   1) `cd AngiogramBlockageDetection`
9) Run the program
   1) `python program.py`
10) See below for sample output

#### Without Docker
4) Clone repository onto your local machine
   1) `git clone <repo url>`
5) Set up virtual environment (conda, etc.) [Recommended]
   1) Install Miniconda 
      1) `cd /tmp`
      2) `apt-get update && apt-get install wget -y && wget https://repo.anaconda.com/miniconda/Miniconda3-py39_4.10.3-Linux-x86_64.sh`
      3) `chmod +x Miniconda3-py39_4.10.3-Linux-x86_64.sh && ./Miniconda3-py39_4.10.3-Linux-x86_64.sh`
         1) Follow the steps prompted in the command line
      4) Restart terminal to initialize conda 
         1) You should now see `(base)` on the left of your new terminal session
      5) Create conda environment
         1) `conda create --name blockage-detection python=3.9`
         2) `conda activate blockage-detection`
            1) You should now see that `(base)` has changed to `blockage-detection`
6) Install necessary packages
   1) [conda] `pip install opencv-contrib-python matplotlib tqdm && conda install pyqt`
   2) [no virtual enviornment] `pip3 install opencv-contrib-python matplotlib tqdm PyQT5`
7) Gather images you wish to run inference on and place them in [sample-images](sample-images)
8) Run the program
   1) [conda] `python program.py`
   2) [no virtual environment] `python3 program.py`
9) see below for sample output

#### Sample Output
1) Upon running [program.py](program.py) a command line prompt will get displayed asking if you wish to specify a region of interest
   1) This step is to determine if you want the algorithm to process the entire image or just a region of interest that you get to draw
   2) Press Y to draw the region of interest | Press N to let the algorithm process the entire thing
   
<p align="center" width="100%">
    <img width="75%" src="readme-assets/start.png"> 
</p>


2) 
#### Possible errors and how to fix them
1) `ImportError: libGL.so.1: cannot open shared object file: No such file or directory`
   1) This is an opencv package conflict, in order to fix it you must run `apt-get update && apt-get install ffmpeg libsm6 libxext6  -y`
2) Python version
   1) To check your python version, open a command line and run `python`
      1) If the version is < 3.0.0, then you must use `python3` to run the program
      2) run `python3 program.py` instead of `python program.py`
3) `no protocol specified
qt.qpa.xcb: could not connect to display :1
qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "/root/miniconda3/envs/blockage-detection/lib/python3.9/site-packages/cv2/qt/plugins" even though it was found.
This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.`
   1) This means you do not have pyqt installed.  
   2) If you are running conda outside of the container, `conda install pyqt`
   3) If you are not running a virtual environment, `pip3 install PyQt5`
4) If you are stuck on a different error and need assistance, create an issue on this repo and I will be sure to answer ASAP
### Future Directions
- experiment ridge detection
- use segmentation networks and other machine learning approached to generate similar or better results
- 

