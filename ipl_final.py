import streamlit as st
import numpy as np
import pandas as pd
import pydeck as pdk
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
page_bg_img = '''
<style>
body {
background-image: url("https://images.unsplash.com/flagged/photo-1593005510329-8a4035a7238f?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60");
background-size: cover;
}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)

DATA_URL1 = (
    "deliveries.csv"
)

DATA_URL2 = (
    "matches.csv"
)

DATA_URL3 = (
    "most_runs_average_strikerate.csv"
)

DATA_URL4= (
     "teamwise_home_and_away.csv"
)
st.title("Indian Premier League Stats")

@st.cache_data
def load_data(p):
    data = pd.read_csv(p)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis="columns", inplace=True)
    return data

def loadrows(p,nrows):
    data = pd.read_csv(p , nrows = nrows)
    return data

ball_by_ball_data = load_data(DATA_URL1)

matches_data = load_data(DATA_URL2)

batsman_data =load_data(DATA_URL3)

teams   =  matches_data.team1.unique()

homeaway = load_data(DATA_URL4)

##Team Stats
l=matches_data.season.unique()
l.sort()
l=list(l)
l.append('Overall')

st.sidebar.title("India Premier League")
st.sidebar.subheader("Choose Stats")

classifier = st.sidebar.selectbox("Stat Type", ("Team Stats", "Head to Head", "Top Run Scorers","Top Man of the Match Players","Top Wicket Takers"))

if classifier =="Team Stats":
    #if st.checkbox("Ball by Ball  Data", False):
        #st.subheader('Ball by Ball Data')
        #st.write(ball_by_ball_data)

    st.header("Team Stats")
    team   = st.selectbox('Select Team', teams)
    w = st.selectbox("Select Stat" ,("Season-wise stats","Home-Away Records"))
    if w=="Season-wise stats":
        select = st.selectbox('Select Season', l)

        data =  matches_data.loc[matches_data['team1']==team]
        data2 = matches_data.loc[matches_data['team2']==team]
        data = pd.concat([data,data2], ignore_index=True)
        if select!='Overall':
            data = data.loc[data['season']==select ]
        if len(data)==0:
            st.write('No matches played by',team, 'in season ',select)
        else:
            x=data['winner'].value_counts()
            st.write('Matches Played :', len(data))
            st.write('Won :',x[team])
            nr=0
            Won=x[team]
            if 'No Result' in x:
                nr=x['No Result']
                lost= len(data)-x[team]-nr
                st.write('Lost :',lost)
                st.write('No result :',nr)
            else:
                lost= len(data)-x[team]-nr
                st.write('Lost :',lost)
            st.write('Win Ratio :',round(Won/(Won+lost),3))
    else:
        d = homeaway.loc[homeaway['team']==team]
        homematches = d.iloc[0]['home_matches']
        homewins  = d.iloc[0]['home_wins']
        awaymatches = d.iloc[0]['away_matches']
        awaywins  = d.iloc[0]['away_wins']
        homeper = round(d.iloc[0]['home_win_percentage'],2)
        awayper = round(d.iloc[0]['away_win_percentage'],2)
        st.write("Home Matches Played : ",homematches," Home Matches Won :",homewins)
        st.write("Home Win percentage :",homeper)
        st.write("Away Matches Played : ",awaymatches,"Away Matches Won :",awaywins)
        st.write("Away Win percentage :",awayper)



#Head to Head
if classifier =="Head to Head":
    st.header("Head to Head")
    select1 = st.selectbox('Team 1', teams)
    select2 = st.selectbox('Team 2', teams)
    if select1==select2:
        st.write('Teams should not be same')
    else:
        matches= matches_data.loc[matches_data['team1']==select1]
        matches1= matches.loc[matches['team2']==select2]
        t=select1
        select1=select2
        select2=t
        matches2=matches_data.loc[matches_data['team1']==select1]
        matches2=matches2.loc[matches2['team2']==select2]
        if len(matches1)==0 and len(matches2)==0:
            st.write('No matches played between these two teams')
        else:
            matches1.append(matches2,ignore_index=True)
            ans=pd.concat([matches1,matches2],axis=0)
            y=ans['winner'].value_counts()
            st.write('Mathes Played :',len(ans))
            if select2 not in y:
                y[select2]=0
            if select1 not in y:
                y[select1]=0
            st.write(y[select2],'   :   ',y[select1])
            if 'No Result' in y:
                st.write('No result :','  ',y['No Result'])
                labels = [select2, select1,'No Result']
                sizes = [y[select2], y[select1], y['No Result']]
                explode = (0.1, 0.1 ,0.1)
                fig, ax = plt.subplots()
                ax.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')
                st.pyplot(fig)
            else:
                y['No Result'] = 0
                # Create a pie chart
                labels = [select2, select1]
                sizes = [y[select2], y[select1]]
                explode = (0, 0.1)
                fig, ax = plt.subplots()
                ax.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')
                st.pyplot(fig)

if classifier =="Top Run Scorers":
    #Leading Run_Scorers
    st.header("Top Run Scorers")
    select  =  st.slider("Select number of top Run Scorers", 1, 100 )
    st.markdown("Top %i Run Scorers" % (select))
    ans  =  loadrows(DATA_URL3,select)
    st.table(ans)



if classifier =="Top Man of the Match Players":
    #Man of the matches
    st.header('Top 10 Man Of the Match Players')
    select = st.selectbox('Select season',l)
    if select=='Overall':
        ans=matches_data['player_of_match'].value_counts()[:10]
    else:
        matches=matches_data.loc[matches_data['season']==select]
        ans=matches['player_of_match'].value_counts()[:10]

    st.table(ans)

if classifier=="Top Wicket Takers":
    # Most Wicket Holders
    st.header('Top Wicket Holders')
    select  =  st.slider("Select number of top Wicket Takers", 1, 100 )
    q= ball_by_ball_data.dropna(subset=['dismissal_kind'])

    q= q.loc[q.dismissal_kind!= 'run out']
    q= q.loc[q.dismissal_kind!= 'retired hurt']
    ans= q['bowler'].value_counts()[:select]
    Rank =np.arange(1,select+1)
    st.table(ans)
