import unittest
import pandas as pd
import pandas.testing as pdt
import numpy as np

import utils.io


class MyTestCase(unittest.TestCase):
    def test_gdf_merger(self):
        df1 = pd.DataFrame({'ID': ['id1', 'id2', 'id3', 'id4', 'id5', 'id6', 'id7', 'id8', np.nan, ],
                           'X': [152890, np.nan, 152821, 152815, 152875, 152885, 152810, 152861, 152800],
                           'Y': [122596, np.nan, 122512, 122565, 122575, 122581, 122556, 122523, 122546],
                           'Name': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'i'],
                           'Value': [1, 2, 3, 4, np.nan, 5, np.nan, 7, 8]})
        df2 = pd.DataFrame({'ID': ['id1', 'id2', 'id3', 'id4', 'id5', 'id6', 'id7', 'id8', np.nan, np.nan],
                           'X': [152890, 152885, 152821, 152865, 152875, np.nan, 152845, 152861, 152800, 152900],
                           'Y': [122596, 122500, 122556, 122565, 122575, np.nan, 122556, 122523, 122546, 122600],
                           'Name': ['A', 'B', 'D', 'C', 'E', 'F', 'G', 'h', 'i', 'k'],
                           'Value': [1, 3, 2, 4, np.nan, np.nan, 6, 7, 8, 9]})
        actual_df, df_err = utils.io.gdf_merger(df1, df2, how='outer', col_non_na=0, on='ID')
        actual_df.drop(['X_x', 'X_y', 'Y_x', 'Y_y', 'Value_x', 'Value_y', 'Name_x', 'Name_y'], axis='columns', inplace=True)
        actual_df=actual_df[['ID', 'X', 'Y', 'Name', 'Value']]
        expected_df = pd.DataFrame({'ID': ['id1', 'id2', 'id3', 'id4', 'id5', 'id6', 'id7', 'id8', np.nan, np.nan],
                           'X': [152890, 152885, 152821, np.nan, 152875, 152885, np.nan, 152861, 152800, np.nan],
                           'Y': [122596, 122500, np.nan, 122565, 122575, 122581, 122556, 122523, 122546, np.nan],
                           'Name': ['A', 'B', np.nan, np.nan, 'E', 'F', 'G', 'H', 'i', np.nan],
                           'Value': [1, np.nan, np.nan, 4, np.nan, 5, 6, 7, 8, np.nan]})
        print(actual_df, expected_df)
        pdt.assert_frame_equal(actual_df, expected_df)


if __name__ == '__main__':
    unittest.main()
