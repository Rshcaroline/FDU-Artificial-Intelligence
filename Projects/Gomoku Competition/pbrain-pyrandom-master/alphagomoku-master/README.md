# Alpha Gomoku Group Project
#### Written and maintained by Matthew Boakes, Harry Clarke, Matthew Clayton, Max Harris, and Jamie Pont.

### How to install (on a Linux machine connected to the Kent vpn)
* clone the directory from git
* install python3
* pip install -I tensorflow==0.12.1
* run sudo sh ./setup.sh

### How to install (Windows, Mac, Or a Linux machine not connected to the Kent vpn)
* Same as Linux (on the Kent vpn)  but instead of running setup.sh command, create a folder in the root directory (the one with src in) and create a the folder resources
* Download training.zip from the following link:
 * https://drive.google.com/file/d/0B86_99L1GbtLU3BybVB6UEZfakE/view?usp=sharing
* Unzip the training file from training.zip into the resources folder

### How to run
* To train the neural network:
 * python3 neural_network_main.py
  * To run it with previously trained weights pass in the following parameter to the above command: true
 * To play gomoku against the trained neural network and tree search:
  * python3 gomoku_main.py

### Introduction

The AlphaGomoku project aims to bring the concept behind Deep Mind's AlphaGo ("Mastering the game of Go with deep neural networks and tree search", David Silver et al., 28/01/16) to a game called "Gomoku".

### Project Goals
* September
 * Finish learning from the book
* October 
 * Have a basic neural netowkr put together for our understanding
 * Finish Gomoku App for playing the game
* End of Christmas 
 * Apply knowledge gained from basic NN project and develop a NN around gomoku
* After Christmas
 * Fine tune/finish project

