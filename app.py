import dash
import dash_html_components as html
from dash.dependencies import Input, Output

import dash_core_components as dcc
import plotly.graph_objects as go
import plotly.express as px

import pandas as pd
import os
import numpy as np

# colours for dash
COLORS = px.colors.qualitative.Plotly

###############################################################################
#                                                                             #
#                                                                             #
#                                                                             #
###############################################################################

# load in the CSVs

# check if table is there, if not use test
if 'FinalLeagueTable.csv' in os.listdir('logs'):
    dfLeague = pd.read_csv('logs/FinalLeagueTable.csv')
else:
    dfLeague = pd.read_csv('logs_test/FinalLeagueTable.csv')
    

if 'PlayerStats.csv' in os.listdir('logs'):
    dfStats = pd.read_csv('logs/PlayerStats.csv', converters={'MeepleFeatures': eval, 'MeepleTurns': eval})
else:
    dfStats = pd.read_csv('logs_test/PlayerStats.csv', converters={'MeepleFeatures': eval, 'MeepleTurns': eval})    
    
    
#if 'ExpectimaxStats.csv' in os.listdir('logs'):
#    dfMax = pd.read_csv('logs/ExpectimaxStats.csv')
#else:
#    dfMax = pd.read_csv('logs_test/ExpectimaxStats.csv')

if 'MCTSStats.csv' in os.listdir('logs'):
    dfMCTS = pd.read_csv('logs/MCTSStats.csv')
else:
    dfMCTS = pd.read_csv('logs_test/MCTSStats.csv')    

# clean up some of the tables
# round off league table columns
dfLeague = dfLeague.round(2)


# number of games each team played
MATCHES = dfLeague['MatchesPlayed'].values[0]
TOTAL_GAMES = MATCHES*(dfStats['Game'].max())
PLAYERS = dfLeague['Player'].values


###############################################################################
#                                                                             #
#                                                                             #
#                                                                             #
###############################################################################



"""
    2. Results Matrix - Top Right
"""
# create results matrix
dfMatches = dfStats[['FixtureSet', 'Game', 'Player', 'Opponent', 'Result', 'Win', 'Loss']].iloc[::2, :]  # only need these columns
df1 = dfMatches.groupby(['FixtureSet', 'Player', 'Opponent'])[['Win', 'Loss']].sum().reset_index()  # results per match
df1["Scores"] = df1['Win'].map(str) + "-" + df1['Loss'].map(str)
dfT = df1.reset_index()
dfT['Player2'] = dfT['Opponent']
dfT['Players'] = dfT['Player']
dfResults = dfT.pivot(index='Players', columns='Player2', values='Scores').fillna("- ")
dfResults1 = dfResults.reset_index()
dfResults1 = dfResults1.rename(columns={'Players': 'P1 \ P2'})
nResCols = len(dfResults1.columns)


###############################################################################
#                                                                             #
#                                                                             #
#                                                                             #
###############################################################################



"""
    3. Feature Scores - Middle-left (Full Breakdown) 
"""
# Meeple Scores
dfMeepleScores = dfStats[['Player','CompleteCityScore','CompleteRoadScore', 'CompleteMonasteryScore', 'IncompleteCityScore', 'IncompleteRoadScore', 'IncompleteMonasteryScore', 'FarmScore']]
Total = dfMeepleScores[list(dfMeepleScores.columns)[1:]].sum(axis=1)
dfMeepleScores.loc[:,'Total'] = Total
dfAvgMeepleScores = dfMeepleScores.groupby('Player',as_index=False).mean()
dfAvgMeepleScores = dfAvgMeepleScores.melt('Player', var_name='Feature', value_name='Scores').sort_values(['Player','Feature']).reset_index(drop=True)
# feature types
conditions = [
    (dfAvgMeepleScores['Feature'].str.contains("City")),
    (dfAvgMeepleScores['Feature'].str.contains("Road")),
    (dfAvgMeepleScores['Feature'].str.contains("Monastery")),
    (dfAvgMeepleScores['Feature'].str.contains("Farm")),
    (dfAvgMeepleScores['Feature'].str.contains("Total"))
    ]
# create a list of the values we want to assign for each condition
values = ['City','Road','Monastery','Farm', 'Total']
dfAvgMeepleScores['FeatureType'] = np.select(conditions, values)
dfAvgMeepleScores['FeatureType'] = dfAvgMeepleScores['FeatureType']

# full breakdown 
dfAvgMeepleScoresFull = dfAvgMeepleScores[['Player','Feature','Scores']]
# specific feature types
conditions = [
    (dfAvgMeepleScoresFull['Feature'].str.contains("CompleteCityScore")),
    (dfAvgMeepleScoresFull['Feature'].str.contains("IncompleteCityScore")),
    (dfAvgMeepleScoresFull['Feature'].str.contains("CompleteRoadScore")),
    (dfAvgMeepleScoresFull['Feature'].str.contains("IncompleteRoadScore")),
    (dfAvgMeepleScoresFull['Feature'].str.contains("CompleteMonasteryScore")),
    (dfAvgMeepleScoresFull['Feature'].str.contains("IncompleteMonasteryScore")),
    (dfAvgMeepleScoresFull['Feature'].str.contains("Farm")),
    (dfAvgMeepleScoresFull['Feature'].str.contains("Total"))
    ]
values = ['City (C)', 'City (INC)', 'Road (C)', 'Road (INC)', 'Monastery (C)', 'Monastery (INC)', 'Farm', 'Total']
dfAvgMeepleScoresFull['FeatureType'] = np.select(conditions, values)
dfAvgMeepleScoresFull = dfAvgMeepleScoresFull.round(1)

###############################################################################
#                                                                             #
#                                                                             #
#                                                                             #
###############################################################################


"""
    3.A.  Feature Scores by Feature - Middle-left
"""
# Meeple Scores by feature
dfAvgMeepleScoresByFeature = dfAvgMeepleScores.groupby(['Player','FeatureType']).sum().reset_index(drop=False)
dfAvgMeepleScoresByFeature = dfAvgMeepleScoresByFeature.round(1)

###############################################################################
#                                                                             #
#                                                                             #
#                                                                             #
###############################################################################



"""
    3.B. Feature Scores - Middle-left (Percent)
"""
# percentages
dfMeepleScoresPercent = dfMeepleScores.copy(deep=True)
cols = ['CompleteCityScore','CompleteRoadScore', 'CompleteMonasteryScore', 'IncompleteCityScore', 'IncompleteRoadScore', 'IncompleteMonasteryScore','FarmScore']
dfMeepleScoresPercent.loc[:,cols] = dfMeepleScoresPercent.loc[:,cols].divide(dfMeepleScoresPercent.loc[:,"Total"]/100, axis="index")
dfMeepleScoresPercent = dfMeepleScoresPercent.groupby('Player',as_index=False).mean()
dfMeepleScoresPercent = dfMeepleScoresPercent.melt('Player', var_name='Feature', value_name='Scores').sort_values(['Player','Feature']).reset_index(drop=True)
# feature types
conditions = [
    (dfMeepleScoresPercent['Feature'].str.contains("City")),
    (dfMeepleScoresPercent['Feature'].str.contains("Road")),
    (dfMeepleScoresPercent['Feature'].str.contains("Monastery")),
    (dfMeepleScoresPercent['Feature'].str.contains("Farm")),
    (dfMeepleScoresPercent['Feature'].str.contains("Total"))
    ]
# create a list of the values we want to assign for each condition
values = ['City','Road','Monastery','Farm', 'Total']
dfMeepleScoresPercent['FeatureType'] = np.select(conditions, values)

# full breakdown 
dfMeepleScoresPercentFull = dfMeepleScoresPercent[['Player','Feature','Scores']]
# specific feature types
conditions = [
    (dfMeepleScoresPercentFull['Feature'].str.contains("CompleteCityScore")),
    (dfMeepleScoresPercentFull['Feature'].str.contains("IncompleteCityScore")),
    (dfMeepleScoresPercentFull['Feature'].str.contains("CompleteRoadScore")),
    (dfMeepleScoresPercentFull['Feature'].str.contains("IncompleteRoadScore")),
    (dfMeepleScoresPercentFull['Feature'].str.contains("CompleteMonasteryScore")),
    (dfMeepleScoresPercentFull['Feature'].str.contains("IncompleteMonasteryScore")),
    (dfMeepleScoresPercentFull['Feature'].str.contains("Farm")),
    (dfMeepleScoresPercentFull['Feature'].str.contains("Total"))
    ]
values = ['City (C)', 'City (INC)', 'Road (C)', 'Road (INC)', 'Monastery (C)', 'Monastery (INC)', 'Farm', 'Total']
dfMeepleScoresPercentFull['FeatureType'] = np.select(conditions, values)
dfMeepleScoresPercentFull = dfMeepleScoresPercentFull.round(1)



###############################################################################
#                                                                             #
#                                                                             #
#                                                                             #
###############################################################################


"""
    3.C.  Feature Scores by Feature - Middle-left (Percent)
"""
# Meeple Scores by feature
dfMeepleScoresPercentByFeature = dfMeepleScoresPercent.groupby(['Player','FeatureType']).sum().reset_index(drop=False)
dfMeepleScoresPercentByFeature = dfMeepleScoresPercentByFeature.round(1)


###############################################################################
#                                                                             #
#                                                                             #
#                                                                             #
###############################################################################

"""
    4. Meeple Placement - middle-right
"""    
# Meeple Placement
colsMeeple = ['Player', 'Feature', 'Turns']
df1 = pd.DataFrame(columns=colsMeeple)

dfMeepleFeatures = dfStats[['Player','MeeplesPlayed','MeepleTurns','MeepleFeatures']]
for player in (dfMeepleFeatures['Player'].unique()):
    df = dfMeepleFeatures[dfMeepleFeatures['Player'] == player]
    
    locations = df['MeepleFeatures'].values.tolist()
    locationsAll = [item for sublist in locations for item in sublist]
    
    turns = df['MeepleTurns'].values.tolist()
    turnsAll = [item for sublist in turns for item in sublist]
    df_temp = pd.DataFrame({'Player': len(locationsAll)*[player],
                            'Feature': locationsAll,
                            'Turns': turnsAll})
    df1 = df1.append(df_temp)

dfTotalPlacements = pd.crosstab(df1['Player'], df1['Feature'])
dfAvgPlacements = (dfTotalPlacements/TOTAL_GAMES).reset_index(drop=False)
Total = dfAvgPlacements[list(dfAvgPlacements.columns)[1:]].sum(axis=1)
dfAvgPlacements.loc[:,'Total'] = Total
dfAvgPlacementsFinal = dfAvgPlacements.melt('Player', var_name='Feature', value_name='Number').sort_values(['Player','Feature']).reset_index(drop=True)
dfAvgPlacementsFinal = dfAvgPlacementsFinal.round(1)
# fix feature names
conditions = [
    (dfAvgPlacementsFinal['Feature'] == 'C'),
    (dfAvgPlacementsFinal['Feature'] == 'G'),
    (dfAvgPlacementsFinal['Feature'] == 'R'),
    (dfAvgPlacementsFinal['Feature'] == 'Monastery'),
    (dfAvgPlacementsFinal['Feature'] == 'Total'),
    ]
# create a list of the values we want to assign for each condition
values = ['City','Road','Farm','Monastery','Total']
dfAvgPlacementsFinal['Feature'] = np.select(conditions, values)  

###############################################################################
#                                                                             #
#                                                                             #
#                                                                             #
###############################################################################


"""
    4.A. Meeple Placement - Middle-right (percent)
"""
dfAvgPlacementsPercent = dfAvgPlacements.copy(deep=True)
cols = ['C','G', 'Monastery', 'R']
cols=list(set(dfAvgPlacementsPercent.columns).intersection(cols))
dfAvgPlacementsPercent.loc[:,cols] = dfAvgPlacementsPercent.loc[:,cols].divide(dfAvgPlacementsPercent.loc[:,"Total"]/100, axis="index")
dfAvgPlacementsPercent = dfAvgPlacementsPercent.melt('Player', var_name='Feature', value_name='Number').sort_values(['Player','Feature']).reset_index(drop=True)
dfAvgPlacementsPercent = dfAvgPlacementsPercent.round(1)
# fix feature names
conditions = [
    (dfAvgPlacementsPercent['Feature'] == 'C'),
    (dfAvgPlacementsPercent['Feature'] == 'G'),
    (dfAvgPlacementsPercent['Feature'] == 'R'),
    (dfAvgPlacementsPercent['Feature'] == 'Monastery'),
    (dfAvgPlacementsPercent['Feature'] == 'Total'),
    ]
# create a list of the values we want to assign for each condition
values = ['City','Road','Farm','Monastery','Total']
dfAvgPlacementsPercent['Feature'] = np.select(conditions, values)



###############################################################################
#                                                                             #
#                                                                             #
#                                                                             #
###############################################################################



"""
    5. MCTS stats - Bottom-left
"""

# MCTS figure

simulations = dfMCTS['Simulations'].values[0]
dfMCTS_fig = dfMCTS[['Name','Turn','TimeTaken']].groupby(['Name','Turn'], as_index=False).mean()

fig_MCTS = px.line(dfMCTS_fig, x="Turn", y="TimeTaken", color="Name",
                   line_group="Name", hover_name="TimeTaken",
                   labels = {
                     "Turn": "Turn",
                     "TimeTaken": "Avg. Time Taken (secs)"
                     },
                   title = f'Avg. Time Taken per Turn (Simulations = {simulations})')

fig_MCTS.update_layout(legend=dict(orientation="h", 
                                   yanchor="bottom", y=1.02,xanchor="right",x=1),
                                   margin=dict(l=60, r=20, t=80, b=20)
                                   )
fig_MCTS.update_traces(mode="markers+lines", hovertemplate=None)
fig_MCTS.update_layout(hovermode="x unified")

###############################################################################
#                                                                             #
#                                                                             #
#                                                                             #
###############################################################################



"""
    6. MCTS stats - Bottom-right
"""
"""
# Expectimax figure
depth = dfMax['MaxDepth'].values[0]
dfMax_fig = dfMax[['Name','Turn','NodesVisited']].groupby(['Name','Turn'], as_index=False).mean()

fig_Max = px.line(dfMax_fig, x="Turn", y="NodesVisited", color="Name",
                   line_group="Name", hover_name="NodesVisited",
                   labels = {
                       "Turn": "Turn",
                       "NodesVisited": "Avg. Number of Nodes Visited"
                     },
                   title = f'Avg. Number of Nodes Visited per Turn (Depth = {depth})')

fig_Max.update_layout(legend=dict(orientation="h", 
                                   yanchor="bottom", y=1.02,xanchor="right",x=1),
                                   margin=dict(l=60, r=20, t=80, b=20)
                                   )
fig_Max.update_traces(mode="markers+lines", hovertemplate=None)
fig_Max.update_layout(hovermode="x unified")
"""




###############################################################################
#                                                                             #
#                                                                             #
#                                                                             #
###############################################################################



# player option list 
OPTIONS = []
playerList = dfLeague['Player']  # all players

for player in playerList:
    OPTIONS.append({"label":player, "value":player})
    

###############################################################################
#                                                                             #
#                                                                             #
#                                                                             #
###############################################################################

# Initialise the app
app = dash.Dash(__name__)

# Define the app
app.layout = html.Div(children=[
                      html.Div(className='row',  # Define the row element
                               children=[
                                  html.Div(className='two columns div-user-controls',  # Define the left element
                                           children = [  
                                               html.H2('Carcassonne - \nAI Stats '),
                                               html.P('''Visualising Player Stats with Plotly - Dash'''),
                                               html.P('''Pick one or more players from the dropdown below.'''),
                                               # players names
                                               dcc.Dropdown(id = 'Players', options=OPTIONS, multi = True, 
                                                            placeholder="Select Player(s)"
                                                            )
                                            ]),  
                                  
                                  html.Div(className='five columns div-for-charts bg-grey',   # Define the right element
                                           children = [
                                               html.H2('League Table'),
                                               dcc.Graph(id='leagueTable'),
                                               
                                               html.P(''),  # gap
                                               html.P(''),  # gap
                                               html.P(''),  # gap
                                               html.H2('Player Average Score Statistics'),
                                               html.P('''Select to view the scores as totals or as percentages (per player):'''),
                                               dcc.Dropdown(id="Score", options=[{'label':'Total','value':'Total'},
                                                                                 {'label':'Total (Full Feature Breakdown)','value':'Total_Full'},
                                                                                 {'label':'Percent','value':'Percent'},
                                                                                 {'label':'Percent (Full Feature Breakdown)','value':'Percent_Full'}]
                                                            ,value='Total',clearable=False),
                                               dcc.Graph(id="bar-chart-score"),
                                               
                                               
                                               html.P(''),  # gap
                                               html.P(''),  # gap
                                               html.P(''),  # gap
                                               html.H2('MCTS Statistics'),
                                               dcc.Graph(id="mcts", figure = fig_MCTS)
                                               
                                           ]),
                                  
                                  html.Div(className='five columns div-for-charts bg-grey',
                                           children = [
                                               html.H2('Results Matrix'),
                                               dcc.Graph(id='resultsMatrix'),
                                               
                                               html.P(''),  # gap
                                               html.P(''),  # gap
                                               html.P(''),  # gap
                                               html.H2('Player Average Meeple Statistics'),
                                               html.P('''Select to view the numbers as totals or as percentages (per player):'''),
                                               dcc.Dropdown(id="Features", options=[{'label':'Total','value':'Total'},{'label':'Percent','value':'Percent'}],value='Total',clearable=False),
                                               dcc.Graph(id="bar-chart-meeple"),
                                               
                                               html.P(''),  # gap
                                               html.P(''),  # gap
                                               html.P(''),  # gap
                                               html.H2('Expectimax Statistics'),
                                               #dcc.Graph(id="expectimax", figure = fig_Max)
                                               ]
                                           )
                                  ])
                                ])

###############################################################################
#                                                                             #
# League Table                                                                #
#                                                                             #
###############################################################################




@app.callback(Output('leagueTable', 'figure'),
              [Input('Players', 'value')])
def UpdateTableColours(Players):
    # initialize colour
    mapColor = {}
    
    # change colours of selected players
    if Players is not None:
        i=0
        # make it a list
        if not isinstance(Players, list): Players = [Players]
        Players = sorted(Players)  # sort alphabetically
        for player in Players:
            mapColor[player] = COLORS[i]
            i += 1 
    else:
        Players = []
    
    # all players in table
    AllPlayers = dfLeague.Player.values
    
    # league table, top-left
    figure = go.Figure(
        data = go.Table(
            columnwidth = [5, 12, 15, 8, 6, 6, 4, 4, 4, 9],
        
            header = dict(values = list(dfLeague.columns),
                          line = dict(color='rgb(50, 50, 50)'),
                          align = ['left'] * 10,
                          font = dict(color=['rgb(45, 45, 45)'] * 10, size=14),
                          fill = dict(color='#d562be')
                          ),
        
            cells = dict(values=[dfLeague.Pos, dfLeague.Player, dfLeague.MatchesPlayed, dfLeague.Points, dfLeague.BWP,
                                 dfLeague.BLP, dfLeague.W, dfLeague.L, dfLeague.D, dfLeague.PD],
                         align = ['left'] * 10,
                         font = dict(color=['rgb(40, 40, 40)'] * 10, size=12),
                         height = 27,
                         fill = dict(color=[[mapColor[player] if (player in Players) else 'rgb(242,242,242)' for player in AllPlayers]])
                         )
            )
        )
    
    figure.update_layout(
        height=min(50+len(AllPlayers)*30, 300), 
        margin=dict(r=10, l=10, t=0, b=20))
    
    return figure



###############################################################################
#                                                                             #
# Results Matrix                                                              #
#                                                                             #
###############################################################################


@app.callback(
    Output("resultsMatrix", "figure"), 
    [Input("Players", "value")])
def UpdateResultsMatrix(Players):
    # colour cell fill 
    colorFill = dict(color=['rgb(235, 193, 238)', 'rgba(228, 222, 249, 0.65)'])
    
    # results matrix, top-right
    figure = go.Figure(
        data = go.Table(        
            #domain=dict(x=[0, 0.48],y=[0.0, 0.48]),
            header = dict(values = list(dfResults1.columns),
                          line = dict(color='rgb(50, 50, 50)'),
                          align = ['left'] * nResCols,
                          font = dict(color=['rgb(45, 45, 45)'] * nResCols, size=12),
                          fill = dict(color='#d562be')),
            cells = dict(values=[dfResults1[k].tolist() for k in dfResults1.columns],
                         align = ['left'] * nResCols,
                         font = dict(color=['rgb(40, 40, 40)'] * nResCols, size=12),
                         height = 27,
                         fill = colorFill)
            )
        )
    
    figure.update_layout(
            height=min(50+len(playerList)*30, 300), 
            margin=dict(r=10, l=10, t=0, b=20))
    
    return figure


###############################################################################
#                                                                             #
# Player Scores                                                               #
#                                                                             #
###############################################################################


@app.callback(
    Output("bar-chart-score", "figure"), 
    [Input("Players", "value"),
     Input("Score", "value")])
def update_bar_chart(Players, Score):
    print(Players)
    # show total scores or percentage scores
    if Score == 'Total':
        df = dfAvgMeepleScoresByFeature
        title = "Average Scores Per Feature"
        label = "Avg. Scores"
        
    elif Score == 'Total_Full':
        df = dfAvgMeepleScoresFull
        title = "Average Scores Per Feature - Complete and Incomplete Features"
        label = "Avg. Scores"
        
    elif Score == 'Percent':
        df = dfMeepleScoresPercentByFeature[dfMeepleScoresPercentByFeature['FeatureType'] != 'Total']
        title = "Percentage of Scores Per Feature"
        label = "Feature Scores Percentage (%)"
        
    elif Score == 'Percent_Full':
        df = dfMeepleScoresPercentFull[dfMeepleScoresPercentFull['Feature'] != 'Total']
        title = "Percentage of Scores Per Feature - Complete and Incomplete Features"
        label = "Feature Scores Percentage (%)"
        
    # filter by players
    if Players is None or Players==[]:
        df = df
    else:
        df = df[df['Player'].isin(Players)]
        
    # create bar chart    
    fig = px.bar(df, x="FeatureType", y="Scores",color="Player", barmode="group",
                 text = "Scores",
                 labels = {
                     "Scores": label,
                     "FeatureType": "Feature"
                     },
                 hover_data = {'Player':True, 'Scores':True, 'FeatureType':True},
                 title = title)
    # legend position
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02,xanchor="right",x=1),
                      margin=dict(l=40, r=20, t=80, b=20),
                      xaxis={'categoryorder':'category ascending'})    
    return fig

###############################################################################
#                                                                             #
# Player Meeples                                                              #
#                                                                             #
###############################################################################


@app.callback(
    Output("bar-chart-meeple", "figure"), 
    [Input("Players", "value"),
     Input("Features", "value")])
def update_bar_chart_1(Players, Features):
    # show total scores or percentage scores
    if Features == 'Total':
        df = dfAvgPlacementsFinal
        title = "Average Meeples Per Feature"
        label = "Avg. Number"
    elif Features == 'Percent':
        df = dfAvgPlacementsPercent[dfAvgPlacementsPercent['Feature'] != 'Total']
        title = "Percentage of Meeples Per Feature"
        label = "Feature Numbers Percentage (%)"
    
    # players
    if Players is None:
        df = df
    else:
        df = df[df['Player'].isin(Players)]
        
    # create bar chart
    fig = px.bar(df, x="Feature", y="Number", color="Player", barmode="group",
                 text = "Number",
                 labels = {
                     "Number": label,
                     },
                 title = title)
    # legend position
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02,xanchor="right",x=1),
                      margin=dict(l=40, r=20, t=80, b=20),
                      xaxis={'categoryorder':'category ascending'})   
    
    return fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
