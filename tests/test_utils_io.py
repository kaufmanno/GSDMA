import unittest
import pandas as pd
import pandas.testing as pdt
import numpy as np

import utils.io


class MyTestCase(unittest.TestCase):
    def test_gdf_merger_positions(self):
        df1 = pd.DataFrame({'ID': ['id1', 'id2', 'id3', 'id4', 'id5', 'id6', 'id8', np.nan, np.nan],
                           'X': [152890, np.nan, 152821, np.nan, 152875, 152885, 152810, 152861, np.nan],
                           'Y': [122596, np.nan, 122512, np.nan, 122575, 122581, 122556, 122523, np.nan]})
        df2 = pd.DataFrame({'ID': ['id1', 'id2', 'id3', 'id4', 'id5', 'id6', 'id7'],
                           'X': [152890, 152885, np.nan, np.nan, 152875, 152895, 152861],
                           'Y': [122596, 122500, np.nan, np.nan, 122576, 122581, 122546]})
        actual_df, df_conflicts = utils.io.gdf_merger(df1, df2, how='outer', on='ID', dist_max=2.)
        actual_df.set_index('ID', inplace=True)
        # actual_df=actual_df[['ID', 'X', 'Y']]
        expected_df = pd.DataFrame({'ID': ['id1', 'id2', 'id3', 'id4', 'id5', '_id6_', 'id6', 'id7', 'id8', '?0', '?1'],
                                   'X': [152890, 152885, 152821, np.nan, 152875, 152885, 152895, 152861, 152810, 152861, np.nan],
                                   'Y': [122596, 122500, 122512, np.nan, 122575, 122581, 122581, 122546, 122556, 122523, np.nan]})
            #               'index' : [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            #               'split_index' : [False, False, False, False, False, False, False, False, False, False]})
        expected_df.set_index('ID', inplace=True)
        print(f'actual dataframe:\n{actual_df}\n\n', f'expected dataframe:\n{expected_df}')
        pdt.assert_frame_equal(actual_df, expected_df, check_like=True, check_names=False)


if __name__ == '__main__':
    unittest.main()
