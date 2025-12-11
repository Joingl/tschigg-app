import streamlit as st
import tschigg as gg
import polars as pl
import json

with open('values_low.json', 'r') as file:
    values_low = json.load(file)

with open('values_high_standard.json', 'r') as file:
    values_high_standard = json.load(file)

with open('values_high_special.json', 'r') as file:
    values_high_special = json.load(file)

# Initialize session state
if 'estimated' not in st.session_state:
    st.session_state['estimated'] = False

if 'wins' not in st.session_state:
    st.session_state['wins'] = 0

if 'mids' not in st.session_state:
    st.session_state['mids'] = 0

if 'losses' not in st.session_state:
    st.session_state['losses'] = 0

#st.set_page_config(layout="wide")

st.title('Tschigg Probability Estimator')
st.divider()

with st.container():
    col1, col2, col3 = st.columns(3)

    d1 = col1.number_input('Die 1', min_value=1, max_value=6, value=1, step=1, icon='🎲', width=150)
    d2 = col2.number_input('Die 2', min_value=1, max_value=6, value=1, step=1, icon='🎲', width=150)
    d3 = col3.number_input('Die 3', min_value=1, max_value=6, value=1, step=1, icon='🎲', width=150)
    roll = [d1, d2, d3]

    num_players = col1.number_input('Number of players', min_value=2, max_value=10, value=3, step=1, help='Total number of players, including you.', width=150)
    num_rolls = col2.number_input('Number of rolls', min_value=1, max_value=3, value=1, step=1, help='Max. number of rolls allowed per player.', width=150)
    num_games = col3.selectbox('Number of games', [10, 100, 1000, 10000, 100000], index=1, help='Number of simulated games used for probability estimation.', width=150)


    col2.space()
    if col2.button('Estimate probabilities'):
        estimate = True
        st.session_state['estimated'] = True
        st.session_state['wins'], st.session_state['mids'], st.session_state['losses'] = gg.run_simulation(roll=roll, num_players=num_players, num_rolls=num_rolls, num_games=num_games)

st.divider()

with st.container():
    scores = [gg.get_score(roll, mode='low'), gg.get_score(roll, mode='high_std'), gg.get_score(roll, mode='high_sp')]

    if st.session_state['estimated']:
        col1, col2, col3 = st.columns(3, width=250)
        col1.subheader(f'🎲{roll[0]}')
        col2.subheader(f'🎲{roll[1]}')
        col3.subheader(f'🎲{roll[2]}')

        wins = st.session_state['wins']
        mids = st.session_state['mids']
        losses = st.session_state['losses']

        col0 = ['Win', 'Mid', 'Loss', 'Total']
        col1 = [wins[0], mids[0], losses[0], wins[0] + mids[0] + losses[0]]
        col2 = [wins[1], mids[1], losses[1], wins[1] + mids[1] + losses[1]]
        col3 = [wins[2], mids[2], losses[2], wins[2] + mids[2] + losses[2]]

        number_format = st.selectbox('',['Probabilities', 'Absolute values'], index=0)

        df = pl.DataFrame({'Outcome': col0, f'Low (Score: {scores[0]})': col1, f'High Standard (Score: {scores[1]})': col2, f'High Special (Score: {scores[2]})': col3})
        df2 = df.with_columns(
    pl.col('Outcome'),
            (pl.col(f'Low (Score: {scores[0]})')/num_games),
            (pl.col(f'High Standard (Score: {scores[1]})')/num_games),
            (pl.col(f'High Special (Score: {scores[2]})')/num_games)
        )

        if number_format == 'Probabilities':
            st.data_editor(df2, column_config={
                f'Low (Score: {scores[0]})': st.column_config.ProgressColumn(
                    help='Lowest score wins',
                    format='percent'),
                f'High Standard (Score: {scores[1]})': st.column_config.ProgressColumn(
                    help='Highest score wins',
                    format='percent'),
                f'High Special (Score: {scores[2]})': st.column_config.ProgressColumn(
                    help='Highest score wins, 1s count as 100',
                    format='percent')

            })
        elif number_format == 'Absolute values':
            st.dataframe(df)

        st.info(f'The table shows the estimated probability of each outcome depending on the chosen strategy, estimated over {num_games} games.')
