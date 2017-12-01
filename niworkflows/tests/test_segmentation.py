# -*- coding: utf-8 -*-
""" Segmentation tests """

from __future__ import absolute_import, division, print_function, unicode_literals

import os
from shutil import copy
import pytest

from niworkflows.interfaces.segmentation import FASTRPT, ReconAllRPT
from niworkflows.interfaces.masks import BETRPT, BrainExtractionRPT, \
    SimpleShowMaskRPT


def _smoke_test_report(report_interface, artifact_name):
    report_interface.run()
    out_report = report_interface.inputs.out_report

    save_artifacts = os.getenv('SAVE_CIRCLE_ARTIFACTS', False)
    if save_artifacts:
        copy(out_report, os.path.join(save_artifacts, artifact_name))
    assert os.path.isfile(out_report), 'Report does not exist'


def test_BETRPT(moving):
    """ the BET report capable test """
    bet_rpt = BETRPT(generate_report=True, in_file=moving)
    _smoke_test_report(bet_rpt, 'testBET.svg')


def test_SimpleShowMaskRPT(oasis_dir):
    """ the BET report capable test """

    msk_rpt = SimpleShowMaskRPT(
        generate_report=True,
        background_file=os.path.join(oasis_dir, 'T_template0.nii.gz'),
        mask_file=os.path.join(oasis_dir, 'T_template0_BrainCerebellumRegistrationMask.nii.gz')
    )
    _smoke_test_report(msk_rpt, 'testSimpleMask.svg')


def test_BrainExtractionRPT(oasis_dir, moving, nthreads):
    """ test antsBrainExtraction with reports"""
    bex_rpt = BrainExtractionRPT(
        generate_report=True,
        dimension=3,
        use_floatingpoint_precision=1,
        anatomical_image=moving,
        brain_template=os.path.join(oasis_dir, 'T_template0.nii.gz'),
        brain_probability_mask=os.path.join(
            oasis_dir, 'T_template0_BrainCerebellumProbabilityMask.nii.gz'),
        extraction_registration_mask=os.path.join(
            oasis_dir, 'T_template0_BrainCerebellumRegistrationMask.nii.gz'),
        out_prefix='testBrainExtractionRPT',
        debug=True, # run faster for testing purposes
        num_threads=nthreads
    )
    _smoke_test_report(bex_rpt, 'testANTSBrainExtraction.svg')


@pytest.mark.parametrize("segments", [True, False])
def test_FASTRPT(segments, reference, reference_mask):
    """ test FAST with the two options for segments """
    from niworkflows.nipype.interfaces.fsl.maths import ApplyMask
    brain = ApplyMask(
        in_file=reference, mask_file=reference_mask).run().outputs.out_file
    fast_rpt = FASTRPT(
        in_files=brain,
        generate_report=True,
        no_bias=True,
        probability_maps=True,
        segments=segments,
        out_basename='test'
    )
    _smoke_test_report(
        fast_rpt, 'testFAST_%ssegments.svg' % ('no' * int(not segments)))


def test_ReconAllRPT():
    rall_rpt = ReconAllRPT(
        subject_id='fsaverage',
        directive='all',
        subjects_dir=os.getenv('SUBJECTS_DIR'),
        generate_report=True
    )
    rall_rpt.mock_run = True

    _smoke_test_report(rall_rpt, 'testReconAll.svg')
