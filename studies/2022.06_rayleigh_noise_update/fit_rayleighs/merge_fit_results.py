# importing pandas
import pandas as pd
import numpy as np

def remove_outliers(the_dataframe):
    the_dataframe.loc[the_dataframe.Fit > 1E-5, 'Fit'] = np.nan # remove tall peaks
    the_dataframe.loc[the_dataframe.Fit < 0, 'Fit'] = np.nan # remove negative numbers
    mask = np.isnan(the_dataframe.Fit)
    the_dataframe.Fit[mask] = np.interp(np.flatnonzero(mask), np.flatnonzero(~mask), the_dataframe.Fit[~mask])


base = pd.read_csv('sigmavsfreq_ch0.txt')
base.sort_values(by='Frequency', inplace=True)
base.drop(columns=['ChiSquare', 'Channel'], axis=1, inplace=True)
remove_outliers(base)


final_df = None

final_labels = ['Ch0']


for i in range(1, 16):
# for i in np.zeros(15):
    i = int(i)
    df_new = pd.read_csv('sigmavsfreq_ch{}.txt'.format(i))
    df_new.sort_values(by='Frequency', inplace=True)
    df_new.drop(columns=['ChiSquare', 'Channel'], axis=1, inplace=True)
    remove_outliers(df_new)
    print("Len df is {}".format( len(df_new['Fit'])))
    
    final_labels.append('Ch{}'.format(i))

    if final_df is None:
        print("Final DF is one, on i {}".format(i))
        final_df = pd.merge(base, df_new, on='Frequency')
        # final_df.set_index('Frequency', inplace=True)
    else:
        print("Final DF is NOT none, on i {}".format(i))
        final_df = pd.merge(final_df, df_new, on='Frequency')


final_df.set_index('Frequency', inplace=True)
final_df.drop_duplicates(inplace=True)
final_df.to_csv('test.txt', header=final_labels, float_format='%.3e')
