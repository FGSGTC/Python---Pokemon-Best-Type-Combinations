import pandas as pd
import random as rd
import numpy as np
import math as ma
import datetime as dt


StartTime = dt.datetime.now()

Runs = 0
NewRuns = 1
SummaryFile = 'DualTypeSimulationSummary'

# Generates lists to iterate through.
Targets = ['U', 'O']
Stats = ['HP', 'Atk', 'Def', 'SpA', 'SpD', 'Spe']
PokemonKeys = ['Type1', 'Type2', 'StartHP', 'CurrentHP', 'CurrentAtk', 'CurrentDef', 'CurrentSpA', 'CurrentSpD',
               'CurrentSpe', 'Rating', 'DamageInflicted', 'DamageReceived', 'IsActive', 'TrainerID', 'PokemonID']

# Updates a chosen value for an active Pokemon in the Teams data frame.
def targetupdate(target, key, value):
    T[target][key] = value
    dfPokemon.at[T[target]['PokemonID'] - 1, key] = T[target][key]
    global dfActive
    dfActive = dfPokemon.loc[dfPokemon['IsActive'] == True]


# Calculates the effectiveness of the move against the opponents types.
def typematchup(attackingtype):
    typemultiplier = 1
    for multiplier in range(1, 3):
        typemultiplier = typemultiplier * \
                         dfTypes.loc[(dfTypes['AttackingType'] == attackingtype) &
                                     (dfTypes['DefendingType'] == T['O']['Type' + str(multiplier)]),
                                     'Effectiveness'].iloc[0]
    return typemultiplier

for r in range(Runs + 1, Runs + NewRuns + 1):

    # Imports files.
    dfTypes = pd.read_csv('Types.csv')
    dfPokemon = pd.read_csv('BaseStatsTypeAverage.csv')
    dfSetList = pd.read_csv('DualTypeSetList.csv')

    dfPokemon['CurrentHP'] = 2 * dfPokemon['BaseHP'] + 141
    for s in Stats[1:]:
        dfPokemon['Current' + s] = 2 * dfPokemon['Base' + s] + 36
    dfPokemon['Rating'] = 0
    dfPokemon['DamageInflicted'] = 0
    dfPokemon['DamageReceived'] = 0
    dfPokemon['PokemonID'] = np.arange(len(dfPokemon)) + 1
    dfPokemon['IsActive'] = 0
    dfPokemon['TrainerID'] = 0
    dfPokemon['StartHP'] = dfPokemon['CurrentHP']

    Run = str(r)
    NoDamage = 0
    x = 0

    for T1Type1, T1Type2, T2Type1, T2Type2 in zip(dfSetList['T1Type1'], dfSetList['T1Type2'],
                                                  dfSetList['T2Type1'], dfSetList['T2Type2']):

        x += 1
        print('Round: ' + str(x), T1Type1 + '/' + T1Type2 + ' & ' + T2Type1 + '/' + T2Type2)

        dfPokemon['CurrentHP'] = dfPokemon['StartHP']
        dfPokemon['IsActive'] = 0
        dfPokemon.loc[(dfPokemon['Type1'] == T1Type1) & (dfPokemon['Type2'] == T1Type2), 'IsActive'] = 1
        dfPokemon.loc[(dfPokemon['Type1'] == T1Type1) & (dfPokemon['Type2'] == T1Type2), 'TrainerID'] = 1
        dfPokemon.loc[(dfPokemon['Type1'] == T2Type1) & (dfPokemon['Type2'] == T2Type2), 'IsActive'] = 1
        dfPokemon.loc[(dfPokemon['Type1'] == T2Type1) & (dfPokemon['Type2'] == T2Type2), 'TrainerID'] = 2
        dfActive = dfPokemon.loc[dfPokemon['IsActive'] == 1]

        while True:

            if NoDamage > 0:
                NoDamage = 0

            # Calculates which player will move first.
            T = {}
            MoveOrder = 1
            for Move in range(1, 3):
                T['Spe' + str(Move)] = dfActive.loc[dfActive['TrainerID'] == Move, 'CurrentSpe'].iloc[0]
            if T['Spe1'] < T['Spe2']:
                MoveOrder = 2
            elif T['Spe1'] == T['Spe2']:
                MoveOrder = rd.randint(1, 2)

            # Loops through move calculations for each player.
            for Trainer in range(MoveOrder, -3 * MoveOrder + 6, -2 * MoveOrder + 3):

                # Retrieves stats used for turn calculations.
                T = {'U': {}, 'O': {}}
                for Key in PokemonKeys:
                    T['U'][Key] = dfActive.loc[dfActive['TrainerID'] == Trainer, Key].iloc[0]
                    T['O'][Key] = dfActive.loc[dfActive['TrainerID'] == -1 * Trainer + 3, Key].iloc[0]

                if T['U']['Type2'] == 'Typeless':
                    if typematchup(T['U']['Type1']) == 0:
                        NoDamage += 1
                else:
                    if typematchup(T['U']['Type1']) + typematchup(T['U']['Type2']) == 0:
                        NoDamage += 1

                # Calculates a random percentage to modify any direct damage by.
                MinMax = rd.randint(85, 100) / 100

                # Calculates and applies the total damage.
                if T['U']['Type2'] == 'Typeless':
                    Modifier = round(MinMax * typematchup(T['U']['Type1']) * 1.5, 2)
                else:
                    Modifier = round(MinMax * max(typematchup(T['U']['Type1']), typematchup(T['U']['Type2'])) * 1.5, 2)
                Damage = 0
                Power = 60
                if T['U']['CurrentAtk'] > T['U']['CurrentSpA']:
                    Damage = ma.ceil((40 * Power * T['U']['CurrentAtk'] /
                                      (T['O']['CurrentDef'] * 50) + 2) * Modifier)
                elif T['U']['CurrentSpA'] > T['U']['CurrentAtk']:
                    Damage = ma.ceil((40 * Power * T['U']['CurrentSpA'] /
                                      (T['O']['CurrentSpD'] * 50) + 2) * Modifier)
                else:
                    if rd.randint(1, 2) == 1:
                        Damage = ma.ceil((40 * Power * T['U']['CurrentAtk'] /
                                          (T['O']['CurrentDef'] * 50) + 2) * Modifier)
                    else:
                        Damage = ma.ceil((40 * Power * T['U']['CurrentSpA'] /
                                          (T['O']['CurrentSpD'] * 50) + 2) * Modifier)

                targetupdate('O', 'CurrentHP', max(T['O']['CurrentHP'] - Damage, 0))
                targetupdate('O', 'DamageReceived', T['O']['DamageReceived'] + Damage)
                targetupdate('U', 'DamageInflicted', T['U']['DamageInflicted'] + Damage)

                if NoDamage == 2:
                    break

                if T['O']['CurrentHP'] == 0:
                    targetupdate('U', 'Rating', T['U']['Rating'] + 1)
                    targetupdate('U', 'IsActive', 0)
                    targetupdate('O', 'IsActive', 0)
                    DualTypeSimulationSummary = open(SummaryFile + Run + '.csv', 'w+')
                    DualTypeSimulationSummary.close()
                    dfPokemon.to_csv(SummaryFile + Run + '.csv', mode='a', header=True, index=False)
                    break

            if NoDamage == 2:
                break

            if T['O']['CurrentHP'] == 0:
                break

    dfPokemon['CurrentHP'] = dfPokemon['StartHP']
    dfPokemon = dfPokemon.drop(columns=['StartHP', 'IsActive', 'PokemonID', 'TrainerID'])
    Summary = open(SummaryFile + Run + '.csv', 'w+')
    Summary.close()
    dfPokemon.to_csv(SummaryFile + Run + '.csv', mode='a', header=True, index=False)

EndTime = dt.datetime.now()
ProcessTime = EndTime - StartTime
print('Process Time: ' + str(ProcessTime))
