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

Controls:
* Arrows - Rotate tile (Left & Right)
* NumKeys - Placement of Meeple, if available. (Numbers seen in menu on right as well as on the tile image)
* Click - Place tile one of the available positions
* Spacebar - Make AI controller to choose move

Square Colours:
* Green - Available position on board
* Blue - Available position on board, but **not** for that Meeple choice


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

Run the app script (`python Plotly_App.py`) and the following message should appear:

> Dash is running on **http://127.0.0.1:8050/**</br>
> * Serving Flask app "Plotly_App" (lazy loading)
> * Environment: production
>   WARNING: This is a development server. Do not use it in a production deployment.
>   Use a production WSGI server instead.
> * Debug mode: on

Copy and paste the url (hyperlink) into a browser to access the UI containing statistical results from the experiments. A page (similar to below) should appear.

![results_ui](https://github.com/chiefSim/MSc_Carcassonne_AI/blob/main/readme-editor/results_ui.PNG)

Use the dropdowns available to filter through the different results sets and filter by AI controller. All plots are **interactive** and will display extra information when hovered over. UI will remain online as long as the `Plotly_App.py` is running.


### Game UI
[(Back to top)](#table-of-contents)

Run the following:

```
bash ./PLAY_GAME_UI.sh
```

Then a menu will pop up. Use the **arrows** to choose Player 1 and Player 2. Click `Play` to start the game. The game UI (seen above), powered by `pygame` will pop-up next.
