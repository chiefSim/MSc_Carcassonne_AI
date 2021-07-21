<!-- Add banner here -->
![Banner](https://github.com/chiefSim/MSc_Carcassonne_AI/blob/main/readme-editor/banner.png)

# MSC - Building AI Controllers for the Game of Carcacassonne
Master's Project - Carcassonne, AI, MCTS, Expectimax

<!-- Add buttons here -->

<!-- Describe your project in brief -->

The main idea behind the thesis is building and testing AI controllers to play the famous euro-style board game of Carcassonne. AI algorithms include Monte Carlo Tree Search (MCTS), MCTS with Rapid Actio Value Estimation (MCTS-RAVE) and Minimax search algorithms. Some controllers incorporate evolutionary algorithms, in paarticular Evolutionary Strategies (ES) to improve the decision making processes of these AI algorthims.

Extra features include an interactive Game UI that allows human players to compete against AI controllers


# Demo-Preview

<!-- Add a demo for your project -->

<!-- After you have written about your project, it is a good idea to have a demo/preview(**video/gif/screenshots** are good options) of your project so that people can know what to expect in your project. You could also add the demo in the previous section with the product description. -->
Game UI:

<!-- [menu](https://github.com/chiefSim/MSc_Carcassonne_AI/blob/main/readme-editor/menu.gif) -->
![pygame](https://github.com/chiefSim/MSc_Carcassonne_AI/blob/main/readme-editor/pygame.gif)


# Table of contents

- [Project Title](#project-title)
- [Demo-Preview](#demo-preview)
- [Table of contents](#table-of-contents)
- [Packages Required](#packages-required)
- [Usage](#usage)
    - [Experiments](#experiments)
    - [Results UI](#results-ui)
    - [Game UI](#game-ui)
- [Development](#development)
- [Footer](#footer)

# Installation
[(Back to top)](#table-of-contents)

* Clone the project
* Go to project folder
* Install all packages in `requirements.txt`:

```
pip install -r requirement.txt
```


# Usage
[(Back to top)](#table-of-contents)


### Experiments
[(Back to top)](#table-of-contents)

To replicate the results from any of the experiments, just execute any of the python scripts with prefix of `EXP_...`. Results of each experiment are stored within their own folder within the `.../logs` directory.

Example:

* Run script:

```
python EXP_MCTS_Param
```
* Location of log files:

```
.../Carcassonne/logs/MCTS_Param_EXP_2021-07-18
```

### Results UI
[(Back to top)](#table-of-contents)

Run the app script (`python Plotly_App.py`) and 

### Game UI
[(Back to top)](#table-of-contents)


# Development
[(Back to top)](#table-of-contents)

<!-- This is the place where you give instructions to developers on how to modify the code.

You could give **instructions in depth** of **how the code works** and how everything is put together.

You could also give specific instructions to how they can setup their development environment.

Ideally, you should keep the README simple. If you need to add more complex explanations, use a wiki. Check out [this wiki](https://github.com/navendu-pottekkat/nsfw-filter/wiki) for inspiration. -->


# Footer
[(Back to top)](#table-of-contents)

<!-- Let's also add a footer because I love footers and also you **can** use this to convey important info.

Let's make it an image because by now you have realised that multimedia in images == cool(*please notice the subtle programming joke). -->

Leave a star in GitHub, give a clap in Medium and share this guide if you found this helpful.

<!-- Add the footer here -->

<!-- ![Footer](https://github.com/navendu-pottekkat/awesome-readme/blob/master/fooooooter.png) -->
