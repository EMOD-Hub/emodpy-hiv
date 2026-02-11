import unittest
import os
import sys
import time

# Use non-interactive backend for testing to avoid tkinter issues
import matplotlib
matplotlib.use('Agg')

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

        # Use image comparison instead of byte comparison for PNGs
        # This handles matplotlib version differences and metadata changes
        if file_extension == ".png":
            self._compare_png_images(exp_image_filenames, act_dir)
        else:
            # For non-PNG files, use byte comparison
            for exp_fn in exp_image_filenames:
                exp_base_fn = os.path.basename(exp_fn)
                act_fn = os.path.join(act_dir, exp_base_fn)
                if not os.path.exists(act_fn):
                    raise ValueError(f"Image {act_fn} does not exist.")

                with open(exp_fn, "rb") as file:
                    exp_data = file.read()

                with open(act_fn, "rb") as file:
                    act_data = file.read()

                self.assertEqual(exp_data, act_data, f"File {exp_fn} does not match {act_fn}.")

        # If we reach this point, all images match
        # delete actual images
        for act_fn in act_image_filenames:
            os.remove(act_fn)
        os.removedirs(act_dir)

    def _compare_png_images(self, exp_filenames, act_dir):
        """Compare PNG images using image content, ignoring metadata differences."""
        try:
            from PIL import Image
            import numpy as np

            for exp_fn in exp_filenames:
                exp_base_fn = os.path.basename(exp_fn)
                act_fn = os.path.join(act_dir, exp_base_fn)
                if not os.path.exists(act_fn):
                    raise ValueError(f"Image {act_fn} does not exist.")

                # Load images and compare pixel data
                exp_img = Image.open(exp_fn)
                act_img = Image.open(act_fn)

                # Convert to numpy arrays for comparison
                exp_array = np.array(exp_img)
                act_array = np.array(act_img)

                # Check shape matches
                self.assertEqual(exp_array.shape, act_array.shape,
                               f"Image shapes don't match for {exp_base_fn}")

                # Calculate difference with tolerance for minor rendering differences
                # Allow small differences due to matplotlib version changes
                diff = np.abs(exp_array.astype(float) - act_array.astype(float))
                max_diff = np.max(diff)
                mean_diff = np.mean(diff)

                # Allow small differences (tolerance of 2 out of 255 for pixel values)
                self.assertLess(max_diff, 3.0,
                              f"Max pixel difference too large for {exp_base_fn}: {max_diff}")
                self.assertLess(mean_diff, 0.5,
                              f"Mean pixel difference too large for {exp_base_fn}: {mean_diff}")

        except ImportError:
            # If PIL is not available, fall back to byte comparison with a warning
            import warnings
            warnings.warn("PIL not available, using byte comparison which may fail with "
                        "matplotlib version differences. Install Pillow for better PNG comparison.")
            for exp_fn in exp_filenames:
                exp_base_fn = os.path.basename(exp_fn)
                act_fn = os.path.join(act_dir, exp_base_fn)
                with open(exp_fn, "rb") as file:
                    exp_data = file.read()
                with open(act_fn, "rb") as file:
                    act_data = file.read()
                self.assertEqual(exp_data, act_data, f"File {exp_fn} does not match {act_fn}.")
