# smart-image-correction
Repo contains source code for smart image correction application. This application is developed by PRC SMG TEG ADC IOT team to provide AI capability on Core platform to leverage iGPU acceleration.

The application will scan input image with Intel(R) Core platform, auto-remove messy background and enhance, precisely restore,  and finally generate HD image. It targets for conference, education scenarios, etc.

![image](https://user-images.githubusercontent.com/102839943/205550534-6ac1b8f7-0be8-4dcf-8cee-cea6ec2758b1.png)


## Part One: Development Environment Setup Procedure
Users can utilize source code to deploy their application based on this Smart Image Correction project on Windows/Ubuntu.
The following steps are verified on TGL-U i7-1185G7 Windows10.

### Step1: Install Python 3.9

Pythons 3.9 is available from this link (https://www.python.org/downloads/), download and follow the instructions to complete Python 3.9 installation.

### Step2: PyCharm Community Edition 2021.3.2 Installation

The PyCharm download is available via this link:
https://www.jetbrains.com/pycharm/download/other.html

<img width="638" alt="image" src="https://user-images.githubusercontent.com/102839943/204227661-c9a3d03b-cf39-47c4-b4f6-2afe914d112d.png">

### Step3: PIP (>= 22.1.2) Installation

https://packaging.python.org/en/latest/tutorials/installing-packages/


### Step4: Download Smart Image Correction Source Code

Please get the source from 
https://github.com/intel/smart-image-correction

### Step5: Download u2net Model

Download public pre-trained model u2net.onnx from https://drive.google.com/uc?id=1tCU5MM1LhRgGou5OpmpjBQbSrYIUoYab

Create a folder named .unet in C:\Users\username\

Copy u2net.onnx to folder C:\Users\username\\.u2net\

### Step6: Install Dependencies

Open Windows “Command Prompt” App, navigate to Smart Image Correction source directory and execute:
> pip install -r requirements.txt

### Step7: Run Smart Image Correction App with PyCharm


•	Open Smart Image Correction project by PyCharm.
•	Choose Main.py
•	Click "Run" button.



### Step8:	Export Smart Image Correction project to SmartImageCorrection.exe.

Open Windows “Command Prompt” App, navigate to Smart Image Correction source directory and execute:
>Pyinstaller -F -w Main.py


## Part Two: Usage


Users can use all features of Smart Image Correction App as Figure 3-1 by double clicking SmartImageCorrection.exe on Windows 10 without library dependencies installation after completing the u2net model environment setup as described in Part One.

### Step 1: Launch application by double clicking SmartImageCorrection.exe

## Note:	The path of SmartImageCorrection.exe and input an image can’t include Chinese characters.

### Step 2:	Using Smart Image Correction application

1.	When use Distortion Correction Feature, once click “Quad Detection” Button, then Quad GUI titled “Adjust 4 corners OR close this dialog” will show up in Figure 3-2.

•	If the auto-detected four squares (blue points) meet users' expectation, please close this Quad GUI directly. 

•	If users aren't satisfied with the location of any squares, please click your prefer squares' location (red points) in Quad GUI and then close this Quad GUI.

2.	When use Surface Flatten Feature, please input an image such as the paper is bent caused by the spine.

3.	When use Image Enhancement Feature, once click "Image Enhancement" Button, then Image Enhancement GUI titled "Dialog" will show up. This "Dialog" includes 7 Image Enhancement functions and 1 Remove Handwritten function as shown in Figure 3-3.

•	There are 5 image enhancement function with default parameter, e.g., Brightness, Color, Contrast, Sharpness and Gamma. If users want to adjust one of these parameters, i.e., change the right-side parameter of the corresponding "Run Brightness" button firstly and then click "Run Brightness" button.

<img width="114" alt="image" src="https://user-images.githubusercontent.com/102839943/205550821-4bf8e42b-0f85-4aeb-b286-078a52be2148.png">

•	There are 2 image enhancement functions without default parameter, such as Laplace named "Run Laplace", White Background and Black Font named "Black font White bg".

•	1 Remove Handwritten function can apply to image directly without parameter such as Remove Red and Blue.

#### Figure 3-1 Feature Usage Diagram

![image](https://user-images.githubusercontent.com/102839943/204228110-5dae8d5b-fe7a-45ce-a749-b488ea580b53.png)

#### Figure 3-2 Main GUI and Quad GUI of Smart Image Correction

<img width="821" alt="image" src="https://user-images.githubusercontent.com/102839943/204229161-c11071a5-25e2-45b1-aeab-6e9633dff679.png">

#### Figure 3-3 Main GUI and Dialog of Smart Image Correction

<img width="791" alt="image" src="https://user-images.githubusercontent.com/102839943/204229527-e457258e-d1ce-43d8-8eea-3e31ea14edc1.png">

### Reference
page_dewarp.py comes from https://github.com/mzucker/page_dewarp
