import unittest
import os
import sys
import time

import emodpy_hiv.plotting.helpers as helpers


class PlotTestBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        #cls.output_dir = output_folder
        #if not os.path.isdir(cls.output_dir):
        #    os.makedirs(cls.output_dir)
        cls.test_folder = os.path.dirname(os.path.abspath(__file__))

    def setUp(self):
        print(f"running test: {self._testMethodName}:")
        self.start_time = time.perf_counter()

    def tearDown(self):
        end_time = time.perf_counter()
        elapsed_time = end_time - self.start_time
        print(f"Test {self._testMethodName} took {elapsed_time:.2f} seconds.")

    def compare_files(self, exp_dir: str, act_dir: str, file_extension: str=".png"):
        # ----------------------------------------------------------------------------
        # the windows and linux image files are different.  they look exactly the same
        # but the comparision is different.  I think it is a compression difference.
        # ----------------------------------------------------------------------------
        if sys.platform.startswith('linux'):
            exp_dir = exp_dir + "_linux"

        exp_image_filenames = helpers.get_filenames(dir_or_filename=exp_dir,
                                                    file_prefix="",
                                                    file_extension=file_extension)
        act_image_filenames = helpers.get_filenames(dir_or_filename=act_dir,
                                                    file_prefix="",
                                                    file_extension=file_extension)
        
        self.assertEqual(len(exp_image_filenames), len(act_image_filenames),
                         f"Number of images in {exp_dir} and {act_dir} do not match.")

        for exp_fn in exp_image_filenames:
            # Get the filename without the directory
            exp_base_fn = os.path.basename(exp_fn)
            # Construct the corresponding actual filename
            act_fn = os.path.join(act_dir, exp_base_fn)
            if not os.path.exists(act_fn):
                raise ValueError(f"Image {act_fn} does not exist.")

            with open( exp_fn, "rb") as file:
                exp_data = file.read()

            with open( act_fn, "rb") as file:
                act_data = file.read()

            self.assertEqual(exp_data, act_data, f"File {exp_fn} does not match {act_fn}.")
            
        # If we reach this point, all images match
        # delete actual images
        for act_fn in act_image_filenames:
            os.remove(act_fn) 
        os.removedirs(act_dir)
