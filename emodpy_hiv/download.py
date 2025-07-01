def download( experiment_id, local_output_path="", files_to_get=None ):
    """
    Download HIV output file(s) to local disk. Just gets ReportHIVByAgeAndGender.csv. Intended to be
    used command line: python -m emopyhiv.download <COMPS Experiment ID> <Optional Output Path> <Files To Get>
    Note that target files need to include "output/" if that's where they are.
    """
    from idmtools.core.platform_factory import Platform
    platform = Platform("Calculon", node_group="idm_48cores", priority="Highest")
    from idmtools_platform_comps.utils.download.download import DownloadWorkItem
    if files_to_get is None:
        files_to_get = ["output/ReportHIVByAgeAndGender.csv"]
    elif type(files_to_get) is str:
        files_to_get = files_to_get.split(',')

    print( f"Attempting to download {files_to_get} for experiment {experiment_id} into {local_output_path}." )
    dl_wi = DownloadWorkItem(
        related_experiments=[experiment_id],
        file_patterns=files_to_get,
        output_path=local_output_path,
    )
    dl_wi.run(wait_until_done=True, platform=platform)


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        print( "Usage: python -m emopyhiv.download <COMPS Experiment ID> <Optional Output Path> <Optional List Of Files To Get>" )
        sys.exit()
    download( sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else ""), (sys.argv[3] if len(sys.argv) == 4 else None) )
