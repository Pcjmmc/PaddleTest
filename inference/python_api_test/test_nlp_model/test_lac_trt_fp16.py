# -*- coding: utf-8 -*-
# encoding=utf-8 vi:ts=4:sw=4:expandtab:ft=python
"""
test lac model
"""

import os
import sys
import logging
import tarfile
import six
import wget
import pytest
import numpy as np

# pylint: disable=wrong-import-position
sys.path.append("..")
from test_case import InferenceTest

# pylint: enable=wrong-import-position


def check_model_exist():
    """
    check model exist
    """
    lac_url = "https://paddle-qa.bj.bcebos.com/inference_model_clipped/2.2.2/nlp/lac.tgz"
    if not os.path.exists("./lac/inference.pdiparams"):
        wget.download(lac_url, out="./")
        tar = tarfile.open("lac.tgz")
        tar.extractall()
        tar.close()


def test_config():
    """
    test combined model config
    """
    check_model_exist()
    test_suite = InferenceTest()
    test_suite.load_config(
        model_file="./lac/inference.pdmodel",
        params_file="./lac/inference.pdiparams",
    )
    test_suite.config_test()


@pytest.mark.win
@pytest.mark.server
@pytest.mark.trt_fp16
def test_lac_trt_fp16():
    """
    compared trt_fp16 lac outputs with true val
    """
    check_model_exist()

    test_suite = InferenceTest()
    test_suite.load_config(
        model_file="./lac/inference.pdmodel",
        params_file="./lac/inference.pdiparams",
    )
    in1 = np.random.randint(0, 100, (1, 20)).astype(np.int64)
    in2 = np.array([20]).astype(np.int64)
    input_data_dict = {"token_ids": in1, "length": in2}
    output_data_dict = test_suite.get_truth_val(input_data_dict, device="gpu")

    del test_suite  # destroy class to save memory

    test_suite1 = InferenceTest()
    test_suite1.load_config(
        model_file="./lac/inference.pdmodel",
        params_file="./lac/inference.pdiparams",
    )
    test_suite1.trt_more_bz_test(
        input_data_dict,
        output_data_dict,
        delta=1e-5,
        precision="trt_fp16",
        dynamic=True,
        tuned=True,
        min_subgraph_size=1,
        # see comments in test_lac_trt_fp32.py
        delete_op_list=["transpose_2.tmp_0_slice_0"],
    )

    del test_suite1  # destroy class to save memory

    test_suite2 = InferenceTest()
    test_suite2.load_config(
        model_file="./lac/inference.pdmodel",
        params_file="./lac/inference.pdiparams",
    )
    test_suite2.trt_more_bz_test(
        input_data_dict,
        output_data_dict,
        delta=1e-5,
        precision="trt_fp16",
        dynamic=True,
        tuned=False,
        min_subgraph_size=1,
        # see comments in test_lac_trt_fp32.py
        delete_op_list=["transpose_2.tmp_0_slice_0"],
    )
