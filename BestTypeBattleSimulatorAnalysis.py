import pandas as pd
import datetime as dt

StartTime = dt.datetime.now()

Runs = 10
Columns = ['Type1', 'Type2', 'BaseHP', 'BaseAtk', 'BaseDef', 'BaseSpA', 'BaseSpD', 'BaseSpe',
           'CurrentHP', 'CurrentAtk', 'CurrentDef', 'CurrentSpA', 'CurrentSpD', 'CurrentSpe',
           'Rating', 'DamageInflicted', 'DamageReceived']

dfSummary = pd.DataFrame(columns=Columns)
dfRankings = pd.DataFrame()
for r in range(1, Runs + 1):
    dfRunSummary = pd.read_csv('DualTypeSimulationSummary' + str(r) + '.csv')
    dfRunSummary = dfRunSummary[dfRunSummary.columns.drop(Columns[2:14])]
    dfSummary = dfSummary.append(dfRunSummary)

dfSummary[Columns[-3:]] = dfSummary[Columns[-3:]].apply(pd.to_numeric, errors='coerce', axis=1)
dfSummary = dfSummary.groupby(['Type1', 'Type2']).mean()
dfSummary.reset_index(level=['Type1', 'Type2'], inplace=True)

dfSummary['Type'] = dfSummary['Type1'] + ' / ' + dfSummary['Type2']
dfSummary['Type'] = dfSummary['Type'].str.replace('/ Typeless', '')
dfSummary['WinRate'] = dfSummary['Rating'] / (len(dfSummary) - 1)
dfRankings['Rank'] = dfSummary['Rank'] = dfSummary.index
for s in Columns[-3:]:
    if s == 'DamageReceived':
        dfSummary = dfSummary.sort_values(s, ascending=True)
    else:
        dfSummary = dfSummary.sort_values(s, ascending=False)
    dfSummary = dfSummary.reset_index(drop=True)
    dfRankings['TypesBy' + s] = dfSummary['Type']
    dfRankings[s] = dfSummary[s]
    if s == 'Rating':
        dfRankings['WinRate'] = dfSummary['WinRate']

dfRankings = dfRankings.reset_index(drop=True)
dfRankings['Rank'] += 1
Rankings = open('DualTypeSimulationStats.csv', 'w+')
Rankings.close()
dfRankings.to_csv('DualTypeSimulationStats.csv', mode='a', header=True, index=False)

EndTime = dt.datetime.now()
ProcessTime = EndTime - StartTime
print('Process Time: ' + str(ProcessTime))
