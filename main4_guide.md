
# Understanding and Running the `main4.py` Script

This document provides a clear explanation of the `main4.py` script and step-by-step instructions on how to run it, designed for users who are not familiar with coding.

## What the Script Does

The `main4.py` script is a tool that automatically creates a video from an audio file. It uses artificial intelligence to analyze the audio, generate images that match the content, and combine them into a video with subtitles. This is particularly useful for creating engaging video stories from audio recordings.

### How It Works

The script follows a three-step process to generate the video:

1.  **Audio Analysis and Scene Creation**: The script first analyzes the audio file to understand its content. It then transcribes the audio into text and divides it into different scenes, creating subtitles for each scene.
2.  **Image Generation**: For each scene, the script generates a unique image that visually represents the content of that scene. These images are created using an AI image generation model.
3.  **Video Creation**: Finally, the script combines the generated images, the original audio, and the subtitles to create a complete video file. The images are displayed in sync with the audio, and the subtitles appear at the bottom of the screen.

## How to Run the Script

To run the `main4.py` script, you will need to use the command line, but the process is straightforward. Follow these steps carefully:

### Step 1: Activate the Virtual Environment

Before running the script, you need to activate its virtual environment. This ensures that the script has access to all the necessary tools and libraries.

To activate the virtual environment, open your terminal and run the following command:

`source venv/bin/activate`

This command sets up the correct environment for the script to run.

### Step 2: Install Dependencies

Next, you need to install the required dependencies for the script. These are libraries and packages that the script relies on to function correctly.

Run the following command to install the dependencies:

`pip install -r requirements.txt`

This command reads the `requirements.txt` file and installs all the necessary packages.

### Step 3: Run the Script

Once the virtual environment is activated and the dependencies are installed, you can run the `main4.py` script. You will need to provide the audio file you want to use and a project name for the output.

Use the following command to run the script:

`python3 main4.py --audio tnk.mp3 --project tnk`

- `--audio tnk.mp3`: This specifies the audio file to be used. Make sure the audio file is in the same directory as the script.
- `--project tnk`: This sets a name for your project, which will be used to create a folder for the output video.

After running this command, the script will start the video generation process. You will see progress updates in the terminal as it completes each step.

### Step 4: Deactivate the Virtual Environment

When the script has finished running, you can deactivate the virtual environment by running the following command:

`deactivate`

This will return your terminal to its normal state.

By following these instructions, you can easily run the `main4.py` script and create your own videos from audio files without needing to write any code.
